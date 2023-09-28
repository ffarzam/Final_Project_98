# Generated by Django 4.2.5 on 2023-09-28 14:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feeder', '0004_alter_channel_last_item_guid'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('interactions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsRead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feeder.news')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EpisodeTrace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seconds_listened', models.PositiveIntegerField()),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feeder.episode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
