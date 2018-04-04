import os

AWS_REGION = os.environ.get('AWS_REGION')
CLOUDWATCH_NAMESPACE = os.environ.get('CLOUDWATCH_NAMESPACE', 'Celery/Queue')