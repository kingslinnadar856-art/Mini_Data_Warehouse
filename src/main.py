"""
==============================================================================
MAIN PIPELINE ORCHESTRATOR: main.py
PROJECT: Mini Data Warehouse using DuckDB and Python
CASE STUDY: E-Commerce Sales Analytics Mini Data Warehouse
==============================================================================
"""

import os
import sys

# Safe encoding configuration for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure src module directory is in python search path
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from generate_data import generate_datasets
from load_data import get_connection, load_warehouse_tables
from transform import validate_data_quality, create_analytical_views
from analytics import calculate_business_metrics, display_metrics_summary, export_reports, format_inr


def run_pipeline():
    """
    Executes the end-to-end Data Warehouse ELT pipeline:
    Raw CSVs -> DuckDB Star Schema -> Data Cleaning -> Joins & Views -> Business Metrics -> Export
    """
    print("\n" + "=" * 50)
    print("      MINI DATA WAREHOUSE USING DUCKDB        ")
    print("   E-Commerce Sales Analytics Practical Case  ")
    print("=" * 50 + "\n")

    # -------------------------------------------------------------------------
    # STEP 1: Generate Raw CSV Datasets
    # -------------------------------------------------------------------------
    print("[1] Generating / verifying CSV datasets...")
    datasets = generate_datasets(force=False)
    print(f"    ✓ Customers:   {len(datasets['customers'])} records")
    print(f"    ✓ Products:    {len(datasets['products'])} records")
    print(f"    ✓ Orders:      {len(datasets['orders'])} records")
    print(f"    ✓ Order Items: {len(datasets['order_items'])} records\n")

    # -------------------------------------------------------------------------
    # STEP 2: Connect to DuckDB & Load Star Schema Tables
    # -------------------------------------------------------------------------
    print("[2] Loading data into DuckDB warehouse (Star Schema)...")
    con = get_connection()
    try:
        row_counts = load_warehouse_tables(con)
        print("    ✓ dim_customer loaded")
        print("    ✓ dim_product loaded")
        print("    ✓ fact_order loaded")
        print("    ✓ fact_order_item loaded\n")

        # ---------------------------------------------------------------------
        # STEP 3: Data Quality Validation
        # ---------------------------------------------------------------------
        print("[3] Performing data quality validation...")
        val_results = validate_data_quality(con)
        print("    ✓ No NULL primary keys")
        print("    ✓ No duplicate orders")
        print("    ✓ No invalid quantities or prices")
        print("    ✓ Strict referential integrity verified\n")

        # ---------------------------------------------------------------------
        # STEP 4: Create Analytical Views & Reporting Layer
        # ---------------------------------------------------------------------
        print("[4] Creating analytical views & star-schema joins...")
        views = create_analytical_views(con)
        print("    ✓ vw_order_details (Multi-table INNER JOIN)")
        print("    ✓ vw_customer_sales (Customer aggregated sales)")
        print("    ✓ vw_product_sales (Product sales by category)")
        print("    ✓ vw_monthly_sales (Monthly trend analysis)")
        print("    ✓ 5 Reporting Layer views initialized\n")

        # ---------------------------------------------------------------------
        # STEP 5: Calculate Business Metrics
        # ---------------------------------------------------------------------
        print("[5] Calculating e-commerce business metrics...")
        metrics = calculate_business_metrics(con)
        kpis = metrics["kpis"]
        
        print("\n    ---------------------------------------")
        print(f"    Total Revenue:            {format_inr(kpis['total_revenue'])}")
        print(f"    Total Orders:             {int(kpis['total_orders']):,}")
        print(f"    Total Customers:          {int(kpis['total_customers']):,}")
        print(f"    Total Units Sold:         {int(kpis['total_units_sold']):,}")
        print(f"    Average Order Value:      {format_inr(kpis['avg_order_value'])}")
        print(f"    Average Selling Price:    {format_inr(kpis['avg_selling_price'])}")
        print("    ---------------------------------------\n")

        # ---------------------------------------------------------------------
        # STEP 6: Export Analytical Reporting CSVs
        # ---------------------------------------------------------------------
        print("[6] Generating analytical reports...")
        exported = export_reports(con)
        print("    ✓ Reports exported to output/reports/\n")

    finally:
        con.close()

    print("=" * 50)
    print("      PIPELINE COMPLETED SUCCESSFULLY!        ")
    print("=" * 50)
    print("\nNext Steps:")
    print("  1. Launch Streamlit Dashboard:  streamlit run dashboard/app.py")
    print("  2. Explore DuckDB Database:     duckdb/ecommerce.duckdb")
    print("  3. Check Exported Reports:      output/reports/")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_pipeline()
