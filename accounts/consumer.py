import json
import logging
import pika
import os

from config import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import CustomUser, UserNotifications, Notification, UserLastActivity
from .tasks import broadcast_notification

from interactions.models import Bookmark

logger = logging.getLogger('elastic_logger')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


def start_consumers(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    ch = connection.channel()

    ch.queue_declare(queue=queue_name)
    callback_func = callback_mapper(queue_name)
    ch.basic_consume(queue=queue_name, on_message_callback=callback_func)

    ch.start_consuming()


def auth_callback(ch, method, property, body):
    body = json.loads(body)
    user = CustomUser.objects.get(username=body["username"])

    create_user_activity(user, body)

    routing_key = body["routing_key"]
    if routing_key in settings.auth_allowed_notification:
        create_auth_notification(user, body)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def rss_feed_callback(ch, method, property, body):
    body = json.loads(body)

    channel_id = body["channel_id"]
    content_type_obj = ContentType.objects.get(model="channel")
    # qs = Bookmark.objects.filter(content_type=content_type_obj, object_id=channel_id)
    qs = Bookmark.objects.select_related("customuser").filter(content_type=content_type_obj, object_id=channel_id)
    if qs.exists():
        create_rss_feed_notification(body, qs)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def callback_mapper(arg):
    callback_select = {
        "login": auth_callback,
        "register": auth_callback,
        "rss_feed_update": rss_feed_callback,
        "refresh": auth_callback,
        "logout": auth_callback,
        "logout_all": auth_callback,
        "selected_logout": auth_callback,
    }
    return callback_select[arg]


def create_auth_notification_log_data(user, body):
    return {
        "unique_id": body["unique_id"],
        'user_id': str(user.id),
        'user_agent': body["user_agent"],
        'event': f"consumer.{body['routing_key']}",
        "status": "success"
    }


def create_auth_notification_exception_log_data(user, body, e):
    return {
        "unique_id": body["unique_id"],
        'user_id': str(user.id),
        'user_agent': body["user_agent"],
        'exception_type': e.__class__.__name__,
        'exception_message': str(e),
        'event': f"consumer.{body['routing_key']}",
        'exception': True,
    }


def create_auth_notification(user, body):
    try:
        with transaction.atomic():
            notification = Notification.objects.create(notification=body["message"], action=body["routing_key"])
            UserNotifications.objects.create(user=user, notification=notification)
    except Exception as e:
        log_data = create_auth_notification_exception_log_data(user, body, e)
        logger.error(json.dumps(log_data))
    else:
        broadcast_notification.delay(notification.id, body["unique_id"])
        log_data = create_auth_notification_log_data(user, body)
        logger.info(json.dumps(log_data))


def create_rss_feed_notification(body, qs):
    try:
        with transaction.atomic():
            notification = Notification.objects.create(notification=body["message"], action=body["routing_key"])
            items = (UserNotifications(user=item.user, notification=notification) for item in qs)
            UserNotifications.objects.bulk_create(items)
    except Exception as e:
        log_data = create_rss_feed_notification_exception_log_data(body, e)
        logger.error(json.dumps(log_data))
    else:
        broadcast_notification.delay(notification.id, body["unique_id"])
        log_data = create_rss_feed_notification_log_data(body)
        logger.info(json.dumps(log_data))


def create_rss_feed_notification_log_data(body):
    return {
        "unique_id": body["unique_id"],
        "channel_id": body["channel_id"],
        'event': f"consumer.{body['routing_key']}",
        "status": "success"
    }


def create_rss_feed_notification_exception_log_data(body, e):
    return {
        "unique_id": body["unique_id"],
        "channel_id": body["channel_id"],
        'exception_type': e.__class__.__name__,
        'exception_message': str(e),
        'event': f"consumer.{body['routing_key']}",
        'exception': True,
    }


def create_user_activity(user, body):
    user_last_activity_qs = UserLastActivity.objects.filter(user=user)
    if not user_last_activity_qs.exists():
        UserLastActivity.objects.create(user=user, action=body["routing_key"], user_agent=body["user_agent"],
                                        ip=body["ip"])
    else:
        user_last_activity_qs.update(action=body["routing_key"], user_agent=body["user_agent"],
                                     ip=body["ip"])
