# Generated by Django 4.2.5 on 2023-10-12 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_userlastactivity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='is_sent',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='userlastactivity',
            name='ip',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]
