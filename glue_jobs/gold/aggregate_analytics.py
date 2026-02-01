"""
AWS Glue ETL Job - Gold Layer
This script creates aggregated, business-ready datasets for analytics and reporting
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'silver_path', 'gold_path'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Job parameters
silver_path = args['silver_path']
gold_path = args['gold_path']

# Read data from Silver layer
print(f"Reading data from Silver layer: {silver_path}")
silver_df = spark.read.parquet(silver_path)

# Create business-level aggregations
print("Creating business-level aggregations...")

# Example: Daily aggregations
daily_aggregates = silver_df.groupBy("ingestion_date") \
    .agg(
        F.count("*").alias("total_records"),
        F.countDistinct("id").alias("unique_ids"),
        F.current_timestamp().alias("aggregation_timestamp")
    )

# Write to Gold layer - optimized for analytics
print(f"Writing aggregated data to Gold layer: {gold_path}")
daily_aggregates.write.mode("overwrite") \
    .parquet(f"{gold_path}/daily_aggregates")

# Create additional analytical views
# Example: Latest snapshot view
latest_snapshot = silver_df.filter(
    F.col("ingestion_date") == silver_df.agg(F.max("ingestion_date")).collect()[0][0]
)

latest_snapshot.write.mode("overwrite") \
    .parquet(f"{gold_path}/latest_snapshot")

# Log aggregation metrics
print(f"Aggregation Summary:")
print(f"Total aggregated records: {daily_aggregates.count()}")
print(f"Latest snapshot records: {latest_snapshot.count()}")

job.commit()
print("Gold layer aggregation completed successfully")
