-- Create Bronze Database
CREATE DATABASE IF NOT EXISTS bronze_db
COMMENT 'Bronze layer - Raw data from source systems'
LOCATION 's3://your-bronze-bucket/';

-- Create Silver Database
CREATE DATABASE IF NOT EXISTS silver_db
COMMENT 'Silver layer - Cleaned and conformed data'
LOCATION 's3://your-silver-bucket/';

-- Create Gold Database
CREATE DATABASE IF NOT EXISTS gold_db
COMMENT 'Gold layer - Business-ready aggregated data'
LOCATION 's3://your-gold-bucket/';
