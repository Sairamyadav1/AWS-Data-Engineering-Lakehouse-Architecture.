-- AWS Athena Query Examples for Lakehouse Analytics

-- Query 1: Analyze Bronze Layer Data
-- View raw ingested data with metadata
SELECT 
    *,
    ingestion_date,
    ingestion_timestamp,
    source_file
FROM lakehouse_bronze_db.bronze_data
WHERE ingestion_date >= DATE_ADD('day', -7, CURRENT_DATE)
ORDER BY ingestion_timestamp DESC
LIMIT 100;

-- Query 2: Data Quality Analysis on Silver Layer
-- Check data quality metrics
SELECT 
    ingestion_date,
    data_quality_flag,
    COUNT(*) as record_count,
    COUNT(DISTINCT id) as unique_records
FROM lakehouse_silver_db.silver_data
GROUP BY ingestion_date, data_quality_flag
ORDER BY ingestion_date DESC;

-- Query 3: Gold Layer Analytics - Daily Aggregates
-- Business intelligence query on gold layer
SELECT 
    ingestion_date,
    total_records,
    unique_ids,
    aggregation_timestamp
FROM lakehouse_gold_db.daily_aggregates
ORDER BY ingestion_date DESC;

-- Query 4: Latest Snapshot Analysis
-- Get most recent data snapshot
SELECT *
FROM lakehouse_gold_db.latest_snapshot
LIMIT 1000;

-- Query 5: Trend Analysis
-- Calculate week-over-week growth
WITH weekly_stats AS (
    SELECT 
        DATE_TRUNC('week', CAST(ingestion_date AS DATE)) as week,
        SUM(total_records) as weekly_total
    FROM lakehouse_gold_db.daily_aggregates
    GROUP BY DATE_TRUNC('week', CAST(ingestion_date AS DATE))
)
SELECT 
    week,
    weekly_total,
    LAG(weekly_total) OVER (ORDER BY week) as prev_week_total,
    weekly_total - LAG(weekly_total) OVER (ORDER BY week) as week_over_week_change
FROM weekly_stats
ORDER BY week DESC;

-- Query 6: Data Lineage Tracking
-- Track data from Bronze to Silver
SELECT 
    b.source_file,
    b.ingestion_timestamp as bronze_ingestion,
    s.processed_timestamp as silver_processed,
    COUNT(*) as record_count
FROM lakehouse_bronze_db.bronze_data b
LEFT JOIN lakehouse_silver_db.silver_data s 
    ON b.id = s.id AND b.ingestion_date = s.ingestion_date
GROUP BY b.source_file, b.ingestion_timestamp, s.processed_timestamp
ORDER BY b.ingestion_timestamp DESC;
