"""
Snowflake Integration for AWS Lakehouse
This script demonstrates integration between S3 and Snowflake for advanced analytics
"""

import snowflake.connector
from snowflake.connector import DictCursor
import os

class SnowflakeLakehouseIntegration:
    """
    Integration class for Snowflake and AWS S3 Lakehouse
    """
    
    def __init__(self, account, user, password, warehouse, database, schema):
        """Initialize Snowflake connection"""
        self.conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        self.cursor = self.conn.cursor(DictCursor)
    
    def create_external_stage(self, stage_name, s3_path, storage_integration_name='aws_integration'):
        """
        Create external stage pointing to S3 lakehouse
        
        Args:
            stage_name: Name of the Snowflake stage
            s3_path: S3 path (e.g., s3://bucket-name/gold/)
            storage_integration_name: Name of the Snowflake storage integration (default: 'aws_integration')
        """
        sql = f"""
        CREATE OR REPLACE STAGE {stage_name}
        URL = '{s3_path}'
        STORAGE_INTEGRATION = {storage_integration_name}
        FILE_FORMAT = (TYPE = PARQUET);
        """
        
        self.cursor.execute(sql)
        print(f"External stage '{stage_name}' created successfully")
    
    def create_external_table(self, table_name, stage_name, columns):
        """
        Create external table from S3 data
        
        Args:
            table_name: Name of the external table
            stage_name: Snowflake stage name
            columns: List of column definitions
        """
        column_defs = ", ".join(columns)
        
        sql = f"""
        CREATE OR REPLACE EXTERNAL TABLE {table_name}
        WITH LOCATION = @{stage_name}
        FILE_FORMAT = (TYPE = PARQUET)
        ({column_defs});
        """
        
        self.cursor.execute(sql)
        print(f"External table '{table_name}' created successfully")
    
    def load_gold_data(self, target_table, stage_name):
        """
        Load data from Gold layer into Snowflake table
        
        Args:
            target_table: Snowflake table name
            stage_name: Stage name pointing to Gold layer
        """
        sql = f"""
        COPY INTO {target_table}
        FROM @{stage_name}
        FILE_FORMAT = (TYPE = PARQUET)
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        ON_ERROR = CONTINUE;
        """
        
        self.cursor.execute(sql)
        print(f"Data loaded into '{target_table}' successfully")
    
    def create_analytics_views(self):
        """Create analytical views for reporting"""
        
        # Business summary view
        sql_business_summary = """
        CREATE OR REPLACE VIEW vw_business_summary AS
        SELECT 
            ingestion_date,
            total_records,
            unique_ids,
            aggregation_timestamp
        FROM gold_daily_aggregates
        ORDER BY ingestion_date DESC;
        """
        
        self.cursor.execute(sql_business_summary)
        print("Analytics views created successfully")
    
    def execute_analytics_query(self, query):
        """
        Execute analytical query
        
        Args:
            query: SQL query to execute
        
        Returns:
            Query results
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results
    
    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()
        print("Snowflake connection closed")

# Example usage
if __name__ == "__main__":
    # Configuration
    SNOWFLAKE_CONFIG = {
        'account': 'your_account',
        'user': 'your_user',
        'password': os.getenv('SNOWFLAKE_PASSWORD'),
        'warehouse': 'LAKEHOUSE_WH',
        'database': 'LAKEHOUSE_DB',
        'schema': 'ANALYTICS'
    }
    
    # Initialize integration
    sf_integration = SnowflakeLakehouseIntegration(**SNOWFLAKE_CONFIG)
    
    # Create external stage for Gold layer
    sf_integration.create_external_stage(
        stage_name='gold_layer_stage',
        s3_path='s3://your-bucket/gold/',
        storage_integration_name='aws_integration'
    )
    
    # Create external table
    columns = [
        "ingestion_date VARCHAR AS (value:ingestion_date::VARCHAR)",
        "total_records NUMBER AS (value:total_records::NUMBER)",
        "unique_ids NUMBER AS (value:unique_ids::NUMBER)"
    ]
    
    sf_integration.create_external_table(
        table_name='gold_daily_aggregates',
        stage_name='gold_layer_stage',
        columns=columns
    )
    
    # Create analytics views
    sf_integration.create_analytics_views()
    
    # Close connection
    sf_integration.close()
