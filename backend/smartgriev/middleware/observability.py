"""
Observability Middleware for SmartGriev
Provides request tracing, metrics collection, and structured logging
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Configure structured logger
logger = structlog.get_logger(__name__)

# Prometheus metrics
request_count = Counter(
    'smartgriev_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'smartgriev_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'smartgriev_http_active_requests',
    'Number of active HTTP requests'
)

request_size = Histogram(
    'smartgriev_http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

response_size = Histogram(
    'smartgriev_http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)


class ObservabilityMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive observability:
    - Request/response metrics
    - Request tracing
    - Structured logging
    - Performance monitoring
    """
    
    def process_request(self, request):
        """Start request processing and increment metrics"""
        request._start_time = time.time()
        active_requests.inc()
        
        # Log structured request info
        logger.info(
            "request_started",
            method=request.method,
            path=request.path,
            user_id=request.user.id if request.user.is_authenticated else None,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip=self._get_client_ip(request)
        )
        
        return None
    
    def process_response(self, request, response):
        """Process response and record metrics"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Record metrics
            endpoint = self._get_endpoint_name(request)
            status_code = str(response.status_code)
            
            request_count.labels(
                method=request.method,
                endpoint=endpoint,
                status=status_code
            ).inc()
            
            request_duration.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            active_requests.dec()
            
            # Record request/response sizes
            request_size_bytes = int(request.META.get('CONTENT_LENGTH', 0))
            response_size_bytes = len(response.content) if hasattr(response, 'content') else 0
            
            request_size.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(request_size_bytes)
            
            response_size.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(response_size_bytes)
            
            # Structured logging
            log_data = {
                "request_completed": True,
                "method": request.method,
                "path": request.path,
                "status": status_code,
                "duration_ms": round(duration * 1000, 2),
                "request_size_bytes": request_size_bytes,
                "response_size_bytes": response_size_bytes,
                "user_id": request.user.id if request.user.is_authenticated else None,
                "ip": self._get_client_ip(request)
            }
            
            # Log as warning for slow requests
            if duration > getattr(settings, 'SLOW_REQUEST_THRESHOLD', 1.0):
                logger.warning("slow_request", **log_data, slow=True)
            else:
                logger.info("request_completed", **log_data)
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions with context"""
        active_requests.dec()
        
        logger.error(
            "request_exception",
            method=request.method,
            path=request.path,
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            user_id=request.user.id if request.user.is_authenticated else None,
            ip=self._get_client_ip(request)
        )
        
        return None
    
    def _get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_endpoint_name(self, request):
        """Get normalized endpoint name for metrics"""
        path = request.path
        
        # Normalize paths with IDs
        import re
        path = re.sub(r'/\d+/', '/{id}/', path)
        path = re.sub(r'/[0-9a-f-]{36}/', '/{uuid}/', path)
        
        return path[:100]  # Limit length
