# AWS Data Engineering Lakehouse Architecture

An end-to-end data engineering pipeline implementation on AWS, following the Medallion architecture pattern with Bronze, Silver, and Gold layers.

## 🏗️ Architecture Overview

This project implements a comprehensive lakehouse architecture on AWS that processes data through three distinct layers:

- **Bronze Layer**: Raw data ingestion with metadata tracking
- **Silver Layer**: Cleansed, deduplicated, and validated data
- **Gold Layer**: Business-ready aggregated analytics data

## 🔹 Key Features

### Medallion Architecture (Bronze, Silver, Gold Layers)
- **Bronze Layer**: Stores raw, unprocessed data from various sources in Amazon S3
- **Silver Layer**: Contains cleansed, validated, and deduplicated data
- **Gold Layer**: Business-level aggregations optimized for analytics and reporting

### AWS Glue ETL Jobs
- Automated data transformation pipelines
- PySpark-based processing for scalability
- Metadata tracking and lineage
- Data quality checks and validation

### AWS Glue Crawler
- Automatic schema discovery and cataloging
- Continuous metadata synchronization
- Support for partitioned data structures

### Amazon Athena
- Serverless SQL analytics
- Direct querying of S3 data
- Cost-effective ad-hoc analysis
- Pre-built analytical queries

### Snowflake Integration
- Advanced analytics and reporting
- External table integration with S3
- Business intelligence views
- Machine learning workloads

### Amazon CloudWatch
- Comprehensive monitoring and logging
- Custom metrics for pipeline health
- Automated alerting for failures
- Performance tracking

### AWS IAM
- Secure role-based access control
- Least-privilege principle
- Service-specific policies
- Cross-service permissions

## 📁 Project Structure

```
AWS-Data-Engineering-Lakehouse-Architecture/
├── README.md
├── architecture/
│   └── architecture_diagram.md          # Visual architecture diagram
├── glue_jobs/
│   ├── bronze/
│   │   └── ingest_raw_data.py          # Bronze layer ingestion job
│   ├── silver/
│   │   └── transform_and_clean.py      # Silver layer transformation job
│   └── gold/
│       └── aggregate_analytics.py       # Gold layer aggregation job
├── glue_crawlers/
│   └── create_crawlers.py              # Crawler configuration script
├── athena_queries/
│   └── analytics_queries.sql           # Sample Athena SQL queries
├── snowflake/
│   └── snowflake_integration.py        # Snowflake integration script
├── cloudwatch/
│   └── monitoring_setup.py             # CloudWatch monitoring configuration
├── iam_policies/
│   ├── glue_job_policy.json           # IAM policy for Glue jobs
│   ├── glue_crawler_policy.json       # IAM policy for Glue crawlers
│   ├── athena_query_policy.json       # IAM policy for Athena
│   └── snowflake_s3_policy.json       # IAM policy for Snowflake S3 access
├── infrastructure/
│   ├── cloudformation_template.yaml    # CloudFormation IaC template
│   └── deploy.sh                       # Deployment script
└── sample_data/
    ├── schemas.md                      # Data schema definitions
    ├── sample_customers.csv            # Sample customer data
    └── sample_transactions.csv         # Sample transaction data
```

## 🚀 Getting Started

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.8+
- Boto3 library
- (Optional) Snowflake account for advanced analytics

### Deployment Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Sairamyadav1/AWS-Data-Engineering-Lakehouse-Architecture.git
   cd AWS-Data-Engineering-Lakehouse-Architecture
   ```

2. **Deploy Infrastructure**
   ```bash
   cd infrastructure
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Configure Parameters**
   - Update `PROJECT_NAME` and `ENVIRONMENT` in deploy.sh
   - Modify CloudFormation template parameters as needed
   - Update bucket names in IAM policies

4. **Create Glue Crawlers**
   ```bash
   cd ../glue_crawlers
   python create_crawlers.py
   ```

5. **Setup Monitoring**
   ```bash
   cd ../cloudwatch
   python monitoring_setup.py
   ```

6. **Upload Sample Data** (Optional)
   ```bash
   aws s3 cp sample_data/sample_customers.csv s3://YOUR-BUCKET/bronze/customers/
   aws s3 cp sample_data/sample_transactions.csv s3://YOUR-BUCKET/bronze/transactions/
   ```

## 📊 Data Pipeline Flow

### 1. Bronze Layer - Data Ingestion
```python
# Run Bronze layer Glue job
aws glue start-job-run \
    --job-name bronze-ingest-job \
    --arguments='--source_path=s3://source-bucket/data/ --target_path=s3://lakehouse-bucket/bronze/'
```

### 2. Silver Layer - Data Transformation
```python
# Run Silver layer Glue job
aws glue start-job-run \
    --job-name silver-transform-job \
    --arguments='--bronze_path=s3://lakehouse-bucket/bronze/ --silver_path=s3://lakehouse-bucket/silver/'
```

### 3. Gold Layer - Data Aggregation
```python
# Run Gold layer Glue job
aws glue start-job-run \
    --job-name gold-aggregate-job \
    --arguments='--silver_path=s3://lakehouse-bucket/silver/ --gold_path=s3://lakehouse-bucket/gold/'
```

### 4. Query with Athena
```sql
-- Example: Query gold layer analytics
SELECT * FROM lakehouse_gold_db.daily_aggregates
WHERE ingestion_date >= DATE_ADD('day', -7, CURRENT_DATE)
ORDER BY ingestion_date DESC;
```

## 🔐 Security Best Practices

1. **IAM Roles**: Use separate IAM roles for each service component
2. **Encryption**: Enable S3 bucket encryption (AES-256)
3. **Access Control**: Implement least-privilege access policies
4. **Monitoring**: Enable CloudWatch logging for all components
5. **Network**: Use VPC endpoints for private connectivity
6. **Secrets**: Store credentials in AWS Secrets Manager

## 📈 Monitoring and Alerting

The pipeline includes comprehensive monitoring:

- **CloudWatch Logs**: Detailed execution logs for all Glue jobs
- **Custom Metrics**: Record counts, processing times, failure rates
- **Alarms**: Automated alerts for job failures and data quality issues
- **Dashboards**: Visual monitoring of pipeline health

## 🧪 Data Quality

Data quality checks implemented in the Silver layer:

- Null value detection and handling
- Duplicate record removal
- Data type validation
- Format standardization
- Referential integrity checks

## 💡 Use Cases

- **Customer Analytics**: Track customer behavior and lifetime value
- **Sales Analytics**: Daily/weekly/monthly sales aggregations
- **Operational Reporting**: Real-time operational metrics
- **Data Science**: Prepared datasets for ML model training
- **Business Intelligence**: Executive dashboards and reports

## 📝 Sample Queries

See `athena_queries/analytics_queries.sql` for example queries including:

- Data quality analysis
- Trend analysis
- Customer segmentation
- Revenue reporting
- Data lineage tracking

## 🛠️ Customization

### Adding New Data Sources

1. Create a new Glue job in `glue_jobs/bronze/`
2. Update crawler configuration for the new data path
3. Add corresponding schema definition in `sample_data/schemas.md`
4. Update IAM policies if needed

### Modifying Transformations

1. Edit the transformation logic in `glue_jobs/silver/transform_and_clean.py`
2. Add custom business rules as needed
3. Update data quality checks
4. Test with sample data before production deployment

## 📚 Documentation

- [Architecture Diagram](architecture/architecture_diagram.md) - Detailed visual architecture
- [Data Schemas](sample_data/schemas.md) - Complete schema definitions
- [IAM Policies](iam_policies/) - Security policies for each component

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Sairam Yadav**

## 🙏 Acknowledgments

- AWS Glue Documentation
- Apache Spark Community
- Snowflake Documentation
- Data Engineering Community

## 📞 Support

For issues, questions, or suggestions, please open an issue in the GitHub repository.

---

**Built with ❤️ using AWS Data Engineering Services**