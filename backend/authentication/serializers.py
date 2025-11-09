from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Allow login with email or username.

    This looks for an 'email' field in the request body or checks the
    provided 'username' for an email pattern and resolves to the actual
    username before delegating to the base serializer.
    """

    # allow clients to POST {email, password} instead of username
    email = serializers.EmailField(required=False, write_only=True)

    def validate(self, attrs):
        request = self.context.get('request')

        # If the frontend sent 'email' instead of 'username', use that.
        if request is not None:
            if 'email' in request.data and not attrs.get(self.username_field):
                attrs[self.username_field] = request.data.get('email')

        username_val = attrs.get(self.username_field, '') or ''
        username_val = username_val.strip()

        # If the value looks like an email, try to map to username
        if '@' in username_val:
            try:
                user = User.objects.get(email__iexact=username_val)
                attrs[self.username_field] = user.get_username()
            except User.DoesNotExist:
                # no user with this email; leave and let base serializer handle it
                attrs[self.username_field] = username_val
        else:
            # Not an email. First try exact username match (case-insensitive).
            try:
                user = User.objects.get(username__iexact=username_val)
                attrs[self.username_field] = user.get_username()
            except User.DoesNotExist:
                # Try matching username with spaces removed (frontend may send 'John Doe')
                compact = username_val.replace(' ', '')
                if compact and compact != username_val:
                    try:
                        user = User.objects.get(username__iexact=compact)
                        attrs[self.username_field] = user.get_username()
                    except User.DoesNotExist:
                        # Last resort: try email field matching again
                        try:
                            user = User.objects.get(email__iexact=username_val)
                            attrs[self.username_field] = user.get_username()
                        except User.DoesNotExist:
                            # leave as provided; base serializer will return the no active account message
                            attrs[self.username_field] = username_val

        return super().validate(attrs)
