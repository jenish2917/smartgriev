from rest_framework import serializers
from .models import (
    AnalyticsDashboard, RealTimeMetrics, UserActivity, 
    PerformanceMetrics, AlertRule, AlertInstance
)

class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsDashboard
        fields = '__all__'
        read_only_fields = ('user',)

class RealTimeMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealTimeMetrics
        fields = '__all__'

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = '__all__'
        read_only_fields = ('user',)

class PerformanceMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceMetrics
        fields = '__all__'

class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = '__all__'
        read_only_fields = ('created_by',)

class AlertInstanceSerializer(serializers.ModelSerializer):
    rule = AlertRuleSerializer(read_only=True)
    
    class Meta:
        model = AlertInstance
        fields = '__all__'

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_complaints = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    resolved_complaints = serializers.IntegerField()
    resolution_rate = serializers.FloatField()
    avg_resolution_time = serializers.FloatField()
    satisfaction_score = serializers.FloatField()
    sentiment_distribution = serializers.DictField()
    department_performance = serializers.ListField()
    recent_activity = serializers.ListField()
    geographic_hotspots = serializers.ListField()
