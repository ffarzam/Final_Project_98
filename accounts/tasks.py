import logging
from uuid import uuid4

from celery import shared_task

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import CustomUser, UserNotifications, Notification
from .utils import send_email

from config.celery import CustomTask

logger = logging.getLogger('elastic_logger')


class BaseTaskWithRetry(CustomTask):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True
    task_time_limit = 60


@shared_task(bind=True, base=BaseTaskWithRetry)
def send_reset_password_link(self, current_site, user_id, unique_id):
    self.request.args = list(map(str, self.request.args))
    uidb64 = urlsafe_base64_encode(force_bytes(user_id))
    user = CustomUser.objects.get(id=user_id)
    token = PasswordResetTokenGenerator().make_token(user)
    relative_link = reverse("accounts:password_reset", kwargs={"uidb64": uidb64, "token": token})
    absolute_link = f"http://{current_site}{relative_link}"
    email_body = f"Hello {user.username},\n Use the link below to reset your password:\n {absolute_link}"
    email_data = {"email_body": email_body, "to_email": [user.email], "email_subject": "Reset The Password"}
    send_email(email_data)


@shared_task(bind=True, base=BaseTaskWithRetry)
def broadcast_notification(self, notification_id, unique_id=None):
    if unique_id is None:
        unique_id = uuid4().hex
        self.request.args.append(unique_id)
    self.request.args = list(map(str, self.request.args))
    notification = Notification.objects.get(id=notification_id)
    user_notifications = UserNotifications.objects.filter(notification=notification)
    if user_notifications.exists():
        users = (user_notification.user for user_notification in user_notifications)
    else:
        users = CustomUser.objects.filter(is_staff=False).iterator()

    users_emails = (user.email for user in users)
    email_body = f"Hello Dear User,\n {notification.notification}"
    email_data = {"email_body": email_body, "to_email": users_emails, "email_subject": " "}
    send_email(email_data)
    notification.is_sent = True
    notification.save()
