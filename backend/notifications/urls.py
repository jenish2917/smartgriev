from django.urls import path
from . import views

urlpatterns = [
    # Notification templates
    path('templates/', views.NotificationTemplateView.as_view(), name='notification-templates'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView.as_view(), name='template-detail'),
    
    # Notification rules
    path('rules/', views.NotificationRuleView.as_view(), name='notification-rules'),
    path('rules/<int:pk>/', views.NotificationRuleDetailView.as_view(), name='rule-detail'),
    
    # Notification queue
    path('queue/', views.NotificationQueueView.as_view(), name='notification-queue'),
    
    # User preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    path('preferences/<int:pk>/', views.NotificationPreferenceDetailView.as_view(), name='user-preferences'),
    
    # Delivery logs
    path('logs/', views.NotificationLogView.as_view(), name='notification-logs'),
    
    # Device tracking
    path('devices/', views.DeviceTrackingView.as_view(), name='device-tracking'),
    
    # Send notification manually
    path('send/', views.send_notification, name='send-notification'),
    
    # Statistics
    path('stats/', views.notification_stats, name='notification-stats'),
]
