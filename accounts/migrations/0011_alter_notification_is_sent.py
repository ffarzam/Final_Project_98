# Generated by Django 4.2.5 on 2023-10-09 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_notification_is_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='is_sent',
            field=models.BooleanField(default=False),
        ),
    ]
