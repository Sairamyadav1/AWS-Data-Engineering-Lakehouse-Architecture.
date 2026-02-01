# Sample Data

This directory contains sample datasets for testing the AWS Lakehouse architecture.

## Files

### `sample_transactions.csv`
Sample e-commerce transaction data with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Unique transaction ID |
| timestamp | TIMESTAMP | Transaction timestamp |
| customer_id | STRING | Customer identifier |
| category | STRING | Product category |
| amount | DECIMAL | Transaction amount |
| status | STRING | Transaction status (completed, pending, cancelled) |
| region | STRING | Geographic region |

## Usage

### Upload to S3 Bronze Bucket

```bash
# Upload sample data to Bronze layer
aws s3 cp sample_transactions.csv s3://your-bronze-bucket/raw-data/2024/01/sample_transactions.csv
```

### Test ETL Pipeline

1. Run Bronze ingestion job
2. Run Silver transformation job
3. Run Gold aggregation job
4. Query results in Athena

### Expected Output

After processing through all layers:

- **Bronze**: 30 raw records
- **Silver**: ~28-30 cleaned records (depending on data quality rules)
- **Gold**: Aggregated metrics by date and category

## Generating More Data

You can generate additional sample data using this Python script:

```python
import csv
from datetime import datetime, timedelta
import random

categories = ['Electronics', 'Clothing', 'Home', 'Books']
regions = ['US-West', 'US-East', 'EU-West', 'APAC']
statuses = ['completed', 'pending', 'cancelled']

with open('more_transactions.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'timestamp', 'customer_id', 'category', 'amount', 'status', 'region'])
    
    start_date = datetime(2024, 1, 1)
    for i in range(1000):
        timestamp = start_date + timedelta(days=random.randint(0, 90), 
                                          hours=random.randint(0, 23),
                                          minutes=random.randint(0, 59))
        customer_id = f"C{random.randint(1000, 2000)}"
        category = random.choice(categories)
        amount = round(random.uniform(10, 3000), 2)
        status = random.choices(statuses, weights=[0.85, 0.10, 0.05])[0]
        region = random.choice(regions)
        
        writer.writerow([i+1, timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
                        customer_id, category, amount, status, region])
```

## Data Quality Notes

This sample dataset includes:
- Valid transactions (majority)
- Pending transactions (for testing filtering)
- Cancelled transactions (for testing filtering)
- Multiple transactions per customer (for deduplication testing)
- Data across multiple dates (for partitioning testing)

## Best Practices

1. Always test with sample data before processing production data
2. Validate data quality rules with edge cases
3. Test partition strategies with date-based data
4. Verify aggregations manually for accuracy
5. Use sample data for performance benchmarking
