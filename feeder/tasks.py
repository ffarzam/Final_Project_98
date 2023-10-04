import itertools

from celery import shared_task, Task, group, chain
from django.db import transaction

from .models import XmlLink, Channel
from .parsers import channel_parser_mapper, item_model_mapper, items_parser_mapper

from accounts.publisher import publish


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True
    worker_concurrency = 5
    worker_prefetch_multiplier = 1


@shared_task(task_time_limit=600)
def update_all_rss():
    CHUNK_SIZE = 5
    xml_links = XmlLink.objects.all()
    tasks = (update_single_rss.si(xml_link_obj.xml_link) for xml_link_obj in xml_links)
    group_chain_list = chunks(tasks, CHUNK_SIZE)
    work_flow = chain(*group_chain_list)
    work_flow.apply_async()


@shared_task(base=BaseTaskWithRetry, task_time_limit=180)
def update_single_rss(xml_link):
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

            print("1"*100)
            print(channel.id)
            print(type(channel.id))
            if flag:
                info = {
                    "channel_id": channel.id,
                    "message": f"Channel {channel.title} Has Been Updated",
                    "routing_key": "rss_feed"
                }
                publish(info)
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
