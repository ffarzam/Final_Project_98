from django_redis import get_redis_connection


class HitCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (not request.path.startswith('/admin')
                and not request.path.startswith("/visitors_count")
                and not request.path.startswith("/status")
                and not request.path.startswith("/create")
                and not request.path.startswith("/update")):

            conn = get_redis_connection('hit_count')

            ip_addr = get_client_ip_address(request)

            conn.sadd('ip', ip_addr)

        # number_of_visitors = conn.scard("ip")

        # request.META.get('HTTP_REMOTE_ADDR', None)
        # request.META.get('HTTP_X_REAL_IP', None)
        # request.META.get('HTTP_X_FORWARDED_FOR', None)
        # request.META.get('REMOTE_ADDR', None)
        # request.META.get('X_REAL_IP', None)
        # request.META.get('X_FORWARDED_FOR', None)

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


