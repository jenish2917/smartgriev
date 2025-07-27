# Middleware for tracking user activity and performance metrics
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from analytics.models import UserActivity, PerformanceMetrics

class UserActivityMiddleware(MiddlewareMixin):
    """Middleware to track user activity and API usage"""
    
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Skip tracking for static files and admin
        if any(request.path.startswith(path) for path in ['/static/', '/media/', '/admin/static/']):
            return response
        
        # Skip if user is not authenticated for non-API endpoints
        if isinstance(request.user, AnonymousUser) and not request.path.startswith('/api/'):
            return response
        
        try:
            duration = time.time() - getattr(request, '_start_time', time.time())
            
            # Get client IP
            ip_address = self.get_client_ip(request)
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
            
            # Determine activity type
            activity_type = self.get_activity_type(request)
            
            # Create activity record (only for authenticated users)
            if not isinstance(request.user, AnonymousUser):
                UserActivity.objects.create(
                    user=request.user,
                    activity_type=activity_type,
                    endpoint=request.path,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    duration=duration,
                    response_code=response.status_code,
                    metadata={
                        'method': request.method,
                        'query_params': dict(request.GET),
                        'content_type': request.content_type
                    }
                )
            
            # Record performance metrics for slow requests
            if duration > 1.0:  # Log requests taking more than 1 second
                PerformanceMetrics.objects.create(
                    metric_name='slow_request',
                    metric_value=duration,
                    metadata={
                        'endpoint': request.path,
                        'method': request.method,
                        'status_code': response.status_code,
                        'user_id': request.user.id if not isinstance(request.user, AnonymousUser) else None
                    }
                )
                
        except Exception as e:
            # Don't break the request if activity logging fails
            print(f"Failed to log user activity: {e}")
        
        return response
    
    def get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_activity_type(self, request):
        """Determine the activity type based on the request"""
        path = request.path.lower()
        method = request.method.upper()
        
        if '/api/auth/' in path:
            return 'authentication'
        elif '/api/complaints/' in path:
            if method == 'POST':
                return 'complaint_create'
            elif method in ['PUT', 'PATCH']:
                return 'complaint_update'
            else:
                return 'complaint_view'
        elif '/api/chatbot/' in path:
            return 'chatbot_interaction'
        elif '/api/analytics/' in path:
            return 'analytics_view'
        elif '/api/' in path:
            return 'api_call'
        else:
            return 'page_view'

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses"""
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        if not request.path.startswith('/admin/'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' ws: wss:; "
                "frame-ancestors 'none';"
            )
        
        return response

class CacheControlMiddleware(MiddlewareMixin):
    """Add appropriate cache control headers"""
    
    def process_response(self, request, response):
        # API responses should not be cached by default
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Static files can be cached for longer
        elif any(request.path.startswith(path) for path in ['/static/', '/media/']):
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
        
        return response
