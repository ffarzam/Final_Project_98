from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class ExpiredAccessTokenError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Access Token Has Been Expired')
    default_code = 'expired_access_token'

