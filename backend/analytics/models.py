# Real-time Analytics and Dashboard System
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class AnalyticsDashboard(models.Model):
    """Real-time analytics dashboard configuration"""
    DASHBOARD_TYPES = [
        ('citizen', 'Citizen Dashboard'),
        ('officer', 'Officer Dashboard'), 
        ('admin', 'Admin Dashboard'),
        ('department', 'Department Dashboard')
    ]
    
    name = models.CharField(max_length=100)
    dashboard_type = models.CharField(max_length=20, choices=DASHBOARD_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'name')

class Widget(models.Model):
    dashboard = models.ForeignKey(AnalyticsDashboard, on_delete=models.CASCADE, related_name='widgets')
    # Add fields for your widget configuration, e.g.:
    # name = models.CharField(max_length=100)
    # type = models.CharField(max_length=50)
    # config = models.JSONField(default=dict)

class Layout(models.Model):
    dashboard = models.OneToOneField(AnalyticsDashboard, on_delete=models.CASCADE, related_name='layout')
    # Add fields for your layout settings, e.g.:
    # positions = models.JSONField(default=dict)

class RealTimeMetrics(models.Model):
    """Store real-time metrics for dashboard display"""
    METRIC_TYPES = [
        ('complaint_count', 'Complaint Count'),
        ('resolution_rate', 'Resolution Rate'),
        ('avg_response_time', 'Average Response Time'),
        ('satisfaction_score', 'Satisfaction Score'),
        ('department_performance', 'Department Performance'),
        ('geographic_distribution', 'Geographic Distribution'),
        ('sentiment_trends', 'Sentiment Trends'),
        ('chatbot_effectiveness', 'Chatbot Effectiveness')
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    department = models.ForeignKey('complaints.Department', null=True, blank=True, on_delete=models.CASCADE)
    time_period = models.CharField(max_length=20)  # hourly, daily, weekly, monthly
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['department', 'metric_type']),
        ]

class MetricValue(models.Model):
    metric = models.OneToOneField(RealTimeMetrics, on_delete=models.CASCADE, related_name='metric_value')
    # Add fields for your metric value, e.g.:
    # value = models.FloatField()
    # series = models.JSONField(default=list)

class MetricMetadata(models.Model):
    metric = models.OneToOneField(RealTimeMetrics, on_delete=models.CASCADE, related_name='metadata')
    # Add fields for your metadata, e.g.:
    # unit = models.CharField(max_length=20)
    # description = models.TextField()

class UserActivity(models.Model):
    """Track user activity for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    endpoint = models.CharField(max_length=255, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    duration = models.FloatField(null=True)  # Request duration in seconds
    response_code = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
        ]

class ActivityMetadata(models.Model):
    activity = models.OneToOneField(UserActivity, on_delete=models.CASCADE, related_name='metadata')
    # Add fields for your metadata, e.g.:
    # device = models.CharField(max_length=50)
    # browser = models.CharField(max_length=50)

class PerformanceMetrics(models.Model):
    """System performance metrics"""
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    server_node = models.CharField(max_length=50, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
        ]

class PerformanceMetadata(models.Model):
    metric = models.OneToOneField(PerformanceMetrics, on_delete=models.CASCADE, related_name='metadata')
    # Add fields for your metadata, e.g.:
    # unit = models.CharField(max_length=20)
    # description = models.TextField()

class NotificationChannel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # Add fields for your notification channel, e.g.:
    # type = models.CharField(max_length=20)
    # config = models.JSONField(default=dict)

class AlertRule(models.Model):
    """Define alert rules for monitoring"""
    CONDITION_TYPES = [
        ('threshold', 'Threshold'),
        ('percentage_change', 'Percentage Change'),
        ('anomaly', 'Anomaly Detection')
    ]
    
    name = models.CharField(max_length=100)
    metric_type = models.CharField(max_length=50)
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES)
    threshold_value = models.FloatField(null=True)
    comparison_operator = models.CharField(max_length=10)  # >, <, >=, <=, ==
    is_active = models.BooleanField(default=True)
    notification_channels = models.ManyToManyField(NotificationChannel)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class AlertInstance(models.Model):
    """Alert instances when rules are triggered"""
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    triggered_value = models.FloatField()
    message = models.TextField()
    severity = models.CharField(max_length=20, default='medium')
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True)
    triggered_at = models.DateTimeField(auto_now_add=True)

class AlertMetadata(models.Model):
    alert = models.OneToOneField(AlertInstance, on_delete=models.CASCADE, related_name='metadata')
    # Add fields for your metadata, e.g.:
    # affected_users = models.IntegerField()
    # related_complaints = models.ManyToManyField('complaints.Complaint')