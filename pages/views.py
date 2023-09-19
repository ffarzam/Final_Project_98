from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.

class Status(APIView):

    def get(self, request):
        return Response({"message": "Server is running"}, status=status.HTTP_200_OK)


class VisitorsCount(APIView):

    def get(self, request):
        conn = get_redis_connection('hit_count')
        number_of_visitors = conn.scard("ip")
        return Response({"Visitors Count": number_of_visitors}, status=status.HTTP_200_OK)
