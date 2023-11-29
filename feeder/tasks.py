import itertools
import functools
from uuid import uuid4

from celery import shared_task, group, chain

from django.db import transaction

from .models import XmlLink, Channel
from .parsers import channel_parser_mapper, item_model_mapper, items_parser_mapper

from accounts.publisher import publish
from config.celery import CustomTask


class BaseTaskWithRetry(CustomTask):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True
    task_time_limit = 60


@shared_task(task_time_limit=600)
def update_all_rss(unique_id=None):

    CHUNK_SIZE = 5
    xml_links = XmlLink.objects.all()
    tasks = (update_single_rss.si(xml_link_obj.xml_link, unique_id) for xml_link_obj in xml_links)
    group_chain_list = chunks(tasks, CHUNK_SIZE)
    work_flow = functools.reduce(lambda x, y: x | y, group_chain_list, chain())
    work_flow.apply_async()


@shared_task(bind=True, base=BaseTaskWithRetry)
def update_single_rss(self, xml_link, unique_id=None):
    if unique_id is None:
        unique_id = uuid4().hex
        self.request.args.append(unique_id)

    xml_link_obj = XmlLink.objects.get(xml_link=xml_link)
    channel_parser = channel_parser_mapper(xml_link_obj.channel_parser)
    channel_info = channel_parser(xml_link_obj.xml_link)
    items_parser = items_parser_mapper(xml_link_obj.items_parser)
    items_info = items_parser(xml_link_obj.xml_link)
    ItemClass = item_model_mapper(xml_link_obj.rss_type.name)

    channel_qs = Channel.objects.filter(xml_link=xml_link_obj)
    if not channel_qs.exists():
        with transaction.atomic():
            channel = Channel.objects.create(xml_link=xml_link_obj, **channel_info)
            create_item(items_info, ItemClass, channel)
        return {"Message": "Channel and the Items Was Created"}

    else:
        channel = channel_qs.get()
        if channel.last_update != channel_info.get("last_update") or channel.last_update is None:
            with transaction.atomic():
                Channel.objects.filter(id=channel.id).update(**channel_info)
                last_item_guid_in_db = channel.last_item_guid
                flag = create_item(items_info, ItemClass, channel, last_item_guid_in_db=last_item_guid_in_db)

            if flag:
                info = {
                    "unique_id": unique_id,
                    "channel_id": channel.id,
                    "message": f"Channel {channel.title} Has Been Updated",
                    "routing_key": "rss_feed_update"
                }
                notification_microservice_info = {
                    "unique_id": unique_id,
                    "channel_id": channel.id,
                    "channel_title": channel.title,
                    "routing_key": "notification_rss_feed_update"
                }
                publish(info)
                publish(notification_microservice_info)
            return {"Message": f"Channel {channel.title} Has Been Updated"}

        return {"Message": f"Channel {channel.title} is Already Updated"}


def create_item(items_info, item_class, channel, last_item_guid_in_db=None):
    flag = False
    first_item = next(items_info, None)
    if first_item and first_item["guid"] != last_item_guid_in_db:
        flag = True
        first_item = item_class.objects.create(**first_item, channel=channel)
        channel.last_item_guid = first_item.guid
        channel.save()
        items = (item_class(**item, channel=channel) for item in items_info)
        item_class.objects.bulk_create(items, ignore_conflicts=True)
    return flag


def chunks(iterator, chunk_size):
    for first in iterator:
        yield group(itertools.chain([first], itertools.islice(iterator, chunk_size - 1)))
