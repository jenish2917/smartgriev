from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    # Field aliases for frontend compatibility
    mobile_number = serializers.CharField(source='mobile', required=False, allow_blank=True)
    language_preference = serializers.CharField(source='language', required=False, allow_blank=True)
    role = serializers.SerializerMethodField()
    is_email_verified = serializers.BooleanField(read_only=True, default=False)
    is_mobile_verified = serializers.BooleanField(read_only=True, default=False)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    updated_at = serializers.DateTimeField(source='last_login', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 
                  'mobile', 'mobile_number', 'address', 'language', 'language_preference', 
                  'is_officer', 'role', 'is_email_verified', 'is_mobile_verified', 'created_at', 'updated_at')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'mobile': {'required': False, 'write_only': True},  # Made optional and write-only
            'address': {'required': False},
            'language': {'required': False, 'write_only': True},  # Made write-only
            'is_officer': {'write_only': True},  # Write-only, use role for reading
        }
    
    def get_role(self, obj):
        """Map is_officer boolean to role string"""
        if obj.is_superuser:
            return 'admin'
        elif obj.is_officer:
            return 'official'
        else:
            return 'citizen'

    def create(self, validated_data):
        # Remove confirm_password from validated_data as it's not a model field
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class UpdateLanguageSerializer(serializers.Serializer):
    """Serializer for updating user's preferred language"""
    language = serializers.ChoiceField(
        choices=[
            ('en', 'English'),
            ('hi', 'Hindi'),
            ('bn', 'Bengali'),
            ('te', 'Telugu'),
            ('mr', 'Marathi'),
            ('ta', 'Tamil'),
            ('gu', 'Gujarati'),
            ('kn', 'Kannada'),
            ('ml', 'Malayalam'),
            ('pa', 'Punjabi'),
            ('or', 'Odia'),
            ('as', 'Assamese'),
        ],
        required=True,
        help_text="User's preferred language for interface"
    )