import re

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers

from account.models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')


    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9-]+$', value):
            raise serializers.ValidationError(
                "The username can only contain letters, numbers, and the '-' symbol"
            )

        if len(value) < 3 or len(value) > 15:
            raise serializers.ValidationError(
                "The username must be between 3 and 15 characters long"
            )

        # Reserved usernames
        if value.lower() in settings.RESERVED_NAMES:
            raise serializers.ValidationError(
                "This username is not available for use"
            )

        return value.lower()

    def validate_password(self, value):
        if not re.match(r'^[a-zA-Z0-9-]+$', value):
            raise serializers.ValidationError(
                "The password can only contain letters, numbers, and the '-' symbol"
            )
        if len(value) < 3 or len(value) > 15:
            raise serializers.ValidationError(
                "The password must be between 3 and 15 characters long"
            )
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords didn't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("The username or password is incorrect")
            if not user.is_active:
                raise serializers.ValidationError("User account is inactive")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Username and password required")

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'subdomain', 'max_tunnels')
        read_only_fields = ('id', 'username', 'subdomain', 'max_tunnels', 'created_at')


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('api_key',)
        read_only_fields = ('api_key',)