from django_redis import get_redis_connection


class HitCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lst = ['admin', "visitors_count", "status", "create", "update"]

        path_blacklist = list(filter(lambda x: request.path.startswith(f"/{x}"), lst))
        if len(path_blacklist) == 0:
            conn = get_redis_connection('hit_count')

            ip_addr = get_client_ip_address(request)

            conn.sadd('ip', ip_addr)

        response = self.get_response(request)

        return response


def get_client_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')
    return ip_addr
