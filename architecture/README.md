# Architecture Diagram

A detailed architecture diagram should be placed in this directory showing:

1. **Data Sources**
   - S3 raw data sources
   - External APIs
   - Database exports
   - Streaming sources

2. **Bronze Layer**
   - S3 Bronze bucket
   - AWS Glue Crawler
   - Raw data catalog

3. **Silver Layer**
   - S3 Silver bucket
   - AWS Glue ETL jobs for cleaning
   - Data quality checks
   - Cleaned data catalog

4. **Gold Layer**
   - S3 Gold bucket
   - AWS Glue ETL jobs for aggregation
   - Business logic transformations
   - Aggregated data catalog

5. **Analytics Layer**
   - Amazon Athena
   - AWS QuickSight
   - Snowflake integration
   - BI tools

6. **Orchestration & Monitoring**
   - AWS Glue Workflows
   - CloudWatch monitoring
   - CloudWatch Logs
   - SNS notifications

7. **Security & Governance**
   - IAM roles and policies
   - S3 bucket policies
   - KMS encryption
   - AWS Lake Formation (optional)

## Creating the Diagram

You can create the architecture diagram using:

1. **draw.io** (https://draw.io)
   - Free online diagramming tool
   - AWS architecture icons available
   - Export as PNG or SVG

2. **Lucidchart** (https://lucidchart.com)
   - Professional diagramming tool
   - AWS shape libraries
   - Collaboration features

3. **AWS Architecture Icons** (https://aws.amazon.com/architecture/icons/)
   - Official AWS icons
   - Use in PowerPoint, draw.io, etc.

4. **CloudCraft** (https://cloudcraft.co)
   - 3D AWS architecture diagrams
   - Cost estimation
   - Live AWS sync

## Example Diagram Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   S3     │  │  APIs    │  │   RDS    │  │ Kinesis  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   BRONZE LAYER (Raw)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        S3 Bronze Bucket (Immutable Storage)            │ │
│  │  - Parquet/CSV/JSON files                              │ │
│  │  - Partitioned by ingestion date                       │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────┐         ┌─────────────────────────┐    │
│  │ Glue Crawler   │────────▶│  Glue Data Catalog      │    │
│  └────────────────┘         │  (bronze_db)            │    │
│                              └─────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               SILVER LAYER (Cleaned & Validated)             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │     AWS Glue ETL Job (PySpark)                      │    │
│  │  - Data quality checks                              │    │
│  │  - Deduplication                                    │    │
│  │  - Schema enforcement                               │    │
│  │  - Type conversions                                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │     S3 Silver Bucket (Conformed Data)              │     │
│  │  - Parquet format (Snappy compression)             │     │
│  │  - Partitioned by processed_date                   │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              GOLD LAYER (Business Ready)                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │     AWS Glue ETL Job (PySpark)                      │    │
│  │  - Business logic                                   │    │
│  │  - Aggregations                                     │    │
│  │  - Metrics calculation                              │    │
│  │  - Dimension modeling                               │    │
│  └─────────────────────────────────────────────────────┘    │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │       S3 Gold Bucket (Analytics Ready)             │     │
│  │  - Parquet format (Snappy compression)             │     │
│  │  - Partitioned by year/month                       │     │
│  │  - Optimized for queries                           │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 ANALYTICS & BI LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Athena     │  │  QuickSight  │  │  Snowflake   │      │
│  │  (SQL Query) │  │ (Dashboards) │  │ (Data WH)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATION & MONITORING                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Glue Workflow │  │  CloudWatch  │  │     SNS      │      │
│  │              │  │  (Logs/Metrics)  │ (Alerts)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 SECURITY & GOVERNANCE                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  IAM Roles   │  │   KMS Keys   │  │Lake Formation│      │
│  │  & Policies  │  │ (Encryption) │  │ (Optional)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Save Your Diagram

Once created, save your architecture diagram as:
- `architecture-diagram.png` (for README)
- `architecture-diagram.pdf` (for documentation)
- `architecture-diagram.drawio` (source file for editing)

Place all files in this `architecture/` directory.
