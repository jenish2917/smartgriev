from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    complaint_title = serializers.CharField(source='complaint.title', read_only=True)
    complaint_id = serializers.IntegerField(source='complaint.id', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority',
            'complaint', 'complaint_id', 'complaint_title',
            'is_read', 'read_at', 'created_at',
            'sent_via_email', 'sent_via_sms', 'sent_via_push'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled',
            'notify_complaint_created', 'notify_complaint_updated',
            'notify_status_changed', 'notify_comment_added',
            'notify_assigned', 'notify_resolved',
            'digest_enabled', 'digest_frequency',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
