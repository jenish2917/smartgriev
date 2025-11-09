#!/usr/bin/env python
"""
Lightweight Django server for chatbot only - bypasses heavy ML models
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Minimal Django settings for chatbot only
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='dev-key-for-chatbot-only',
        ALLOWED_HOSTS=['*'],
        ROOT_URLCONF='chatbot_urls',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'rest_framework',
            'corsheaders',
            'chatbot',
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.common.CommonMiddleware',
        ],
        # CORS settings
        CORS_ALLOW_ALL_ORIGINS=True,
        CORS_ALLOW_CREDENTIALS=True,
        # REST Framework
        REST_FRAMEWORK={
            'DEFAULT_RENDERER_CLASSES': [
                'rest_framework.renderers.JSONRenderer',
            ],
        },
        # Database (required but minimal)
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3',
            }
        },
        # Google API Keys
        GOOGLE_API_KEY='AIzaSyA6jaqmJJOF69GjtYGz8d7lZ2DLg9nImWk',
        GEMINI_API_KEY='AIzaSyA6jaqmJJOF69GjtYGz8d7lZ2DLg9nImWk',
    )
    django.setup()

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '__main__')
    execute_from_command_line(['manage.py', 'runserver', '8000', '--noreload'])
