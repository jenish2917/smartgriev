# Advanced Notification System
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    NOTIFICATION_TYPES = [
        ('complaint_status', 'Complaint Status Update'),
        ('department_assignment', 'Department Assignment'),
        ('resolution_reminder', 'Resolution Reminder'),
        ('escalation', 'Escalation Alert'),
        ('system_alert', 'System Alert'),
        ('marketing', 'Marketing Message'),
        ('announcement', 'Announcement'),
        ('feedback_request', 'Feedback Request')
    ]
    
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
        ('whatsapp', 'WhatsApp'),
        ('webhook', 'Webhook')
    ]
    
    name = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS)
    
    # Template content
    subject_template = models.CharField(max_length=255, help_text="Subject for email/push notifications")
    body_template = models.TextField(help_text="Use {{variable}} for dynamic content")
    
    # Template variables documentation
    available_variables = models.JSONField(default=list, help_text="List of available template variables")
    
    # Styling and formatting
    html_template = models.TextField(blank=True, help_text="HTML version for email")
    css_styles = models.TextField(blank=True)
    
    # Localization
    language = models.CharField(max_length=10, default='en')
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('notification_type', 'channel', 'language')

class NotificationRule(models.Model):
    """Rules for when to send notifications"""
    TRIGGER_EVENTS = [
        ('complaint_created', 'Complaint Created'),
        ('status_changed', 'Status Changed'),
        ('assignment_changed', 'Assignment Changed'),
        ('comment_added', 'Comment Added'),
        ('deadline_approaching', 'Deadline Approaching'),
        ('escalation_triggered', 'Escalation Triggered'),
        ('resolution_confirmed', 'Resolution Confirmed'),
        ('feedback_received', 'Feedback Received')
    ]
    
    name = models.CharField(max_length=200)
    trigger_event = models.CharField(max_length=50, choices=TRIGGER_EVENTS)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    
    # Conditions for triggering
    conditions = models.JSONField(default=dict, help_text="Conditions that must be met")
    
    # Recipient rules
    recipient_type = models.CharField(max_length=50, choices=[
        ('complaint_user', 'Complaint Creator'),
        ('department_officer', 'Department Officer'),
        ('all_officers', 'All Officers'),
        ('admin_users', 'Admin Users'),
        ('custom', 'Custom Recipients')
    ])
    custom_recipients = models.ManyToManyField(User, blank=True)
    
    # Timing
    delay_minutes = models.IntegerField(default=0, help_text="Delay before sending")
    
    # Frequency control
    max_frequency_hours = models.IntegerField(default=24, help_text="Minimum hours between same notifications")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notification_rules')
    created_at = models.DateTimeField(auto_now_add=True)

class NotificationQueue(models.Model):
    """Queue for processing notifications"""
    QUEUE_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    
    notification_id = models.UUIDField(default=uuid.uuid4, unique=True)
    rule = models.ForeignKey(NotificationRule, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Content
    subject = models.CharField(max_length=255)
    body = models.TextField()
    html_body = models.TextField(blank=True)
    
    # Delivery details
    channel = models.CharField(max_length=20)
    recipient_address = models.CharField(max_length=255)  # email, phone, device_token
    
    # Status and timing
    status = models.CharField(max_length=20, choices=QUEUE_STATUS, default='pending')
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True)
    
    # Delivery tracking
    provider_message_id = models.CharField(max_length=255, null=True)
    delivery_status = models.CharField(max_length=50, null=True)
    opened_at = models.DateTimeField(null=True)
    clicked_at = models.DateTimeField(null=True)
    
    # Error handling
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    # Metadata
    context_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    whatsapp_enabled = models.BooleanField(default=False)
    
    # Notification type preferences
    complaint_updates = models.BooleanField(default=True)
    system_alerts = models.BooleanField(default=True)
    marketing_messages = models.BooleanField(default=False)
    reminders = models.BooleanField(default=True)
    
    # Timing preferences
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Frequency limits
    max_emails_per_day = models.IntegerField(default=10)
    max_sms_per_day = models.IntegerField(default=5)
    
    updated_at = models.DateTimeField(auto_now=True)

class NotificationDeliveryLog(models.Model):
    """Log of notification delivery attempts"""
    notification = models.ForeignKey(NotificationQueue, on_delete=models.CASCADE, related_name='delivery_logs')
    
    # Attempt details
    attempt_number = models.IntegerField()
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    # Provider details
    provider_name = models.CharField(max_length=100)
    provider_response = models.JSONField(default=dict)
    
    # Result
    success = models.BooleanField()
    error_code = models.CharField(max_length=50, null=True)
    error_message = models.TextField(blank=True)
    
    # Performance metrics
    response_time_ms = models.IntegerField(null=True)

class NotificationAnalytics(models.Model):
    """Analytics for notification performance"""
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, related_name='analytics')
    
    # Time period
    date = models.DateField()
    
    # Volume metrics
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    # Engagement metrics
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    unsubscribed_count = models.IntegerField(default=0)
    
    # Performance metrics
    avg_delivery_time_seconds = models.FloatField(null=True)
    bounce_rate = models.FloatField(null=True)
    
    # Calculated rates
    delivery_rate = models.FloatField(null=True)
    open_rate = models.FloatField(null=True)
    click_rate = models.FloatField(null=True)
    
    updated_at = models.DateTimeField(auto_now=True)

class PushNotificationDevice(models.Model):
    """User devices for push notifications"""
    DEVICE_TYPES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web Browser')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_devices')
    device_token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    
    # Device info
    device_name = models.CharField(max_length=200, blank=True)
    app_version = models.CharField(max_length=50, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    registered_at = models.DateTimeField(auto_now_add=True)
