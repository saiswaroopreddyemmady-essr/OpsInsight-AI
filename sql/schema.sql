PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT UNIQUE NOT NULL,
    product_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_region (
    region_key INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    region TEXT,
    order_ts TEXT,
    quantity INTEGER,
    unit_price REAL,
    revenue REAL,
    processing_minutes INTEGER,
    status TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_orders_ts
ON fact_orders(order_ts);

CREATE INDEX IF NOT EXISTS idx_fact_orders_region_status
ON fact_orders(region, status);

CREATE INDEX IF NOT EXISTS idx_fact_orders_product
ON fact_orders(product_id);

CREATE TABLE IF NOT EXISTS dq_results (
    run_ts TEXT,
    rule_name TEXT,
    severity TEXT,
    failed_rows INTEGER,
    details TEXT
);

CREATE TABLE IF NOT EXISTS anomaly_results (
    run_ts TEXT,
    anomaly_type TEXT,
    entity TEXT,
    score REAL,
    details TEXT
);

CREATE VIEW IF NOT EXISTS vw_daily_kpis AS
SELECT
    substr(order_ts, 1, 10) AS order_date,
    COUNT(*) AS orders,
    ROUND(SUM(CASE WHEN status = 'COMPLETED' THEN revenue ELSE 0 END), 2) AS completed_revenue,
    ROUND(AVG(processing_minutes), 2) AS avg_processing_minutes,
    ROUND(100.0 * SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate
FROM fact_orders
GROUP BY substr(order_ts, 1, 10);
