from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class UserActivity(models.Model):
    """Track user activity for analytics"""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('complaint_created', 'Complaint Created'),
        ('complaint_viewed', 'Complaint Viewed'),
        ('complaint_updated', 'Complaint Updated'),
        ('chat_message', 'Chat Message'),
        ('profile_updated', 'Profile Updated'),
        ('search', 'Search'),
        ('page_view', 'Page View'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.created_at}"


class ComplaintStats(models.Model):
    """Aggregated complaint statistics"""
    
    date = models.DateField(unique=True)
    
    # Daily counts
    total_complaints = models.IntegerField(default=0)
    new_complaints = models.IntegerField(default=0)
    resolved_complaints = models.IntegerField(default=0)
    rejected_complaints = models.IntegerField(default=0)
    pending_complaints = models.IntegerField(default=0)
    
    # By priority
    high_priority_count = models.IntegerField(default=0)
    medium_priority_count = models.IntegerField(default=0)
    low_priority_count = models.IntegerField(default=0)
    
    # Response metrics
    avg_response_time_hours = models.FloatField(null=True, blank=True)
    avg_resolution_time_hours = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Complaint Statistics'
    
    def __str__(self):
        return f"Stats for {self.date}"


class DepartmentMetrics(models.Model):
    """Department-wise performance metrics"""
    
    department = models.ForeignKey(
        'complaints.Department',
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    date = models.DateField()
    
    # Complaint volumes
    total_complaints = models.IntegerField(default=0)
    resolved_complaints = models.IntegerField(default=0)
    pending_complaints = models.IntegerField(default=0)
    rejected_complaints = models.IntegerField(default=0)
    
    # Performance metrics
    avg_response_time_hours = models.FloatField(null=True, blank=True)
    avg_resolution_time_hours = models.FloatField(null=True, blank=True)
    resolution_rate = models.FloatField(null=True, blank=True)  # Percentage
    
    # User satisfaction
    avg_rating = models.FloatField(null=True, blank=True)
    total_ratings = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', 'department']
        unique_together = ['department', 'date']
        verbose_name_plural = 'Department Metrics'
    
    def __str__(self):
        return f"{self.department.name} - {self.date}"


class SystemMetrics(models.Model):
    """Overall system performance metrics"""
    
    timestamp = models.DateTimeField(unique=True)
    
    # User metrics
    total_users = models.IntegerField(default=0)
    active_users_today = models.IntegerField(default=0)
    new_users_today = models.IntegerField(default=0)
    
    # Complaint metrics
    total_complaints = models.IntegerField(default=0)
    open_complaints = models.IntegerField(default=0)
    resolved_complaints = models.IntegerField(default=0)
    
    # Performance metrics
    avg_api_response_time_ms = models.FloatField(null=True, blank=True)
    total_api_calls = models.IntegerField(default=0)
    failed_api_calls = models.IntegerField(default=0)
    
    # System health
    database_size_mb = models.FloatField(null=True, blank=True)
    media_storage_mb = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'System Metrics'
    
    def __str__(self):
        return f"System Metrics - {self.timestamp}"
