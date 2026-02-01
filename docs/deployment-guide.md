# Deployment Guide

This guide provides step-by-step instructions for deploying the AWS Data Engineering Lakehouse Architecture.

## Prerequisites

Before you begin, ensure you have:

1. **AWS Account** with administrative access
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```
3. **Python 3.8+** installed
4. **Git** installed
5. **Snowflake Account** (optional, for Snowflake integration)

## Architecture Components

The deployment includes:
- S3 buckets (Bronze, Silver, Gold layers)
- AWS Glue Data Catalog databases
- AWS Glue Crawlers
- AWS Glue ETL Jobs
- IAM roles and policies
- Athena workgroup
- Snowflake integration (optional)

## Step 1: Clone the Repository

```bash
git clone https://github.com/Sairamyadav1/AWS-Data-Engineering-Lakehouse-Architecture.git
cd AWS-Data-Engineering-Lakehouse-Architecture
```

## Step 2: Set Up Environment Variables

Create a configuration file:

```bash
cat > config.env << EOF
AWS_REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BRONZE_BUCKET=lakehouse-bronze-\${ACCOUNT_ID}
SILVER_BUCKET=lakehouse-silver-\${ACCOUNT_ID}
GOLD_BUCKET=lakehouse-gold-\${ACCOUNT_ID}
SCRIPTS_BUCKET=lakehouse-scripts-\${ACCOUNT_ID}
EOF

source config.env
```

## Step 3: Create S3 Buckets

```bash
# Create buckets for each layer
aws s3 mb s3://${BRONZE_BUCKET} --region ${AWS_REGION}
aws s3 mb s3://${SILVER_BUCKET} --region ${AWS_REGION}
aws s3 mb s3://${GOLD_BUCKET} --region ${AWS_REGION}
aws s3 mb s3://${SCRIPTS_BUCKET} --region ${AWS_REGION}

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ${BRONZE_BUCKET} \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket ${BRONZE_BUCKET} \
  --server-side-encryption-configuration \
  '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'

# Repeat for other buckets
for bucket in ${SILVER_BUCKET} ${GOLD_BUCKET} ${SCRIPTS_BUCKET}; do
  aws s3api put-bucket-versioning \
    --bucket $bucket \
    --versioning-configuration Status=Enabled
  
  aws s3api put-bucket-encryption \
    --bucket $bucket \
    --server-side-encryption-configuration \
    '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
done

# Configure lifecycle policies (optional)
cat > lifecycle-policy.json << EOF
{
  "Rules": [
    {
      "Id": "TransitionToIA",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 180,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket ${BRONZE_BUCKET} \
  --lifecycle-configuration file://lifecycle-policy.json
```

## Step 4: Create IAM Roles

```bash
# Update policy files with actual bucket names
sed -i "s/YOUR_ACCOUNT_ID/${ACCOUNT_ID}/g" iam-policies/*.json
sed -i "s/your-bronze-bucket/${BRONZE_BUCKET}/g" iam-policies/*.json
sed -i "s/your-silver-bucket/${SILVER_BUCKET}/g" iam-policies/*.json
sed -i "s/your-gold-bucket/${GOLD_BUCKET}/g" iam-policies/*.json
sed -i "s/your-scripts-bucket/${SCRIPTS_BUCKET}/g" iam-policies/*.json

# Create Glue ETL Role
aws iam create-role \
  --role-name GlueETLRole \
  --assume-role-policy-document file://iam-policies/glue-trust-policy.json

aws iam put-role-policy \
  --role-name GlueETLRole \
  --policy-name GlueS3Access \
  --policy-document file://iam-policies/glue-s3-policy.json

# Create Glue Crawler Role
aws iam create-role \
  --role-name GlueServiceRole \
  --assume-role-policy-document file://iam-policies/glue-trust-policy.json

aws iam put-role-policy \
  --role-name GlueServiceRole \
  --policy-name GlueCrawlerAccess \
  --policy-document file://iam-policies/glue-crawler-policy.json

# Wait for roles to propagate
sleep 10
```

## Step 5: Upload Glue Scripts

```bash
# Upload ETL scripts to S3
aws s3 cp glue-scripts/ s3://${SCRIPTS_BUCKET}/glue-scripts/ --recursive
```

## Step 6: Create Glue Data Catalog Databases

```bash
# Create databases
aws glue create-database \
  --database-input "{
    \"Name\": \"bronze_db\",
    \"Description\": \"Bronze layer - Raw data\"
  }"

aws glue create-database \
  --database-input "{
    \"Name\": \"silver_db\",
    \"Description\": \"Silver layer - Cleaned data\"
  }"

aws glue create-database \
  --database-input "{
    \"Name\": \"gold_db\",
    \"Description\": \"Gold layer - Aggregated data\"
  }"
```

## Step 7: Create Glue Crawlers

```bash
# Update crawler configurations
sed -i "s/YOUR_ACCOUNT_ID/${ACCOUNT_ID}/g" glue-crawlers/*.json
sed -i "s|s3://your-bronze-bucket|s3://${BRONZE_BUCKET}|g" glue-crawlers/*.json
sed -i "s|s3://your-silver-bucket|s3://${SILVER_BUCKET}|g" glue-crawlers/*.json
sed -i "s|s3://your-gold-bucket|s3://${GOLD_BUCKET}|g" glue-crawlers/*.json

# Create crawlers
aws glue create-crawler --cli-input-json file://glue-crawlers/bronze-crawler.json
aws glue create-crawler --cli-input-json file://glue-crawlers/silver-crawler.json
aws glue create-crawler --cli-input-json file://glue-crawlers/gold-crawler.json
```

## Step 8: Create Glue Jobs

```bash
# Update job configurations
for file in glue-scripts/*/job-config.json; do
  sed -i "s/YOUR_ACCOUNT_ID/${ACCOUNT_ID}/g" "$file"
  sed -i "s|s3://your-scripts-bucket|s3://${SCRIPTS_BUCKET}|g" "$file"
  sed -i "s|s3://your-bronze-bucket|s3://${BRONZE_BUCKET}|g" "$file"
  sed -i "s|s3://your-silver-bucket|s3://${SILVER_BUCKET}|g" "$file"
  sed -i "s|s3://your-gold-bucket|s3://${GOLD_BUCKET}|g" "$file"
done

# Create jobs
aws glue create-job --cli-input-json file://glue-scripts/bronze/job-config.json
aws glue create-job --cli-input-json file://glue-scripts/silver/job-config.json
aws glue create-job --cli-input-json file://glue-scripts/gold/job-config.json
```

## Step 9: Upload Sample Data

```bash
# Upload sample data to Bronze bucket
aws s3 cp sample-data/sample_transactions.csv \
  s3://${BRONZE_BUCKET}/raw-data/2024/01/sample_transactions.csv
```

## Step 10: Run the Pipeline

```bash
# 1. Run Bronze crawler to catalog raw data
aws glue start-crawler --name bronze-layer-crawler

# Wait for crawler to complete
while [ "$(aws glue get-crawler --name bronze-layer-crawler --query 'Crawler.State' --output text)" != "READY" ]; do
  echo "Waiting for crawler to complete..."
  sleep 10
done

# 2. Run Bronze ingestion job
BRONZE_RUN_ID=$(aws glue start-job-run \
  --job-name bronze-ingestion-job \
  --query 'JobRunId' \
  --output text)

echo "Bronze job run ID: ${BRONZE_RUN_ID}"

# 3. Run Silver transformation job
aws glue start-job-run --job-name silver-transformation-job

# 4. Run Gold aggregation job
aws glue start-job-run --job-name gold-aggregation-job
```

## Step 11: Set Up Athena

```bash
# Create Athena workgroup
aws athena create-work-group \
  --name lakehouse-workgroup \
  --configuration "{
    \"ResultConfigurationUpdates\": {
      \"OutputLocation\": \"s3://${SCRIPTS_BUCKET}/athena-results/\"
    },
    \"EnforceWorkGroupConfiguration\": true
  }"

# Run sample queries
aws athena start-query-execution \
  --query-string "SELECT * FROM gold_db.daily_summary LIMIT 10" \
  --work-group lakehouse-workgroup \
  --result-configuration "OutputLocation=s3://${SCRIPTS_BUCKET}/athena-results/"
```

## Step 12: Set Up Snowflake Integration (Optional)

Follow the instructions in `snowflake-integration/README.md`

## Verification

### 1. Check S3 Buckets

```bash
aws s3 ls s3://${BRONZE_BUCKET}/processed/ --recursive
aws s3 ls s3://${SILVER_BUCKET}/cleaned/ --recursive
aws s3 ls s3://${GOLD_BUCKET}/aggregated/ --recursive
```

### 2. Check Glue Jobs

```bash
aws glue get-job-runs --job-name bronze-ingestion-job --max-results 5
```

### 3. Check Athena Tables

```bash
aws athena start-query-execution \
  --query-string "SHOW DATABASES" \
  --work-group lakehouse-workgroup
```

## Monitoring

### CloudWatch Dashboards

Create a dashboard to monitor:
- Glue job execution times
- S3 bucket sizes
- Athena query costs
- Error rates

### CloudWatch Alarms

```bash
# Create alarm for failed Glue jobs
aws cloudwatch put-metric-alarm \
  --alarm-name glue-job-failures \
  --alarm-description "Alert on Glue job failures" \
  --metric-name glue.driver.ExecutorAllocationManager.executors.numberAllExecutors \
  --namespace Glue \
  --statistic Average \
  --period 300 \
  --threshold 0 \
  --comparison-operator LessThanThreshold
```

## Cleanup

To remove all resources:

```bash
# Delete Glue jobs
aws glue delete-job --job-name bronze-ingestion-job
aws glue delete-job --job-name silver-transformation-job
aws glue delete-job --job-name gold-aggregation-job

# Delete crawlers
aws glue delete-crawler --name bronze-layer-crawler
aws glue delete-crawler --name silver-layer-crawler
aws glue delete-crawler --name gold-layer-crawler

# Delete databases
aws glue delete-database --name bronze_db
aws glue delete-database --name silver_db
aws glue delete-database --name gold_db

# Empty and delete S3 buckets
for bucket in ${BRONZE_BUCKET} ${SILVER_BUCKET} ${GOLD_BUCKET} ${SCRIPTS_BUCKET}; do
  aws s3 rm s3://$bucket --recursive
  aws s3 rb s3://$bucket
done

# Delete IAM roles
aws iam delete-role-policy --role-name GlueETLRole --policy-name GlueS3Access
aws iam delete-role --role-name GlueETLRole
aws iam delete-role-policy --role-name GlueServiceRole --policy-name GlueCrawlerAccess
aws iam delete-role --role-name GlueServiceRole
```

## Troubleshooting

See `troubleshooting.md` for common issues and solutions.

## Next Steps

1. Set up automated workflows with AWS Step Functions
2. Implement data quality checks with AWS Deequ
3. Add real-time streaming with Kinesis
4. Set up CI/CD for ETL jobs
5. Implement data governance with AWS Lake Formation

## Support

For issues or questions:
1. Check the troubleshooting guide
2. Review AWS Glue documentation
3. Open an issue on GitHub
