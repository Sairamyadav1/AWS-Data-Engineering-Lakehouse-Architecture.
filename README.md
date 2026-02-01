# AWS Data Engineering Lakehouse Architecture

A production-ready, end-to-end AWS data engineering project implementing a modern Lakehouse architecture using the Bronze-Silver-Gold medallion pattern.

## 🏗️ Architecture Overview

This project demonstrates a scalable data lakehouse implementation on AWS, featuring:

- **Bronze Layer**: Raw data ingestion from various sources
- **Silver Layer**: Cleaned and conformed data
- **Gold Layer**: Business-level aggregated data ready for analytics

### Architecture Diagram

```
┌─────────────┐
│ Data Sources│
│ (S3, APIs)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│        BRONZE LAYER (Raw)           │
│  - Raw data ingestion               │
│  - Schema on read                   │
│  - Immutable storage                │
│  - AWS Glue Crawlers                │
└──────────────┬──────────────────────┘
               │
               ▼ AWS Glue ETL Jobs
┌─────────────────────────────────────┐
│      SILVER LAYER (Cleaned)         │
│  - Data quality checks              │
│  - Deduplication                    │
│  - Schema enforcement               │
│  - Partitioned by date              │
└──────────────┬──────────────────────┘
               │
               ▼ AWS Glue ETL Jobs
┌─────────────────────────────────────┐
│   GOLD LAYER (Business Ready)       │
│  - Aggregated metrics               │
│  - Business logic applied           │
│  - Optimized for querying           │
│  - Star/Snowflake schema            │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│        Analytics & BI Layer          │
│  - Amazon Athena                     │
│  - AWS QuickSight                    │
│  - Snowflake Integration             │
└──────────────────────────────────────┘
```

## 📁 Project Structure

```
.
├── README.md
├── architecture/
│   └── architecture-diagram.png      # Detailed architecture diagram
├── glue-scripts/
│   ├── bronze/                       # Raw data ingestion scripts
│   ├── silver/                       # Data cleaning & transformation
│   └── gold/                         # Business-level aggregations
├── athena-queries/
│   └── *.sql                        # SQL queries for data analysis
├── glue-crawlers/
│   └── crawler-configs/             # Glue Crawler configurations
├── snowflake-integration/
│   ├── setup/                       # Snowflake setup scripts
│   └── queries/                     # Snowflake queries
├── iam-policies/
│   └── *.json                       # IAM roles and policies
├── sample-data/
│   └── *.csv                        # Sample datasets for testing
└── docs/
    ├── deployment-guide.md          # Step-by-step deployment
    ├── best-practices.md            # Data engineering best practices
    └── troubleshooting.md           # Common issues and solutions
```

## 🚀 Features

- ✅ **Medallion Architecture**: Bronze → Silver → Gold data layers
- ✅ **AWS Glue ETL**: Serverless Spark-based transformations
- ✅ **AWS Glue Data Catalog**: Centralized metadata management
- ✅ **Amazon Athena**: SQL-based data querying
- ✅ **Snowflake Integration**: Cloud data warehouse connectivity
- ✅ **IAM Security**: Least-privilege access controls
- ✅ **Data Quality**: Validation and error handling
- ✅ **Partitioning**: Optimized for query performance
- ✅ **Cost Optimization**: S3 lifecycle policies and resource tagging

## 🛠️ Technologies Used

- **Storage**: Amazon S3
- **ETL**: AWS Glue (PySpark)
- **Catalog**: AWS Glue Data Catalog
- **Query Engine**: Amazon Athena
- **Data Warehouse**: Snowflake
- **Orchestration**: AWS Glue Workflows
- **Security**: AWS IAM
- **Monitoring**: AWS CloudWatch

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.8+ (for local testing)
- Snowflake account (optional, for integration)
- Basic understanding of:
  - AWS services (S3, Glue, Athena)
  - SQL
  - PySpark
  - Data engineering concepts

## 🎯 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Sairamyadav1/AWS-Data-Engineering-Lakehouse-Architecture.git
cd AWS-Data-Engineering-Lakehouse-Architecture
```

### 2. Set Up AWS Resources

```bash
# Create S3 buckets for each layer
aws s3 mb s3://your-bronze-bucket
aws s3 mb s3://your-silver-bucket
aws s3 mb s3://your-gold-bucket

# Upload sample data
aws s3 cp sample-data/ s3://your-bronze-bucket/raw-data/ --recursive
```

### 3. Create IAM Roles

Apply the IAM policies from the `iam-policies/` directory:

```bash
aws iam create-role --role-name GlueETLRole --assume-role-policy-document file://iam-policies/glue-trust-policy.json
aws iam put-role-policy --role-name GlueETLRole --policy-name GlueS3Access --policy-document file://iam-policies/glue-s3-policy.json
```

### 4. Deploy Glue Crawlers

```bash
# Create crawlers for each layer
aws glue create-crawler --cli-input-json file://glue-crawlers/bronze-crawler.json
aws glue create-crawler --cli-input-json file://glue-crawlers/silver-crawler.json
aws glue create-crawler --cli-input-json file://glue-crawlers/gold-crawler.json
```

### 5. Run ETL Jobs

```bash
# Upload Glue scripts to S3
aws s3 cp glue-scripts/ s3://your-scripts-bucket/glue-scripts/ --recursive

# Create and run Glue jobs
aws glue create-job --cli-input-json file://glue-scripts/bronze/job-config.json
aws glue start-job-run --job-name bronze-ingestion-job
```

### 6. Query with Athena

Use the SQL queries in `athena-queries/` to analyze your data:

```sql
-- Example: Query gold layer data
SELECT * FROM gold_db.sales_summary
WHERE year = 2024
LIMIT 10;
```

## 📊 Data Flow

1. **Ingestion (Bronze)**
   - Raw data lands in S3 bronze bucket
   - Glue Crawler catalogs the schema
   - Data stored in original format (CSV, JSON, Parquet)

2. **Transformation (Silver)**
   - Glue ETL job reads from bronze
   - Applies data quality rules
   - Deduplicates records
   - Standardizes formats
   - Writes cleaned data to silver bucket

3. **Aggregation (Gold)**
   - Glue ETL job reads from silver
   - Applies business logic
   - Creates aggregated views
   - Optimizes for analytics queries
   - Writes to gold bucket in Parquet format

4. **Analytics**
   - Athena queries gold layer tables
   - QuickSight dashboards visualize data
   - Snowflake integration for advanced analytics

## 🔐 Security Best Practices

- **Encryption**: All S3 buckets use AES-256 encryption
- **IAM Roles**: Least-privilege access for Glue jobs
- **VPC**: Glue jobs run in private subnets (optional)
- **Secrets Manager**: Database credentials stored securely
- **CloudTrail**: All API calls are logged
- **S3 Bucket Policies**: Restrict access by IP/VPC

## 💰 Cost Optimization

- Use S3 Intelligent-Tiering for cost savings
- Partition data by date to reduce Athena scan costs
- Use Glue bookmarks to avoid reprocessing data
- Set Glue job timeout limits
- Use Spot instances for non-critical workloads
- Implement data lifecycle policies

## 📈 Monitoring & Logging

- **CloudWatch Metrics**: Monitor Glue job execution
- **CloudWatch Logs**: Debug ETL failures
- **Glue Job Metrics**: Track DPU usage and costs
- **Athena Query History**: Analyze query performance
- **S3 Access Logs**: Audit data access patterns

## 🧪 Testing

```bash
# Run unit tests for Glue scripts
python -m pytest tests/

# Validate data quality
python scripts/validate_data_quality.py
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Sai Ram Yadav**

- GitHub: [@Sairamyadav1](https://github.com/Sairamyadav1)

## 🙏 Acknowledgments

- AWS Documentation
- Data Engineering Community
- Medallion Architecture Pattern

## 📚 Additional Resources

- [AWS Glue Developer Guide](https://docs.aws.amazon.com/glue/)
- [Amazon Athena User Guide](https://docs.aws.amazon.com/athena/)
- [Lakehouse Architecture Whitepaper](https://www.databricks.com/lakehouse)
- [Data Engineering Best Practices](https://aws.amazon.com/big-data/datalakes-and-analytics/)

---

⭐ **Star this repository if you find it helpful!**