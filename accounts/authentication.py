import jwt
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import CustomUser
from .utils import decode_jwt
from django.core.cache import caches


class CustomJWTAuthentication(BaseAuthentication):
    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def authenticate_header(self, request):
        return self.authentication_header_prefix

    def authenticate(self, request):

        refresh_token = request.data.get("refresh_token")

        payload = self.get_payload_from_refresh_token(refresh_token)

        user = self.get_user_from_payload(payload)

        # if jti not in map(lambda x: x.decode("utf8"), redis_instance.keys("*")):
        self.validate_refresh_token(payload)

        authorization_header = self.get_authorization_header(request)

        self.check_prefix(authorization_header)

        payload = self.get_payload_from_access_token(authorization_header)

        return user, payload

    @staticmethod
    def get_payload_from_refresh_token(refresh_token):
        try:
            payload = decode_jwt(refresh_token)
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.PermissionDenied(
                'Expired refresh token, please login again.')
        except Exception as e:
            raise exceptions.NotAcceptable(str(e))

    @staticmethod
    def get_user_from_payload(payload):
        user_id = payload.get('user_id')
        if user_id is None:
            raise exceptions.PermissionDenied('User id not found')

        try:
            user = CustomUser.objects.get(id=user_id)
        except:
            raise exceptions.PermissionDenied('User Not Found')

        if not user.is_active:
            raise exceptions.PermissionDenied('User is inactive')

        return user

    @staticmethod
    def validate_refresh_token(payload):
        jti = payload.get('jti')
        if jti not in caches['auth'].keys('*'):  # ???
            raise exceptions.PermissionDenied(
                'Invalid refresh token, please login again.')

    def get_authorization_header(self, request):
        authorization_header = request.headers.get(self.authentication_header_name)
        if not authorization_header:
            raise exceptions.PermissionDenied('Authorization Header was not set')
        return authorization_header

    def check_prefix(self, authorization_header):
        prefix = authorization_header.split(' ')[0]
        if prefix != self.authentication_header_prefix:
            raise exceptions.PermissionDenied('Token prefix missing')

    @staticmethod
    def get_payload_from_access_token(authorization_header):
        try:
            access_token = authorization_header.split(' ')[1]
            payload = decode_jwt(access_token)
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.NotAuthenticated('Access token expired')
        except jwt.InvalidSignatureError as e:
            raise exceptions.NotAcceptable(str(e))


