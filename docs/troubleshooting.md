# Troubleshooting Guide

Common issues and solutions for the AWS Data Engineering Lakehouse Architecture.

## Table of Contents

1. [AWS Glue Issues](#aws-glue-issues)
2. [S3 Issues](#s3-issues)
3. [Athena Issues](#athena-issues)
4. [Crawler Issues](#crawler-issues)
5. [Snowflake Integration Issues](#snowflake-integration-issues)
6. [Performance Issues](#performance-issues)
7. [IAM & Security Issues](#iam--security-issues)

## AWS Glue Issues

### Issue: Glue Job Fails with "Access Denied" Error

**Symptoms**:
```
Error: Access Denied (Service: Amazon S3; Status Code: 403)
```

**Causes**:
- IAM role missing S3 permissions
- Bucket policy blocking access
- KMS key permissions missing

**Solutions**:

1. Check IAM role permissions:
```bash
aws iam get-role-policy \
  --role-name GlueETLRole \
  --policy-name GlueS3Access
```

2. Verify bucket policy:
```bash
aws s3api get-bucket-policy --bucket your-bucket
```

3. Test permissions:
```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT_ID:role/GlueETLRole \
  --action-names s3:GetObject s3:PutObject \
  --resource-arns arn:aws:s3:::your-bucket/*
```

### Issue: Glue Job Timeout

**Symptoms**:
```
Job run exceeded timeout of 60 minutes
```

**Solutions**:

1. Increase job timeout:
```bash
aws glue update-job \
  --job-name your-job \
  --job-update Timeout=120
```

2. Optimize job performance:
- Increase DPU (workers)
- Partition input data
- Use job bookmarks
- Filter data early

### Issue: "Schema Mismatch" Error

**Symptoms**:
```
Error: Schema mismatch between expected and actual
```

**Solutions**:

1. Use ApplyMapping to handle schema changes:
```python
from awsglue.transforms import ApplyMapping

mapped_df = ApplyMapping.apply(
    frame=df,
    mappings=[
        ("old_column", "string", "new_column", "string"),
        ("amount", "string", "amount", "double")
    ]
)
```

2. Enable schema evolution:
```python
df.write \
  .option("mergeSchema", "true") \
  .parquet("s3://bucket/path/")
```

### Issue: Job Bookmarks Not Working

**Symptoms**:
- Job reprocesses all data every run
- Duplicate records in output

**Solutions**:

1. Verify bookmark is enabled:
```bash
aws glue get-job --job-name your-job | grep bookmark
```

2. Use transformation context:
```python
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="db",
    table_name="table",
    transformation_ctx="unique_ctx_name"  # Must be unique and consistent
)
```

3. Commit job at the end:
```python
job.commit()  # Don't forget this!
```

### Issue: Out of Memory Error

**Symptoms**:
```
Error: java.lang.OutOfMemoryError: Java heap space
```

**Solutions**:

1. Increase worker memory:
```bash
aws glue update-job \
  --job-name your-job \
  --job-update WorkerType=G.2X  # or G.4X, G.8X
```

2. Process data in batches:
```python
# Read in smaller chunks
df = spark.read.option("maxFilesPerTrigger", 1000) \
    .parquet("s3://bucket/path/")
```

3. Optimize transformations:
```python
# Use columnar operations instead of UDFs
df = df.withColumn("new_col", col("old_col") * 2)  # Good
# df = df.withColumn("new_col", udf_function(col("old_col")))  # Avoid if possible
```

## S3 Issues

### Issue: S3 Data Not Visible in Glue Catalog

**Symptoms**:
- Crawler succeeds but no tables created
- Tables exist but show no partitions

**Solutions**:

1. Check S3 path structure:
```bash
# Partitions should follow Hive format
s3://bucket/table/year=2024/month=01/data.parquet
```

2. Verify file formats:
```bash
aws s3 ls s3://bucket/path/ --recursive | head
```

3. Check crawler exclusions:
```bash
aws glue get-crawler --name crawler-name | grep -A 5 Exclusions
```

4. Repair partitions manually:
```sql
MSCK REPAIR TABLE database.table;
```

### Issue: S3 Upload Fails

**Symptoms**:
```
Error: An error occurred (SlowDown) when calling the PutObject operation
```

**Solutions**:

1. Implement retry logic:
```python
from botocore.exceptions import ClientError
import time

def upload_with_retry(s3_client, bucket, key, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            s3_client.put_object(Bucket=bucket, Key=key, Body=data)
            break
        except ClientError as e:
            if e.response['Error']['Code'] == 'SlowDown':
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

2. Use multipart upload for large files:
```python
s3_client.upload_file(
    filename,
    bucket,
    key,
    Config=TransferConfig(
        multipart_threshold=1024 * 25,  # 25MB
        max_concurrency=10
    )
)
```

### Issue: S3 Lifecycle Policy Not Working

**Symptoms**:
- Objects not transitioning to different storage classes
- Old data not being deleted

**Solutions**:

1. Verify lifecycle policy:
```bash
aws s3api get-bucket-lifecycle-configuration --bucket your-bucket
```

2. Check policy syntax:
```json
{
  "Rules": [
    {
      "Id": "Transition",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "logs/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        }
      ]
    }
  ]
}
```

3. Wait for policy to take effect (can take 24-48 hours)

## Athena Issues

### Issue: "HIVE_PARTITION_SCHEMA_MISMATCH" Error

**Symptoms**:
```
Error: HIVE_PARTITION_SCHEMA_MISMATCH: There is a mismatch between the table and partition schemas
```

**Solutions**:

1. Drop and recreate table:
```sql
DROP TABLE IF EXISTS database.table;

-- Recreate with correct schema
CREATE EXTERNAL TABLE database.table (
    col1 string,
    col2 int
)
PARTITIONED BY (year int, month int)
STORED AS PARQUET
LOCATION 's3://bucket/path/';

MSCK REPAIR TABLE database.table;
```

2. Or update partition schema:
```sql
ALTER TABLE database.table DROP PARTITION (year=2024, month=01);
ALTER TABLE database.table ADD PARTITION (year=2024, month=01) 
    LOCATION 's3://bucket/path/year=2024/month=01/';
```

### Issue: Query Returns No Results

**Symptoms**:
- Query completes successfully but returns 0 rows
- Expected data exists in S3

**Solutions**:

1. Check partition filters:
```sql
-- Verify partitions exist
SHOW PARTITIONS database.table;

-- Check data in specific partition
SELECT * FROM database.table 
WHERE year = 2024 AND month = 1
LIMIT 10;
```

2. Repair partitions:
```sql
MSCK REPAIR TABLE database.table;
```

3. Verify file format matches table definition:
```sql
SHOW CREATE TABLE database.table;
```

### Issue: High Query Costs

**Symptoms**:
- Unexpected charges from Athena
- Queries scanning TBs of data

**Solutions**:

1. Check data scanned:
```sql
-- View query history
SELECT 
    query_id,
    query,
    data_scanned_in_bytes / 1024 / 1024 / 1024 as data_scanned_gb,
    execution_time_in_millis / 1000 as execution_time_sec
FROM "information_schema"."queries"
ORDER BY data_scanned_in_bytes DESC
LIMIT 10;
```

2. Use partitioning:
```sql
-- Good: Partition filter
SELECT * FROM table 
WHERE year = 2024 AND month = 1;

-- Bad: No partition filter
SELECT * FROM table 
WHERE amount > 100;
```

3. Use columnar format and compression:
```sql
CREATE TABLE optimized_table
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    partitioned_by = ARRAY['year', 'month']
) AS
SELECT * FROM original_table;
```

## Crawler Issues

### Issue: Crawler Running Too Long

**Symptoms**:
- Crawler takes hours to complete
- High costs from crawler DPUs

**Solutions**:

1. Use crawling filters:
```json
{
  "Exclusions": [
    "**.tmp",
    "**_$folder$",
    "**/archive/**"
  ]
}
```

2. Use CRAWL_NEW_FOLDERS_ONLY:
```json
{
  "RecrawlPolicy": {
    "RecrawlBehavior": "CRAWL_NEW_FOLDERS_ONLY"
  }
}
```

3. Reduce crawler frequency:
```bash
# Change from hourly to daily
aws glue update-crawler \
  --name crawler-name \
  --schedule "cron(0 2 * * ? *)"
```

### Issue: Crawler Creates Wrong Schema

**Symptoms**:
- Column types are incorrect
- Nested structures flattened

**Solutions**:

1. Specify classifier:
```bash
aws glue create-classifier \
  --csv-classifier Name=my-classifier,Delimiter=',',QuoteSymbol='"',ContainsHeader=PRESENT
```

2. Use custom classifier:
```bash
aws glue update-crawler \
  --name crawler-name \
  --classifiers my-classifier
```

3. Manually create table with correct schema:
```sql
CREATE EXTERNAL TABLE database.table (
    col1 string,
    col2 array<struct<field1:string, field2:int>>
)
STORED AS PARQUET
LOCATION 's3://bucket/path/';
```

## Snowflake Integration Issues

### Issue: External Table Returns No Data

**Symptoms**:
```sql
SELECT * FROM external_table; -- Returns 0 rows
```

**Solutions**:

1. Verify storage integration:
```sql
DESC STORAGE INTEGRATION aws_integration;
```

2. Check stage configuration:
```sql
LIST @stage_name;
```

3. Test S3 access:
```sql
SELECT $1, $2, $3 FROM @stage_name (FILE_FORMAT => 'PARQUET_FORMAT') LIMIT 10;
```

4. Verify IAM trust relationship:
```bash
aws iam get-role --role-name SnowflakeS3Role
```

### Issue: Snowpipe Not Loading Data

**Symptoms**:
- New files in S3 but not appearing in Snowflake
- Pipe status shows no files processed

**Solutions**:

1. Check pipe status:
```sql
SELECT SYSTEM$PIPE_STATUS('pipe_name');
```

2. Verify S3 event notification:
```bash
aws s3api get-bucket-notification-configuration --bucket your-bucket
```

3. Check copy history:
```sql
SELECT * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'YOUR_TABLE',
    START_TIME => DATEADD(HOURS, -1, CURRENT_TIMESTAMP())
));
```

4. Manually refresh pipe:
```sql
ALTER PIPE pipe_name REFRESH;
```

## Performance Issues

### Issue: Slow ETL Jobs

**Symptoms**:
- Jobs taking much longer than expected
- High DPU consumption

**Solutions**:

1. Profile job execution:
```python
# Enable Spark UI
df.explain(True)  # See query plan
```

2. Optimize joins:
```python
# Broadcast small tables
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")
```

3. Repartition data:
```python
# Balance data across partitions
df = df.repartition(200, "key_column")
```

4. Cache intermediate results:
```python
df.cache()
df.count()  # Trigger caching
```

### Issue: Athena Queries Timing Out

**Symptoms**:
```
Error: Query exhausted resources at this scale factor
```

**Solutions**:

1. Optimize query:
```sql
-- Use WITH clauses instead of subqueries
WITH filtered_data AS (
    SELECT * FROM large_table 
    WHERE date >= '2024-01-01'
)
SELECT * FROM filtered_data;
```

2. Increase workgroup limits:
```bash
aws athena update-work-group \
  --work-group analytics \
  --configuration-updates \
  ResultConfigurationUpdates={OutputLocation=s3://bucket/},BytesScannedCutoffPerQuery=10000000000
```

3. Break query into smaller parts:
```sql
-- Process data in batches
SELECT * FROM table WHERE year = 2024 AND month = 1;
SELECT * FROM table WHERE year = 2024 AND month = 2;
-- etc.
```

## IAM & Security Issues

### Issue: "User is not authorized" Error

**Symptoms**:
```
Error: User: arn:aws:iam::xxx:user/xxx is not authorized to perform: glue:GetDatabase
```

**Solutions**:

1. Check user permissions:
```bash
aws iam list-attached-user-policies --user-name username
```

2. Add required policy:
```bash
aws iam attach-user-policy \
  --user-name username \
  --policy-arn arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess
```

3. Verify resource-based policies:
```bash
aws glue get-resource-policy
```

### Issue: Cross-Account Access Not Working

**Symptoms**:
- Cannot access S3 bucket in another account
- Permission denied on cross-account resources

**Solutions**:

1. Configure bucket policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::OTHER_ACCOUNT:role/GlueRole"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::bucket/*",
        "arn:aws:s3:::bucket"
      ]
    }
  ]
}
```

2. Update IAM role trust policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::OTHER_ACCOUNT:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## Getting Help

If you can't resolve an issue:

1. **Check AWS Service Health Dashboard**: https://status.aws.amazon.com/
2. **Review CloudWatch Logs**: Look for detailed error messages
3. **AWS Support**: Open a support ticket
4. **Community Forums**: AWS re:Post, Stack Overflow
5. **GitHub Issues**: Report bugs or request features

## Useful Commands

### Debug Glue Jobs

```bash
# Get job run details
aws glue get-job-run --job-name job-name --run-id run-id

# View CloudWatch logs
aws logs tail /aws-glue/jobs/error --follow

# Get job metrics
aws cloudwatch get-metric-statistics \
  --namespace Glue \
  --metric-name glue.driver.aggregate.numCompletedTasks \
  --dimensions Name=JobName,Value=job-name
```

### Debug S3

```bash
# Check bucket permissions
aws s3api get-bucket-acl --bucket bucket-name

# List recent objects
aws s3 ls s3://bucket/path/ --recursive --human-readable --summarize

# Check bucket region
aws s3api get-bucket-location --bucket bucket-name
```

### Debug Athena

```bash
# Get query execution details
aws athena get-query-execution --query-execution-id query-id

# View query results
aws athena get-query-results --query-execution-id query-id
```
