"""
==============================================================================
MODULE: transform.py
PROJECT: Mini Data Warehouse using DuckDB and Python
PURPOSE: Perform Data Quality Validation & Build Analytical Transformation Views
==============================================================================
"""

import os
import sys
import duckdb

# Safe encoding configuration for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "duckdb", "ecommerce.duckdb")
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")


def validate_data_quality(con: duckdb.DuckDBPyConnection) -> dict:
    """
    Executes automated data quality checks against the warehouse tables.
    Checks for null primary keys, duplicate records, non-positive values,
    and broken foreign key references.
    """
    # 1. NULL checks
    null_cust_id = con.execute("SELECT COUNT(*) FROM dim_customer WHERE customer_id IS NULL").fetchone()[0]
    null_prod_id = con.execute("SELECT COUNT(*) FROM dim_product WHERE product_id IS NULL").fetchone()[0]
    null_ord_id = con.execute("SELECT COUNT(*) FROM fact_order WHERE order_id IS NULL").fetchone()[0]

    # 2. Duplicate order check
    dup_orders = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT order_id FROM fact_order GROUP BY order_id HAVING COUNT(*) > 1
        )
    """).fetchone()[0]

    # 3. Invalid quantities and prices (<= 0)
    invalid_quantities = con.execute("SELECT COUNT(*) FROM fact_order_item WHERE quantity <= 0").fetchone()[0]
    invalid_prices = con.execute("SELECT COUNT(*) FROM dim_product WHERE price <= 0").fetchone()[0]

    # 4. Referential integrity checks (Orphaned records)
    orphaned_orders = con.execute("""
        SELECT COUNT(*) 
        FROM fact_order fo
        LEFT JOIN dim_customer dc ON fo.customer_id = dc.customer_id
        WHERE dc.customer_id IS NULL
    """).fetchone()[0]

    orphaned_items_orders = con.execute("""
        SELECT COUNT(*) 
        FROM fact_order_item foi
        LEFT JOIN fact_order fo ON foi.order_id = fo.order_id
        WHERE fo.order_id IS NULL
    """).fetchone()[0]

    orphaned_items_products = con.execute("""
        SELECT COUNT(*) 
        FROM fact_order_item foi
        LEFT JOIN dim_product dp ON foi.product_id = dp.product_id
        WHERE dp.product_id IS NULL
    """).fetchone()[0]

    results = {
        "null_cust_id": null_cust_id,
        "null_prod_id": null_prod_id,
        "null_ord_id": null_ord_id,
        "dup_orders": dup_orders,
        "invalid_quantities": invalid_quantities,
        "invalid_prices": invalid_prices,
        "orphaned_orders": orphaned_orders,
        "orphaned_items_orders": orphaned_items_orders,
        "orphaned_items_products": orphaned_items_products
    }

    # Print Data Quality Report
    print("========================================")
    print("         DATA QUALITY REPORT            ")
    print("========================================")
    print(f"Customers with NULL ID:          {null_cust_id}")
    print(f"Products with NULL ID:           {null_prod_id}")
    print(f"Orders with NULL ID:             {null_ord_id}")
    print(f"Duplicate Orders:                {dup_orders}")
    print(f"Invalid Quantities (<= 0):       {invalid_quantities}")
    print(f"Invalid Prices (<= 0):           {invalid_prices}")
    print(f"Orders with Missing Customers:   {orphaned_orders}")
    print(f"Items with Missing Orders:       {orphaned_items_orders}")
    print(f"Items with Missing Products:     {orphaned_items_products}")
    print("----------------------------------------")

    is_clean = all(v == 0 for v in results.values())
    if is_clean:
        print("[✓] Data Quality Verification: PASSED (100% Clean Data)")
    else:
        print("[!] Data Quality Verification: ISSUES DETECTED")
    print("========================================\n")

    return results


def create_analytical_views(con: duckdb.DuckDBPyConnection) -> list:
    """
    Executes sql/create_views.sql to build the star-schema analytical views
    and reporting layer views.
    """
    create_views_sql_path = os.path.join(SQL_DIR, "create_views.sql")
    with open(create_views_sql_path, "r", encoding="utf-8") as f:
        views_script = f.read()

    con.execute(views_script)

    views_created = [
        "vw_order_details",
        "vw_customer_sales",
        "vw_product_sales",
        "vw_monthly_sales",
        "report_sales_summary",
        "report_product_performance",
        "report_customer_performance",
        "report_monthly_sales",
        "report_geographical_sales"
    ]

    print("[*] Creating Analytical Views and Reporting Layer...")
    for v in views_created:
        # Validate view existence and queryability
        count = con.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0]
        print(f"    [✓] View '{v}' verified ({count} rows)")

    return views_created


def run_transformations():
    """
    Standalone runner for transform.py.
    """
    con = duckdb.connect(database=DB_PATH)
    try:
        validate_data_quality(con)
        create_analytical_views(con)
    finally:
        con.close()


if __name__ == "__main__":
    run_transformations()
