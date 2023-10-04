from django.core.management.base import BaseCommand
from accounts.consumer import start_login_consumer, start_register_consumer, start_rss_feed_update_consumer
import threading


class Command(BaseCommand):
    help = 'Launches Consumer for login message : RabbitMQ'

    def handle(self, *args, **options):
        # start_register_consumer()
        # start_login_consumer()
        # start_rss_feed_update_consumer()

        thread1 = threading.Thread(target=start_register_consumer)
        thread2 = threading.Thread(target=start_login_consumer)
        thread3 = threading.Thread(target=start_rss_feed_update_consumer)

        thread1.start()
        thread2.start()
        thread3.start()
