from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class ExpiredAccessTokenError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Access Token Has Been Expired')
    default_code = 'expired_access_token'


class ExpiredRefreshTokenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('Refresh Token Has Been Expired, Please Login Again')
    default_code = 'expired_refresh_token'


class InvalidTokenError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Invalid Token, Please Login Again')
    default_code = 'invalid_token'


class NotActiveUserError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('User Is Not Active')
    default_code = 'not_active_user'


class UserNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('User Not Found')
    default_code = 'user_not_found'


class AuthorizationHeaderError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Authorization Header Is Not Set In Request Header')
    default_code = 'no_authorization_header'


class NotFoundAccessToken(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Access Token Not Found In Authorization Header')
    default_code = 'no_access_token'


class NotFoundPrefix(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Token Prefix Not Found In Authorization Header')
    default_code = 'no_prefix'


class CommonError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('An error occurred')
    default_code = 'error'
