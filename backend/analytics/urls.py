from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard and overview
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('trends/', views.complaint_trends, name='complaint-trends'),
    path('departments/', views.department_analytics, name='department-analytics'),
    
    # User activity
    path('activity/', views.user_activity_log, name='user-activity-log'),
    path('activity/log/', views.log_user_activity, name='log-activity'),
    
    # Statistics endpoints
    path('complaint-stats/', views.ComplaintStatsListView.as_view(), name='complaint-stats-list'),
    path('department-metrics/', views.DepartmentMetricsListView.as_view(), name='department-metrics-list'),
]
