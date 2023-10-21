from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers

from .models import CustomUser


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2')

    def create(self, validated_data):
        del validated_data['password2']
        return CustomUser.objects.create_user(**validated_data)

    def validate_username(self, value):
        if len(value) < 6:
            raise serializers.ValidationError('Username must be more than 6 characters long')

        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        if data['email'] == data['username']:
            raise serializers.ValidationError("Email and username can't be same")
        if data['password'] == data['username']:
            raise serializers.ValidationError("Password and username can't be same")
        if data['password'] == data['email']:
            raise serializers.ValidationError("Password and email can't be same")

        return data


class UserLoginSerializer(serializers.Serializer):
    user_identifier = serializers.CharField()
    password = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = '__all__' #???
        exclude = ["password", "groups", "user_permissions"]  # ???


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('old_password', 'password', 'password2')

    def validate(self, data):
        user = self.context['request'].user
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        if user.email == data['password']:
            raise serializers.ValidationError("Password and your email can't be same")
        if data['password'] == user.username:
            raise serializers.ValidationError("Password and your username can't be same")

        return super().validate(data)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def validate(self, data):
        user = self.context['request'].user
        if data['email'] == data['username']:
            raise serializers.ValidationError("Email and username can't be same")
        if user.check_password(data['username']):
            raise serializers.ValidationError("Password and username can't be same")
        if user.check_password(data['email']):
            raise serializers.ValidationError("Password and email can't be same")
        return super().validate(data)

    def validate_username(self, value):
        if len(value) < 6:
            raise serializers.ValidationError('Username must be more than 6 characters long')
        return value

    def update(self, instance, validated_data):

        instance.username = validated_data['username']
        instance.email = validated_data['email']

        instance.save()

        return instance


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data["email"]
        user = CustomUser.objects.filter(email=email)
        if not user.exists():
            raise serializers.ValidationError("This email doesn't exist")
        return user.get()


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('password', 'password2')

    def validate(self, data):

        password = data['password']
        token = self.context.get('kwargs').get("token")
        uidb64 = self.context.get('kwargs').get("uidb64")
        if token is None or uidb64 is None:
            raise serializers.ValidationError("Missing Data")

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)
        except Exception as e:
            raise serializers.ValidationError(str(e))

        if user.email == password:
            raise serializers.ValidationError("Password and your email can't be same")
        if password == user.username:
            raise serializers.ValidationError("Password and your username can't be same")
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is not valid, please request again")

        return user, password


class AccountVerificationSerializer(serializers.Serializer):
    def validate(self, data):

        token = self.context.get('kwargs').get("token")
        uidb64 = self.context.get('kwargs').get("uidb64")
        if token is None or uidb64 is None:
            raise serializers.ValidationError("Missing Data")
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is not valid, please request again")

        return user


class VerifyAccountResetSerializer(PasswordResetSerializer):
    pass
