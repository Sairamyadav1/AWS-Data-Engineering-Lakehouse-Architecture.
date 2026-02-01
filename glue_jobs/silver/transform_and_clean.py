"""
AWS Glue ETL Job - Silver Layer
This script transforms and cleanses data from Bronze to Silver layer
Performs data quality checks, deduplication, and standardization
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'bronze_path', 'silver_path'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Job parameters
bronze_path = args['bronze_path']
silver_path = args['silver_path']

# Read data from Bronze layer
print(f"Reading data from Bronze layer: {bronze_path}")
bronze_df = spark.read.parquet(bronze_path)

# Data quality checks and cleansing
print("Performing data quality checks and cleansing...")

# Remove duplicates based on key columns
window_spec = Window.partitionBy("id").orderBy(F.col("ingestion_timestamp").desc())
cleaned_df = bronze_df.withColumn("row_num", F.row_number().over(window_spec)) \
                      .filter(F.col("row_num") == 1) \
                      .drop("row_num")

# Remove null values from critical columns
cleaned_df = cleaned_df.filter(F.col("id").isNotNull())

# Standardize data formats
cleaned_df = cleaned_df.withColumn("processed_timestamp", F.current_timestamp()) \
                       .withColumn("data_quality_flag", F.lit("PASSED"))

# Write to Silver layer
print(f"Writing cleansed data to Silver layer: {silver_path}")
cleaned_df.write.mode("overwrite") \
    .partitionBy("ingestion_date") \
    .parquet(f"{silver_path}/silver_data")

# Log data quality metrics
total_records = bronze_df.count()
cleaned_records = cleaned_df.count()
print(f"Data Quality Report:")
print(f"Total records in Bronze: {total_records}")
print(f"Records after cleansing: {cleaned_records}")
print(f"Records removed: {total_records - cleaned_records}")

job.commit()
print("Silver layer transformation completed successfully")
