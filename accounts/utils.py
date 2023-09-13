import datetime
import jwt
from django.conf import settings
from uuid import uuid4


def generate_access_token(request, user_id, jti):
    access_token_payload = {
        "token_type": "access",
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=7),
        'iat': datetime.datetime.utcnow(),
        'jti': jti,
        'OS': request.META['OS'],
        'USER_AGENT': request.META['HTTP_USER_AGENT'],
        'USERNAME': request.META['USERNAME']
    }
    access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY, algorithm='HS256')
    return access_token


def generate_refresh_token(request, user_id, jti, ttl):
    refresh_token_payload = {
        "token_type": "refresh",
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl),
        'iat': datetime.datetime.utcnow(),
        'jti': jti,

    }
    refresh_token = jwt.encode(
        refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return refresh_token



