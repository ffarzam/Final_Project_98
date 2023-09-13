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


class UserLogin(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_identifier = serializer.validated_data.get('user_identifier')
        password = serializer.validated_data.get('password')
        user = AuthBackend().authenticate(request, username=user_identifier, password=password)
        if user is None:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        jti = jti_maker(request, user.id)
        access_token = generate_access_token(user.id, jti)
        refresh_token = generate_refresh_token(user.id, jti, settings.REDIS_AUTH_TTL)

        caches['auth'].set(jti, 0)

        data = {
            "access": access_token,
            "refresh": refresh_token,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class RefreshToken(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        payload = request.auth
        jti = payload["jti"]
        caches['auth'].delete(jti)

        user_identifier = payload["user_identifier"]
        user = find_user(user_identifier)
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        jti = jti_maker(request, user.id)
        access_token = generate_access_token(user.id, jti)
        refresh_token = generate_refresh_token(user.id, jti, settings.REDIS_AUTH_TTL)
        caches['auth'].set(jti, 0, timeout=settings.REDIS_AUTH_TTL, version=None)

        data = {
            "access": access_token,
            "refresh": refresh_token
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            payload = request.auth
            jti = payload["jti"]
            caches['auth'].delete(jti)

            return Response({"message": "Successful Logout"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


