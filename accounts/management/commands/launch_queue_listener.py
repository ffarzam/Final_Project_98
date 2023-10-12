from django.core.management.base import BaseCommand
import threading
from config import settings
from accounts.consumer import start_consumers


class Command(BaseCommand):
    help = 'Launches Consumer for login message : RabbitMQ'

    def handle(self, *args, **options):
        for item in settings.queue_name_list:
            threading.Thread(target=start_consumers, args=[item]).start()
