from datetime import datetime

from elasticsearch import Elasticsearch
from django.conf import settings


class ElasticAPILoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        log_data = {
            'timestamp': datetime.now(),
            'request_method': request.method,
            'request_path': request.path,
            'request_ip': get_client_ip_address(request),
            'request_user_agent': request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
        }
        response = self.get_response(request)

        log_data['user_id'] = request.user.id if request.user.is_authenticated else None
        log_data['response_status'] = response.status_code
        es = Elasticsearch(settings.RABBITMQ_HOS)
        es.index(index='api_logs', document=log_data)
        return response


def get_client_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')
    return ip_addr
