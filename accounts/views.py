from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import authenticate
from django.core.cache import caches

from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .custom_middleware import get_client_ip_address
from .models import CustomUser
from .serializers import UserRegisterSerializer, UserLoginSerializer, ProfileSerializer, ChangePasswordSerializer, \
    UpdateUserSerializer, PasswordResetSerializer, SetNewPasswordSerializer
from .authentication import AccessTokenAuthentication, RefreshTokenAuthentication
from .tasks import send_reset_password_link
from .utils import generate_refresh_token, generate_access_token, jti_maker, cache_key_setter, cache_value_setter, \
    cache_key_parser
from .publisher import publish


# Create your views here.


class UserRegister(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

    def post(self, request):
        ser_data = self.serializer_class(data=request.POST)
        if ser_data.is_valid():
            ser_data.create(ser_data.validated_data)
            username = ser_data.validated_data["username"]
            info = {
                "username": username,
                "message": f"User with {username} successfully registered",
                "routing_key": "register",
                "user_agent": request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
                "ip": get_client_ip_address(request) or " "
            }
            publish(info)
            user = CustomUser.objects.get(username=username)
            request.user = user
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
        info = {
            "username": user.username,
            "message": f"New Login Record With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')}",
            "routing_key": "login",
            "user_agent": request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
            "ip": get_client_ip_address(request) or " "

        }
        publish(info)
        request.user = user
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
        info = {
            "username": user.username,
            "message": f"New Login Record With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')}",
            "routing_key": "refresh",
            "user_agent": request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
            "ip": get_client_ip_address(request) or " "
        }
        publish(info)

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
            info = {
                "username": user.username,
                "message": f"Logout Record With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')}",
                "routing_key": "logout",
                "user_agent": request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
                "ip": get_client_ip_address(request) or " "
            }
            publish(info)

            return Response({"message": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckAllActiveLogin(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        active_login_data = []
        for key, value in caches['auth'].get_many(caches['auth'].keys(f'user_{user.id} || *')).items():
            jti = cache_key_parser(key)[1]

            active_login_data.append({
                "jti": jti,
                "user_agent": value,
            })

        return Response(active_login_data, status=status.HTTP_200_OK)


class LogoutAll(APIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        caches['auth'].delete_many(caches['auth'].keys(f'user_{user.id} || *'))
        info = {
            "username": user.username,
            "message": f"Logout-all Record With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')}",
            "routing_key": "logout_all",
            "user_agent": request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
            "ip": get_client_ip_address(request) or " "
        }
        publish(info)

        return Response({"message": "All accounts logged out"}, status=status.HTTP_200_OK)


class SelectedLogout(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        jti = request.data.get("jti")
        user_agent = caches['auth'].get(f'user_{user.id} || {jti}')
        caches['auth'].delete(f'user_{user.id} || {jti}')
        info = {
            "username": user.username,
            "message": f"Logout Record With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')} for session {user_agent}",
            "routing_key": "selected_logout",
            "user_agent": request.META.get('HTTP_USER_AGENT', 'UNKNOWN'),
            "ip": get_client_ip_address(request) or " "
        }
        publish(info)

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
    http_method_names = ["patch"]
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def patch(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.serializer_class(instance, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Password has been successfully updated"})


class UpdateProfileView(UpdateAPIView):
    http_method_names = ["patch"]
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = CustomUser.objects.filter(email=email)
        if not user.exists():
            return Response({'message': "This email doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        user = user.get()
        current_site = get_current_site(request).domain
        send_reset_password_link.delay(current_site, user.id)

        return Response({"message": "A link Was Sent To You To Reset Your Password"}, status=status.HTTP_200_OK)


class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"kwargs": kwargs})
        serializer.is_valid(raise_exception=True)

        uidb64 = kwargs["uibd64"]

        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(id=user_id)
        password = serializer.validated_data['password']
        user.set_password(password)
        user.save()
        return Response({"success": "Password Reset Done"}, status=status.HTTP_200_OK)
