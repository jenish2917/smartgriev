from rest_framework import serializers
from .models import UserActivity, ComplaintStats, DepartmentMetrics, SystemMetrics


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'username', 'activity_type', 'description',
            'ip_address', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class ComplaintStatsSerializer(serializers.ModelSerializer):
    """Serializer for ComplaintStats model"""
    
    class Meta:
        model = ComplaintStats
        fields = [
            'id', 'date', 'total_complaints', 'new_complaints',
            'resolved_complaints', 'rejected_complaints', 'pending_complaints',
            'high_priority_count', 'medium_priority_count', 'low_priority_count',
            'avg_response_time_hours', 'avg_resolution_time_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentMetricsSerializer(serializers.ModelSerializer):
    """Serializer for DepartmentMetrics model"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = DepartmentMetrics
        fields = [
            'id', 'department', 'department_name', 'date',
            'total_complaints', 'resolved_complaints', 
            'pending_complaints', 'rejected_complaints',
            'avg_response_time_hours', 'avg_resolution_time_hours',
            'resolution_rate', 'avg_rating', 'total_ratings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemMetricsSerializer(serializers.ModelSerializer):
    """Serializer for SystemMetrics model"""
    
    class Meta:
        model = SystemMetrics
        fields = [
            'id', 'timestamp', 'total_users', 'active_users_today', 'new_users_today',
            'total_complaints', 'open_complaints', 'resolved_complaints',
            'avg_api_response_time_ms', 'total_api_calls', 'failed_api_calls',
            'database_size_mb', 'media_storage_mb', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard overview statistics"""
    
    # User stats
    total_users = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    new_users_this_week = serializers.IntegerField()
    
    # Complaint stats
    total_complaints = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    resolved_complaints = serializers.IntegerField()
    resolved_this_week = serializers.IntegerField()
    
    # Performance stats
    avg_resolution_time_hours = serializers.FloatField()
    resolution_rate = serializers.FloatField()
    
    # Trends
    complaints_trend = serializers.ListField(child=serializers.DictField())
    department_performance = serializers.ListField(child=serializers.DictField())
