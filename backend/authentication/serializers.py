from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'mobile', 'address', 'language', 'is_officer')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'mobile': {'required': False},  # Made optional
            'address': {'required': False},
            'language': {'required': False},
        }

    def create(self, validated_data):
        # Remove confirm_password from validated_data as it's not a model field
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])