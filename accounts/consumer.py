import json
import logging
import traceback

import pika
import os

from config import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import CustomUser, UserNotifications, Notification, UserLastActivity
from .publisher import publish
from .tasks import broadcast_notification

from interactions.models import Bookmark

logger = logging.getLogger('elastic_logger')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

MAX_RETRIES = 3


def start_consumers(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    ch = connection.channel()

    ch.queue_declare(queue=queue_name)
    callback_func = callback_mapper(queue_name)
    ch.basic_consume(queue=queue_name, on_message_callback=callback_func)

    ch.start_consuming()


def callback_mapper(arg):
    callback_select = {
        "login": auth_callback,
        "register": auth_callback,
        "activate": auth_callback,
        "rss_feed_update": rss_feed_callback,
        "refresh": auth_callback,
        "logout": auth_callback,
        "logout_all": auth_callback,
        "selected_logout": auth_callback,
    }
    return callback_select[arg]


def auth_callback(ch, method, properties, body):
    body = json.loads(body)
    user = CustomUser.objects.get(username=body["username"])
    try:
        with transaction.atomic():
            create_user_activity(user, body)
            routing_key = body["routing_key"]
            if routing_key in settings.AUTH_ALLOWED_NOTIFICATION:
                notification_id = create_auth_notification(user, body)

    except Exception as e:
        if properties.priority >= MAX_RETRIES:
            log_data = create_auth_callback_exception_log_data(user, body, method.delivery_tag, e, properties.priority)
            log_data["status"] = "failed"
            del log_data["attempt_on"]
            logger.critical(json.dumps(log_data))
        else:
            publish(body, priority=properties.priority + 1)
            log_data = create_auth_callback_exception_log_data(user, body, method.delivery_tag, e, properties.priority)
            logger.error(json.dumps(log_data))
    else:
        broadcast_notification.delay(notification_id, body["unique_id"])
        log_data = create_auth_callback_log_data(user, body, method.delivery_tag, properties.priority)
        logger.info(json.dumps(log_data))
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("done")


def create_auth_callback_log_data(user, body, delivery_tag, priority):
    return {
        "unique_id": body["unique_id"],
        'user_id': str(user.id),
        'delivery_tag': delivery_tag,
        'event': f"consumer.auth_callback.{body['routing_key']}",
        "attempt": priority,
        "status": "success"
    }


def create_auth_callback_exception_log_data(user, body, delivery_tag, e, priority):
    return {
        "unique_id": body["unique_id"],
        'user_id': str(user.id),
        'user_agent': body["user_agent"],
        'delivery_tag': delivery_tag,
        'exception_type': e.__class__.__name__,
        'exception_message': str(e),
        'exception_traceback': traceback.format_exc(),
        'event': f"consumer.auth_callback.{body['routing_key']}",
        'exception': True,
        "attempt_on": priority,
        "status": "retry"
    }


def rss_feed_callback(ch, method, properties, body):
    body = json.loads(body)

    channel_id = body["channel_id"]
    try:
        with transaction.atomic():
            content_type_obj = ContentType.objects.get(model="channel")
            # qs = Bookmark.objects.filter(content_type=content_type_obj, object_id=channel_id)
            qs = Bookmark.objects.select_related("user").filter(content_type=content_type_obj, object_id=channel_id)
            if qs.exists():
                notification_id = create_rss_feed_notification(body, qs)

    except Exception as e:
        if properties.priority >= MAX_RETRIES:
            log_data = create_rss_feed_callback_exception_log_data(body, method.delivery_tag, e, properties.priority)
            log_data["status"] = "failed"
            del log_data["attempt_on"]
            logger.critical(json.dumps(log_data))
        else:
            log_data = create_rss_feed_callback_exception_log_data(body, method.delivery_tag, e, properties.priority)
            logger.critical(json.dumps(log_data))
    else:
        broadcast_notification.delay(notification_id, body["unique_id"])
        log_data = create_rss_feed_callback_log_data(body, method.delivery_tag, properties.priority)
        logger.info(json.dumps(log_data))
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def create_rss_feed_callback_log_data(body, delivery_tag, priority):
    return {
        "unique_id": body["unique_id"],
        'delivery_tag': delivery_tag,
        "channel_id": body["channel_id"],
        'event': f"consumer.rss_feed_callback.{body['routing_key']}",
        "attempt_on": priority,
        "status": "success"
    }


def create_rss_feed_callback_exception_log_data(body, delivery_tag, e, priority):
    return {
        "unique_id": body["unique_id"],
        "channel_id": body["channel_id"],
        'user_agent': body["user_agent"],
        'delivery_tag': delivery_tag,
        'exception_type': e.__class__.__name__,
        'exception_message': str(e),
        'exception_traceback': traceback.format_exc(),
        'event': f"consumer.rss_feed_callback.{body['routing_key']}",
        'exception': True,
        "attempt_on": priority,
        "status": "retry"
    }


def create_auth_notification(user, body):
    with transaction.atomic():
        notification = Notification.objects.create(notification=body["message"], action=body["routing_key"])
        UserNotifications.objects.create(user=user, notification=notification)

    # broadcast_notification.delay(notification.id, body["unique_id"])
    log_data = create_auth_notification_log_data(user, body)
    logger.info(json.dumps(log_data))
    return notification.id


def create_auth_notification_log_data(user, body):
    return {
        "unique_id": body["unique_id"],
        'user_id': str(user.id),
        'user_agent': body["user_agent"],
        'event': f"consumer.notification.{body['routing_key']}",
        "status": "success"
    }


def create_rss_feed_notification(body, qs):
    with transaction.atomic():
        notification = Notification.objects.create(notification=body["message"], action=body["routing_key"])
        items = (UserNotifications(user=item.user, notification=notification) for item in qs)
        UserNotifications.objects.bulk_create(items)

    # broadcast_notification.delay(notification.id, body["unique_id"])
    log_data = create_rss_feed_notification_log_data(body)
    logger.info(json.dumps(log_data))
    return notification.id


def create_rss_feed_notification_log_data(body):
    return {
        "unique_id": body["unique_id"],
        "channel_id": body["channel_id"],
        'event': f"consumer.notification.{body['routing_key']}",
        "status": "success"
    }


def create_user_activity(user, body):
    with transaction.atomic():
        user_last_activity_qs = UserLastActivity.objects.filter(user=user)
        if not user_last_activity_qs.exists():
            UserLastActivity.objects.create(user=user, action=body["routing_key"], user_agent=body["user_agent"],
                                            ip=body["ip"])
        else:
            user_last_activity_qs.update(action=body["routing_key"], user_agent=body["user_agent"],
                                         ip=body["ip"])

    log_data = create_user_activity_notification_log_data(user, body)
    logger.info(json.dumps(log_data))


def create_user_activity_notification_log_data(user, body):
    return {
        "unique_id": body["unique_id"],
        'user_id': str(user.id),
        'user_agent': body["user_agent"],
        'event': f"consumer.user_activity.{body['routing_key']}",
        "status": "success"
    }
