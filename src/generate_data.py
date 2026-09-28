"""
==============================================================================
MODULE: generate_data.py
PROJECT: Mini Data Warehouse using DuckDB and Python
PURPOSE: Generate realistic, synthetically consistent E-Commerce CSV datasets
==============================================================================
"""

import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd

# Safe encoding configuration for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Set fixed seed for reproducible dataset generation
random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def generate_datasets(force: bool = False) -> dict:
    """
    Generates 4 CSV datasets (customers, products, orders, order_items) with
    strict relational integrity if they do not exist.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    cust_file = os.path.join(DATA_DIR, "customers.csv")
    prod_file = os.path.join(DATA_DIR, "products.csv")
    ord_file = os.path.join(DATA_DIR, "orders.csv")
    item_file = os.path.join(DATA_DIR, "order_items.csv")

    files_exist = all(os.path.exists(f) for f in [cust_file, prod_file, ord_file, item_file])

    if files_exist and not force:
        cust_df = pd.read_csv(cust_file)
        prod_df = pd.read_csv(prod_file)
        ord_df = pd.read_csv(ord_file)
        item_df = pd.read_csv(item_file)

        print("[OK] Existing datasets detected. Loaded from disk:")
        print(f"    - Customers:   {len(cust_df)} records")
        print(f"    - Products:    {len(prod_df)} records")
        print(f"    - Orders:      {len(ord_df)} records")
        print(f"    - Order Items: {len(item_df)} records")
        return {
            "customers": cust_df,
            "products": prod_df,
            "orders": ord_df,
            "order_items": item_df,
        }

    print("[*] Generating realistic E-Commerce datasets...")

    # -------------------------------------------------------------------------
    # 1. GENERATE CUSTOMERS (50 Indian Customers)
    # -------------------------------------------------------------------------
    first_names = [
        "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
        "Krishna", "Ishaan", "Shaurya", "Atharva", "Kabir", "Rudra", "Aryan",
        "Priya", "Ananya", "Diya", "Saanvi", "Isha", "Rhea", "Sneha", "Kavya",
        "Tanvi", "Pooja", "Deepika", "Neha", "Meera", "Swati", "Nandini",
        "Rohan", "Vikram", "Amit", "Rajesh", "Suresh", "Manish", "Gaurav",
        "Sunil", "Alok", "Kunal", "Harish", "Prateek", "Tarun", "Naveen",
        "Ankita", "Bhavna", "Kiran", "Divya", "Shilpa", "Payal"
    ]
    last_names = [
        "Sharma", "Verma", "Patel", "Gupta", "Iyer", "Nair", "Singh", "Reddy",
        "Deshmukh", "Kulkarni", "Joshi", "Menon", "Rao", "Chopra", "Bose",
        "Mukherjee", "Chatterjee", "Mehta", "Bhat", "Pillai", "Agarwal",
        "Malhotra", "Kapoor", "Banerjee", "Dutta"
    ]

    city_state_map = [
        ("Mumbai", "Maharashtra"),
        ("Pune", "Maharashtra"),
        ("Nagpur", "Maharashtra"),
        ("Bengaluru", "Karnataka"),
        ("Mysuru", "Karnataka"),
        ("Hyderabad", "Telangana"),
        ("Warangal", "Telangana"),
        ("Chennai", "Tamil Nadu"),
        ("Coimbatore", "Tamil Nadu"),
        ("Kolkata", "West Bengal"),
        ("Delhi", "Delhi"),
        ("Ahmedabad", "Gujarat"),
        ("Surat", "Gujarat"),
        ("Jaipur", "Rajasthan"),
        ("Udaipur", "Rajasthan"),
        ("Kochi", "Kerala"),
        ("Thiruvananthapuram", "Kerala"),
        ("Lucknow", "Uttar Pradesh"),
        ("Noida", "Uttar Pradesh"),
        ("Chandigarh", "Punjab"),
        ("Indore", "Madhya Pradesh"),
        ("Bhopal", "Madhya Pradesh"),
        ("Patna", "Bihar"),
        ("Bhubaneswar", "Odisha")
    ]

    customers = []
    start_date = datetime(2023, 1, 1)

    for i in range(1, 51):
        cust_id = f"CUST{i:03d}"
        f_name = first_names[i - 1]
        l_name = random.choice(last_names)
        full_name = f"{f_name} {l_name}"
        city, state = random.choice(city_state_map)
        signup_dt = start_date + timedelta(days=random.randint(0, 365))
        signup_str = signup_dt.strftime("%Y-%m-%d")

        customers.append({
            "customer_id": cust_id,
            "customer_name": full_name,
            "city": city,
            "state": state,
            "signup_date": signup_str
        })

    cust_df = pd.DataFrame(customers)
    cust_df.to_csv(cust_file, index=False)

    # -------------------------------------------------------------------------
    # 2. GENERATE PRODUCTS (30 Products across Categories)
    # -------------------------------------------------------------------------
    catalog = [
        ("Wireless Noise-Canceling Headphones", "Electronics", 4999.00),
        ("5G Smartphone 128GB", "Electronics", 18999.00),
        ("4K Smart LED TV 43-inch", "Electronics", 28499.00),
        ("Bluetooth Portable Speaker", "Electronics", 1799.00),
        ("Mechanical Gaming Keyboard", "Electronics", 3299.00),
        ("Ergonomic Wireless Mouse", "Electronics", 1199.00),
        ("USB-C Fast Charging Hub", "Accessories", 899.00),
        ("Laptop Backpack Water-Resistant", "Accessories", 1499.00),
        ("Tempered Glass Screen Protector", "Accessories", 349.00),
        ("Heavy Duty Phone Case", "Accessories", 499.00),
        ("Smart Fitness Band Pro", "Wearables", 2499.00),
        ("Luxury Chronograph Smartwatch", "Wearables", 6999.00),
        ("Sports Wireless Earbuds", "Wearables", 1999.00),
        ("Ergonomic High-Back Office Chair", "Furniture", 8999.00),
        ("Solid Wood Study Desk", "Furniture", 6499.00),
        ("Adjustable Monitor Riser", "Furniture", 1299.00),
        ("Orthopedic Memory Foam Cushion", "Furniture", 999.00),
        ("Men Slim Fit Cotton Shirt", "Clothing", 1299.00),
        ("Women Embroidered Kurti", "Clothing", 1599.00),
        ("Unisex Classic Denim Jeans", "Clothing", 2199.00),
        ("Breathable Athletic Gym T-Shirt", "Clothing", 699.00),
        ("Cotton Casual Summer Dress", "Clothing", 1899.00),
        ("Lightweight Running Shoes", "Footwear", 2799.00),
        ("Classic Leather Formal Shoes", "Footwear", 3499.00),
        ("Comfort Slip-on Walking Shoes", "Footwear", 1699.00),
        ("Stainless Steel Insulated Bottle", "Home & Kitchen", 799.00),
        ("Cast Iron Induction Cookware Pan", "Home & Kitchen", 1899.00),
        ("Electric Cordless Kettle 1.5L", "Home & Kitchen", 1399.00),
        ("Automatic Drip Coffee Maker", "Home & Kitchen", 3299.00),
        ("Air Tight Food Storage Containers (Set of 6)", "Home & Kitchen", 999.00)
    ]

    products = []
    for i, (name, cat, price) in enumerate(catalog, start=1):
        prod_id = f"PROD{i:03d}"
        products.append({
            "product_id": prod_id,
            "product_name": name,
            "category": cat,
            "price": price
        })

    prod_df = pd.DataFrame(products)
    prod_df.to_csv(prod_file, index=False)

    # -------------------------------------------------------------------------
    # 3. GENERATE ORDERS (200 Orders across Year 2024)
    # -------------------------------------------------------------------------
    order_statuses = ["Delivered", "Delivered", "Delivered", "Delivered", "Shipped", "Processing", "Cancelled", "Returned"]
    order_start = datetime(2024, 1, 1)
    orders = []

    for i in range(1, 201):
        ord_id = f"ORD{1000 + i}"
        cust_id = random.choice(cust_df["customer_id"].tolist())
        ord_dt = order_start + timedelta(days=random.randint(0, 360))
        status = random.choice(order_statuses)

        orders.append({
            "order_id": ord_id,
            "customer_id": cust_id,
            "order_date": ord_dt.strftime("%Y-%m-%d"),
            "order_status": status
        })

    ord_df = pd.DataFrame(orders)
    ord_df = ord_df.sort_values(by="order_date").reset_index(drop=True)
    ord_df.to_csv(ord_file, index=False)

    # -------------------------------------------------------------------------
    # 4. GENERATE ORDER ITEMS (500+ items across 200 orders)
    # -------------------------------------------------------------------------
    order_items = []
    all_prod_ids = prod_df["product_id"].tolist()

    for ord_id in ord_df["order_id"]:
        # Each order has 1 to 5 distinct items (avg ~2.8 -> ~560 items)
        num_items = random.choices([1, 2, 3, 4, 5], weights=[15, 35, 30, 15, 5])[0]
        chosen_prods = random.sample(all_prod_ids, num_items)

        for prod_id in chosen_prods:
            qty = random.choices([1, 2, 3, 4, 5], weights=[50, 30, 12, 5, 3])[0]
            order_items.append({
                "order_id": ord_id,
                "product_id": prod_id,
                "quantity": qty
            })

    item_df = pd.DataFrame(order_items)
    item_df.to_csv(item_file, index=False)

    print("Datasets generated successfully.")
    print(f"[✓] Customers:   {len(cust_df)} records saved to data/customers.csv")
    print(f"[✓] Products:    {len(prod_df)} records saved to data/products.csv")
    print(f"[✓] Orders:      {len(ord_df)} records saved to data/orders.csv")
    print(f"[✓] Order Items: {len(item_df)} records saved to data/order_items.csv")

    return {
        "customers": cust_df,
        "products": prod_df,
        "orders": ord_df,
        "order_items": item_df,
    }


if __name__ == "__main__":
    generate_datasets(force=True)
