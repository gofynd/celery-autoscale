"""
my_celery_app.py

Usage::

   (window1)$ python my_celery_app.py worker -l info

   (window2)$ python
   >>> from my_celery_app import submit_tasks
   >>> submit_tasks()


You can also specify the app to use with the `celery` command,
using the `-A` / `--app` option::

    $ celery -A my_celery_app worker -l info

With the `-A myproj` argument the program will search for an app
instance in the module ``myproj``.  You can also specify an explicit
name using the fully qualified form::

    $ celery -A my_celery_app:app worker -l info

"""
from celery import Celery

app = Celery(
    'my_celery_app',
    # broker='amqp://root:root@localhost:5672/vhost',
    broker='redis://localhost:6379/0',
    # ## add result backend here if needed.
    backend='redis://localhost:6379/0'
)

import time

@app.task
def add(x, y):
    time.sleep(60)
    return x + y


def submit_tasks():
    for t in range(1, 100):
        add.delay(20, t)

if __name__ == '__main__':
    app.start()