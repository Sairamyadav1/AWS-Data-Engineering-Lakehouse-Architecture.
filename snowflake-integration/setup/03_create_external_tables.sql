-- Create External Tables
-- These tables query data directly from S3 without loading into Snowflake

USE ROLE SYSADMIN;
USE DATABASE LAKEHOUSE;
USE SCHEMA GOLD;

-- External table for daily summary (Gold layer)
CREATE OR REPLACE EXTERNAL TABLE gold_daily_summary_ext
  WITH LOCATION = @gold_stage
  FILE_FORMAT = LAKEHOUSE.PUBLIC.PARQUET_FORMAT
  PATTERN = '.*[.]parquet'
  AUTO_REFRESH = TRUE
  REFRESH_ON_CREATE = TRUE
(
  processed_date DATE AS (value:c1::DATE),
  category VARCHAR AS (value:c2::VARCHAR),
  total_transactions NUMBER AS (value:c3::NUMBER),
  total_amount DECIMAL(18,2) AS (value:c4::DECIMAL(18,2)),
  average_amount DECIMAL(18,2) AS (value:c5::DECIMAL(18,2)),
  min_amount DECIMAL(18,2) AS (value:c6::DECIMAL(18,2)),
  max_amount DECIMAL(18,2) AS (value:c7::DECIMAL(18,2)),
  unique_customers NUMBER AS (value:c8::NUMBER),
  transaction_density DECIMAL(10,2) AS (value:c9::DECIMAL(10,2)),
  year NUMBER AS (value:c10::NUMBER),
  month NUMBER AS (value:c11::NUMBER),
  quarter NUMBER AS (value:c12::NUMBER),
  day_of_week NUMBER AS (value:c13::NUMBER),
  category_rank NUMBER AS (value:c14::NUMBER),
  moving_avg_7d DECIMAL(18,2) AS (value:c15::DECIMAL(18,2)),
  aggregation_timestamp TIMESTAMP AS (value:c16::TIMESTAMP),
  layer VARCHAR AS (value:c17::VARCHAR),
  aggregation_type VARCHAR AS (value:c18::VARCHAR)
)
PARTITION BY (year, month)
COMMENT = 'External table for Gold layer daily summary data';

-- Create a regular table with data from external table
-- This is faster for frequent queries
CREATE OR REPLACE TABLE gold_daily_summary AS
SELECT * FROM gold_daily_summary_ext;

-- Add clustering for better query performance
ALTER TABLE gold_daily_summary CLUSTER BY (processed_date, category);

-- Create materialized view for real-time aggregations
CREATE OR REPLACE MATERIALIZED VIEW gold_monthly_metrics AS
SELECT 
  year,
  month,
  category,
  SUM(total_transactions) as monthly_transactions,
  SUM(total_amount) as monthly_revenue,
  AVG(average_amount) as avg_transaction_value,
  COUNT(DISTINCT processed_date) as active_days
FROM gold_daily_summary
GROUP BY year, month, category;

-- Grant permissions
GRANT SELECT ON TABLE gold_daily_summary_ext TO ROLE DATA_ANALYST;
GRANT SELECT ON TABLE gold_daily_summary TO ROLE DATA_ANALYST;
GRANT SELECT ON MATERIALIZED VIEW gold_monthly_metrics TO ROLE DATA_ANALYST;

-- Verify tables
SHOW EXTERNAL TABLES;
SHOW TABLES;
SHOW MATERIALIZED VIEWS;

-- Sample query to test
SELECT * FROM gold_daily_summary_ext LIMIT 10;
