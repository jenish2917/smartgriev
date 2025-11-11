"""
SmartGriev Application Initialization
Configure observability on startup
"""

# This will make Celery app discoverable
from .celery import app as celery_app

__all__ = ('celery_app',)

# Initialize observability
try:
    from .logging_config import configure_structured_logging
    # from .telemetry import configure_opentelemetry
    
    # Configure structured logging
    configure_structured_logging()
    
    # Configure OpenTelemetry (if enabled in settings)
    # Note: settings import must be done after Django setup
    # Temporarily disabled due to Redis import issues
    # import django
    # if django.VERSION[0] >= 3:
    #     from django.conf import settings
    #     if getattr(settings, 'ENABLE_OPENTELEMETRY', False):
    #         configure_opentelemetry()
except Exception as e:
    import logging
    logging.warning(f"Failed to initialize observability: {e}")
