# Generated by Django 4.2.5 on 2023-10-23 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_notification_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_account_enable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]