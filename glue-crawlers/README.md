# AWS Glue Crawler Configuration Guide

This directory contains AWS Glue Crawler configurations for the Bronze, Silver, and Gold layers of the Lakehouse architecture.

## Crawler Overview

AWS Glue Crawlers automatically discover and catalog metadata about your data stored in S3. They:
- Infer schema from data files
- Create or update tables in the AWS Glue Data Catalog
- Handle partitions automatically
- Support schema evolution

## Crawler Configurations

### 1. Bronze Layer Crawler (`bronze-crawler.json`)
- **Purpose**: Catalog raw data in Bronze layer
- **Database**: `bronze_db`
- **Schedule**: Daily at 2 AM UTC (`cron(0 2 * * ? *)`)
- **Path**: `s3://your-bronze-bucket/processed/`
- **Behavior**: Crawl new folders only to optimize performance

### 2. Silver Layer Crawler (`silver-crawler.json`)
- **Purpose**: Catalog cleaned data in Silver layer
- **Database**: `silver_db`
- **Schedule**: Daily at 3 AM UTC (`cron(0 3 * * ? *)`)
- **Path**: `s3://your-silver-bucket/cleaned/`
- **Table Prefix**: `clean_`
- **Behavior**: Update existing tables with new partitions

### 3. Gold Layer Crawler (`gold-crawler.json`)
- **Purpose**: Catalog aggregated data in Gold layer
- **Database**: `gold_db`
- **Schedule**: Daily at 4 AM UTC (`cron(0 4 * * ? *)`)
- **Path**: `s3://your-gold-bucket/aggregated/`
- **Table Prefix**: `agg_`
- **Behavior**: Handle multiple tables with table threshold

## Deployment Instructions

### Create Crawlers via AWS CLI

```bash
# Create Bronze crawler
aws glue create-crawler --cli-input-json file://bronze-crawler.json

# Create Silver crawler
aws glue create-crawler --cli-input-json file://silver-crawler.json

# Create Gold crawler
aws glue create-crawler --cli-input-json file://gold-crawler.json
```

### Run Crawlers Manually

```bash
# Start a specific crawler
aws glue start-crawler --name bronze-layer-crawler

# Check crawler status
aws glue get-crawler --name bronze-layer-crawler

# Get crawler metrics
aws glue get-crawler-metrics --crawler-name-list bronze-layer-crawler
```

### Update Crawlers

```bash
# Update crawler configuration
aws glue update-crawler --cli-input-json file://bronze-crawler.json
```

## Schema Change Policies

All crawlers are configured with:

- **UpdateBehavior**: `UPDATE_IN_DATABASE` - Updates table schema when changes are detected
- **DeleteBehavior**: `LOG` - Logs deletions but doesn't remove tables from catalog

## Best Practices

1. **Scheduling**: Run crawlers after ETL jobs complete
   - Bronze: After raw data ingestion
   - Silver: After data cleaning
   - Gold: After aggregation

2. **Recrawl Policy**: Use `CRAWL_NEW_FOLDERS_ONLY` to avoid unnecessary costs

3. **Exclusions**: Exclude temporary files and folders
   - `*.tmp`
   - `*_$folder$`
   - `*.log`

4. **Partitioning**: Ensure your data is properly partitioned
   - Bronze: By ingestion date
   - Silver: By processed date
   - Gold: By year and month

5. **Lineage**: Enable lineage tracking for data governance

## Monitoring

Monitor crawler execution using CloudWatch:

```bash
# View crawler logs
aws logs tail /aws-glue/crawlers --follow

# Get crawler run history
aws glue get-crawler-metrics --crawler-name-list bronze-layer-crawler silver-layer-crawler gold-layer-crawler
```

## Troubleshooting

### Crawler Not Finding Data
- Verify S3 path is correct
- Check IAM role has `s3:GetObject` permission
- Ensure data files exist in the specified location

### Schema Not Updating
- Check `UpdateBehavior` is set to `UPDATE_IN_DATABASE`
- Verify data format is consistent
- Review crawler logs for errors

### Partition Discovery Issues
- Ensure partition folder structure follows Hive format (`year=2024/month=01/`)
- Run `MSCK REPAIR TABLE` if partitions are missing
- Check crawler configuration allows partition discovery

## Cost Optimization

- Use `CRAWL_NEW_FOLDERS_ONLY` to avoid re-scanning unchanged data
- Set appropriate schedule intervals (avoid over-crawling)
- Use table/partition filters when possible
- Monitor DPU consumption in CloudWatch

## Security

Ensure the Glue service role has:
- `s3:GetObject` and `s3:ListBucket` for source buckets
- `glue:*` permissions for catalog operations
- `logs:CreateLogGroup` and `logs:PutLogEvents` for CloudWatch

Example IAM policy is available in `../iam-policies/glue-crawler-policy.json`
