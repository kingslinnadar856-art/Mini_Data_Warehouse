-- ============================================================================
-- SQL SCRIPT: analytical_queries.sql
-- PROJECT: Mini Data Warehouse using DuckDB and Python
-- PURPOSE: Key Analytical and Business Metric SQL Queries for Viva Demonstration
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. EXECUTIVE KPI SUMMARY (Revenue, Orders, Customers, AOV, ASP)
-- ----------------------------------------------------------------------------
SELECT 
    CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)) AS total_revenue,
    COUNT(DISTINCT fo.order_id) AS total_orders,
    COUNT(DISTINCT dc.customer_id) AS total_customers,
    COUNT(DISTINCT dp.product_id) AS total_products,
    SUM(foi.quantity) AS total_units_sold,
    CAST(SUM(foi.quantity * dp.price) / NULLIF(COUNT(DISTINCT fo.order_id), 0) AS DECIMAL(10, 2)) AS average_order_value,
    CAST(SUM(foi.quantity * dp.price) / NULLIF(SUM(foi.quantity), 0) AS DECIMAL(10, 2)) AS average_selling_price
FROM fact_order fo
INNER JOIN fact_order_item foi ON fo.order_id = foi.order_id
INNER JOIN dim_customer dc ON fo.customer_id = dc.customer_id
INNER JOIN dim_product dp ON foi.product_id = dp.product_id;


-- ----------------------------------------------------------------------------
-- 2. TOP 5 PRODUCTS BY REVENUE
-- ----------------------------------------------------------------------------
SELECT 
    dp.product_id,
    dp.product_name,
    dp.category,
    SUM(foi.quantity) AS total_units_sold,
    CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)) AS total_revenue
FROM fact_order_item foi
INNER JOIN dim_product dp ON foi.product_id = dp.product_id
GROUP BY dp.product_id, dp.product_name, dp.category
ORDER BY total_revenue DESC
LIMIT 5;


-- ----------------------------------------------------------------------------
-- 3. TOP 5 PRODUCT CATEGORIES BY REVENUE
-- ----------------------------------------------------------------------------
SELECT 
    dp.category,
    COUNT(DISTINCT foi.order_id) AS total_orders,
    SUM(foi.quantity) AS total_units_sold,
    CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)) AS total_revenue
FROM fact_order_item foi
INNER JOIN dim_product dp ON foi.product_id = dp.product_id
GROUP BY dp.category
ORDER BY total_revenue DESC
LIMIT 5;


-- ----------------------------------------------------------------------------
-- 4. TOP 10 CUSTOMERS BY REVENUE
-- ----------------------------------------------------------------------------
SELECT 
    dc.customer_id,
    dc.customer_name,
    dc.city,
    dc.state,
    COUNT(DISTINCT fo.order_id) AS orders_placed,
    SUM(foi.quantity) AS items_purchased,
    CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)) AS total_spent
FROM dim_customer dc
INNER JOIN fact_order fo ON dc.customer_id = fo.customer_id
INNER JOIN fact_order_item foi ON fo.order_id = foi.order_id
INNER JOIN dim_product dp ON foi.product_id = dp.product_id
GROUP BY dc.customer_id, dc.customer_name, dc.city, dc.state
ORDER BY total_spent DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- 5. MONTHLY REVENUE AND GROWTH TREND
-- ----------------------------------------------------------------------------
SELECT 
    strftime(fo.order_date, '%Y-%m') AS sales_month,
    COUNT(DISTINCT fo.order_id) AS order_count,
    SUM(foi.quantity) AS total_quantity,
    CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)) AS monthly_revenue
FROM fact_order fo
INNER JOIN fact_order_item foi ON fo.order_id = foi.order_id
INNER JOIN dim_product dp ON foi.product_id = dp.product_id
GROUP BY strftime(fo.order_date, '%Y-%m')
ORDER BY sales_month ASC;


-- ----------------------------------------------------------------------------
-- 6. REVENUE BY STATE (GEOGRAPHICAL PERFORMANCE)
-- ----------------------------------------------------------------------------
SELECT 
    dc.state,
    COUNT(DISTINCT dc.customer_id) AS customer_count,
    COUNT(DISTINCT fo.order_id) AS orders_count,
    CAST(SUM(foi.quantity * dp.price) AS DECIMAL(12, 2)) AS state_revenue
FROM dim_customer dc
INNER JOIN fact_order fo ON dc.customer_id = fo.customer_id
INNER JOIN fact_order_item foi ON fo.order_id = foi.order_id
INNER JOIN dim_product dp ON foi.product_id = dp.product_id
GROUP BY dc.state
ORDER BY state_revenue DESC;


-- ----------------------------------------------------------------------------
-- 7. ORDER STATUS DISTRIBUTION (FULFILLMENT METRICS)
-- ----------------------------------------------------------------------------
SELECT 
    order_status,
    COUNT(order_id) AS order_count,
    ROUND(COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM fact_order), 2) AS percentage_share
FROM fact_order
GROUP BY order_status
ORDER BY order_count DESC;
