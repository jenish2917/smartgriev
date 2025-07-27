from django.urls import path, include
from . import views

urlpatterns = [
    # Dashboard and Analytics
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('real-time-updates/', views.real_time_updates, name='real-time-updates'),
    
    # Metrics
    path('metrics/', views.RealTimeMetricsView.as_view(), name='real-time-metrics'),
    path('performance/', views.PerformanceMetricsView.as_view(), name='performance-metrics'),
    path('activity/', views.UserActivityView.as_view(), name='user-activity'),
    
    # Alerts
    path('alerts/rules/', views.AlertRuleView.as_view(), name='alert-rules'),
    path('alerts/instances/', views.AlertInstanceView.as_view(), name='alert-instances'),
    path('alerts/<int:alert_id>/resolve/', views.mark_alert_resolved, name='mark-alert-resolved'),
    
    # Export and Health
    path('export/', views.export_analytics_data, name='export-analytics'),
    path('health/', views.system_health, name='system-health'),
]
