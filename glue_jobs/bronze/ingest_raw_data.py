"""
AWS Glue ETL Job - Bronze Layer
This script ingests raw data from source systems into the Bronze layer (S3)
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_path', 'target_path'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Job parameters
source_path = args['source_path']
target_path = args['target_path']
current_date = datetime.now().strftime('%Y-%m-%d')

# Read raw data from source
print(f"Reading data from source: {source_path}")
raw_df = spark.read.option("header", "true").csv(source_path)

# Add metadata columns for lineage tracking
raw_df = raw_df.withColumn("ingestion_timestamp", F.current_timestamp()) \
               .withColumn("ingestion_date", F.lit(current_date)) \
               .withColumn("source_file", F.input_file_name())

# Write to Bronze layer in Parquet format with partitioning
print(f"Writing data to Bronze layer: {target_path}")
raw_df.write.mode("append") \
    .partitionBy("ingestion_date") \
    .parquet(f"{target_path}/bronze_data")

job.commit()
print("Bronze layer ingestion completed successfully")
