# Data Engineering Best Practices

This document outlines industry best practices for building and maintaining data lakehouse architectures.

## Table of Contents

1. [Architecture Patterns](#architecture-patterns)
2. [Data Quality](#data-quality)
3. [Performance Optimization](#performance-optimization)
4. [Security](#security)
5. [Cost Optimization](#cost-optimization)
6. [Monitoring & Observability](#monitoring--observability)
7. [Data Governance](#data-governance)

## Architecture Patterns

### Medallion Architecture (Bronze-Silver-Gold)

**Bronze Layer (Raw)**
- Store data in original format
- Immutable storage (append-only)
- Preserve full history
- Minimal transformation
- Schema on read

**Silver Layer (Cleaned)**
- Data quality checks
- Deduplication
- Schema enforcement
- Type casting
- Standardization
- Partitioned for performance

**Gold Layer (Business)**
- Business logic applied
- Aggregated metrics
- Dimension modeling
- Optimized for queries
- Star/snowflake schema

### Why This Pattern?

✅ **Flexibility**: Can reprocess data from any layer
✅ **Auditability**: Full lineage from source to consumption
✅ **Performance**: Each layer optimized for its purpose
✅ **Reliability**: Failures isolated to specific layers
✅ **Scalability**: Independent scaling of layers

## Data Quality

### 1. Data Validation Rules

Implement checks at each layer:

```python
# Example: Data quality checks in Silver layer
def validate_data(df):
    """
    Apply data quality rules
    """
    # Null checks
    assert df.filter(col("id").isNull()).count() == 0, "ID cannot be null"
    
    # Range checks
    assert df.filter(col("amount") < 0).count() == 0, "Amount must be positive"
    
    # Uniqueness checks
    assert df.count() == df.select("id").distinct().count(), "Duplicate IDs found"
    
    # Format checks
    assert df.filter(~col("email").rlike(r'^[\w\.-]+@[\w\.-]+\.\w+$')).count() == 0, \
        "Invalid email format"
    
    return df
```

### 2. Data Quality Metrics

Track these metrics:

- **Completeness**: % of non-null values
- **Uniqueness**: % of unique records
- **Validity**: % of records meeting business rules
- **Consistency**: Cross-field validation
- **Timeliness**: Data freshness
- **Accuracy**: Comparison with source systems

### 3. Error Handling

```python
# Graceful error handling
try:
    df = transform_data(raw_df)
except Exception as e:
    # Log error
    logger.error(f"Transformation failed: {str(e)}")
    
    # Write to dead letter queue
    raw_df.write.parquet("s3://bucket/errors/")
    
    # Send alert
    send_alert(f"ETL failed: {str(e)}")
    
    # Continue with partial data if acceptable
    df = raw_df.filter(col("is_valid") == True)
```

### 4. Data Profiling

Before processing, profile your data:

```sql
-- Data profiling query
SELECT 
  COUNT(*) as total_records,
  COUNT(DISTINCT id) as unique_ids,
  SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) as null_ids,
  MIN(amount) as min_amount,
  MAX(amount) as max_amount,
  AVG(amount) as avg_amount,
  STDDEV(amount) as stddev_amount
FROM source_table;
```

## Performance Optimization

### 1. Partitioning Strategy

```python
# Partition by date for time-series data
df.write.partitionBy("year", "month", "day") \
    .parquet("s3://bucket/data/")

# Partition by high-cardinality column
df.write.partitionBy("region") \
    .parquet("s3://bucket/data/")
```

**Rules of Thumb**:
- Partition size: 128MB - 1GB
- Number of partitions: < 10,000
- Partition key: High query predicate, low cardinality

### 2. File Format Selection

| Format | Use Case | Pros | Cons |
|--------|----------|------|------|
| Parquet | Analytics | Columnar, compression, schema | Not human-readable |
| ORC | Hive/Hadoop | Better compression | Less compatible |
| Avro | Streaming | Schema evolution | Row-based |
| CSV | Simple data | Human-readable | No schema, slow |
| JSON | Semi-structured | Flexible | Verbose, slow |

**Recommendation**: Use Parquet for lakehouse layers

### 3. Compression

```python
# Use Snappy for balance of speed and size
df.write.option("compression", "snappy") \
    .parquet("s3://bucket/data/")

# Compression comparison
# Snappy: Fast compression, moderate size
# Gzip: Slower, better compression
# LZO: Fast, splittable
# Brotli: Best compression, slower
```

### 4. Predicate Pushdown

```python
# Good: Filter pushed to source
df = spark.read.parquet("s3://bucket/data/") \
    .filter(col("date") >= "2024-01-01")

# Bad: Filter after reading all data
df = spark.read.parquet("s3://bucket/data/")
df = df.filter(col("date") >= "2024-01-01")
```

### 5. Broadcasting Small Tables

```python
from pyspark.sql.functions import broadcast

# Broadcast small dimension tables
result = large_fact.join(
    broadcast(small_dimension),
    on="key"
)
```

### 6. Caching

```python
# Cache frequently accessed data
df.cache()
df.count()  # Materialize cache

# Unpersist when done
df.unpersist()
```

## Security

### 1. Encryption

- **At Rest**: S3 encryption (AES-256 or KMS)
- **In Transit**: TLS/SSL for all connections
- **Column-level**: For sensitive data (PII)

```bash
# Enable S3 encryption
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration \
  '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "key-id"}}]}'
```

### 2. Access Control

Implement least-privilege:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::bucket/gold/*",
  "Condition": {
    "StringEquals": {
      "aws:PrincipalOrgID": "o-xxxxx"
    }
  }
}
```

### 3. Data Masking

```python
# Mask PII in Silver layer
from pyspark.sql.functions import sha2, regexp_replace

df = df.withColumn(
    "email_masked",
    regexp_replace(col("email"), r'(.{2}).*(@.*)', r'\1***\2')
)

df = df.withColumn(
    "ssn_hashed",
    sha2(col("ssn"), 256)
)
```

### 4. Audit Logging

- Enable CloudTrail for all API calls
- Log data access with AWS Lake Formation
- Monitor with CloudWatch Logs

## Cost Optimization

### 1. S3 Storage Classes

```bash
# Lifecycle policy for cost optimization
{
  "Rules": [
    {
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER"},
        {"Days": 365, "StorageClass": "DEEP_ARCHIVE"}
      ]
    }
  ]
}
```

### 2. Glue Job Optimization

- Use appropriate worker type (G.1X vs G.2X)
- Set job timeout to prevent runaway costs
- Use job bookmarks to avoid reprocessing
- Schedule jobs during off-peak hours

```python
# Job bookmark example
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
job.init(args['JOB_NAME'], args)

# Glue tracks what's processed
df = glueContext.create_dynamic_frame.from_catalog(
    database="db",
    table_name="table",
    transformation_ctx="datasource"
)

job.commit()  # Checkpoint bookmark
```

### 3. Athena Cost Control

- Partition data aggressively
- Use columnar formats (Parquet)
- Compress data
- Limit query results
- Use workgroup limits

```sql
-- Create cost-controlled workgroup
CREATE WORKGROUP analytics_team
WITH (
  per_query_data_usage_control = 10GB,
  enforce_workgroup_configuration = true
)
```

### 4. Resource Tagging

```bash
# Tag all resources for cost allocation
aws glue tag-resource \
  --resource-arn arn:aws:glue:region:account:job/jobname \
  --tags-to-add Project=Lakehouse,Environment=Production,CostCenter=Analytics
```

## Monitoring & Observability

### 1. Key Metrics

Track these metrics:

**Infrastructure**:
- Glue job duration and DPU hours
- S3 storage size and growth rate
- Athena query execution time and data scanned
- Error rates and retries

**Data Quality**:
- Record counts at each layer
- Null percentages
- Duplicate rates
- Schema changes

**Business**:
- Data freshness (time since last update)
- SLA compliance
- Pipeline success rate

### 2. CloudWatch Dashboards

```python
# Example: Custom metric for data quality
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='Lakehouse',
    MetricData=[
        {
            'MetricName': 'RecordCount',
            'Value': record_count,
            'Unit': 'Count',
            'Dimensions': [
                {'Name': 'Layer', 'Value': 'Silver'},
                {'Name': 'Table', 'Value': 'transactions'}
            ]
        }
    ]
)
```

### 3. Alerting

Set up alerts for:
- Job failures
- Data quality threshold violations
- Cost anomalies
- Performance degradation

## Data Governance

### 1. Data Catalog

- Maintain metadata in Glue Data Catalog
- Document table schemas and business definitions
- Track data lineage
- Version control schema changes

### 2. Data Lineage

```python
# Track lineage in metadata
metadata = {
    "source": "s3://bronze/raw/",
    "transformation": "silver_transformation_v2.py",
    "destination": "s3://silver/cleaned/",
    "timestamp": datetime.now(),
    "record_count": df.count(),
    "schema_version": "2.1"
}
```

### 3. Data Quality SLAs

Define and monitor:
- **Availability**: 99.9% uptime
- **Freshness**: Data < 1 hour old
- **Completeness**: > 95% non-null
- **Accuracy**: < 0.1% error rate

### 4. Schema Evolution

Handle schema changes gracefully:

```python
# Add columns with defaults
df = df.withColumn("new_column", lit(None))

# Rename columns
df = df.withColumnRenamed("old_name", "new_name")

# Maintain version history
df.write.option("mergeSchema", "true") \
    .parquet("s3://bucket/data/")
```

## Testing

### 1. Unit Tests

```python
import pytest
from pyspark.sql import SparkSession

def test_transformation():
    spark = SparkSession.builder.getOrCreate()
    
    # Create test data
    test_df = spark.createDataFrame([
        (1, "test", 100),
        (2, "test", 200)
    ], ["id", "name", "amount"])
    
    # Apply transformation
    result = transform_function(test_df)
    
    # Assert expectations
    assert result.count() == 2
    assert result.filter("amount < 0").count() == 0
```

### 2. Integration Tests

Test full pipeline with sample data:

```bash
# Run end-to-end test
python test_pipeline.py --env test --sample-size 1000
```

### 3. Data Quality Tests

```sql
-- Test: No duplicates
SELECT id, COUNT(*) as cnt
FROM gold.daily_summary
GROUP BY id
HAVING cnt > 1;

-- Test: Referential integrity
SELECT f.customer_id
FROM fact_table f
LEFT JOIN customer_dim c ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

## Documentation

Maintain documentation for:

1. **Architecture Diagrams**: System design and data flow
2. **Data Dictionary**: Table schemas and business definitions
3. **Runbooks**: Operational procedures
4. **Deployment Guide**: Setup and configuration
5. **Troubleshooting Guide**: Common issues and solutions

## Continuous Improvement

- Regular performance reviews
- Cost optimization audits
- Security assessments
- User feedback loops
- Technology stack updates

## References

- [AWS Big Data Blog](https://aws.amazon.com/blogs/big-data/)
- [Data Engineering Cookbook](https://github.com/andkret/Cookbook)
- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
