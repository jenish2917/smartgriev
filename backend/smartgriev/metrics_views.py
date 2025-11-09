"""
Prometheus Metrics Endpoints for SmartGriev
Exposes custom application metrics
"""
from django.http import HttpResponse
from django.views import View
from prometheus_client import (
    Counter, Gauge, Histogram, Info,
    generate_latest, CONTENT_TYPE_LATEST, REGISTRY
)
from django.contrib.auth import get_user_model
from complaints.models import Complaint
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Custom application metrics
complaints_total = Counter(
    'smartgriev_complaints_total',
    'Total number of complaints',
    ['status', 'category']
)

complaints_by_status = Gauge(
    'smartgriev_complaints_by_status',
    'Current number of complaints by status',
    ['status']
)

complaint_resolution_time = Histogram(
    'smartgriev_complaint_resolution_time_hours',
    'Complaint resolution time in hours',
    buckets=[1, 6, 12, 24, 48, 72, 168, 336]  # 1h to 2 weeks
)

active_users = Gauge(
    'smartgriev_active_users',
    'Number of active users (logged in last 24h)'
)

database_queries = Histogram(
    'smartgriev_database_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

app_info = Info(
    'smartgriev_app',
    'SmartGriev application information'
)


class MetricsView(View):
    """
    Prometheus metrics endpoint
    
    Exposes metrics at /metrics for Prometheus scraping
    """
    
    def get(self, request):
        """Generate and return Prometheus metrics"""
        # Update real-time metrics before export
        self._update_metrics()
        
        # Generate metrics in Prometheus format
        metrics = generate_latest(REGISTRY)
        return HttpResponse(
            metrics,
            content_type=CONTENT_TYPE_LATEST
        )
    
    def _update_metrics(self):
        """Update gauges with current values"""
        try:
            # Update complaint counts by status
            for status_choice in ['submitted', 'pending', 'in_progress', 'resolved', 'rejected']:
                count = Complaint.objects.filter(status=status_choice).count()
                complaints_by_status.labels(status=status_choice).set(count)
            
            # Update active users (last 24 hours)
            yesterday = timezone.now() - timedelta(hours=24)
            active_count = User.objects.filter(last_login__gte=yesterday).count()
            active_users.set(active_count)
            
            # Set app info
            from django.conf import settings
            app_info.info({
                'version': getattr(settings, 'APP_VERSION', '1.0.0'),
                'environment': getattr(settings, 'ENVIRONMENT', 'development'),
                'django_version': __import__('django').get_version(),
            })
            
        except Exception as e:
            # Log error but don't fail the metrics endpoint
            import logging
            logging.error(f"Error updating metrics: {e}")


class HealthCheckView(View):
    """
    Health check endpoint for load balancers and monitoring
    
    Returns 200 OK if application is healthy
    """
    
    def get(self, request):
        """Perform health checks"""
        health_status = {
            'status': 'healthy',
            'checks': {}
        }
        
        # Check database
        try:
            User.objects.count()
            health_status['checks']['database'] = 'ok'
        except Exception as e:
            health_status['checks']['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check cache (gracefully handle if not configured)
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['checks']['cache'] = 'ok'
            else:
                health_status['checks']['cache'] = 'degraded: cache read failed'
                # Don't mark as unhealthy, cache is not critical
        except Exception as e:
            health_status['checks']['cache'] = f'not_configured: {str(e)}'
            # Cache failure is not critical for app health
        
        # Return appropriate status code (200 if db is ok, even if cache fails)
        status_code = 200 if health_status['checks'].get('database') == 'ok' else 503
        
        from django.http import JsonResponse
        return JsonResponse(health_status, status=status_code)
