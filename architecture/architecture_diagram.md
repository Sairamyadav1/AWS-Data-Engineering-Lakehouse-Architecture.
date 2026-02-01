# AWS Data Engineering Lakehouse Architecture Diagram

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Database   │  │     APIs     │  │  Log Files   │  │   S3 Files   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼──────────────────┼──────────────────┼──────────────────┼──────────┘
          │                  │                  │                  │
          └──────────────────┴──────────────────┴──────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────────────┐
          │              BRONZE LAYER (Raw Data)                   │
          │  ┌─────────────────────────────────────────────────┐  │
          │  │         Amazon S3 - Bronze Bucket               │  │
          │  │  • Parquet format                               │  │
          │  │  • Partitioned by ingestion_date                │  │
          │  │  • Raw data with metadata                       │  │
          │  └─────────────────────────────────────────────────┘  │
          │              ▲                         │               │
          │              │                         │               │
          │    ┌─────────────────┐    ┌────────────────────┐      │
          │    │  AWS Glue       │    │  AWS Glue Crawler  │      │
          │    │  ETL Job        │    │  (Schema Discovery)│      │
          │    │  (Ingestion)    │    └────────────────────┘      │
          │    └─────────────────┘                                 │
          └───────────────────────────────────────────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────────────┐
          │           SILVER LAYER (Cleansed Data)                 │
          │  ┌─────────────────────────────────────────────────┐  │
          │  │         Amazon S3 - Silver Bucket               │  │
          │  │  • Parquet format                               │  │
          │  │  • Deduplicated data                            │  │
          │  │  • Data quality checks applied                  │  │
          │  │  • Standardized formats                         │  │
          │  └─────────────────────────────────────────────────┘  │
          │              ▲                         │               │
          │              │                         │               │
          │    ┌─────────────────┐    ┌────────────────────┐      │
          │    │  AWS Glue       │    │  AWS Glue Crawler  │      │
          │    │  ETL Job        │    │  (Schema Discovery)│      │
          │    │  (Transform)    │    └────────────────────┘      │
          │    └─────────────────┘                                 │
          └───────────────────────────────────────────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────────────┐
          │          GOLD LAYER (Analytical Data)                  │
          │  ┌─────────────────────────────────────────────────┐  │
          │  │         Amazon S3 - Gold Bucket                 │  │
          │  │  • Parquet format                               │  │
          │  │  • Business-level aggregations                  │  │
          │  │  • Optimized for analytics                      │  │
          │  │  • Ready for reporting                          │  │
          │  └─────────────────────────────────────────────────┘  │
          │              ▲                         │               │
          │              │                         │               │
          │    ┌─────────────────┐    ┌────────────────────┐      │
          │    │  AWS Glue       │    │  AWS Glue Crawler  │      │
          │    │  ETL Job        │    │  (Schema Discovery)│      │
          │    │  (Aggregate)    │    └────────────────────┘      │
          │    └─────────────────┘                                 │
          └───────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
          ┌──────────────────┐              ┌──────────────────┐
          │  Amazon Athena   │              │   Snowflake      │
          │                  │              │                  │
          │  • SQL Queries   │              │  • Advanced      │
          │  • Serverless    │              │    Analytics     │
          │  • Ad-hoc        │              │  • BI Reports    │
          │    Analysis      │              │  • ML Workloads  │
          └──────────────────┘              └──────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                          ┌────────────────────┐
                          │   AWS Glue Data    │
                          │      Catalog       │
                          │                    │
                          │  • Metadata Store  │
                          │  • Schema Registry │
                          └────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING & SECURITY LAYER                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Amazon          │  │      AWS IAM     │  │    AWS KMS       │          │
│  │  CloudWatch      │  │                  │  │                  │          │
│  │  • Logs          │  │  • Roles         │  │  • Encryption    │          │
│  │  • Metrics       │  │  • Policies      │  │  • Key Mgmt      │          │
│  │  • Alarms        │  │  • Access Ctrl   │  │                  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Ingestion (Bronze Layer)**
   - Raw data from various sources is ingested
   - AWS Glue ETL jobs load data into S3 Bronze layer
   - Data stored in Parquet format with partitioning
   - Metadata (ingestion timestamp, source file) added
   - Glue Crawlers discover and catalog schemas

2. **Transformation (Silver Layer)**
   - AWS Glue ETL jobs read from Bronze layer
   - Data cleansing and quality checks performed
   - Deduplication and standardization applied
   - Transformed data written to S3 Silver layer
   - Glue Crawlers update catalog schemas

3. **Aggregation (Gold Layer)**
   - AWS Glue ETL jobs create business-level aggregations
   - Analytical datasets optimized for queries
   - Data written to S3 Gold layer
   - Glue Crawlers catalog final schemas

4. **Analytics & Reporting**
   - Amazon Athena for serverless SQL queries
   - Snowflake for advanced analytics and BI
   - Both services query via Glue Data Catalog

5. **Monitoring & Security**
   - CloudWatch monitors all components
   - IAM controls access permissions
   - KMS handles encryption keys

## Key Components

- **Amazon S3**: Data lake storage (Bronze, Silver, Gold layers)
- **AWS Glue ETL**: Data transformation pipeline
- **AWS Glue Crawlers**: Automatic schema discovery
- **AWS Glue Data Catalog**: Centralized metadata repository
- **Amazon Athena**: Serverless SQL analytics
- **Snowflake**: Advanced analytics and reporting
- **Amazon CloudWatch**: Monitoring and logging
- **AWS IAM**: Security and access control
- **AWS KMS**: Encryption key management
