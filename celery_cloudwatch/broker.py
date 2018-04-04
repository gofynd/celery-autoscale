import numbers
import requests
from celery_cloudwatch.logger import logger
from requests.auth import HTTPBasicAuth

try:
    from urllib.parse import urlparse, urljoin, quote, unquote
except ImportError:
    from urlparse import urlparse, urljoin
    from urllib import quote, unquote

try:
    import redis
except ImportError:
    redis = None


class BrokerBase(object):
    def __init__(self, broker_url, *args, **kwargs):
        purl = urlparse(broker_url)
        self.host = purl.hostname
        self.port = purl.port
        self.vhost = purl.path[1:]

        username = purl.username
        password = purl.password

        self.username = unquote(username) if username else username
        self.password = unquote(password) if password else password

    def queues(self, names):
        raise NotImplementedError


class RabbitMQ(BrokerBase):
    def __init__(self, broker_url, http_api=None, **kwargs):
        super(RabbitMQ, self).__init__(broker_url)

        self.host = self.host or 'localhost'
        self.port = 15672 # rabbitMQ web interface run on this port by default so, its hard coded
        self.vhost = quote(self.vhost, '') or '/'
        self.username = self.username or 'guest'
        self.password = self.password or 'guest'

        if not http_api:
            http_api = "http://{0}:{1}@{2}:{3}/api/".format(
                self.username, self.password, self.host, self.port)

        try:
            self.validate_http_api(http_api)
        except Exception as e:
            logger.error("Invalid broker api url:%s", http_api)

        self.http_api = http_api

    def queues(self, names):
        url = urljoin(self.http_api, 'queues/' + self.vhost)
        api_url = urlparse(self.http_api)
        username = unquote(api_url.username or '') or self.username
        password = unquote(api_url.password or '') or self.password

        try:
            response = requests.get(url, auth=HTTPBasicAuth(username, password))
            if response.status_code == 200:
                info = response.json()
                return [x for x in info if x['name'] in names]
            else:
                response.rethrow()
        except Exception as e:
            logger.error("RabbitMQ management API call failed: %s", e)
            return []

    @classmethod
    def validate_http_api(cls, http_api):
        url = urlparse(http_api)
        if url.scheme not in ('http', 'https'):
            raise ValueError("Invalid http api schema: %s" % url.scheme)


class Redis(BrokerBase):
    SEP = '\x06\x16'
    DEFAULT_PRIORITY_STEPS = [0, 3, 6, 9]

    def __init__(self, broker_url, *args, **kwargs):
        super(Redis, self).__init__(broker_url)
        self.host = self.host or 'localhost'
        self.port = self.port or 6379
        self.db = self._get_db_value(self.vhost)
        self.priority_steps = self.DEFAULT_PRIORITY_STEPS

        if not redis:
            raise ImportError('redis library is required')

        self.redis = redis.Redis(host=self.host, port=self.port,
                                 db=self.db, password=self.password)

        broker_options = kwargs.get('broker_options')

        if broker_options and 'priority_steps' in broker_options:
            self.priority_steps = broker_options['priority_steps']

    def _q_for_pri(self, queue, pri):
        if pri not in self.priority_steps:
            raise ValueError('Priority not in priority steps')
        return '{0}{1}{2}'.format(*((queue, self.SEP, pri) if pri else (queue, '', '')))

    def queues(self, names):
        queue_stats = []
        for name in names:
            priority_names = [self._q_for_pri(name, pri) for pri in self.priority_steps]
            pipeline = self.redis.pipeline()
            for x in priority_names:
                pipeline.llen(x)
            queue_stats_messages = pipeline.execute()
            queue_stats.append({
                'name': name,
                'messages': sum(queue_stats_messages)
            })
        return queue_stats

    def _get_db_value(self, db):
        if not isinstance(db, numbers.Integral):
            if not db or db == '/':
                db = 0
            elif db.startswith('/'):
                db = db[1:]
            try:
                db = int(db)
            except ValueError:
                raise ValueError(
                    'Database is int between 0 and limit - 1, not {0}'.format(
                        db,
                    ))
        return db


class Broker(object):
    def __new__(cls, broker_url, *args, **kwargs):
        scheme = urlparse(broker_url).scheme
        if scheme == 'amqp':
            return RabbitMQ(broker_url, *args, **kwargs)
        elif scheme == 'redis':
            return Redis(broker_url, *args, **kwargs)
        else:
            raise NotImplementedError
