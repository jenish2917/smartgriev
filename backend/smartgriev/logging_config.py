"""
Structured Logging Configuration for SmartGriev
JSON-formatted logs with contextual information
"""
import structlog
import logging
from pythonjsonlogger import jsonlogger
from django.conf import settings


def configure_structured_logging():
    """
    Configure structlog for JSON-formatted structured logging
    
    Call this function during Django app initialization
    """
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(settings, 'LOG_LEVEL', 'INFO'),
    )
    
    # Add JSON formatter for production
    if getattr(settings, 'USE_JSON_LOGGING', False):
        log_handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        log_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.addHandler(log_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # Add JSON rendering for production
            structlog.processors.JSONRenderer() if getattr(settings, 'USE_JSON_LOGGING', False)
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """
    Get a structured logger instance
    
    Usage:
        logger = get_logger(__name__)
        logger.info("user_login", user_id=123, ip="192.168.1.1")
    """
    return structlog.get_logger(name)
