import json
import pika

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from .models import CustomUser, UserNotifications, Notification

from interactions.models import Bookmark

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


def callback(ch, method, property, body):
    body = json.loads(body)
    user = CustomUser.objects.get(username=body["username"])
    notification = Notification.objects.create(notification=body["message"], action=body["routing_key"])
    UserNotifications.objects.create(user=user, notification=notification)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_login_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    ch = connection.channel()

    ch.queue_declare(queue="login")
    ch.basic_consume(queue="login", on_message_callback=callback)

    ch.start_consuming()


def start_register_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    ch = connection.channel()

    ch.queue_declare(queue="register")
    ch.basic_consume(queue="register", on_message_callback=callback)

    ch.start_consuming()


def rss_feed_callback(ch, method, property, body):
    body = json.loads(body)

    channel_id = body["channel_id"]
    content_type_obj = ContentType.objects.get(model="channel")
    qs = Bookmark.objects.filter(content_type=content_type_obj, object_id=channel_id)
    notification = Notification.objects.create(notification=body["message"])
    for item in qs:
        user = CustomUser.objects.get(id=item.user.id)
        UserNotifications.objects.create(user=user, notification=notification)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_rss_feed_update_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    ch = connection.channel()

    ch.queue_declare(queue="rss_feed")
    ch.basic_consume(queue="rss_feed", on_message_callback=rss_feed_callback)

    ch.start_consuming()
