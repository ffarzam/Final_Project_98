# Generated by Django 4.2.5 on 2023-09-27 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='last_item_guid',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
