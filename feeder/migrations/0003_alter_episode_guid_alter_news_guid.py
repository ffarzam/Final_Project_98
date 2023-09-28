# Generated by Django 4.2.5 on 2023-09-27 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeder', '0002_channel_last_item_guid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='guid',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='guid',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]