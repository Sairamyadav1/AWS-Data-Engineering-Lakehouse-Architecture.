-- Query Silver Layer: Analyze cleaned data
SELECT 
    processed_date,
    category,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM silver_db.cleaned_data
WHERE processed_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY processed_date, category
ORDER BY processed_date DESC, total_amount DESC;

-- Data quality metrics for Silver layer
SELECT 
    'Total Records' as metric,
    COUNT(*) as value
FROM silver_db.cleaned_data
UNION ALL
SELECT 
    'Records with Quality Issues',
    COUNT(*)
FROM silver_db.cleaned_data
WHERE quality_score < 100
UNION ALL
SELECT 
    'Valid Records',
    COUNT(*)
FROM silver_db.cleaned_data
WHERE is_valid = true;

-- Identify duplicates that might have been missed
SELECT 
    id,
    timestamp,
    COUNT(*) as duplicate_count
FROM silver_db.cleaned_data
GROUP BY id, timestamp
HAVING COUNT(*) > 1;
