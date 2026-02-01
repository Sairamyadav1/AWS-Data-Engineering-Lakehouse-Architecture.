"""
Gold Layer - Business-Level Aggregations
This script reads from Silver layer and creates aggregated,
business-ready datasets optimized for analytics and reporting.
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from pyspark.sql.types import *

# Initialize contexts
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'silver_database',
    'silver_table',
    'gold_path',
    'gold_database',
    'gold_table'
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Job parameters
SILVER_DATABASE = args['silver_database']
SILVER_TABLE = args['silver_table']
GOLD_PATH = args['gold_path']
GOLD_DATABASE = args['gold_database']
GOLD_TABLE = args['gold_table']

print(f"Starting Gold layer aggregation from {SILVER_DATABASE}.{SILVER_TABLE}")

try:
    # Read from Silver layer
    silver_dyf = glueContext.create_dynamic_frame.from_catalog(
        database=SILVER_DATABASE,
        table_name=SILVER_TABLE,
        transformation_ctx="silver_source"
    )
    
    # Convert to Spark DataFrame
    df = silver_dyf.toDF()
    
    print(f"Processing {df.count()} records from Silver layer")
    
    # Business Aggregations
    # Example 1: Daily summary metrics
    daily_summary = df.groupBy(
        "processed_date",
        "category"
    ).agg(
        count("*").alias("total_transactions"),
        sum("amount").alias("total_amount"),
        avg("amount").alias("average_amount"),
        min("amount").alias("min_amount"),
        max("amount").alias("max_amount"),
        countDistinct("customer_id").alias("unique_customers")
    )
    
    # Add calculated fields
    daily_summary = daily_summary.withColumn(
        "transaction_density",
        col("total_transactions") / col("unique_customers")
    )
    
    # Add time dimensions
    daily_summary = daily_summary.withColumn("year", year(col("processed_date")))
    daily_summary = daily_summary.withColumn("month", month(col("processed_date")))
    daily_summary = daily_summary.withColumn("quarter", quarter(col("processed_date")))
    daily_summary = daily_summary.withColumn("day_of_week", dayofweek(col("processed_date")))
    
    # Add ranking and window functions
    window_spec = Window.partitionBy("category").orderBy(col("total_amount").desc())
    daily_summary = daily_summary.withColumn(
        "category_rank",
        row_number().over(window_spec)
    )
    
    # Calculate moving averages (7-day)
    window_spec_7d = Window.partitionBy("category").orderBy("processed_date").rowsBetween(-6, 0)
    daily_summary = daily_summary.withColumn(
        "moving_avg_7d",
        avg("total_amount").over(window_spec_7d)
    )
    
    # Add business metadata
    daily_summary = daily_summary.withColumn("aggregation_timestamp", current_timestamp())
    daily_summary = daily_summary.withColumn("layer", lit("gold"))
    daily_summary = daily_summary.withColumn("aggregation_type", lit("daily_summary"))
    
    # Convert back to DynamicFrame
    gold_dyf = DynamicFrame.fromDF(daily_summary, glueContext, "gold_aggregated")
    
    print(f"Created {gold_dyf.count()} aggregated records")
    
    # Write to Gold layer (partitioned by year and month for optimal query performance)
    glueContext.write_dynamic_frame.from_options(
        frame=gold_dyf,
        connection_type="s3",
        format="parquet",
        connection_options={
            "path": GOLD_PATH,
            "partitionKeys": ["year", "month"]
        },
        format_options={
            "compression": "snappy"
        },
        transformation_ctx="gold_sink"
    )
    
    # Update Data Catalog
    glueContext.write_dynamic_frame.from_catalog(
        frame=gold_dyf,
        database=GOLD_DATABASE,
        table_name=GOLD_TABLE,
        transformation_ctx="catalog_update"
    )
    
    print(f"Successfully created Gold layer aggregations: {GOLD_PATH}")
    
    # Show sample data for validation
    print("Sample aggregated data:")
    daily_summary.show(5, truncate=False)
    
except Exception as e:
    print(f"Error during Gold aggregation: {str(e)}")
    raise e

finally:
    job.commit()
