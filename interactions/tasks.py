from celery import shared_task, Task

from .models import Comment

from feeder.models import Channel
from feeder.parsers import item_model_mapper

from config.celery import CustomTask


class BaseTaskWithRetry(CustomTask):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True


@shared_task(bind=True, base=BaseTaskWithRetry, task_time_limit=120)
def create_comment(self, content, channel_id, item_id, user_id, unique_id):
    self.request.args = list(map(str, self.request.args))
    channel = Channel.objects.get(id=channel_id)
    ItemClass = item_model_mapper(channel.xml_link.rss_type.name)
    item = ItemClass.objects.get(id=item_id)
    content_type_obj = item.get_content_type_obj
    Comment.objects.create(content=content,
                           content_type=content_type_obj,
                           object_id=item.id,
                           user_id=user_id)
    return f"User {user_id} submit a comment"
