# Generated by Django 4.2.5 on 2023-10-16 07:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feeder', '0002_alter_category_options_alter_channel_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='episode',
            options={'verbose_name': 'Podcast Episode', 'verbose_name_plural': 'Podcasts Episodes'},
        ),
    ]
