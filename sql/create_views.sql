-- ============================================================================
-- SQL SCRIPT: create_views.sql
-- PROJECT: Mini Data Warehouse using DuckDB and Python
-- PURPOSE: Create Analytical Views & Reporting Layer Views
-- ============================================================================

-- Drop views if they already exist
DROP VIEW IF EXISTS report_geographical_sales;
DROP VIEW IF EXISTS report_monthly_sales;
DROP VIEW IF EXISTS report_customer_performance;
DROP VIEW IF EXISTS report_product_performance;
DROP VIEW IF EXISTS report_sales_summary;
DROP VIEW IF EXISTS vw_monthly_sales;
DROP VIEW IF EXISTS vw_product_sales;
DROP VIEW IF EXISTS vw_customer_sales;
DROP VIEW IF EXISTS vw_order_details;

-- ============================================================================
-- SECTION 1: CORE ANALYTICAL VIEWS (JOINING STAR SCHEMA TABLES)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. VIEW: vw_order_details
-- The primary flattened analytical view joining facts and dimensions.
-- Demonstrates multi-table INNER JOIN and calculated business metrics.
-- ----------------------------------------------------------------------------
CREATE VIEW vw_order_details AS
SELECT 
    fo.order_id,
    fo.order_date,
    fo.customer_id,
    dc.customer_name,
    dc.city,
    dc.state,
    foi.product_id,
    dp.product_name,
    dp.category,
    foi.quantity,
    dp.price AS unit_price,
    CAST(foi.quantity * dp.price AS DECIMAL(12, 2)) AS sales_amount,
    fo.order_status
FROM fact_order fo
INNER JOIN fact_order_item foi 
    ON fo.order_id = foi.order_id
INNER JOIN dim_customer dc 
    ON fo.customer_id = dc.customer_id
INNER JOIN dim_product dp 
    ON foi.product_id = dp.product_id;

-- ----------------------------------------------------------------------------
-- 2. VIEW: vw_customer_sales
-- Customer-level aggregated sales analysis.
-- ----------------------------------------------------------------------------
CREATE VIEW vw_customer_sales AS
SELECT 
    dc.customer_id,
    dc.customer_name,
    dc.city,
    dc.state,
    COUNT(DISTINCT fo.order_id) AS total_orders,
    COALESCE(SUM(foi.quantity), 0) AS total_quantity,
    COALESCE(CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)), 0.00) AS total_sales
FROM dim_customer dc
LEFT JOIN fact_order fo 
    ON dc.customer_id = fo.customer_id
LEFT JOIN fact_order_item foi 
    ON fo.order_id = foi.order_id
LEFT JOIN dim_product dp 
    ON foi.product_id = dp.product_id
GROUP BY 
    dc.customer_id,
    dc.customer_name,
    dc.city,
    dc.state;

-- ----------------------------------------------------------------------------
-- 3. VIEW: vw_product_sales
-- Product-level sales performance with categories and volumes.
-- ----------------------------------------------------------------------------
CREATE VIEW vw_product_sales AS
SELECT 
    dp.product_id,
    dp.product_name,
    dp.category,
    COALESCE(SUM(foi.quantity), 0) AS total_quantity_sold,
    COALESCE(CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)), 0.00) AS total_sales
FROM dim_product dp
LEFT JOIN fact_order_item foi 
    ON dp.product_id = foi.product_id
LEFT JOIN fact_order fo 
    ON foi.order_id = fo.order_id
GROUP BY 
    dp.product_id,
    dp.product_name,
    dp.category;

-- ----------------------------------------------------------------------------
-- 4. VIEW: vw_monthly_sales
-- Monthly aggregated sales trends and order volumes.
-- ----------------------------------------------------------------------------
CREATE VIEW vw_monthly_sales AS
SELECT 
    strftime(fo.order_date, '%Y-%m') AS month,
    COUNT(DISTINCT fo.order_id) AS total_orders,
    CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)) AS total_sales
FROM fact_order fo
INNER JOIN fact_order_item foi 
    ON fo.order_id = foi.order_id
INNER JOIN dim_product dp 
    ON foi.product_id = dp.product_id
GROUP BY 
    strftime(fo.order_date, '%Y-%m')
ORDER BY 
    month ASC;

-- ============================================================================
-- SECTION 2: ANALYTICAL REPORTING LAYER (BUSINESS READY CONSUMPTION VIEWS)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 5. REPORT VIEW: report_sales_summary
-- Executive-level overall sales KPI summary
-- ----------------------------------------------------------------------------
CREATE VIEW report_sales_summary AS
SELECT 
    CAST(SUM(sales_amount) AS DECIMAL(12, 2)) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT product_id) AS total_products_sold,
    SUM(quantity) AS total_units_sold,
    CAST(SUM(sales_amount) / NULLIF(COUNT(DISTINCT order_id), 0) AS DECIMAL(10, 2)) AS avg_order_value,
    CAST(SUM(sales_amount) / NULLIF(SUM(quantity), 0) AS DECIMAL(10, 2)) AS avg_selling_price
FROM vw_order_details;

-- ----------------------------------------------------------------------------
-- 6. REPORT VIEW: report_product_performance
-- Top ranking products by revenue and units sold
-- ----------------------------------------------------------------------------
CREATE VIEW report_product_performance AS
SELECT 
    product_id,
    product_name,
    category,
    total_quantity_sold,
    total_sales,
    RANK() OVER (ORDER BY total_sales DESC) AS revenue_rank
FROM vw_product_sales
ORDER BY total_sales DESC;

-- ----------------------------------------------------------------------------
-- 7. REPORT VIEW: report_customer_performance
-- Top revenue-generating customers
-- ----------------------------------------------------------------------------
CREATE VIEW report_customer_performance AS
SELECT 
    customer_id,
    customer_name,
    city,
    state,
    total_orders,
    total_quantity,
    total_sales,
    RANK() OVER (ORDER BY total_sales DESC) AS customer_rank
FROM vw_customer_sales
ORDER BY total_sales DESC;

-- ----------------------------------------------------------------------------
-- 8. REPORT VIEW: report_monthly_sales
-- Ready-to-export monthly performance analysis
-- ----------------------------------------------------------------------------
CREATE VIEW report_monthly_sales AS
SELECT 
    month,
    total_orders,
    total_sales,
    CAST(total_sales / NULLIF(total_orders, 0) AS DECIMAL(10, 2)) AS monthly_avg_order_value
FROM vw_monthly_sales
ORDER BY month ASC;

-- ----------------------------------------------------------------------------
-- 9. REPORT VIEW: report_geographical_sales
-- State-wise sales distribution and customer density
-- ----------------------------------------------------------------------------
CREATE VIEW report_geographical_sales AS
SELECT 
    state,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS units_sold,
    CAST(SUM(sales_amount) AS DECIMAL(12, 2)) AS total_revenue
FROM vw_order_details
GROUP BY state
ORDER BY total_revenue DESC;
