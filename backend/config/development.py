"""
Development Configuration
Extends base configuration with development-specific settings
"""

from .base import *

# Override settings for development
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_development.sqlite3',
    }
}

# Development cache (dummy cache for faster development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['grievance_system']['level'] = 'DEBUG'

# Django Debug Toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Disable HTTPS requirements for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
