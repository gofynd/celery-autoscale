from celery_cloudwatch.logger import logger
from celery_cloudwatch.broker import Broker
import celery_cloudwatch.cloudwatch_helper as cloudwatch_helper


def update_task_stats(event, context):
    try:
        service = event.get("service")
        broker_url = event.get("broker")
        queue_names = event.get("queues")
        broker = Broker(broker_url)
        queues = broker.queues(queue_names)
        '''
            output data of queues
            [{'name': 'celery', 'messages': 0}]
        '''
        total_pending_tasks = 0
        for q in queues:
            total_pending_tasks += q.get("messages", 0)

        logger.info("Total pending task are: %s", total_pending_tasks)
        cloudwatch_helper.put_total_pending_tasks_metric_data(service, total_pending_tasks)
    except Exception as e:
        logger.exception(e)
