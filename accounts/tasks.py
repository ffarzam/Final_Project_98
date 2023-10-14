import logging
from uuid import uuid4

from celery import shared_task

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import get_template
from django.urls import reverse, resolve
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


@shared_task(bind=True, base=BaseTaskWithRetry)
def send_link(self, current_site, user_id, app_name, url_name, unique_id):
    self.request.args = list(map(str, self.request.args))
    uidb64 = urlsafe_base64_encode(force_bytes(user_id))
    user = CustomUser.objects.get(id=user_id)
    token = PasswordResetTokenGenerator().make_token(user)
    url_name = url_mapper(url_name)
    relative_link = reverse(f"{app_name}:{url_name}", kwargs={"uidb64": uidb64, "token": token})
    absolute_link = f"http://{current_site}{relative_link}"
    template_path = email_html_template_path(url_name)
    context = email_html_template_context(url_name, user, absolute_link)
    subject = get_email_subject(url_name)
    email_body = get_template(template_path).render(context)
    email_data = {"email_body": email_body, "to_email": [user.email],
                  "email_subject": subject, "content_subtype": "html"}
    send_email(email_data)


def url_mapper(url_name):
    url = {
        "register": "verify_account",
        "password_reset_request": "password_reset"
    }
    return url[url_name]


def email_html_template_path(url_name):
    html = {
        "verify_account": "email_templates/accounts/verify_account.html",
        "password_reset": "email_templates/accounts/password_reset.html"
    }
    return html[url_name]


def email_html_template_context(url_name, user, absolute_link, *args, **kwargs):
    html_context = {
        "verify_account": {"user": user, "absolute_link": absolute_link},
        "password_reset": {"user": user, "absolute_link": absolute_link}
    }
    return html_context[url_name]


def get_email_subject(url_name):
    email_subject = {
        "verify_account": "Account Verification",
        "password_reset": "Reset The Password"
    }
    return email_subject[url_name]
