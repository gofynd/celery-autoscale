import sys
from celery_cloudwatch.broker import Broker


def main():
    broker_url = sys.argv[1] if len(sys.argv) > 1 else 'amqp://'
    queue_name = sys.argv[2] if len(sys.argv) > 2 else 'celery'
    if len(sys.argv) > 3:
        http_api = sys.argv[3]
    else:
        http_api = 'http://guest:guest@localhost:15672/api/'

    queue_names = queue_name.split(",")
    broker = Broker(broker_url, http_api=http_api)
    queues = broker.queues(queue_names)
    if queues:
        print(queues)


if __name__ == "__main__":
    main()