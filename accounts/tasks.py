from celery import shared_task, Task

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import CustomUser
from .utils import send_email


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True
    task_concurrency = 4,
    worker_prefetch_multiplier = 1
    task_time_limit = 120


@shared_task(base=BaseTaskWithRetry)
def send_reset_password_link(current_site, user_id):
    uidb64 = urlsafe_base64_encode(force_bytes(user_id))
    user = CustomUser.objects.get(id=user_id)
    token = PasswordResetTokenGenerator().make_token(user)
    relative_link = reverse("password_reset", kwargs={"uidb64": uidb64, "token": token})
    absolute_link = f"http://{current_site}{relative_link}"
    email_body = f"Hello {user.username},\n Use the link below to reset your password:\n {absolute_link}"
    email_data = {"email_body": email_body, "to_email": user.email, "email_subject": "Reset The Password"}
    send_email(email_data)
