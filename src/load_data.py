"""
==============================================================================
MODULE: load_data.py
PROJECT: Mini Data Warehouse using DuckDB and Python
PURPOSE: Initialize DuckDB database, create Star Schema tables, and ingest CSVs
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
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DUCKDB_DIR = os.path.join(PROJECT_ROOT, "duckdb")
DB_PATH = os.path.join(DUCKDB_DIR, "ecommerce.duckdb")
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")


def get_connection(db_path: str = DB_PATH, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """
    Establishes and returns a DuckDB database connection.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return duckdb.connect(database=db_path, read_only=read_only)


def load_warehouse_tables(con: duckdb.DuckDBPyConnection = None) -> dict:
    """
    Creates Star Schema tables in DuckDB and ingests CSV datasets.
    Returns a dictionary mapping table name to ingested row count.
    """
    close_con = False
    if con is None:
        con = get_connection()
        close_con = True

    try:
        # 1. Execute DDL script to create warehouse tables
        create_tables_sql_path = os.path.join(SQL_DIR, "create_tables.sql")
        with open(create_tables_sql_path, "r", encoding="utf-8") as f:
            ddl_script = f.read()

        con.execute(ddl_script)

        # 2. Ingest raw CSV data into Star Schema tables
        # Use forward slashes for cross-platform DuckDB SQL compatibility
        cust_csv = os.path.join(DATA_DIR, "customers.csv").replace("\\", "/")
        prod_csv = os.path.join(DATA_DIR, "products.csv").replace("\\", "/")
        ord_csv = os.path.join(DATA_DIR, "orders.csv").replace("\\", "/")
        item_csv = os.path.join(DATA_DIR, "order_items.csv").replace("\\", "/")

        con.execute(f"INSERT INTO dim_customer SELECT * FROM read_csv_auto('{cust_csv}', header=True);")
        con.execute(f"INSERT INTO dim_product SELECT * FROM read_csv_auto('{prod_csv}', header=True);")
        con.execute(f"INSERT INTO fact_order SELECT * FROM read_csv_auto('{ord_csv}', header=True);")
        con.execute(f"INSERT INTO fact_order_item SELECT * FROM read_csv_auto('{item_csv}', header=True);")

        # 3. Retrieve row counts
        tables = ["dim_customer", "dim_product", "fact_order", "fact_order_item"]
        row_counts = {}
        for tbl in tables:
            cnt = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            row_counts[tbl] = cnt

        # 4. Display formatted summary
        print("-" * 45)
        print(f"{'Table Name':<25} | {'Row Count':<15}")
        print("-" * 45)
        for tbl, cnt in row_counts.items():
            print(f"{tbl:<25} | {cnt:<15}")
        print("-" * 45)

        return row_counts

    finally:
        if close_con:
            con.close()


if __name__ == "__main__":
    print("[*] Loading datasets into DuckDB Data Warehouse...")
    load_warehouse_tables()
    print("[✓] All warehouse tables successfully loaded into duckdb/ecommerce.duckdb")
