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
            'Analytics': '/api/analytics/',
            'ML Experiments': '/api/ml-experiments/',
            'Geospatial': '/api/geospatial/',
            'Notifications': '/api/notifications/',
            'Admin': '/admin/',
        },
        'auth': {
            'token_obtain': '/api/token/',
            'token_refresh': '/api/token/refresh/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('authentication.urls')),
    path('api/complaints/', include('complaints.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/ml/', include('mlmodels.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/ml-experiments/', include('ml_experiments.urls')),
    path('api/geospatial/', include('geospatial.urls')),
    path('api/notifications/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
