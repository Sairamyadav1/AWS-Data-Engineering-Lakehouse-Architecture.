# IAM Policies for AWS Lakehouse Architecture

This directory contains IAM policies required for the AWS Data Engineering Lakehouse project.

## Overview

Proper IAM configuration is critical for:
- Security (least-privilege access)
- Cost control
- Compliance
- Audit trails

## Policy Files

### 1. `glue-trust-policy.json`
**Purpose**: Trust policy allowing AWS Glue service to assume the role

**Usage**:
```bash
aws iam create-role \
  --role-name GlueETLRole \
  --assume-role-policy-document file://glue-trust-policy.json
```

### 2. `glue-s3-policy.json`
**Purpose**: Grants Glue ETL jobs access to S3 buckets and Data Catalog

**Permissions Include**:
- S3 read/write for Bronze, Silver, Gold buckets
- Glue Data Catalog operations
- CloudWatch Logs for monitoring
- CloudWatch Metrics for job metrics

**Usage**:
```bash
aws iam put-role-policy \
  --role-name GlueETLRole \
  --policy-name GlueS3Access \
  --policy-document file://glue-s3-policy.json
```

### 3. `glue-crawler-policy.json`
**Purpose**: Grants Glue Crawlers access to discover and catalog data

**Permissions Include**:
- S3 read access to data buckets
- Glue Data Catalog table creation/updates
- CloudWatch Logs

**Usage**:
```bash
aws iam create-role \
  --role-name GlueServiceRole \
  --assume-role-policy-document file://glue-trust-policy.json

aws iam put-role-policy \
  --role-name GlueServiceRole \
  --policy-name GlueCrawlerAccess \
  --policy-document file://glue-crawler-policy.json
```

### 4. `athena-user-policy.json`
**Purpose**: Grants users/applications access to query data with Athena

**Permissions Include**:
- Athena query execution
- Glue Data Catalog read access
- S3 read for data buckets
- S3 write for query results

**Usage**:
```bash
aws iam create-policy \
  --policy-name AthenaQueryAccess \
  --policy-document file://athena-user-policy.json

aws iam attach-user-policy \
  --user-name analytics-user \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/AthenaQueryAccess
```

## Setup Instructions

### Complete IAM Setup

```bash
#!/bin/bash

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 1. Create Glue ETL Role
aws iam create-role \
  --role-name GlueETLRole \
  --assume-role-policy-document file://glue-trust-policy.json

aws iam put-role-policy \
  --role-name GlueETLRole \
  --policy-name GlueS3Access \
  --policy-document file://glue-s3-policy.json

# 2. Create Glue Crawler Role
aws iam create-role \
  --role-name GlueServiceRole \
  --assume-role-policy-document file://glue-trust-policy.json

aws iam put-role-policy \
  --role-name GlueServiceRole \
  --policy-name GlueCrawlerAccess \
  --policy-document file://glue-crawler-policy.json

# 3. Create Athena User Policy
aws iam create-policy \
  --policy-name AthenaQueryAccess \
  --policy-document file://athena-user-policy.json

echo "IAM roles and policies created successfully!"
echo "Glue ETL Role ARN: arn:aws:iam::${ACCOUNT_ID}:role/GlueETLRole"
echo "Glue Service Role ARN: arn:aws:iam::${ACCOUNT_ID}:role/GlueServiceRole"
```

## Security Best Practices

### 1. Least Privilege Access
- Grant only necessary permissions
- Use resource-level permissions where possible
- Avoid wildcards (`*`) in resource ARNs

### 2. Bucket Policies
Add bucket policies to enforce encryption:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::your-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

### 3. Enable MFA Delete
```bash
aws s3api put-bucket-versioning \
  --bucket your-bucket \
  --versioning-configuration Status=Enabled,MFADelete=Enabled \
  --mfa "arn:aws:iam::ACCOUNT_ID:mfa/USER TOKENCODE"
```

### 4. VPC Endpoints (Optional)
For enhanced security, create VPC endpoints:
```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxx \
  --service-name com.amazonaws.region.s3 \
  --route-table-ids rtb-xxxxx
```

### 5. Secrets Management
Store sensitive credentials in AWS Secrets Manager:
```bash
aws secretsmanager create-secret \
  --name snowflake/credentials \
  --secret-string '{"username":"user","password":"pass"}'
```

Add Secrets Manager access to Glue role:
```json
{
  "Effect": "Allow",
  "Action": [
    "secretsmanager:GetSecretValue"
  ],
  "Resource": "arn:aws:secretsmanager:*:*:secret:snowflake/*"
}
```

## Monitoring and Compliance

### CloudTrail Logging
Ensure CloudTrail is enabled to log all IAM and S3 API calls:
```bash
aws cloudtrail create-trail \
  --name lakehouse-trail \
  --s3-bucket-name your-cloudtrail-bucket
```

### IAM Access Analyzer
Use IAM Access Analyzer to identify unintended access:
```bash
aws accessanalyzer create-analyzer \
  --analyzer-name lakehouse-analyzer \
  --type ACCOUNT
```

### Regular Audits
- Review IAM policies quarterly
- Remove unused roles and permissions
- Monitor CloudTrail logs for suspicious activity
- Use AWS Config to track IAM changes

## Troubleshooting

### Access Denied Errors

1. **Glue Job Fails with S3 Access Denied**
   - Verify the role has `s3:GetObject` and `s3:PutObject`
   - Check bucket policies don't deny access
   - Ensure KMS key permissions if using encryption

2. **Crawler Cannot Read S3 Data**
   - Verify `s3:ListBucket` permission
   - Check S3 path is correct
   - Ensure no bucket policies block access

3. **Athena Query Fails**
   - Verify results bucket permissions
   - Check Data Catalog read permissions
   - Ensure workgroup configuration is correct

### Permission Testing

Test permissions using the IAM Policy Simulator:
```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT_ID:role/GlueETLRole \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::your-bucket/*
```

## Cost Optimization

- Use resource-based policies to avoid redundant IAM roles
- Implement S3 lifecycle policies to transition old data
- Set up budget alerts for unexpected costs
- Tag all resources for cost allocation

## Additional Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Glue Security](https://docs.aws.amazon.com/glue/latest/dg/security.html)
- [AWS Lake Formation](https://aws.amazon.com/lake-formation/) - For fine-grained access control
