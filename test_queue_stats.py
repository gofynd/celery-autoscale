from handler import celery_task_status_watch_handler

if __name__ == "__main__":
    event = {
        "service": "test",
        "broker": "redis://localhost:6379/0",
        "queues": ['celery']
    }
    celery_task_status_watch_handler(event,{})

    event = {
        "service": "test",
        "broker": "amqp://root:root@localhost:5672/vhost",
        "queues": ['celery']
    }
    celery_task_status_watch_handler(event,{})