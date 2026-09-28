"""
==============================================================================
STREAMLIT REPORTING DASHBOARD: app.py
PROJECT: Mini Data Warehouse using DuckDB and Python
CASE STUDY: E-Commerce Sales Analytics Dashboard
==============================================================================
"""

import os
import sys
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Safe encoding configuration for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Page configuration
st.set_page_config(
    page_title="E-Commerce Sales Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #EFF6FF;
        color: #1D4ED8;
    }
</style>
""", unsafe_allow_html=True)

# Locate DuckDB database
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "duckdb", "ecommerce.duckdb")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "output", "reports")


@st.cache_resource
def get_db_connection():
    """Establishes read-only connection to DuckDB warehouse."""
    if not os.path.exists(DB_PATH):
        st.error(f"Database not found at: {DB_PATH}. Please run `python src/main.py` first.")
        st.stop()
    return duckdb.connect(database=DB_PATH, read_only=True)


def format_inr(val: float) -> str:
    """Formats numeric amount into Indian Rupee format (₹)."""
    if val is None or pd.isna(val):
        return "₹0.00"
    return f"₹{val:,.2f}"


def main():
    con = get_db_connection()

    # Title & Header
    st.markdown('<div class="main-header">🛒 E-Commerce Sales Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Mini Data Warehouse powered by <b>DuckDB</b>, <b>SQL Star Schema</b> & <b>Python</b></div>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------------------
    # SIDEBAR: WAREHOUSE FILTERS
    # -------------------------------------------------------------------------
    st.sidebar.header("🔍 Analytical Filters")

    # Fetch distinct filter values from warehouse view
    categories_all = [r[0] for r in con.execute("SELECT DISTINCT category FROM vw_order_details ORDER BY category").fetchall()]
    states_all = [r[0] for r in con.execute("SELECT DISTINCT state FROM vw_order_details ORDER BY state").fetchall()]
    statuses_all = [r[0] for r in con.execute("SELECT DISTINCT order_status FROM vw_order_details ORDER BY order_status").fetchall()]

    min_date = con.execute("SELECT MIN(order_date) FROM vw_order_details").fetchone()[0]
    max_date = con.execute("SELECT MAX(order_date) FROM vw_order_details").fetchone()[0]

    # Sidebar Filter Controls
    date_range = st.sidebar.date_input(
        "Order Date Range",
        value=(pd.to_datetime(min_date), pd.to_datetime(max_date)),
        min_value=pd.to_datetime(min_date),
        max_value=pd.to_datetime(max_date)
    )

    selected_categories = st.sidebar.multiselect("Product Category", options=categories_all, default=categories_all)
    selected_states = st.sidebar.multiselect("Customer State", options=states_all, default=states_all)
    selected_statuses = st.sidebar.multiselect("Order Status", options=statuses_all, default=statuses_all)

    # Construct dynamic SQL WHERE clause based on filters
    where_clauses = ["1=1"]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        where_clauses.append(f"order_date >= '{date_range[0]}' AND order_date <= '{date_range[1]}'")
    elif isinstance(date_range, tuple) and len(date_range) == 1:
        where_clauses.append(f"order_date >= '{date_range[0]}'")

    if selected_categories:
        cat_str = ", ".join([f"'{c}'" for c in selected_categories])
        where_clauses.append(f"category IN ({cat_str})")
    else:
        where_clauses.append("1=0")

    if selected_states:
        state_str = ", ".join([f"'{s}'" for s in selected_states])
        where_clauses.append(f"state IN ({state_str})")
    else:
        where_clauses.append("1=0")

    if selected_statuses:
        status_str = ", ".join([f"'{st_val}'" for st_val in selected_statuses])
        where_clauses.append(f"order_status IN ({status_str})")
    else:
        where_clauses.append("1=0")

    filter_sql = " AND ".join(where_clauses)

    # -------------------------------------------------------------------------
    # QUERY FILTERED DATASET
    # -------------------------------------------------------------------------
    filtered_query = f"""
    SELECT * FROM vw_order_details
    WHERE {filter_sql}
    """
    df_filtered = con.execute(filtered_query).fetchdf()

    # Calculate filtered KPIs
    if len(df_filtered) > 0:
        total_revenue = df_filtered["sales_amount"].sum()
        total_orders = df_filtered["order_id"].nunique()
        total_customers = df_filtered["customer_id"].nunique()
        total_units = df_filtered["quantity"].sum()
        avg_order_val = total_revenue / total_orders if total_orders > 0 else 0
    else:
        total_revenue = 0
        total_orders = 0
        total_customers = 0
        total_units = 0
        avg_order_val = 0

    # -------------------------------------------------------------------------
    # TOP KPI CARDS
    # -------------------------------------------------------------------------
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        st.metric(label="💰 Total Revenue", value=format_inr(total_revenue))
    with kpi_col2:
        st.metric(label="📦 Total Orders", value=f"{total_orders:,}")
    with kpi_col3:
        st.metric(label="👥 Total Customers", value=f"{total_customers:,}")
    with kpi_col4:
        st.metric(label="🏷️ Total Units Sold", value=f"{total_units:,}")
    with kpi_col5:
        st.metric(label="🎯 Avg Order Value", value=format_inr(avg_order_val))

    st.markdown("---")

    # -------------------------------------------------------------------------
    # DASHBOARD TABS
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Visual Analytics", 
        "🏛️ Data Warehouse & Views", 
        "💻 Live SQL Console (Viva Demo)", 
        "📁 Analytical Reports"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: VISUAL ANALYTICS
    # -------------------------------------------------------------------------
    with tab1:
        if len(df_filtered) == 0:
            st.warning("No records found matching the selected sidebar filters. Please adjust the filters.")
        else:
            # Row 1: Monthly Sales Trend & Category Revenue
            row1_col1, row1_col2 = st.columns([6, 4])

            with row1_col1:
                st.subheader("📈 1. Monthly Revenue Trend")
                monthly_trend_query = f"""
                SELECT 
                    strftime(order_date, '%Y-%m') AS month,
                    COUNT(DISTINCT order_id) AS orders,
                    SUM(quantity) AS units,
                    CAST(SUM(sales_amount) AS DOUBLE) AS revenue
                FROM vw_order_details
                WHERE {filter_sql}
                GROUP BY strftime(order_date, '%Y-%m')
                ORDER BY month ASC
                """
                df_monthly = con.execute(monthly_trend_query).fetchdf()

                fig_trend = px.line(
                    df_monthly,
                    x="month",
                    y="revenue",
                    markers=True,
                    labels={"month": "Month", "revenue": "Revenue (₹)"},
                    title="Monthly Sales Trajectory (2024)"
                )
                fig_trend.update_traces(line_color="#2563EB", line_width=3, marker=dict(size=8, color="#1E40AF"))
                fig_trend.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), hovermode="x unified")
                st.plotly_chart(fig_trend, use_container_width=True)

            with row1_col2:
                st.subheader("🍩 2. Revenue by Category")
                cat_query = f"""
                SELECT 
                    category,
                    CAST(SUM(sales_amount) AS DOUBLE) AS revenue
                FROM vw_order_details
                WHERE {filter_sql}
                GROUP BY category
                ORDER BY revenue DESC
                """
                df_cat = con.execute(cat_query).fetchdf()

                fig_cat = px.pie(
                    df_cat,
                    names="category",
                    values="revenue",
                    hole=0.45,
                    title="Category Share of Revenue",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_cat.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_cat, use_container_width=True)

            # Row 2: Top 5 Products, State Revenue, Order Status
            row2_col1, row2_col2, row2_col3 = st.columns([4, 4, 3])

            with row2_col1:
                st.subheader("🏆 3. Top 5 Products by Revenue")
                top_p_query = f"""
                SELECT 
                    product_name,
                    category,
                    SUM(quantity) AS units_sold,
                    CAST(SUM(sales_amount) AS DOUBLE) AS revenue
                FROM vw_order_details
                WHERE {filter_sql}
                GROUP BY product_name, category
                ORDER BY revenue DESC
                LIMIT 5
                """
                df_top_p = con.execute(top_p_query).fetchdf()

                fig_prod = px.bar(
                    df_top_p,
                    x="revenue",
                    y="product_name",
                    orientation="h",
                    color="category",
                    labels={"revenue": "Revenue (₹)", "product_name": "Product"},
                    title="Highest Grossing Products"
                )
                fig_prod.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_prod, use_container_width=True)

            with row2_col2:
                st.subheader("🗺️ 4. Revenue by State")
                state_query = f"""
                SELECT 
                    state,
                    COUNT(DISTINCT order_id) AS orders,
                    CAST(SUM(sales_amount) AS DOUBLE) AS revenue
                FROM vw_order_details
                WHERE {filter_sql}
                GROUP BY state
                ORDER BY revenue DESC
                LIMIT 8
                """
                df_state = con.execute(state_query).fetchdf()

                fig_state = px.bar(
                    df_state,
                    x="state",
                    y="revenue",
                    color="revenue",
                    color_continuous_scale="Blues",
                    labels={"state": "State", "revenue": "Revenue (₹)"},
                    title="Top States by Sales"
                )
                fig_state.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_state, use_container_width=True)

            with row2_col3:
                st.subheader("📦 5. Order Status")
                status_query = f"""
                SELECT 
                    order_status,
                    COUNT(DISTINCT order_id) AS order_count
                FROM vw_order_details
                WHERE {filter_sql}
                GROUP BY order_status
                ORDER BY order_count DESC
                """
                df_status = con.execute(status_query).fetchdf()

                fig_status = px.pie(
                    df_status,
                    names="order_status",
                    values="order_count",
                    title="Fulfillment Status",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_status.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_status, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 2: DATA WAREHOUSE & VIEWS EXPLORER
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("🏛️ Star Schema Warehouse Tables & Analytical Views")
        st.markdown(
            """
            This section allows inspecting the underlying **Dimensions**, **Facts**, and **Analytical Views** 
            stored in the local **DuckDB** database (`duckdb/ecommerce.duckdb`).
            """
        )

        view_choice = st.selectbox(
            "Select Warehouse Table or Analytical View to Inspect:",
            options=[
                "vw_order_details (Flattened Star-Schema View)",
                "vw_customer_sales (Customer Aggregations)",
                "vw_product_sales (Product Performance)",
                "vw_monthly_sales (Monthly Trends)",
                "dim_customer (Dimension)",
                "dim_product (Dimension)",
                "fact_order (Fact Table)",
                "fact_order_item (Fact Table)"
            ]
        )

        table_map = {
            "vw_order_details (Flattened Star-Schema View)": "vw_order_details",
            "vw_customer_sales (Customer Aggregations)": "vw_customer_sales",
            "vw_product_sales (Product Performance)": "vw_product_sales",
            "vw_monthly_sales (Monthly Trends)": "vw_monthly_sales",
            "dim_customer (Dimension)": "dim_customer",
            "dim_product (Dimension)": "dim_product",
            "fact_order (Fact Table)": "fact_order",
            "fact_order_item (Fact Table)": "fact_order_item"
        }

        selected_table = table_map[view_choice]
        df_view = con.execute(f"SELECT * FROM {selected_table} LIMIT 100").fetchdf()
        total_count = con.execute(f"SELECT COUNT(*) FROM {selected_table}").fetchone()[0]

        st.info(f"Displaying top 100 rows of **{selected_table}** (Total Records in Warehouse: **{total_count}**)")
        st.dataframe(df_view, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 3: LIVE SQL CONSOLE (VIVA DEMONSTRATION)
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("💻 Interactive DuckDB SQL Query Console")
        st.markdown(
            """
            Demonstrate real-time SQL querying against DuckDB tables and analytical views during your practical or viva.
            """
        )

        sample_queries = {
            "Multi-table Star-Schema JOIN": """SELECT 
    fo.order_id,
    fo.order_date,
    dc.customer_name,
    dc.city,
    dp.product_name,
    dp.category,
    foi.quantity,
    dp.price AS unit_price,
    (foi.quantity * dp.price) AS total_amount
FROM fact_order fo
JOIN fact_order_item foi ON fo.order_id = foi.order_id
JOIN dim_customer dc ON fo.customer_id = dc.customer_id
JOIN dim_product dp ON foi.product_id = dp.product_id
LIMIT 10;""",
            "Top 5 Product Categories by Revenue": """SELECT 
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    CAST(SUM(sales_amount) AS DECIMAL(12,2)) AS total_revenue
FROM vw_order_details
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 5;""",
            "Top 10 High Value Customers": """SELECT 
    customer_id,
    customer_name,
    city,
    state,
    total_orders,
    total_sales
FROM vw_customer_sales
ORDER BY total_sales DESC
LIMIT 10;""",
            "Monthly Sales Summary with Growth": """SELECT 
    month,
    total_orders,
    total_sales
FROM vw_monthly_sales
ORDER BY month ASC;"""
        }

        selected_sample = st.selectbox("Load Sample Practical Query:", list(sample_queries.keys()))
        user_query = st.text_area("SQL Query Editor:", value=sample_queries[selected_sample], height=180)

        if st.button("▶ Execute SQL Query", type="primary"):
            try:
                query_result = con.execute(user_query).fetchdf()
                st.success(f"Query executed successfully! ({len(query_result)} rows returned)")
                st.dataframe(query_result, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Error: {str(e)}")

    # -------------------------------------------------------------------------
    # TAB 4: EXPORTED ANALYTICAL REPORTS
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader("📁 Analytical Reporting Layer (Exported CSV Files)")
        st.markdown(
            """
            Pre-aggregated analytical reports generated by the Data Warehouse pipeline for business stakeholders.
            """
        )

        reports = [
            ("sales_summary.csv", "Overall Executive Sales KPIs"),
            ("product_performance.csv", "Product-level Revenue and Volume Metrics"),
            ("customer_performance.csv", "Customer-level Lifetime Spend & Order Counts"),
            ("monthly_sales.csv", "Monthly Revenue & Average Order Value Trends"),
            ("state_sales.csv", "Geographical Sales & Customer Distribution by State")
        ]

        for filename, desc in reports:
            filepath = os.path.join(REPORTS_DIR, filename)
            col_info, col_btn = st.columns([8, 2])
            with col_info:
                st.markdown(f"**📄 `{filename}`** — *{desc}*")
            with col_btn:
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        st.download_button(
                            label=f"⬇ Download",
                            data=f,
                            file_name=filename,
                            mime="text/csv",
                            key=f"dl_{filename}"
                        )
                else:
                    st.caption("Not generated yet")
            st.markdown("---")




if __name__ == "__main__":
    main()
