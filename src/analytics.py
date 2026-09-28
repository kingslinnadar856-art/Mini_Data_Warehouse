"""
==============================================================================
MODULE: analytics.py
PROJECT: Mini Data Warehouse using DuckDB and Python
PURPOSE: Compute Business Metrics using DuckDB SQL & Export Reporting Datasets
==============================================================================
"""

import os
import sys
import duckdb
import pandas as pd

# Safe encoding configuration for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "duckdb", "ecommerce.duckdb")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "output", "reports")


def format_inr(amount: float) -> str:
    """
    Formats a numeric amount into Indian Rupee style currency string (₹ XX,XX,XXX.XX)
    """
    if amount is None:
        return "₹0.00"
    return f"₹{amount:,.2f}"


def calculate_business_metrics(con: duckdb.DuckDBPyConnection) -> dict:
    """
    Executes analytical SQL queries against the DuckDB Data Warehouse
    to calculate all core e-commerce business KPIs.
    """
    print("[*] Calculating Core E-Commerce Business Metrics...")

    # 1. Executive KPIs
    kpi_query = """
    SELECT 
        CAST(SUM(sales_amount) AS DOUBLE) AS total_revenue,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        COUNT(DISTINCT product_id) AS total_products,
        SUM(quantity) AS total_units_sold,
        CAST(SUM(sales_amount) / NULLIF(COUNT(DISTINCT order_id), 0) AS DOUBLE) AS avg_order_value,
        CAST(SUM(sales_amount) / NULLIF(SUM(quantity), 0) AS DOUBLE) AS avg_selling_price
    FROM vw_order_details;
    """
    kpis = con.execute(kpi_query).fetchdf().iloc[0].to_dict()

    # 2. Top 5 Products by Revenue
    top_products_query = """
    SELECT 
        product_id,
        product_name,
        category,
        total_quantity_sold,
        total_sales
    FROM report_product_performance
    ORDER BY total_sales DESC
    LIMIT 5;
    """
    top_products_df = con.execute(top_products_query).fetchdf()

    # 3. Top 5 Categories by Revenue
    top_categories_query = """
    SELECT 
        category,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(quantity) AS total_units_sold,
        CAST(SUM(sales_amount) AS DOUBLE) AS total_revenue
    FROM vw_order_details
    GROUP BY category
    ORDER BY total_revenue DESC
    LIMIT 5;
    """
    top_categories_df = con.execute(top_categories_query).fetchdf()

    # 4. Top 10 Customers by Spend
    top_customers_query = """
    SELECT 
        customer_id,
        customer_name,
        city,
        state,
        total_orders,
        total_quantity,
        total_sales
    FROM report_customer_performance
    ORDER BY total_sales DESC
    LIMIT 10;
    """
    top_customers_df = con.execute(top_customers_query).fetchdf()

    # 5. Monthly Revenue Trend
    monthly_sales_query = """
    SELECT 
        month,
        total_orders,
        total_sales,
        monthly_avg_order_value
    FROM report_monthly_sales
    ORDER BY month ASC;
    """
    monthly_sales_df = con.execute(monthly_sales_query).fetchdf()

    # 6. Geographical Sales Performance
    state_sales_query = """
    SELECT 
        state,
        unique_customers,
        total_orders,
        units_sold,
        total_revenue
    FROM report_geographical_sales
    ORDER BY total_revenue DESC;
    """
    state_sales_df = con.execute(state_sales_query).fetchdf()

    # 7. Order Status Distribution
    status_query = """
    SELECT 
        order_status,
        COUNT(order_id) AS count,
        ROUND(COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM fact_order), 2) AS percentage
    FROM fact_order
    GROUP BY order_status
    ORDER BY count DESC;
    """
    status_df = con.execute(status_query).fetchdf()

    return {
        "kpis": kpis,
        "top_products": top_products_df,
        "top_categories": top_categories_df,
        "top_customers": top_customers_df,
        "monthly_sales": monthly_sales_df,
        "state_sales": state_sales_df,
        "order_status": status_df,
    }


def display_metrics_summary(metrics: dict):
    """
    Prints a formatted, clean business metrics summary to console.
    """
    kpis = metrics["kpis"]

    print("\n" + "=" * 55)
    print("        EXECUTIVE E-COMMERCE BUSINESS METRICS    ")
    print("=" * 55)
    print(f"Total Revenue:            {format_inr(kpis['total_revenue'])}")
    print(f"Total Orders:             {int(kpis['total_orders']):,}")
    print(f"Total Customers:          {int(kpis['total_customers']):,}")
    print(f"Total Products In Sales:  {int(kpis['total_products']):,}")
    print(f"Total Units Sold:         {int(kpis['total_units_sold']):,}")
    print(f"Average Order Value (AOV):{format_inr(kpis['avg_order_value'])}")
    print(f"Average Selling Price:    {format_inr(kpis['avg_selling_price'])}")
    print("-" * 55)

    print("\n[★] TOP 5 PRODUCTS BY REVENUE:")
    for idx, row in metrics["top_products"].iterrows():
        print(f"  {idx+1}. {row['product_name']} ({row['category']}) - {format_inr(row['total_sales'])} ({row['total_quantity_sold']} units)")

    print("\n[★] TOP 5 PRODUCT CATEGORIES BY REVENUE:")
    for idx, row in metrics["top_categories"].iterrows():
        print(f"  {idx+1}. {row['category']:<15} - {format_inr(row['total_revenue'])} ({row['total_units_sold']} units, {row['total_orders']} orders)")

    print("\n[★] TOP 3 REVENUE GENERATING STATES:")
    for idx, row in metrics["state_sales"].head(3).iterrows():
        print(f"  {idx+1}. {row['state']:<15} - {format_inr(row['total_revenue'])} ({row['total_orders']} orders)")

    print("=" * 55 + "\n")


def export_reports(con: duckdb.DuckDBPyConnection) -> list:
    """
    Exports the 5 standard analytical reporting layer datasets to CSV files in output/reports/
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    print("[*] Exporting Analytical Reporting Datasets to output/reports/...")

    reports = [
        ("report_sales_summary", "sales_summary.csv"),
        ("report_product_performance", "product_performance.csv"),
        ("report_customer_performance", "customer_performance.csv"),
        ("report_monthly_sales", "monthly_sales.csv"),
        ("report_geographical_sales", "state_sales.csv")
    ]

    exported_files = []
    for view_name, csv_name in reports:
        target_path = os.path.join(REPORTS_DIR, csv_name)
        df = con.execute(f"SELECT * FROM {view_name}").fetchdf()
        df.to_csv(target_path, index=False)
        exported_files.append(target_path)
        print(f"    [✓] {csv_name:<28} ({len(df)} rows exported)")

    print("[✓] All 5 analytical reports successfully exported!")
    return exported_files


def run_analytics():
    """
    Standalone runner for analytics.py.
    """
    con = duckdb.connect(database=DB_PATH, read_only=True)
    try:
        metrics = calculate_business_metrics(con)
        display_metrics_summary(metrics)
        export_reports(con)
    finally:
        con.close()


if __name__ == "__main__":
    run_analytics()
