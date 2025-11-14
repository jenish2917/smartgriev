"""
URL configuration for smartgriev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .metrics_views import MetricsView, HealthCheckView
from smartgriev.metrics_views import MetricsView, HealthCheckView

# Load custom admin configuration to unregister unwanted models
from . import admin as custom_admin

@api_view(['GET'])
def api_root(request):
    """API Root - SmartGriev System"""
    return Response({
        'message': 'Welcome to SmartGriev API',
        'version': '1.0.0',
        'endpoints': {
            'Authentication': '/api/auth/',
            'Complaints': '/api/complaints/',
            'Chatbot': '/api/chatbot/',
            'ML Models': '/api/ml/',
            'Notifications': '/api/notifications/',
            'Analytics': '/api/analytics/',
            'Admin': '/admin/',
        },
        'auth': {
            'token_obtain': '/api/token/',
            'token_refresh': '/api/token/refresh/',
        }
    })

@api_view(['GET'])
def api_config(request):
    """API Configuration endpoint for frontend"""
    protocol = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    ws_protocol = 'wss' if request.is_secure() else 'ws'
    
    return Response({
        'success': True,
        'config': {
            'apiUrl': f'{protocol}://{host}/api',
            'websocketUrl': f'{ws_protocol}://{host}/ws',
            'version': '1.0.0',
            'features': {
                'voice': True,
                'chatbot': True,
                'ml': True,
                'analytics': True,
                'notifications': True,
                'geospatial': False,  # Disabled due to GDAL dependency
            },
            'limits': {
                'maxFileSize': 10 * 1024 * 1024,  # 10MB
                'maxFilesPerComplaint': 5,
                'allowedFileTypes': ['image/jpeg', 'image/png', 'image/gif', 'audio/mp3', 'audio/wav', 'application/pdf'],
            }
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    
    # Configuration endpoint
    path('api/config/', api_config, name='api_config'),
    
    # Observability endpoints
    path('metrics', MetricsView.as_view(), name='prometheus_metrics'),
    path('health', HealthCheckView.as_view(), name='health_check'),
    
    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Core API Endpoints - Fully Functional
    path('api/auth/', include('authentication.urls')),        # ✅ Login, Register, Language
    path('api/complaints/', include('complaints.urls')),      # ✅ Complaint CRUD
    path('api/chatbot/', include('chatbot.urls')),           # ✅ AI Chatbot
    # path('api/ml/', include('machine_learning.urls')),       # ⚠️ Temporarily disabled - PyTorch import issue
    path('api/notifications/', include('notifications.urls')), # ✅ Notifications
    path('api/analytics/', include('analytics.urls')),       # ✅ Analytics & Metrics
    # Advanced features (disabled - have dependency issues)
    # path('api/geospatial/', include('geospatial.urls')),   # ❌ Requires GDAL
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
