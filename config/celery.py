import os
from datetime import datetime
import time

from celery import Celery, Task
from django.conf import settings
from elasticsearch import Elasticsearch

# from celery.signals import setup_logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

# @setup_logging.connect
# def config_loggers(*args, **kwargs):
#     from logging.config import dictConfig
#     from django.conf import settings
#     dictConfig(settings.LOGGING)


app.autodiscover_tasks()


class CustomTask(Task):
    es = Elasticsearch(f'http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}')

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        log_data = self.create_log_data(task_id, args, kwargs, state="retry",
                                        log_type="CRITICAL", exc=exc, einfo=einfo)
        self.make_log(log_data)

    def on_success(self, retval, task_id, args, kwargs):
        log_data = self.create_log_data(task_id, args, kwargs, state="success",
                                        log_type="INFO", retval=retval)
        self.make_log(log_data)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        log_data = self.create_log_data(task_id, args, kwargs, state="retry",
                                        log_type="WARNING", exc=exc, einfo=einfo)

        self.make_log(log_data)

    @staticmethod
    def create_log_data(task_id, args, kwargs, state, log_type,
                        exc=None, einfo=None, retval=None):
        log_data = {
            'timestamp': datetime.now(),
            'exception_type': exc.__class__.__name__,
            'exception_message': str(exc),
            "log_type": log_type,
            "task_id": task_id,
            "args": args,
            "kwargs": kwargs,
            "Exception information": str(einfo),
            "state": state,
            "result": retval
        }
        return log_data

    def make_log(self, log_data):
        index_name = self.get_index_name()
        self.es.index(index=index_name, document=log_data)

    @staticmethod
    def get_index_name():
        index_name = f'celery_log-{time.strftime("%Y_%m_%d")}'
        return index_name
