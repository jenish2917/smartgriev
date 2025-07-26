from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import VerificationToken
import re

User = get_user_model()

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate(self, attrs):
        token_obj = VerificationToken.objects.filter(
            token=attrs['token'],
            token_type='email',
            is_used=False
        ).first()

        if not token_obj or not token_obj.is_valid():
            raise serializers.ValidationError("Invalid or expired token")
        
        attrs['token_obj'] = token_obj
        return attrs

class MobileVerificationSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    otp = serializers.CharField(required=False)

    def validate_mobile(self, value):
        # Validate Indian mobile number format
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError(
                "Please enter a valid Indian mobile number"
            )
        return value

class TwoFactorEnableSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)

class TwoFactorVerifySerializer(serializers.Serializer):
    code = serializers.CharField()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No user found with this email address"
            )
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })

        token_obj = VerificationToken.objects.filter(
            token=attrs['token'],
            token_type='password',
            is_used=False
        ).first()

        if not token_obj or not token_obj.is_valid():
            raise serializers.ValidationError({
                "token": "Invalid or expired token"
            })

        attrs['token_obj'] = token_obj
        return attrs
