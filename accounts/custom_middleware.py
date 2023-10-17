import json
import logging
import re
import traceback
from uuid import uuid4

from django.middleware.locale import LocaleMiddleware
from django.utils.translation.trans_real import get_language_from_path, check_for_language, get_languages, \
    get_supported_language_variant, parse_accept_lang_header, language_code_re
from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.http import HttpResponseRedirect
from django.utils import translation

from rest_framework import status

from .utils import get_client_ip_address

logger = logging.getLogger('elastic_logger')


class ElasticAPILoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        unique_id = uuid4().hex
        setattr(request, "unique_id", unique_id)
        path_blacklist = self.get_blacklist(request)
        response = self.get_response(request)
        if len(path_blacklist) == 0 and not request.META.get("exception", False):
            user = self.find_user(request)
            log_data = self.api_log_data(request, response, user)
            logger.info(json.dumps(log_data))

        return response

    def process_exception(self, request, exception):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        path_blacklist = self.get_blacklist(request)
        if len(path_blacklist) == 0:
            log_data = self.exception_log_data(request, exception)
            log_data['response_status'] = status_code
            logger.error(json.dumps(log_data))
            request.META["exception"] = True

    @staticmethod
    def find_user(request):
        user = None
        if request.user.is_authenticated:
            user = request.user
        return user

    @staticmethod
    def api_log_data(request, response, user):
        return {
            "unique_id": request.unique_id,
            'request_method': request.method,
            'request_path': request.path,
            'request_language': getattr(request, "LANGUAGE_CODE"),
            'request_ip': get_client_ip_address(request) or ' ',
            'request_user_agent': request.META.get('HTTP_USER_AGENT', ' '),
            'user_id': str(user.id) if user else " ",
            'response_status': response.status_code,
            'event': f"api.{request.resolver_match.app_names[0]}.{request.resolver_match.url_name}"
            if request.resolver_match and len(request.resolver_match.app_names) != 0
            else " "
        }

    @staticmethod
    def exception_log_data(request, exception):
        return {
            "unique_id": request.unique_id,
            'request_method': request.method,
            'request_path': request.path,
            'request_ip': get_client_ip_address(request) or ' ',
            'request_user_agent': request.META.get('HTTP_USER_AGENT', ' '),
            'exception_type': exception.__class__.__name__,
            'exception_message': str(exception),
            'exception_traceback': traceback.format_exc(),
            'event': f"api.{request.resolver_match.app_names[0]}.{request.resolver_match.url_name}"
            if request.resolver_match and len(request.resolver_match.app_names) != 0
            else " ",
            'exception': True,
        }

    @staticmethod
    def get_blacklist(request):
        lst = ['admin', "status", "schema", "favicon", "rosetta", "i18n"]
        path_blacklist = list(filter(lambda x: re.match(rf"(/..|)/({x})(/.*|)$", request.path), lst))
        return path_blacklist


class CustomLocaleMiddleware(LocaleMiddleware):
    response_redirect_class = HttpResponseRedirect

    def process_request(self, request):
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        (
            i18n_patterns_used,
            prefixed_default_language,
        ) = is_language_prefix_patterns_used(urlconf)
        language = self.get_language_from_request(
            request, check_path=i18n_patterns_used
        )
        language_from_path = translation.get_language_from_path(request.path_info)
        if (
                not language_from_path
                and i18n_patterns_used
                and not prefixed_default_language
                and not language
        ):
            language = settings.LANGUAGE_CODE
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    @staticmethod
    def get_language_from_request(request, check_path=False):

        if check_path:
            lang_code = get_language_from_path(request.path_info)
            if lang_code is not None:
                return lang_code

        lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

        if (
                lang_code is not None
                and lang_code in get_languages()
                and check_for_language(lang_code)
        ):
            return lang_code

        try:
            return get_supported_language_variant(lang_code)
        except LookupError:
            pass

        accept = request.headers.get("Accept-Language", "")
        for accept_lang, unused in parse_accept_lang_header(accept):
            if accept_lang == "*":
                break

            if not language_code_re.search(accept_lang):
                continue

            try:
                return get_supported_language_variant(accept_lang)
            except LookupError:
                continue
        try:
            return get_supported_language_variant(settings.LANGUAGE_CODE)
        except LookupError:

            return settings.LANGUAGE_CODE
