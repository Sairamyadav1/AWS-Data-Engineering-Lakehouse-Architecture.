"""
Bronze Layer - Raw Data Ingestion
This script ingests raw data from various sources into the Bronze layer.
No transformation is applied; data is stored in its original format.
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from datetime import datetime

# Initialize contexts
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'source_path',
    'target_path',
    'database_name',
    'table_name'
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Job parameters
SOURCE_PATH = args['source_path']
TARGET_PATH = args['target_path']
DATABASE_NAME = args['database_name']
TABLE_NAME = args['table_name']

# Add processing timestamp
current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f"Starting Bronze layer ingestion from {SOURCE_PATH}")

try:
    # Read raw data from source
    # Supports multiple formats: CSV, JSON, Parquet
    datasource = glueContext.create_dynamic_frame.from_options(
        format_options={
            "quoteChar": '"',
            "withHeader": True,
            "separator": ","
        },
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [SOURCE_PATH],
            "recurse": True
        },
        transformation_ctx="datasource"
    )
    
    # Add metadata columns
    df = datasource.toDF()
    df = df.withColumn("ingestion_timestamp", spark_sql("current_timestamp()"))
    df = df.withColumn("source_file", spark_sql("input_file_name()"))
    
    # Convert back to DynamicFrame
    dynamic_frame = DynamicFrame.fromDF(df, glueContext, "with_metadata")
    
    # Write to Bronze layer (partitioned by ingestion date)
    glueContext.write_dynamic_frame.from_options(
        frame=dynamic_frame,
        connection_type="s3",
        format="parquet",
        connection_options={
            "path": TARGET_PATH,
            "partitionKeys": ["ingestion_date"]
        },
        transformation_ctx="bronze_sink"
    )
    
    # Update Data Catalog
    glueContext.write_dynamic_frame.from_catalog(
        frame=dynamic_frame,
        database=DATABASE_NAME,
        table_name=TABLE_NAME,
        transformation_ctx="catalog_update"
    )
    
    print(f"Successfully ingested data to Bronze layer: {TARGET_PATH}")
    print(f"Records processed: {dynamic_frame.count()}")
    
except Exception as e:
    print(f"Error during Bronze ingestion: {str(e)}")
    raise e

finally:
    job.commit()
