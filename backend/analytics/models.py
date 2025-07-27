# Real-time Analytics and Dashboard System
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
import json

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
    widgets = models.JSONField(default=list)  # Widget configurations
    layout = models.JSONField(default=dict)   # Layout settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'name')

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
    metric_value = models.JSONField()  # Flexible storage for different metric types
    department = models.ForeignKey('complaints.Department', null=True, blank=True, on_delete=models.CASCADE)
    time_period = models.CharField(max_length=20)  # hourly, daily, weekly, monthly
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['department', 'metric_type']),
        ]

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
    metadata = models.JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
        ]

class PerformanceMetrics(models.Model):
    """System performance metrics"""
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    server_node = models.CharField(max_length=50, null=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
        ]

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
    notification_channels = models.JSONField(default=list)  # email, slack, webhook
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
    metadata = models.JSONField(default=dict)
