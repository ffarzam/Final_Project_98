import json
import logging

from django.http import JsonResponse

from rest_framework import status

from uuid import uuid4

logger = logging.getLogger('elastic_logger')


class ElasticAPILoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        unique_id = uuid4().hex
        setattr(request, "unique_id", unique_id)
        path_blacklist = get_blacklist(request)
        response = self.get_response(request)
        if len(path_blacklist) == 0 and not request.META.get("exception", False):
            user = find_user(request)
            log_data = api_log_data(request, response, user)
            logger.info(json.dumps(log_data))

        return response

    def process_exception(self, request, exception):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        path_blacklist = get_blacklist(request)
        if len(path_blacklist) == 0:
            log_data = exception_log_data(request, exception)
            log_data['response_status'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            logger.error(json.dumps(log_data))
            request.META["exception"] = True
        return JsonResponse({"error": str(exception)}, status=status_code)


def get_client_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')
    return ip_addr


def find_user(request):
    user = None
    if request.user.is_authenticated:
        user = request.user
    return user


def api_log_data(request, response, user):
    return {
        "unique_id": request.unique_id,
        'request_method': request.method,
        'request_path': request.path,
        'request_ip': get_client_ip_address(request) or ' ',
        'request_user_agent': request.META.get('HTTP_USER_AGENT', ' '),
        'user_id': str(user.id) if user else " ",
        'response_status': response.status_code,
        'event': f"api.{request.resolver_match.app_names[0]}.{request.resolver_match.url_name}"
    }


def exception_log_data(request, exception):
    return {
        "unique_id": request.unique_id,
        'request_method': request.method,
        'request_path': request.path,
        'request_ip': get_client_ip_address(request) or ' ',
        'request_user_agent': request.META.get('HTTP_USER_AGENT', ' '),
        'exception_type': exception.__class__.__name__,
        'exception_message': str(exception),
        'event': f"api.{request.resolver_match.app_names[0]}.{request.resolver_match.url_name}",
        'exception': True,
    }


def get_blacklist(request):
    lst = ['admin', "status", "schema", "favicon"]
    path_blacklist = list(filter(lambda x: request.path.startswith(f"/{x}"), lst))
    return path_blacklist
