# Generated by Django 4.2.5 on 2023-10-07 14:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_notification_action_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='broadcast_on',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 7, 14, 32, 7, 576391)),
        ),
        migrations.AlterField(
            model_name='notification',
            name='is_sent',
            field=models.BooleanField(default=False),
        ),
    ]