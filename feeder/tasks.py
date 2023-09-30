from celery import shared_task, Task, group

from .models import XmlLink, Channel
from .parsers import channel_parser_mapper, item_model_mapper, items_parser_mapper


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True
    task_concurrency = 4
    worker_prefetch_multiplier = 1


# @shared_task(task_time_limit=600)
# def update_all_rss():
#     for xml_link_obj in XmlLink.objects.all():
#         update_single_rss.delay(xml_link_obj.xml_link)


@shared_task(task_time_limit=600)
def update_all_rss():
    xml_links = list(XmlLink.objects.all())
    tasks = (update_single_rss.s(xml_link_obj.xml_link) for xml_link_obj in xml_links)
    result_group = group(tasks)
    result_group()


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
        channel = Channel.objects.create(xml_link=xml_link_obj, **channel_info)
        items = pre_create_item(items_info, ItemClass, channel)
        ItemClass.objects.bulk_create(items)

        return {"Message": "Channel and the Items Was Created"}

    else:
        channel = channel_qs.get()
        if channel.last_update != channel_info.get("last_update") or channel.last_update is None:
            Channel.objects.filter(id=channel.id).update(**channel_info)
            last_item_guid_in_db = channel.last_item_guid
            items = pre_create_item(items_info, ItemClass, channel, last_item_guid_in_db=last_item_guid_in_db)
            ItemClass.objects.bulk_create(items)
            return {"Message": f"Channel {channel.title} Was Updated"}

        return {"Message": f"Channel {channel.title} is Already Updated"}


def pre_create_item(items_info, item_class, channel, last_item_guid_in_db=False):
    items = []
    counter = 0
    for item in items_info:
        if last_item_guid_in_db:
            if item['guid'] == last_item_guid_in_db:
                break
        if counter == 0:
            first_item = item_class.objects.create(**item, channel=channel)
            channel.last_item_guid = first_item.guid
            channel.save()
        else:
            items.append(item_class(**item, channel=channel))
        counter += 1
    return items
