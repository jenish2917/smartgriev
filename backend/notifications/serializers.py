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
        fields = ('id', 'name', 'notification_type', 'channel', 'subject_template', 'body_template', 'available_variables', 'html_template', 'css_styles', 'language', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class NotificationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRule
        fields = ('id', 'name', 'trigger_event', 'template', 'conditions', 'recipient_type', 'custom_recipients', 'delay_minutes', 'max_frequency_hours', 'is_active', 'created_by', 'created_at')
        read_only_fields = ('id', 'created_at')

class NotificationDeliveryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDeliveryLog
        fields = ('id', 'notification', 'attempt_number', 'attempted_at', 'provider_name', 'provider_response', 'success', 'error_code', 'error_message', 'response_time_ms')
        read_only_fields = ('id', 'attempted_at')

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ('id', 'user', 'email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled', 'whatsapp_enabled', 'complaint_updates', 'system_alerts', 'marketing_messages', 'reminders', 'quiet_hours_start', 'quiet_hours_end', 'timezone', 'max_emails_per_day', 'max_sms_per_day', 'updated_at')
        read_only_fields = ('id', 'user', 'updated_at')

class NotificationQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationQueue
        fields = ('id', 'notification_id', 'rule', 'recipient', 'subject', 'body', 'html_body', 'channel', 'recipient_address', 'status', 'scheduled_at', 'sent_at', 'provider_message_id', 'delivery_status', 'opened_at', 'clicked_at', 'retry_count', 'error_message', 'context_data', 'created_at')
        read_only_fields = ('id', 'notification_id', 'created_at')

class NotificationAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationAnalytics
        fields = ('id', 'template', 'date', 'sent_count', 'delivered_count', 'failed_count', 'opened_count', 'clicked_count', 'unsubscribed_count', 'avg_delivery_time_seconds', 'bounce_rate', 'delivery_rate', 'open_rate', 'click_rate', 'updated_at')
        read_only_fields = ('id', 'date', 'updated_at')

class PushNotificationDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotificationDevice
        fields = ('id', 'user', 'device_token', 'device_type', 'device_name', 'app_version', 'os_version', 'is_active', 'last_used', 'registered_at')
        read_only_fields = ('id', 'user', 'last_used', 'registered_at')