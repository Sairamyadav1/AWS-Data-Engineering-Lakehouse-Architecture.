"""
AWS CloudWatch Monitoring Configuration for Lakehouse Pipeline
This script sets up monitoring and alerting for the data pipeline
"""

import boto3
from datetime import datetime

class LakehouseMonitoring:
    """
    CloudWatch monitoring setup for lakehouse pipeline
    """
    
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.logs = boto3.client('logs')
        self.sns = boto3.client('sns')
    
    def create_log_group(self, log_group_name):
        """Create CloudWatch Log Group"""
        try:
            self.logs.create_log_group(logGroupName=log_group_name)
            print(f"Log group '{log_group_name}' created successfully")
        except self.logs.exceptions.ResourceAlreadyExistsException:
            print(f"Log group '{log_group_name}' already exists")
    
    def put_metric_data(self, namespace, metric_name, value, dimensions=None):
        """
        Send custom metrics to CloudWatch
        
        Args:
            namespace: Metric namespace
            metric_name: Name of the metric
            value: Metric value
            dimensions: Optional dimensions
        """
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Timestamp': datetime.utcnow(),
            'Unit': 'Count'
        }
        
        if dimensions:
            metric_data['Dimensions'] = dimensions
        
        self.cloudwatch.put_metric_data(
            Namespace=namespace,
            MetricData=[metric_data]
        )
        print(f"Metric '{metric_name}' sent to CloudWatch")
    
    def create_alarm(self, alarm_name, metric_name, namespace, threshold, 
                     comparison_operator, evaluation_periods, sns_topic_arn):
        """
        Create CloudWatch Alarm
        
        Args:
            alarm_name: Name of the alarm
            metric_name: Metric to monitor
            namespace: Metric namespace
            threshold: Alarm threshold
            comparison_operator: Comparison operator (e.g., 'GreaterThanThreshold')
            evaluation_periods: Number of periods to evaluate
            sns_topic_arn: SNS topic ARN for notifications
        """
        self.cloudwatch.put_metric_alarm(
            AlarmName=alarm_name,
            ComparisonOperator=comparison_operator,
            EvaluationPeriods=evaluation_periods,
            MetricName=metric_name,
            Namespace=namespace,
            Period=300,
            Statistic='Sum',
            Threshold=threshold,
            ActionsEnabled=True,
            AlarmActions=[sns_topic_arn],
            AlarmDescription=f'Alarm for {metric_name}',
            TreatMissingData='notBreaching'
        )
        print(f"Alarm '{alarm_name}' created successfully")
    
    def setup_lakehouse_monitoring(self, sns_topic_arn):
        """
        Setup complete monitoring for lakehouse pipeline
        """
        # Create log groups for each layer
        log_groups = [
            '/aws/glue/jobs/bronze-layer',
            '/aws/glue/jobs/silver-layer',
            '/aws/glue/jobs/gold-layer',
            '/aws/glue/crawlers'
        ]
        
        for log_group in log_groups:
            self.create_log_group(log_group)
        
        # Create alarms for job failures
        self.create_alarm(
            alarm_name='GlueJobFailureAlarm',
            metric_name='glue.driver.aggregate.numFailedTasks',
            namespace='Glue',
            threshold=1,
            comparison_operator='GreaterThanThreshold',
            evaluation_periods=1,
            sns_topic_arn=sns_topic_arn
        )
        
        # Create alarm for data quality issues
        self.create_alarm(
            alarm_name='DataQualityAlarm',
            metric_name='DataQualityFailures',
            namespace='Lakehouse/Metrics',
            threshold=100,
            comparison_operator='GreaterThanThreshold',
            evaluation_periods=2,
            sns_topic_arn=sns_topic_arn
        )
        
        print("Lakehouse monitoring setup completed")
    
    def log_pipeline_metrics(self, layer, records_processed, records_failed):
        """
        Log pipeline metrics for monitoring
        
        Args:
            layer: Pipeline layer (bronze/silver/gold)
            records_processed: Number of records processed
            records_failed: Number of records failed
        """
        # Records processed metric
        self.put_metric_data(
            namespace='Lakehouse/Metrics',
            metric_name='RecordsProcessed',
            value=records_processed,
            dimensions=[{'Name': 'Layer', 'Value': layer}]
        )
        
        # Records failed metric
        self.put_metric_data(
            namespace='Lakehouse/Metrics',
            metric_name='RecordsFailed',
            value=records_failed,
            dimensions=[{'Name': 'Layer', 'Value': layer}]
        )
        
        print(f"Metrics logged for {layer} layer")

# Example usage
if __name__ == "__main__":
    monitoring = LakehouseMonitoring()
    
    # Setup monitoring
    SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:ACCOUNT_ID:lakehouse-alerts"
    monitoring.setup_lakehouse_monitoring(SNS_TOPIC_ARN)
    
    # Log sample metrics
    monitoring.log_pipeline_metrics(
        layer='bronze',
        records_processed=10000,
        records_failed=5
    )
