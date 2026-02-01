-- Business Analytics Queries for Snowflake

USE DATABASE LAKEHOUSE;
USE SCHEMA GOLD;
USE WAREHOUSE COMPUTE_WH;

-- 1. Revenue Analysis by Category
SELECT 
  category,
  SUM(total_amount) as total_revenue,
  AVG(average_amount) as avg_transaction,
  SUM(total_transactions) as total_transactions,
  SUM(unique_customers) as total_customers
FROM gold_daily_summary
WHERE year = YEAR(CURRENT_DATE())
GROUP BY category
ORDER BY total_revenue DESC;

-- 2. Year-over-Year Growth
WITH yearly_metrics AS (
  SELECT 
    year,
    category,
    SUM(total_amount) as annual_revenue
  FROM gold_daily_summary
  GROUP BY year, category
)
SELECT 
  current.year,
  current.category,
  current.annual_revenue,
  previous.annual_revenue as previous_year_revenue,
  ROUND(
    ((current.annual_revenue - previous.annual_revenue) / previous.annual_revenue * 100),
    2
  ) as yoy_growth_pct
FROM yearly_metrics current
LEFT JOIN yearly_metrics previous
  ON current.category = previous.category
  AND current.year = previous.year + 1
ORDER BY current.year DESC, yoy_growth_pct DESC;

-- 3. Top Performing Days
SELECT 
  processed_date,
  category,
  total_amount,
  total_transactions,
  RANK() OVER (PARTITION BY category ORDER BY total_amount DESC) as revenue_rank
FROM gold_daily_summary
WHERE processed_date >= DATEADD(MONTH, -3, CURRENT_DATE())
QUALIFY revenue_rank <= 10
ORDER BY category, revenue_rank;

-- 4. Weekly Trends
SELECT 
  DATE_TRUNC('WEEK', processed_date) as week_start,
  category,
  SUM(total_amount) as weekly_revenue,
  AVG(total_transactions) as avg_daily_transactions,
  SUM(unique_customers) as weekly_customers
FROM gold_daily_summary
WHERE processed_date >= DATEADD(MONTH, -6, CURRENT_DATE())
GROUP BY DATE_TRUNC('WEEK', processed_date), category
ORDER BY week_start DESC, weekly_revenue DESC;

-- 5. Customer Engagement Metrics
SELECT 
  category,
  AVG(transaction_density) as avg_transactions_per_customer,
  MIN(transaction_density) as min_transactions_per_customer,
  MAX(transaction_density) as max_transactions_per_customer,
  STDDEV(transaction_density) as stddev_transactions
FROM gold_daily_summary
GROUP BY category
ORDER BY avg_transactions_per_customer DESC;

-- 6. Moving Average Analysis
SELECT 
  processed_date,
  category,
  total_amount as daily_revenue,
  moving_avg_7d,
  ROUND(
    ((total_amount - moving_avg_7d) / moving_avg_7d * 100),
    2
  ) as variance_from_avg_pct
FROM gold_daily_summary
WHERE processed_date >= DATEADD(MONTH, -1, CURRENT_DATE())
  AND moving_avg_7d IS NOT NULL
ORDER BY processed_date DESC, category;

-- 7. Seasonality Analysis
SELECT 
  quarter,
  month,
  category,
  AVG(total_amount) as avg_daily_revenue,
  SUM(total_transactions) as total_transactions
FROM gold_daily_summary
GROUP BY quarter, month, category
ORDER BY quarter, month, category;

-- 8. High-Value Transaction Days
SELECT 
  processed_date,
  category,
  total_amount,
  average_amount,
  max_amount,
  CASE 
    WHEN max_amount > average_amount * 3 THEN 'High Outlier'
    WHEN max_amount > average_amount * 2 THEN 'Moderate Outlier'
    ELSE 'Normal'
  END as outlier_status
FROM gold_daily_summary
WHERE processed_date >= DATEADD(MONTH, -3, CURRENT_DATE())
ORDER BY max_amount DESC
LIMIT 100;
