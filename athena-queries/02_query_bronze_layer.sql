-- Query Bronze Layer: Explore raw data
SELECT 
    *,
    date_format(ingestion_timestamp, '%Y-%m-%d') as ingestion_date
FROM bronze_db.raw_data
WHERE ingestion_timestamp >= current_timestamp - interval '7' day
LIMIT 100;

-- Check data quality in Bronze
SELECT 
    ingestion_date,
    COUNT(*) as record_count,
    COUNT(DISTINCT id) as unique_ids,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) as null_ids
FROM bronze_db.raw_data
GROUP BY ingestion_date
ORDER BY ingestion_date DESC;
