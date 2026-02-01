# aws-lakehouse-data-pipeline

## Introduction

This project demonstrates an **end-to-end Data Engineering pipeline on AWS** using a **Lakehouse (Medallion) architecture**.

Data is first ingested into the **Bronze (raw) S3 layer**, then cleaned and transformed into the **Silver layer** using **AWS Glue ETL jobs**, and finally curated into the **Gold layer** for analytics.  
AWS Glue Crawlers are used to automatically create and update table schemas in the Glue Data Catalog.  
The curated data is queried using **Amazon Athena** and integrated with **Snowflake** for advanced analytics.  
Monitoring and logging are handled using **Amazon CloudWatch**, with secure access managed via **AWS IAM**.


---

## Architecture Overview

- Bronze Layer: Raw data stored in Amazon S3  
- Silver Layer: Cleaned and transformed data using AWS Glue  
- Gold Layer: Analytics-ready data stored in S3  
- Schema Management: AWS Glue Crawler & Data Catalog  
- Query Engine: Amazon Athena  
- Analytics Warehouse: Snowflake  
- Monitoring: Amazon CloudWatch  
- Security: AWS IAM roles and policies


## Key Learnings

- Designing scalable data lakes using Medallion architecture  
- Building serverless ETL pipelines with AWS Glue  
- Schema discovery and metadata management  
- Querying large datasets using Athena  
- Integrating AWS data lakes with Snowflake  
- Implementing monitoring and secure access control

## Architecture Diagram 

<img width="1536" height="1024" alt="ChatGPT Image Jan 16, 2026, 01_16_56 AM" src="https://github.com/user-attachments/assets/19edf1ef-5c47-40c3-ada8-871940bf965a" />

