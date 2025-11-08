from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification list and details
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    
    # Notification actions
    path('<int:pk>/read/', views.mark_notification_read, name='mark-read'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete-notification'),
    path('unread-count/', views.unread_count, name='unread-count'),
    
    # Notification preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),
    
    # Send notification (admin/system)
    path('send/', views.send_notification, name='send-notification'),
    
    # SMS endpoints
    path('sms/send/', views.send_sms_notification, name='send-sms'),
    path('sms/status/', views.sms_service_status, name='sms-status'),
]
