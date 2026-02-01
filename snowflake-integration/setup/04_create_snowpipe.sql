-- Create Snowpipe for Continuous Data Loading
-- Automatically loads new data from S3 as it arrives

USE ROLE SYSADMIN;
USE DATABASE LAKEHOUSE;
USE SCHEMA GOLD;

-- Create pipe for auto-ingestion
CREATE OR REPLACE PIPE gold_daily_summary_pipe
  AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:snowflake-gold-notifications'
  COMMENT = 'Auto-ingest pipe for Gold layer daily summary'
AS
  COPY INTO gold_daily_summary
  FROM @gold_stage
  FILE_FORMAT = LAKEHOUSE.PUBLIC.PARQUET_FORMAT
  PATTERN = '.*[.]parquet'
  ON_ERROR = CONTINUE;

-- Show pipe details (contains SQS ARN for S3 event notification)
DESC PIPE gold_daily_summary_pipe;

-- Check pipe status
SELECT SYSTEM$PIPE_STATUS('gold_daily_summary_pipe');

-- Grant ownership and permissions
GRANT OWNERSHIP ON PIPE gold_daily_summary_pipe TO ROLE SYSADMIN;
GRANT MONITOR ON PIPE gold_daily_summary_pipe TO ROLE DATA_ENGINEER;

-- View pipe execution history
SELECT 
  PIPE_NAME,
  FILE_NAME,
  ROW_COUNT,
  ERROR_COUNT,
  FIRST_ERROR_MESSAGE,
  LAST_LOAD_TIME
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'GOLD_DAILY_SUMMARY',
  START_TIME => DATEADD(HOURS, -24, CURRENT_TIMESTAMP())
))
ORDER BY LAST_LOAD_TIME DESC;

-- Manually trigger pipe (for testing)
ALTER PIPE gold_daily_summary_pipe REFRESH;

-- Pause pipe (if needed)
-- ALTER PIPE gold_daily_summary_pipe SET PIPE_EXECUTION_PAUSED = TRUE;

-- Resume pipe
-- ALTER PIPE gold_daily_summary_pipe SET PIPE_EXECUTION_PAUSED = FALSE;

/*
AWS S3 Event Notification Configuration:
After creating the pipe, configure S3 bucket notifications:

1. Get the SQS ARN from DESC PIPE output
2. Configure S3 bucket notification:
   - Event type: s3:ObjectCreated:*
   - Prefix: aggregated/
   - Suffix: .parquet
   - Destination: SQS queue from pipe

AWS CLI example:
aws s3api put-bucket-notification-configuration \
  --bucket your-gold-bucket \
  --notification-configuration file://s3-event-notification.json

s3-event-notification.json:
{
  "QueueConfigurations": [
    {
      "Id": "SnowpipeNotification",
      "QueueArn": "arn:aws:sqs:us-east-1:YOUR_ACCOUNT_ID:snowflake-queue",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {"Name": "prefix", "Value": "aggregated/"},
            {"Name": "suffix", "Value": ".parquet"}
          ]
        }
      }
    }
  ]
}
*/
