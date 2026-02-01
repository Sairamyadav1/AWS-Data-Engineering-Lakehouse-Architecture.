# Snowflake Integration with AWS Lakehouse

This directory contains scripts and documentation for integrating Snowflake with the AWS Lakehouse architecture.

## Overview

Snowflake serves as the cloud data warehouse layer for advanced analytics, BI, and data sharing on top of the Lakehouse.

## Integration Architecture

```
AWS S3 Gold Layer ──> Snowflake External Tables ──> Snowflake Analytics
                  │
                  └─> Snowpipe Auto-Ingestion ──> Snowflake Tables
```

## Setup Instructions

### 1. Prerequisites

- Snowflake account with ACCOUNTADMIN access
- AWS S3 buckets with Gold layer data
- IAM role for Snowflake access to S3

### 2. Create Snowflake Objects

Run the scripts in order:
1. `setup/01_create_storage_integration.sql` - Set up S3 integration
2. `setup/02_create_database_schema.sql` - Create database structure
3. `setup/03_create_external_tables.sql` - Create external tables
4. `setup/04_create_snowpipe.sql` - Set up auto-ingestion (optional)

### 3. Configure AWS IAM

Create an IAM role for Snowflake:
```bash
aws iam create-role \
  --role-name SnowflakeS3Role \
  --assume-role-policy-document file://aws-snowflake-trust-policy.json

aws iam put-role-policy \
  --role-name SnowflakeS3Role \
  --policy-name SnowflakeS3Access \
  --policy-document file://aws-snowflake-s3-policy.json
```

## Features

### External Tables
- Query S3 data directly from Snowflake
- No data duplication
- Automatic schema detection
- Partition pruning for performance

### Snowpipe
- Continuous data ingestion
- Event-driven (S3 notifications)
- Near real-time data availability
- Automatic error handling

### Data Sharing
- Share data with other Snowflake accounts
- No data copying required
- Granular access control
- Real-time updates

## Best Practices

1. **Use External Tables for Infrequent Access**
   - Lower storage costs
   - Reduced maintenance
   - Good for historical data

2. **Use Regular Tables for Frequent Queries**
   - Better performance
   - More query optimization options
   - Recommended for Gold layer analytics

3. **Partition Data Appropriately**
   - Match S3 partition scheme
   - Enable partition pruning
   - Reduce query costs

4. **Monitor Costs**
   - Track compute usage
   - Monitor storage growth
   - Use resource monitors

## Example Queries

See `queries/` directory for:
- Data quality checks
- Business analytics
- Performance optimization
- Data sharing setup

## Troubleshooting

### Common Issues

**External Table Returns No Data**
- Verify S3 path is correct
- Check IAM role permissions
- Validate storage integration status

**Snowpipe Not Loading Data**
- Check S3 event notifications
- Verify pipe status
- Review COPY_HISTORY

**Performance Issues**
- Use appropriate warehouse size
- Enable partition pruning
- Consider materialized views

## Security

- Use AWS PrivateLink for secure connectivity
- Enable Snowflake encryption
- Implement row-level security
- Audit data access with ACCOUNT_USAGE

## Additional Resources

- [Snowflake External Tables Documentation](https://docs.snowflake.com/en/user-guide/tables-external)
- [Snowpipe Documentation](https://docs.snowflake.com/en/user-guide/data-load-snowpipe)
- [Storage Integration Guide](https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration)
