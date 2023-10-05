from datetime import datetime

from elasticsearch import Elasticsearch

from .models import CustomUser
from .utils import decode_jwt
from django.conf import settings


class ElasticAPILoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.es = Elasticsearch(f'http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}')

    def __call__(self, request):
        log_data = {
            'timestamp': datetime.now(),
            'request_method': request.method,
            'request_path': request.path,
            'request_ip': get_client_ip_address(request),
            'request_user_agent': request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
        }

        response = self.get_response(request)
        user = find_user(request, response)

        log_data['user_id'] = user.id if user else None
        log_data['username'] = user.username if user else None
        log_data['response_status'] = response.status_code

        self.es.index(index='test_logs', document=log_data)

        return response

    def process_exception(self, request, exception):
        log_data = {
            'timestamp': datetime.now(),
            'request_method': request.method,
            'request_path': request.path,
            'request_ip': get_client_ip_address(request),
            'request_user_agent': request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
            'exception_type': exception.__class__.__name__,
            'exception_message': exception.message if hasattr(exception, "message") else str(exception),
        }
        self.es.index(index='exception_logs', document=log_data)


def get_client_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')
    return ip_addr


def find_user(request, response):
    user = None
    if request.user.is_authenticated:
        user = request.user
    elif refresh_token := response.data.get("refresh"):
        payload = decode_jwt(refresh_token)
        user = CustomUser.objects.get(id=payload.get("user_id"))
    elif username := response.data.get("username"):
        user = CustomUser.objects.get(username=username)

    return user
