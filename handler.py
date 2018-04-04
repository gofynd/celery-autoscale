import load_vendors  # load vendors directory library
from celery_cloudwatch.logger import logger
from celery_cloudwatch.handler import update_task_stats


def celery_task_status_watch_handler(event, context):
    try:
        update_task_stats(event, context)
    except Exception as e:
        logger.exception(e)

    response = {
        "message": "Celery Cloud Watch Executed Sucessfully",
        "event": event
    }

    return response
