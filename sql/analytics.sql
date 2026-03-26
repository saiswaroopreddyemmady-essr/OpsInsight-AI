-- 1) Regional performance
SELECT
    region,
    COUNT(*) AS orders,
    ROUND(SUM(CASE WHEN status = 'COMPLETED' THEN revenue ELSE 0 END), 2) AS revenue,
    ROUND(AVG(processing_minutes), 2) AS avg_processing_minutes
FROM fact_orders
GROUP BY region
ORDER BY revenue DESC;

-- 2) Products with the highest realized revenue
SELECT
    product_id,
    COUNT(*) AS orders,
    ROUND(SUM(CASE WHEN status = 'COMPLETED' THEN revenue ELSE 0 END), 2) AS revenue
FROM fact_orders
GROUP BY product_id
ORDER BY revenue DESC;

-- 3) Operational delay risk
SELECT
    region,
    COUNT(*) AS delayed_orders,
    ROUND(AVG(processing_minutes), 2) AS avg_delay_minutes
FROM fact_orders
WHERE processing_minutes > 180
GROUP BY region
ORDER BY delayed_orders DESC;

-- 4) Daily trend
SELECT *
FROM vw_daily_kpis
ORDER BY order_date;
