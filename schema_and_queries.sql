-- ==========================================
-- 1. OPTIMIZED TABLE DDL (Partition + Cluster)
-- ==========================================
CREATE TABLE IF NOT EXISTS `analytics.user_events_optimized` (
    event_id STRING NOT NULL,
    customer_id INT64 NOT NULL,
    event_type STRING NOT NULL,
    revenue_usd NUMERIC,
    event_timestamp TIMESTAMP NOT NULL
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY customer_id, event_type
OPTIONS (
    partition_expiration_days = 730,
    require_partition_filter = TRUE
);

-- ==========================================
-- 2. BEFORE: Expensive Full-Table Scan (~48.2 GB)
-- ==========================================
SELECT *
FROM `analytics.user_events_raw`
WHERE EXTRACT(YEAR FROM event_timestamp) = 2026
  AND customer_id = 84920
ORDER BY event_timestamp DESC;

-- ==========================================
-- 3. AFTER: Partition-Pruned & Clustered (~1.4 GB)
-- ==========================================
SELECT
    event_id,
    event_type,
    revenue_usd,
    event_timestamp
FROM `analytics.user_events_optimized`
WHERE event_timestamp >= TIMESTAMP('2026-01-01 00:00:00')
  AND event_timestamp < TIMESTAMP('2027-01-01 00:00:00')
  AND customer_id = 84920
ORDER BY event_timestamp DESC;
