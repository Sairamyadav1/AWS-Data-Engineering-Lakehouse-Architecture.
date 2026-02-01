# Quick Start Guide

This guide will help you get started with the AWS Data Engineering Lakehouse Architecture.

## Prerequisites

Before you begin, ensure you have the following:

### AWS Account Setup
- Active AWS account with admin access
- AWS CLI installed and configured
- AWS credentials with appropriate permissions

### Local Development Setup
- Python 3.8 or higher
- Git
- Text editor or IDE
- (Optional) Docker for local testing

## Step-by-Step Setup

### 1. Install AWS CLI

#### macOS
```bash
brew install awscli
```

#### Linux
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### Windows
Download and run the AWS CLI MSI installer from the AWS website.

### 2. Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

### 3. Clone the Repository

```bash
git clone https://github.com/Sairamyadav1/AWS-Data-Engineering-Lakehouse-Architecture.git
cd AWS-Data-Engineering-Lakehouse-Architecture
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Configure Deployment Parameters

Edit `infrastructure/deploy.sh` and update:

```bash
PROJECT_NAME="your-project-name"
ENVIRONMENT="dev"  # or staging, prod
REGION="us-east-1"  # your preferred region
```

Edit `infrastructure/cloudformation_template.yaml` if you need to customize:
- S3 bucket lifecycle policies
- CloudWatch log retention
- SNS email subscription

### 6. Deploy Infrastructure

```bash
cd infrastructure
chmod +x deploy.sh
./deploy.sh
```

This will:
- Create CloudFormation stack
- Set up S3 buckets with proper structure
- Create Glue databases (Bronze, Silver, Gold)
- Set up IAM roles and policies
- Create Athena workgroup
- Configure SNS topic for alerts
- Upload Glue job scripts to S3

### 7. Create Glue ETL Jobs

After deployment, create Glue jobs using the AWS Console or CLI:

#### Bronze Layer Job
```bash
aws glue create-job \
    --name bronze-ingest-job \
    --role <GLUE_JOB_ROLE_ARN> \
    --command "Name=glueetl,ScriptLocation=s3://<BUCKET>/scripts/bronze/ingest_raw_data.py" \
    --default-arguments '{
        "--job-language":"python",
        "--enable-metrics":"true",
        "--enable-continuous-cloudwatch-log":"true"
    }' \
    --glue-version "3.0" \
    --worker-type "G.1X" \
    --number-of-workers 2
```

#### Silver Layer Job
```bash
aws glue create-job \
    --name silver-transform-job \
    --role <GLUE_JOB_ROLE_ARN> \
    --command "Name=glueetl,ScriptLocation=s3://<BUCKET>/scripts/silver/transform_and_clean.py" \
    --default-arguments '{
        "--job-language":"python",
        "--enable-metrics":"true",
        "--enable-continuous-cloudwatch-log":"true"
    }' \
    --glue-version "3.0" \
    --worker-type "G.1X" \
    --number-of-workers 2
```

#### Gold Layer Job
```bash
aws glue create-job \
    --name gold-aggregate-job \
    --role <GLUE_JOB_ROLE_ARN> \
    --command "Name=glueetl,ScriptLocation=s3://<BUCKET>/scripts/gold/aggregate_analytics.py" \
    --default-arguments '{
        "--job-language":"python",
        "--enable-metrics":"true",
        "--enable-continuous-cloudwatch-log":"true"
    }' \
    --glue-version "3.0" \
    --worker-type "G.1X" \
    --number-of-workers 2
```

### 8. Create Glue Crawlers

Update the configuration in `glue_crawlers/create_crawlers.py` with your bucket name and role ARN, then run:

```bash
cd glue_crawlers
python create_crawlers.py
```

Or use AWS Console to create crawlers manually.

### 9. Setup CloudWatch Monitoring

```bash
cd cloudwatch
python monitoring_setup.py
```

Update the script with your SNS topic ARN before running.

### 10. Upload Sample Data (Optional)

```bash
BUCKET_NAME="your-lakehouse-bucket"

aws s3 cp sample_data/sample_customers.csv s3://$BUCKET_NAME/bronze/customers/
aws s3 cp sample_data/sample_transactions.csv s3://$BUCKET_NAME/bronze/transactions/
```

### 11. Run the Pipeline

#### Start Bronze Layer Crawler
```bash
aws glue start-crawler --name bronze-layer-crawler
```

Wait for crawler to complete, then:

#### Run Bronze Layer ETL Job
```bash
aws glue start-job-run \
    --job-name bronze-ingest-job \
    --arguments='--source_path=s3://your-bucket/source/ --target_path=s3://your-bucket/bronze/'
```

#### Run Silver Layer ETL Job
```bash
aws glue start-job-run \
    --job-name silver-transform-job \
    --arguments='--bronze_path=s3://your-bucket/bronze/ --silver_path=s3://your-bucket/silver/'
```

#### Run Gold Layer ETL Job
```bash
aws glue start-job-run \
    --job-name gold-aggregate-job \
    --arguments='--silver_path=s3://your-bucket/silver/ --gold_path=s3://your-bucket/gold/'
```

### 12. Query Data with Athena

Open AWS Athena console and run queries from `athena_queries/analytics_queries.sql`

Example:
```sql
SELECT * 
FROM lakehouse_gold_db.daily_aggregates
ORDER BY ingestion_date DESC
LIMIT 10;
```

## Snowflake Integration (Optional)

### 1. Setup Snowflake Account

Sign up for Snowflake and create:
- Database: `LAKEHOUSE_DB`
- Warehouse: `LAKEHOUSE_WH`
- Schema: `ANALYTICS`

### 2. Configure Storage Integration

```sql
CREATE STORAGE INTEGRATION aws_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::ACCOUNT_ID:role/SnowflakeS3Role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://your-bucket/gold/');
```

### 3. Update IAM Trust Policy

Add Snowflake's AWS account to the trust policy of your Snowflake S3 role.

### 4. Run Integration Script

Update `snowflake/snowflake_integration.py` with your credentials:

```bash
cd snowflake
export SNOWFLAKE_PASSWORD="your-password"
python snowflake_integration.py
```

## Monitoring and Maintenance

### View CloudWatch Logs
```bash
aws logs tail /aws/glue/jobs/lakehouse --follow
```

### Check Job Status
```bash
aws glue get-job-runs --job-name bronze-ingest-job --max-results 5
```

### Monitor Costs
- Use AWS Cost Explorer
- Set up billing alerts
- Monitor S3 storage costs
- Track Glue job DPU usage

## Troubleshooting

### Common Issues

**Issue**: Glue job fails with permission denied
- **Solution**: Check IAM role has correct S3 and Glue permissions

**Issue**: Crawler doesn't find tables
- **Solution**: Verify S3 path, ensure data files exist

**Issue**: Athena query fails
- **Solution**: Check Glue catalog, verify table schemas

**Issue**: High costs
- **Solution**: Optimize Glue job worker configuration, use S3 lifecycle policies

## Next Steps

1. Schedule Glue jobs using AWS Glue Triggers or EventBridge
2. Set up CI/CD pipeline for automated deployments
3. Implement data quality tests
4. Create custom CloudWatch dashboards
5. Build BI reports in Snowflake or QuickSight
6. Implement data governance policies
7. Add more data sources

## Additional Resources

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- [Amazon Athena Documentation](https://docs.aws.amazon.com/athena/)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review AWS CloudWatch logs
3. Open an issue on GitHub
4. Contact the repository maintainer
