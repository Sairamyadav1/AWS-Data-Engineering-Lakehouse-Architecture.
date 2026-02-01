"""
Silver Layer - Data Cleaning and Transformation
This script reads from Bronze layer, applies data quality rules,
deduplicates, and transforms data into a clean, conformed format.
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize contexts
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'bronze_database',
    'bronze_table',
    'silver_path',
    'silver_database',
    'silver_table'
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Job parameters
BRONZE_DATABASE = args['bronze_database']
BRONZE_TABLE = args['bronze_table']
SILVER_PATH = args['silver_path']
SILVER_DATABASE = args['silver_database']
SILVER_TABLE = args['silver_table']

print(f"Starting Silver layer transformation from {BRONZE_DATABASE}.{BRONZE_TABLE}")

try:
    # Read from Bronze layer
    bronze_dyf = glueContext.create_dynamic_frame.from_catalog(
        database=BRONZE_DATABASE,
        table_name=BRONZE_TABLE,
        transformation_ctx="bronze_source"
    )
    
    # Convert to Spark DataFrame for transformations
    df = bronze_dyf.toDF()
    
    initial_count = df.count()
    print(f"Initial record count: {initial_count}")
    
    # Data Quality Checks
    # 1. Remove null values in critical columns
    df = df.filter(
        col("id").isNotNull() &
        col("timestamp").isNotNull()
    )
    
    # 2. Remove duplicates based on business key
    df = df.dropDuplicates(["id", "timestamp"])
    
    # 3. Filter out invalid records
    df = df.filter(col("amount") >= 0)  # Example: amount should be positive
    
    # Data Transformations
    # 1. Standardize column names (lowercase, replace spaces with underscores)
    for column in df.columns:
        df = df.withColumnRenamed(column, column.lower().replace(" ", "_"))
    
    # 2. Parse and validate dates
    df = df.withColumn("processed_date", to_date(col("timestamp")))
    
    # 3. Add data quality flags
    df = df.withColumn("is_valid", lit(True))
    df = df.withColumn("quality_score", lit(100))
    
    # 4. Add processing metadata
    df = df.withColumn("processing_timestamp", current_timestamp())
    df = df.withColumn("layer", lit("silver"))
    
    # 5. Type casting and validation
    # Example: Ensure numeric columns are properly typed
    if "amount" in df.columns:
        df = df.withColumn("amount", col("amount").cast(DecimalType(18, 2)))
    
    final_count = df.count()
    print(f"Final record count after cleaning: {final_count}")
    print(f"Records filtered out: {initial_count - final_count}")
    
    # Convert back to DynamicFrame
    silver_dyf = DynamicFrame.fromDF(df, glueContext, "silver_transformed")
    
    # Write to Silver layer (partitioned by date)
    glueContext.write_dynamic_frame.from_options(
        frame=silver_dyf,
        connection_type="s3",
        format="parquet",
        connection_options={
            "path": SILVER_PATH,
            "partitionKeys": ["processed_date"]
        },
        format_options={
            "compression": "snappy"
        },
        transformation_ctx="silver_sink"
    )
    
    # Update Data Catalog
    glueContext.write_dynamic_frame.from_catalog(
        frame=silver_dyf,
        database=SILVER_DATABASE,
        table_name=SILVER_TABLE,
        transformation_ctx="catalog_update"
    )
    
    print(f"Successfully transformed data to Silver layer: {SILVER_PATH}")
    
    # Data Quality Metrics
    metrics = {
        "initial_count": initial_count,
        "final_count": final_count,
        "filtered_count": initial_count - final_count,
        "filter_rate": ((initial_count - final_count) / initial_count * 100) if initial_count > 0 else 0
    }
    print(f"Quality Metrics: {metrics}")
    
except Exception as e:
    print(f"Error during Silver transformation: {str(e)}")
    raise e

finally:
    job.commit()
