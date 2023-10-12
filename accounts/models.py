import json

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db import models
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .manager import CustomManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=25, verbose_name=_("Username"), unique=True)
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name=_("Joined Date"), auto_now_add=True, editable=False)
    last_modify = models.DateTimeField(verbose_name=_("Last Modify"), auto_now=True, editable=False)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ["email"]

    objects = CustomManager()

    def __str__(self):
        return self.username


class Notification(models.Model):
    notification = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    is_sent = models.BooleanField(default=False)
    action = models.CharField(null=True, blank=True)
    broadcast_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.notification}"


@receiver(post_save, sender=Notification)
def save_notification_handler(sender, instance, created, **kwargs):
    # from .tasks import broadcast_notification
    if created and instance.broadcast_on:
        schedule, _ = CrontabSchedule.objects.get_or_create(minute=instance.broadcast_on.minute,
                                                            hour=instance.broadcast_on.hour,
                                                            day_of_month=instance.broadcast_on.day,
                                                            month_of_year=instance.broadcast_on.month)
        task = PeriodicTask.objects.create(crontab=schedule,
                                           name=f"broadcast notification {instance.id}",
                                           task="accounts.tasks.broadcast_notification",
                                           args=json.dumps([instance.id]),
                                           one_off=True,
                                           )
        # broadcast_notification.apply_async((instance.id,), eta=instance.broadcast_on)

    elif not created and not instance.is_sent:
        periodic_task_qs = PeriodicTask.objects.filter(name=f"broadcast notification {instance.id}")
        if periodic_task_qs.exists():
            periodic_task_qs.delete()
        if instance.broadcast_on:
            schedule, _ = CrontabSchedule.objects.get_or_create(minute=instance.broadcast_on.minute,
                                                                hour=instance.broadcast_on.hour,
                                                                day_of_month=instance.broadcast_on.day,
                                                                month_of_year=instance.broadcast_on.month)
            task = PeriodicTask.objects.create(clocked=schedule,
                                               name=f"broadcast notification {instance.id}",
                                               task="accounts.tasks.broadcast_notification",
                                               args=json.dumps([instance.id]),
                                               one_off=True,
                                               )
            # broadcast_notification.apply_async((instance.id,), eta=instance.broadcast_on)


@receiver(post_delete, sender=Notification)
def delete_notification_handler(sender, instance, **kwargs):
    if instance.broadcast_on:
        periodic_task_qs = PeriodicTask.objects.filter(name=f"broadcast notification {instance.id}")
        if periodic_task_qs.exists():
            periodic_task_qs.delete()


class UserNotifications(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    notification = models.ForeignKey(Notification, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user} has notification: {self.notification}"


class UserLastActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    action = models.CharField(max_length=50)
    user_agent = models.TextField(null=True, blank=True)
    ip = models.IPAddressField(null=True, blank=True)
