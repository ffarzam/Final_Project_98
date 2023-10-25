from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate
from django.core.cache import caches
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import CustomUser
from .serializers import UserRegisterSerializer, UserLoginSerializer, ProfileSerializer, ChangePasswordSerializer, \
    UpdateUserSerializer, PasswordResetSerializer, SetNewPasswordSerializer, AccountVerificationSerializer, \
    VerifyAccountResetSerializer
from .authentication import AccessTokenAuthentication, RefreshTokenAuthentication
from .tasks import send_link
from .utils import cache_key_parser, publisher, set_token

from config.custom_throttle import ResetPasswordRateThrottle, VerifyAccountRateThrottle, SetPasswordRateThrottle
from config.settings import LANGUAGE_CODE

from Permissions import IsSuperuser


# Create your views here.


class UserRegister(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.POST)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        request.user = user
        current_site = get_current_site(request).domain
        send_link.delay(current_site, user.id, request.resolver_match.app_name, request.resolver_match.url_name,
                        request.META.get("HTTP_ACCEPT_LANGUAGE", LANGUAGE_CODE), request.unique_id)

        message = f"User with id {user.id} successfully registered"
        routing_key = "register"
        publisher(request, user, message, routing_key)

        return Response({'message': _("Registered successfully, activation link was sent to your email"),
                         "data": serializer.data},
                        status=status.HTTP_201_CREATED)


class VerifyAccountRequestView(APIView):
    throttle_classes = [VerifyAccountRateThrottle]
    serializer_class = VerifyAccountResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        request.user = user
        if user.is_account_enable:
            return Response({"message": _("Your account has already activated")}, status=status.HTTP_200_OK)
        current_site = get_current_site(request).domain

        send_link.delay(current_site, user.id, request.resolver_match.app_name, request.resolver_match.url_name,
                        request.META.get("HTTP_ACCEPT_LANGUAGE", LANGUAGE_CODE), request.unique_id)
        return Response({"message": _("A link Was Sent To You To Activate Your Account")}, status=status.HTTP_200_OK)


class VerifyAccount(APIView):
    throttle_classes = [VerifyAccountRateThrottle]
    serializer_class = AccountVerificationSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"kwargs": kwargs})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        request.user = user
        if user.is_account_enable:
            return Response({"message": _("Your account has already activated")}, status=status.HTTP_200_OK)

        user.is_account_enable = True
        user.save()

        message = f"Account for user {user.id} has been successfully activated"
        routing_key = "activate"
        publisher(request, user, message, routing_key)

        return Response({"success": _("Your account has been activated successfully")}, status=status.HTTP_200_OK)


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
            return Response({'message': _('Invalid Username or Password')}, status=status.HTTP_400_BAD_REQUEST)
        elif not user.is_active:
            return Response({'message': _("User is Banned")}, status=status.HTTP_404_NOT_FOUND)
        elif not user.is_account_enable:
            return Response({'message': _("User hasn't activated his/her account yet")}, status=455)

        access_token, refresh_token = set_token(request, user, caches)
        data = {"access": access_token, "refresh": refresh_token}

        message = f"New Login Record for user {user.id} With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')}"
        routing_key = "login"
        publisher(request, user, message, routing_key)

        request.user = user

        return Response({"message": _("Logged in successfully"), "data": data}, status=status.HTTP_201_CREATED)


class RefreshToken(APIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        payload = request.auth

        jti = payload["jti"]
        caches['auth'].delete(f'user_{user.id} || {jti}')

        access_token, refresh_token = set_token(request, user, caches)
        data = {"access": access_token, "refresh": refresh_token}

        message = f"Re_Login Record for user {user.id} With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')}"
        routing_key = "refresh"
        publisher(request, user, message, routing_key)

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
            message = f"Logout Record for user {user.id} With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')}"
            routing_key = "logout"
            publisher(request, user, message, routing_key)
            return Response({"message": _("Logged out successfully")}, status=status.HTTP_200_OK)
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
        message = f"Logout-all Record for user {user.id} With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')}"
        routing_key = "logout_all"
        publisher(request, user, message, routing_key)
        return Response({"message": _("All accounts logged out")}, status=status.HTTP_200_OK)


class SelectedLogout(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        jti = request.data.get("jti")
        user_agent = caches['auth'].get(f'user_{user.id} || {jti}')
        caches['auth'].delete(f'user_{user.id} || {jti}')

        message = f"Selected logout Record for user {user.id} With {request.META.get('HTTP_USER_AGENT', 'UNKNOWN')} for session {user_agent}"
        routing_key = "selected_logout"
        publisher(request, user, message, routing_key)

        return Response({"message": _("Chosen account was successfully logged out")}, status=status.HTTP_200_OK)


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
        caches['auth'].delete_many(caches['auth'].keys(f'user_{instance.id} || *'))
        return Response({"message": _("Password has been successfully updated")})


class UpdateProfileView(UpdateAPIView):
    http_method_names = ["patch"]
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(GenericAPIView):
    throttle_classes = [ResetPasswordRateThrottle]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        request.user = user
        current_site = get_current_site(request).domain
        send_link.delay(current_site, user.id, request.resolver_match.app_name, request.resolver_match.url_name,
                        request.META.get("HTTP_ACCEPT_LANGUAGE", LANGUAGE_CODE), request.unique_id)
        return Response({"message": _("A link Was Sent To You To Reset Your Password")}, status=status.HTTP_200_OK)


class SetNewPasswordView(GenericAPIView):
    throttle_classes = [SetPasswordRateThrottle]
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"kwargs": kwargs})
        serializer.is_valid(raise_exception=True)

        user, password = serializer.validated_data
        user.set_password(password)
        user.save()
        request.user = user
        return Response({"success": _("Password Reset Done")}, status=status.HTTP_200_OK)


class DisableAccount(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsSuperuser,)

    def get(self, request, user_spec):

        if user_spec.isnumeric():
            user = CustomUser.objects.filter(id=user_spec)
        else:
            user = CustomUser.objects.filter(Q(username=user_spec) | Q(email=user_spec))

        if user.exists():
            user = user.get()
            user.is_active = False
            user.save()
            caches['auth'].delete_many(caches['auth'].keys(f'user_{user.id} || *'))

            return Response({"message": _("All accounts logged out and disabled")}, status=status.HTTP_200_OK)

        return Response({"message": _("No user with this specification was found")}, status=status.HTTP_404_NOT_FOUND)


class EnableAccount(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsSuperuser,)

    def get(self, request, user_spec):
        if user_spec.isnumeric():
            user = CustomUser.objects.filter(id=user_spec)
        else:
            user = CustomUser.objects.filter(Q(username=user_spec) | Q(email=user_spec))

        if user.exists():
            user = user.get()
            user.is_active = True
            user.save()

            return Response({"message": _("User account is enabled")}, status=status.HTTP_200_OK)

        return Response({"message": _("No user with this specification was found")}, status=status.HTTP_404_NOT_FOUND)
