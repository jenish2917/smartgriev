from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username', 'user__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'message', 'notification_type', 'priority')
        }),
        ('Related Objects', {
            'fields': ('complaint',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_sent', 'read_at', 'created_at')
        }),
        ('Delivery Channels', {
            'fields': ('sent_via_email', 'sent_via_sms', 'sent_via_push')
        }),
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'sms_enabled', 'push_enabled', 'updated_at']
    list_filter = ['email_enabled', 'sms_enabled', 'push_enabled', 'digest_enabled']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'updated_at'
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Channel Preferences', {
            'fields': ('email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled')
        }),
        ('Notification Types', {
            'fields': (
                'notify_complaint_created', 'notify_complaint_updated',
                'notify_status_changed', 'notify_comment_added',
                'notify_assigned', 'notify_resolved'
            )
        }),
        ('Digest Settings', {
            'fields': ('digest_enabled', 'digest_frequency')
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
