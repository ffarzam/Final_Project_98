from django.contrib.auth import authenticate
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import CustomUser
from .serializers import UserRegisterSerializer, UserLoginSerializer, ProfileSerializer, ChangePasswordSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .authentication import AccessTokenAuthentication, RefreshTokenAuthentication
from .utils import generate_refresh_token, generate_access_token, jti_maker, cache_key_setter, cache_value_setter, \
    cache_key_or_value_parser
from django.core.cache import caches

from Permissions import UserIsOwner


# Create your views here.


class UserRegister(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

    def post(self, request):
        ser_data = self.serializer_class(data=request.POST)
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
        user = authenticate(request, user_identifier=user_identifier, password=password)
        if user is None:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        jti = jti_maker()
        access_token = generate_access_token(user.id, jti)
        refresh_token = generate_refresh_token(user.id, jti)
        key = cache_key_setter(user.id, jti)
        value = cache_value_setter(request)
        caches['auth'].set(key, value)

        data = {
            "access": access_token,
            "refresh": refresh_token,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class RefreshToken(APIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        payload = request.auth

        jti = payload["jti"]
        caches['auth'].delete(f'user_{user.id} || {jti}')

        jti = jti_maker()
        access_token = generate_access_token(user.id, jti)
        refresh_token = generate_refresh_token(user.id, jti)

        key = cache_key_setter(user.id, jti)
        value = cache_value_setter(request)
        caches['auth'].set(key, value)

        data = {
            "access": access_token,
            "refresh": refresh_token
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            payload = request.auth
            user = request.user
            jti = payload["jti"]
            caches['auth'].delete(f'user_{user.id} || {jti}')

            return Response({"message": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckAllActiveLogin(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        payload = request.auth
        user = request.user
        jti = payload["jti"]

        active_login_data = []
        for value in caches['auth'].get_many(caches['auth'].keys(f'user_{user.id} || *')).values():
            user_agent = cache_key_or_value_parser(value)[0]
            OS_accounts = cache_key_or_value_parser(value)[1]

            active_login_data.append({
                "jti": jti,
                "user_agent": user_agent,
                "OS_accounts": OS_accounts,
            })

        return Response(active_login_data, status=status.HTTP_200_OK)


class LogoutAll(APIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        caches['auth'].delete_many(caches['auth'].keys(f'user_{user.id} || *'))

        return Response({"message": "All accounts logged out"}, status=status.HTTP_200_OK)


class SelectedLogout(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        jti = request.data.get("jti")
        caches['auth'].delete(f'user_{user.id} || {jti}')

        return Response({"message": True}, status=status.HTTP_200_OK)


class ShowProfile(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get(self, request):
        user = request.user
        ser_data = self.serializer_class(user)
        return Response(ser_data.data, status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated, UserIsOwner)
    queryset = CustomUser.objects.all()
    serializer_class = ChangePasswordSerializer
