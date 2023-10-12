import json
import logging
import os

from celery import Celery, Task

logger = logging.getLogger('elastic_logger')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


class CustomTask(Task):

    def retry(self, args=None, kwargs=None, exc=None, throw=True,
              eta=None, countdown=None, max_retries=None, **options):
        retry_count = self.request.retries
        log_data = {
            "exe": str(exc),
            'event': f"celery.{self.name}",
            'correlation_id': self.request.correlation_id,
            'args': self.request.args,
            'kwargs': self.request.kwargs,
            "attempt_on": retry_count + 1,
            'status': "retry"
        }
        if retry_count != max_retries:
            logger.error(json.dumps(log_data))
        else:
            log_data['status'] = "fail"
            log_data['exception'] = True
            del log_data["attempt_on"]
            logger.critical(json.dumps(log_data))

        super().retry(args, kwargs, exc, throw, eta, countdown, max_retries, **options)

    def on_success(self, retval, task_id, args, kwargs):
        retry_count = self.request.retries

        log_data = {
            'event': f"celery.{self.name}",
            'correlation_id': self.request.correlation_id,
            'args': self.request.args,
            'kwargs': self.request.kwargs,
            "attempt_on": retry_count + 1,
            'status': "success"
        }
        logger.info(json.dumps(log_data))
