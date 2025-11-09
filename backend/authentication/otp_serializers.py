"""
OTP Authentication Serializers for SmartGriev
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    method = serializers.ChoiceField(choices=['email', 'mobile'], default='email')


class VerifyOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    otp = serializers.CharField(min_length=6, max_length=6)
    method = serializers.ChoiceField(choices=['email', 'mobile'], default='email')


class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()
