"""
Django settings for smartgriev project.
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GDAL Configuration for PostGIS
if os.name == 'nt':  # Windows
    OSGEO4W = r"C:\Program Files\PostgreSQL\15"
    if os.path.exists(OSGEO4W):
        os.environ['OSGEO4W_ROOT'] = OSGEO4W
        os.environ['GDAL_DATA'] = os.path.join(OSGEO4W, 'share', 'gdal')
        os.environ['PROJ_LIB'] = os.path.join(OSGEO4W, 'share', 'proj')
        os.environ['PATH'] = os.path.join(OSGEO4W, 'bin') + ';' + os.environ['PATH']

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# Set this in your .env file for production
# For example: DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# Allow all hosts for global access (development only)
ALLOWED_HOSTS = ['*']  # Allow global access

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.gis',  # PostGIS support - disabled until GDAL is installed
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',  # JWT token blacklist for rotation
    'corsheaders',
    # Local apps - Core Functional Features
    'authentication',        # ✅ WORKING - User authentication & language preferences
    'complaints',           # ✅ WORKING - Complaint management system  
    'chatbot',              # ✅ WORKING - AI chatbot for complaint submission
    'machine_learning',     # ✅ WORKING - ML models, OCR, AI classification
    'notifications',        # ✅ WORKING - Notification system
    'analytics',            # ✅ WORKING - Analytics and metrics
    # Advanced features (disabled - have missing dependencies)
    # 'geospatial',         # ❌ Requires GDAL installation (advanced GIS feature)
    # 'storages',           # ❌ Cloud storage - not needed for local development
    # 'channels',           # ❌ WebSockets - not needed for current features
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'analytics.middleware.UserActivityMiddleware',  # Track user activity - temporarily disabled
    # 'analytics.middleware.SecurityHeadersMiddleware',  # Add security headers - temporarily disabled
    # 'analytics.middleware.CacheControlMiddleware',  # Cache control - temporarily disabled
]

ROOT_URLCONF = 'smartgriev.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smartgriev.wsgi.application'

# Database
# Switch between SQLite (development) and PostgreSQL (production) using environment variable
USE_POSTGRES = os.getenv('USE_POSTGRES', 'False').lower() == 'true'

if USE_POSTGRES:
    # PostgreSQL Configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',  # Standard PostgreSQL backend
            'NAME': os.getenv('POSTGRES_DB', 'smartgriev'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': 600,  # Connection pooling
            'OPTIONS': {
                'connect_timeout': 10,
                'options': '-c statement_timeout=30000',  # 30 second query timeout
            }
        }
    }
else:
    # SQLite Configuration (Development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT Settings - Enhanced for Production
SIMPLE_JWT = {
    # Token Lifetimes (from PDF spec)
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Short-lived access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Long-lived refresh token
    
    # Token Rotation & Blacklisting
    'ROTATE_REFRESH_TOKENS': True,                   # Issue new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': True,                # Blacklist old refresh tokens
    'UPDATE_LAST_LOGIN': True,                       # Update last_login on token refresh
    
    # Security Headers
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # Cookie Settings for HttpOnly
    'AUTH_COOKIE': 'access_token',                   # Access token cookie name
    'AUTH_COOKIE_REFRESH': 'refresh_token',          # Refresh token cookie name
    'AUTH_COOKIE_SECURE': True,                      # HTTPS only in production
    'AUTH_COOKIE_HTTP_ONLY': True,                   # Prevent XSS attacks
    'AUTH_COOKIE_PATH': '/',
    'AUTH_COOKIE_SAMESITE': 'Lax',                   # CSRF protection
    
    # Algorithm & Signing
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    
    # Token Claims
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS settings - Allow global access
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins for global access
CORS_ALLOW_CREDENTIALS = True

# Redis settings
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

# Celery settings
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# S3 Settings (if using AWS)
if os.getenv('USE_S3', 'False') == 'True':
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'ap-south-1')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@smartgriev.com')

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# WebSocket (Channels) configuration
ASGI_APPLICATION = 'smartgriev.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [({REDIS_HOST}, {REDIS_PORT})],
        },
    },
}

# SMS/Notification settings
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Firebase settings for push notifications
# For better security, store your Firebase credentials in a JSON file
# and set the GOOGLE_APPLICATION_CREDENTIALS environment variable
# to the path of the JSON file.
# Example:
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
#
# The firebase-admin library will automatically pick up the credentials.
# You can remove the FIREBASE_CONFIG dictionary below if you use this method.
FIREBASE_CONFIG = {
    'type': os.getenv('FIREBASE_TYPE'),
    'project_id': os.getenv('FIREBASE_PROJECT_ID'),
    'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    'private_key': os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\n', '\n'),
    'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
    'client_id': os.getenv('FIREBASE_CLIENT_ID'),
    'auth_uri': os.getenv('FIREBASE_AUTH_URI'),
    'token_uri': os.getenv('FIREBASE_TOKEN_URI'),
}

# ML Models directory
MODELS_ROOT = BASE_DIR / 'ml_models'

# Analytics settings
ANALYTICS_RETENTION_DAYS = int(os.getenv('ANALYTICS_RETENTION_DAYS', 90))
ENABLE_REAL_TIME_METRICS = os.getenv('ENABLE_REAL_TIME_METRICS', 'True') == 'True'
DASHBOARD_CACHE_TIMEOUT = int(os.getenv('DASHBOARD_CACHE_TIMEOUT', 900))

# Performance monitoring
ENABLE_PERFORMANCE_MONITORING = os.getenv('ENABLE_PERFORMANCE_MONITORING', 'True') == 'True'
SLOW_REQUEST_THRESHOLD = float(os.getenv('SLOW_REQUEST_THRESHOLD', 1.0))  # seconds

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# GPS Validation Settings
GPS_ACCURACY_THRESHOLD = float(os.getenv('GPS_ACCURACY_THRESHOLD', 50))
MIN_LAT = float(os.getenv('MIN_LAT', 6.0))
MAX_LAT = float(os.getenv('MAX_LAT', 37.6))
MIN_LON = float(os.getenv('MIN_LON', 68.7))
MAX_LON = float(os.getenv('MAX_LON', 97.25))

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'analytics': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'machine_learning': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# AI/ML Configuration
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', 'AIzaSyA6jaqmJJOF69GjtYGz8d7lZ2DLg9nImWk')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyA6jaqmJJOF69GjtYGz8d7lZ2DLg9nImWk')  # Same as Google AI
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GOOGLE_AI_API_KEY:
    import warnings
    warnings.warn("GOOGLE_AI_API_KEY not set. Some AI features may be limited.")

if not GROQ_API_KEY:
    import warnings
    warnings.warn("GROQ_API_KEY not set. AI features will use fallback methods.")

# Complaint Classification Settings
COMPLAINT_CLASSIFICATION = {
    'ENABLED': True,
    'AUTO_CLASSIFY': True,
    'MODEL': 'llama-3.1-8b-instant',  # Updated to latest supported Groq model
    'CONFIDENCE_THRESHOLD': 0.7
}