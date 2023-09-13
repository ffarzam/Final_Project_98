from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from .serializers import UserRegisterSerializer, UserLoginSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .authentication import AuthBackend, CustomJWTAuthentication, find_user
from .utils import generate_refresh_token, generate_access_token, jti_maker
from django.conf import settings
from django.core.cache import cache, caches


# Create your views here.


class UserRegister(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        ser_data = UserRegisterSerializer(data=request.POST)
        if ser_data.is_valid():
            ser_data.create(ser_data.validated_data)
            return Response(ser_data.data, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


