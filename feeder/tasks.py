from celery import shared_task, Task

from .models import XmlLink, Channel
from .parsers import channel_parser_mapper, item_model_mapper, items_parser_mapper



class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True
    task_concurrency = 4,
    worker_prefetch_multiplier = 1


@shared_task(task_time_limit=600)
def update_all_rss():
    for xml_link_obj in XmlLink.objects.all().iterator():
        update_single_rss.delay(xml_link_obj.xml_link)


@shared_task(base=BaseTaskWithRetry, task_time_limit=120, acks_late=True)
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
        items = (ItemClass(**item, channel=channel) for item in items_info)
        ItemClass.objects.bulk_create(items)

        return {"Message": "Channel and the Items Was Created"}

    else:
        channel = channel_qs.get()
        if channel.last_update != channel_info.get("last_update") or channel.last_update is None:
            channel.update(**channel_info)
            if ItemClass.objects.all(channel=channel).count() == 0:
                items = (
                    ItemClass(**item, channel=channel)
                    for item in items_info
                )
            else:
                # last_item_published_date_in_db = ItemClass.objects.all().order_by(
                #     "-published_date").first().published_date
                last_item_guid_in_db = ItemClass.objects.all().order_by("-published_date").first().guid
                items = []
                for item in items_info:
                    if item['guid'] == last_item_guid_in_db:
                        break
                    items.append(ItemClass(**item, channel=channel))
                    # items = yield ItemClass(**item, channel=channel) ???

            ItemClass.objects.bulk_create(items)
            return {"Message": f"Channel {channel.title} Was Updated"}

        return {"Message": f"Channel {channel.title} is Already Updated"}


