-- Query Gold Layer: Business analytics
SELECT 
    year,
    month,
    category,
    SUM(total_transactions) as total_transactions,
    SUM(total_amount) as revenue,
    AVG(average_amount) as avg_transaction_value,
    SUM(unique_customers) as total_customers
FROM gold_db.daily_summary
WHERE year = YEAR(CURRENT_DATE)
GROUP BY year, month, category
ORDER BY year DESC, month DESC, revenue DESC;

-- Month-over-month growth analysis
WITH monthly_metrics AS (
    SELECT 
        year,
        month,
        category,
        SUM(total_amount) as monthly_revenue,
        SUM(total_transactions) as monthly_transactions
    FROM gold_db.daily_summary
    GROUP BY year, month, category
)
SELECT 
    current.year,
    current.month,
    current.category,
    current.monthly_revenue,
    previous.monthly_revenue as previous_month_revenue,
    ROUND(
        ((current.monthly_revenue - previous.monthly_revenue) / previous.monthly_revenue * 100), 
        2
    ) as revenue_growth_pct
FROM monthly_metrics current
LEFT JOIN monthly_metrics previous
    ON current.category = previous.category
    AND current.year = previous.year
    AND current.month = previous.month + 1
WHERE current.year = YEAR(CURRENT_DATE)
ORDER BY current.month DESC, revenue_growth_pct DESC;

-- Top performing categories by quarter
SELECT 
    year,
    quarter,
    category,
    SUM(total_amount) as quarterly_revenue,
    SUM(total_transactions) as quarterly_transactions,
    RANK() OVER (PARTITION BY year, quarter ORDER BY SUM(total_amount) DESC) as revenue_rank
FROM gold_db.daily_summary
GROUP BY year, quarter, category
ORDER BY year DESC, quarter DESC, revenue_rank;

-- 7-day moving average trend
SELECT 
    processed_date,
    category,
    total_amount,
    moving_avg_7d,
    ROUND((total_amount - moving_avg_7d) / moving_avg_7d * 100, 2) as variance_pct
FROM gold_db.daily_summary
WHERE processed_date >= DATE_ADD('day', -30, CURRENT_DATE)
ORDER BY processed_date DESC, category;
