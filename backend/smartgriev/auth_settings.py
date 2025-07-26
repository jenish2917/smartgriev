# Authentication Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your app password
DEFAULT_FROM_EMAIL = 'SmartGriev <noreply@smartgriev.com>'

# Frontend URL for email verification and password reset
FRONTEND_URL = 'http://localhost:3000'  # Change in production

# SMS Settings (Twilio)
TWILIO_ACCOUNT_SID = 'your-account-sid'  # Replace with your Twilio SID
TWILIO_AUTH_TOKEN = 'your-auth-token'    # Replace with your Twilio token
TWILIO_FROM_NUMBER = '+1234567890'       # Replace with your Twilio number

# Verification Settings
VERIFICATION_TOKEN_EXPIRY = 24  # hours
OTP_EXPIRY = 10  # minutes
MAX_OTP_ATTEMPTS = 3
