from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    NotificationTemplate, NotificationRule, NotificationDeliveryLog,
    NotificationPreference, NotificationQueue, NotificationAnalytics,
    PushNotificationDevice
)

User = get_user_model()

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = '__all__'
        read_only_fields = ('template_id', 'created_at', 'updated_at')
    
    def validate_template_variables(self, value):
        """Validate template variables format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Template variables must be a list")
        return value

class NotificationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRule
        fields = '__all__'
        read_only_fields = ('rule_id', 'created_at', 'updated_at')
    
    def validate_conditions(self, value):
        """Validate rule conditions format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Conditions must be a dictionary")
        return value

class NotificationDeliveryLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = NotificationDeliveryLog
        fields = '__all__'
        read_only_fields = ('log_id', 'sent_at')

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('preference_id', 'user', 'created_at', 'updated_at')
    
    def validate_preferences(self, value):
        """Validate preferences format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Preferences must be a dictionary")
        
        valid_channels = ['email', 'sms', 'push']
        for channel in value.keys():
            if channel not in valid_channels:
                raise serializers.ValidationError(f"Invalid channel: {channel}")
        
        return value

class NotificationQueueSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = NotificationQueue
        fields = '__all__'
        read_only_fields = ('queue_id', 'created_at', 'updated_at')
    
    def validate_priority(self, value):
        """Validate priority level"""
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if value not in valid_priorities:
            raise serializers.ValidationError(f"Priority must be one of: {valid_priorities}")
        return value

class NotificationAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationAnalytics
        fields = '__all__'
        read_only_fields = ('analytics_id', 'date')

class PushNotificationDeviceSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = PushNotificationDevice
        fields = '__all__'
        read_only_fields = ('device_id', 'user', 'created_at', 'updated_at')
    
    def validate_device_type(self, value):
        """Validate device type"""
        valid_types = ['ios', 'android', 'web']
        if value not in valid_types:
            raise serializers.ValidationError(f"Device type must be one of: {valid_types}")
        return value
