import json
import pika

from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


def publish(info):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    ch = connection.channel()
    routing_key = info["routing_key"]
    ch.queue_declare(queue=routing_key)
    properties = pika.BasicProperties(delivery_mode=2)
    ch.basic_publish(exchange='', routing_key=routing_key, body=json.dumps(info),
                     properties=properties)
    connection.close()
