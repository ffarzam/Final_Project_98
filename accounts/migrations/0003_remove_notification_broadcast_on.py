# Generated by Django 4.2.5 on 2023-10-03 19:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_notification_usernotifications'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='broadcast_on',
        ),
    ]
