# Generated by Django 4.2.5 on 2023-10-05 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_notification_broadcast_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='action',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='broadcast_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
