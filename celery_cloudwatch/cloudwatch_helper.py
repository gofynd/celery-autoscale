import boto3
from datetime import datetime
import celery_cloudwatch.constants as constants


def put_total_pending_tasks_metric_data(service, count=0):
    cloudwatch = boto3.client('cloudwatch', region_name=constants.AWS_REGION)
    cloudwatch.put_metric_data(
        Namespace= constants.CLOUDWATCH_NAMESPACE,
        MetricData=[
            {
                'MetricName': 'pendingTask',
                'Dimensions': [
                    {
                        'Name': 'queue',
                        'Value': 'all'
                    },
                    {
                        'Name': 'service',
                        'Value': service
                    }
                ],
                'Timestamp': datetime.utcnow(),
                'Value': count,
                'Unit': 'Count'
            }
        ]
    )