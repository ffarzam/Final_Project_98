from abc import ABC, abstractmethod
import jwt
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import CustomUser
from .utils import decode_jwt
from django.core.cache import caches


class AbstractTokenAuthentication(ABC, BaseAuthentication):

    @abstractmethod
    def authenticate(self, request):
        ...

    @staticmethod
    def get_payload(token):

        payload = decode_jwt(token)
        return payload

    @staticmethod
    def get_user_from_payload(payload):
        user_id = payload.get('user_id')
        if user_id is None:
            raise exceptions.PermissionDenied('User id not found')

        try:
            user = CustomUser.objects.get(id=user_id)
        except:
            raise exceptions.NotFound('User Not Found')

        if not user.is_active:
            raise exceptions.PermissionDenied('User is inactive')

        return user

    @staticmethod
    def validate_jti_token(payload):
        jti = payload.get('jti')
        if jti not in caches['auth'].keys('*'):
            raise exceptions.PermissionDenied(
                'Invalid refresh token, please login again.')


class AccessTokenAuthentication(AbstractTokenAuthentication):
    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def authenticate_header(self, request):
        return self.authentication_header_prefix

    def authenticate(self, request):

        authorization_header = self.get_authorization_header(request)

        self.check_prefix_exists(authorization_header)

        access_token = self.get_access_token(authorization_header)

        try:
            payload = self.get_payload(access_token)
        except jwt.ExpiredSignatureError:
            raise exceptions.NotAuthenticated('Access Token Expired')
        except Exception as e:
            raise exceptions.ParseError(str(e))

        self.validate_jti_token(payload)

        user = self.get_user_from_payload(payload)

        return user, payload

    def get_authorization_header(self, request):
        authorization_header = request.headers.get(self.authentication_header_name)
        if not authorization_header:
            raise exceptions.NotFound('Authorization Header was not set')
        return authorization_header

    def check_prefix_exists(self, authorization_header):
        prefix = authorization_header.split(' ')[0]
        if prefix != self.authentication_header_prefix:
            raise exceptions.NotFound('Token Prefix Not Found')

    @staticmethod
    def get_access_token(authorization_header):
        access_token = authorization_header.split(' ')[1]
        if access_token:
            return access_token
        raise exceptions.NotFound('Access Token Not Found')


class RefreshTokenAuthentication(AbstractTokenAuthentication):

    def authenticate(self, request):
        refresh_token = request.data.get("refresh_token")

        try:
            payload = self.get_payload(refresh_token)
        except jwt.ExpiredSignatureError:
            raise exceptions.PermissionDenied(
                'Expired refresh token, please login again.')
        except Exception as e:
            raise exceptions.ParseError(str(e))

        self.validate_jti_token(payload)
        user = self.get_user_from_payload(payload)

        return user, payload


class AuthBackend(ModelBackend):

    def authenticate(self, request, user_identifier=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=user_identifier)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=user_identifier)
            except CustomUser.DoesNotExist:
                return None

        if user.check_password(password) and user.is_active:
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
