# Generated by Django 4.2.5 on 2023-10-16 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookmark',
            options={'verbose_name': 'Bookmark', 'verbose_name_plural': 'Bookmark'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'Comment', 'verbose_name_plural': 'Comments'},
        ),
        migrations.AlterModelOptions(
            name='episodetrace',
            options={'verbose_name': 'Episode Trace', 'verbose_name_plural': 'Episodes Trace'},
        ),
        migrations.AlterModelOptions(
            name='like',
            options={'verbose_name': 'Like', 'verbose_name_plural': 'Likes'},
        ),
        migrations.AlterModelOptions(
            name='newsread',
            options={'verbose_name': 'Read News', 'verbose_name_plural': 'Read News'},
        ),
        migrations.AlterModelOptions(
            name='recommendation',
            options={'verbose_name': 'Recommendation', 'verbose_name_plural': 'Recommendations'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Subscription', 'verbose_name_plural': 'Subscriptions'},
        ),
    ]