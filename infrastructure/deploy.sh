#!/bin/bash

# Deployment Script for AWS Lakehouse Architecture
# This script deploys the CloudFormation stack and sets up the lakehouse infrastructure

set -e

# Configuration
PROJECT_NAME="lakehouse"
ENVIRONMENT="dev"
REGION="us-east-1"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-stack"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS Lakehouse Architecture Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Validate AWS credentials
echo -e "${YELLOW}Validating AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: Invalid AWS credentials${NC}"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials validated${NC}"

# Deploy CloudFormation stack
echo -e "${YELLOW}Deploying CloudFormation stack...${NC}"
aws cloudformation deploy \
    --template-file infrastructure/cloudformation_template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        ProjectName=$PROJECT_NAME \
        Environment=$ENVIRONMENT \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

echo -e "${GREEN}✓ CloudFormation stack deployed successfully${NC}"

# Get stack outputs
echo -e "${YELLOW}Retrieving stack outputs...${NC}"
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='LakehouseBucketName'].OutputValue" \
    --output text \
    --region $REGION)

GLUE_JOB_ROLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='GlueJobRoleArn'].OutputValue" \
    --output text \
    --region $REGION)

GLUE_CRAWLER_ROLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='GlueCrawlerRoleArn'].OutputValue" \
    --output text \
    --region $REGION)

echo -e "${GREEN}✓ Stack outputs retrieved${NC}"
echo "  Bucket Name: $BUCKET_NAME"
echo "  Glue Job Role: $GLUE_JOB_ROLE"
echo "  Glue Crawler Role: $GLUE_CRAWLER_ROLE"

# Create S3 folder structure
echo -e "${YELLOW}Creating S3 folder structure...${NC}"
aws s3api put-object --bucket $BUCKET_NAME --key bronze/ --region $REGION
aws s3api put-object --bucket $BUCKET_NAME --key silver/ --region $REGION
aws s3api put-object --bucket $BUCKET_NAME --key gold/ --region $REGION
aws s3api put-object --bucket $BUCKET_NAME --key scripts/ --region $REGION
aws s3api put-object --bucket $BUCKET_NAME --key athena-results/ --region $REGION
echo -e "${GREEN}✓ S3 folder structure created${NC}"

# Upload Glue job scripts to S3
echo -e "${YELLOW}Uploading Glue job scripts...${NC}"
aws s3 cp glue_jobs/bronze/ingest_raw_data.py s3://$BUCKET_NAME/scripts/bronze/ --region $REGION
aws s3 cp glue_jobs/silver/transform_and_clean.py s3://$BUCKET_NAME/scripts/silver/ --region $REGION
aws s3 cp glue_jobs/gold/aggregate_analytics.py s3://$BUCKET_NAME/scripts/gold/ --region $REGION
echo -e "${GREEN}✓ Glue job scripts uploaded${NC}"

# Save configuration
echo -e "${YELLOW}Saving deployment configuration...${NC}"
cat > deployment_config.json <<EOF
{
  "project_name": "$PROJECT_NAME",
  "environment": "$ENVIRONMENT",
  "region": "$REGION",
  "stack_name": "$STACK_NAME",
  "bucket_name": "$BUCKET_NAME",
  "glue_job_role_arn": "$GLUE_JOB_ROLE",
  "glue_crawler_role_arn": "$GLUE_CRAWLER_ROLE"
}
EOF
echo -e "${GREEN}✓ Configuration saved to deployment_config.json${NC}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Create Glue jobs using the uploaded scripts"
echo "2. Create Glue crawlers to catalog data"
echo "3. Start ingesting data into the Bronze layer"
echo "4. Run the ETL pipeline"
echo "5. Query data using Athena"
