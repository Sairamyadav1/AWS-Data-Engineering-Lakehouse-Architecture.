-- Create Storage Integration for AWS S3
-- This allows Snowflake to access data in S3 buckets

USE ROLE ACCOUNTADMIN;

-- Create storage integration
CREATE OR REPLACE STORAGE INTEGRATION aws_lakehouse_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::YOUR_ACCOUNT_ID:role/SnowflakeS3Role'
  STORAGE_ALLOWED_LOCATIONS = (
    's3://your-gold-bucket/aggregated/',
    's3://your-silver-bucket/cleaned/'
  )
  COMMENT = 'Integration for AWS Lakehouse Gold and Silver layers';

-- Retrieve the ARN and External ID for AWS IAM configuration
DESC STORAGE INTEGRATION aws_lakehouse_integration;

-- Grant usage on integration to roles
GRANT USAGE ON INTEGRATION aws_lakehouse_integration TO ROLE SYSADMIN;
GRANT USAGE ON INTEGRATION aws_lakehouse_integration TO ROLE DATA_ENGINEER;

-- Verify integration
SHOW INTEGRATIONS;
