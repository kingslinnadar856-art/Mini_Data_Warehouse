-- ============================================================================
-- SQL SCRIPT: create_tables.sql
-- PROJECT: Mini Data Warehouse using DuckDB and Python
-- CASE STUDY: E-Commerce Sales Analytics Data Warehouse
-- ARCHITECTURE: Star Schema (Dimensions and Facts)
-- ============================================================================

-- Drop existing tables to ensure clean reload during warehouse rebuild
DROP TABLE IF EXISTS fact_order_item;
DROP TABLE IF EXISTS fact_order;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;

-- ----------------------------------------------------------------------------
-- 1. DIMENSION TABLE: dim_customer
-- Contains descriptive attributes of e-commerce customers (Who bought)
-- ----------------------------------------------------------------------------
CREATE TABLE dim_customer (
    customer_id VARCHAR PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    state VARCHAR NOT NULL,
    signup_date DATE NOT NULL
);

-- ----------------------------------------------------------------------------
-- 2. DIMENSION TABLE: dim_product
-- Contains descriptive attributes of products (What was bought)
-- ----------------------------------------------------------------------------
CREATE TABLE dim_product (
    product_id VARCHAR PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 3. FACT TABLE: fact_order
-- Order header table containing transaction metadata (When & Status)
-- ----------------------------------------------------------------------------
CREATE TABLE fact_order (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR NOT NULL,
    order_date DATE NOT NULL,
    order_status VARCHAR NOT NULL
);

-- ----------------------------------------------------------------------------
-- 4. FACT TABLE: fact_order_item
-- Granular line-item facts containing quantities and product references
-- ----------------------------------------------------------------------------
CREATE TABLE fact_order_item (
    order_id VARCHAR NOT NULL,
    product_id VARCHAR NOT NULL,
    quantity INTEGER NOT NULL
);
