"""
AWS Glue Crawler Configuration Script
This script creates Glue Crawlers for schema discovery and cataloging
"""

import boto3
import json

def create_crawler(crawler_name, database_name, s3_path, role_arn):
    """
    Create an AWS Glue Crawler
    
    Args:
        crawler_name: Name of the crawler
        database_name: Target Glue database
        s3_path: S3 path to crawl
        role_arn: IAM role ARN for the crawler
    """
    glue_client = boto3.client('glue')
    
    try:
        response = glue_client.create_crawler(
            Name=crawler_name,
            Role=role_arn,
            DatabaseName=database_name,
            Description=f'Crawler for {crawler_name}',
            Targets={
                'S3Targets': [
                    {
                        'Path': s3_path,
                        'Exclusions': []
                    }
                ]
            },
            SchemaChangePolicy={
                'UpdateBehavior': 'UPDATE_IN_DATABASE',
                'DeleteBehavior': 'LOG'
            },
            RecrawlPolicy={
                'RecrawlBehavior': 'CRAWL_EVERYTHING'
            },
            Configuration=json.dumps({
                "Version": 1.0,
                "CrawlerOutput": {
                    "Partitions": {"AddOrUpdateBehavior": "InheritFromTable"}
                }
            })
        )
        print(f"Crawler '{crawler_name}' created successfully")
        return response
    except Exception as e:
        print(f"Error creating crawler '{crawler_name}': {str(e)}")
        raise

def create_lakehouse_crawlers(bucket_name, role_arn):
    """
    Create crawlers for all lakehouse layers
    """
    # Bronze layer crawler
    create_crawler(
        crawler_name='bronze-layer-crawler',
        database_name='lakehouse_bronze_db',
        s3_path=f's3://{bucket_name}/bronze/',
        role_arn=role_arn
    )
    
    # Silver layer crawler
    create_crawler(
        crawler_name='silver-layer-crawler',
        database_name='lakehouse_silver_db',
        s3_path=f's3://{bucket_name}/silver/',
        role_arn=role_arn
    )
    
    # Gold layer crawler
    create_crawler(
        crawler_name='gold-layer-crawler',
        database_name='lakehouse_gold_db',
        s3_path=f's3://{bucket_name}/gold/',
        role_arn=role_arn
    )
    
    print("All lakehouse crawlers created successfully")

if __name__ == "__main__":
    # Configuration
    BUCKET_NAME = "your-lakehouse-bucket"
    GLUE_ROLE_ARN = "arn:aws:iam::ACCOUNT_ID:role/GlueCrawlerRole"
    
    create_lakehouse_crawlers(BUCKET_NAME, GLUE_ROLE_ARN)
