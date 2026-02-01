-- Performance optimization queries

-- 1. Optimize table by converting to Parquet with compression
CREATE TABLE gold_db.daily_summary_optimized
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    partitioned_by = ARRAY['year', 'month'],
    bucketed_by = ARRAY['category'],
    bucket_count = 10
) AS
SELECT * FROM gold_db.daily_summary;

-- 2. Create a view for frequently accessed data
CREATE OR REPLACE VIEW gold_db.current_month_summary AS
SELECT 
    processed_date,
    category,
    total_transactions,
    total_amount,
    average_amount,
    unique_customers
FROM gold_db.daily_summary
WHERE year = YEAR(CURRENT_DATE)
    AND month = MONTH(CURRENT_DATE);

-- 3. Repair partitions after loading new data
MSCK REPAIR TABLE gold_db.daily_summary;

-- 4. Analyze table statistics for better query planning
ANALYZE TABLE gold_db.daily_summary COMPUTE STATISTICS;

-- 5. Show table partitions
SHOW PARTITIONS gold_db.daily_summary;

-- 6. Get table properties and metadata
SHOW CREATE TABLE gold_db.daily_summary;

-- 7. Optimize JOIN performance with bucketing
CREATE TABLE gold_db.customer_summary
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    bucketed_by = ARRAY['customer_id'],
    bucket_count = 10
) AS
SELECT 
    customer_id,
    COUNT(DISTINCT processed_date) as active_days,
    SUM(amount) as lifetime_value,
    AVG(amount) as avg_transaction,
    MIN(processed_date) as first_transaction_date,
    MAX(processed_date) as last_transaction_date
FROM silver_db.cleaned_data
GROUP BY customer_id;
