from django.contrib import admin
from django.utils.html import format_html
from .models import ChatLog, ChatFeedback, QuickReplyTemplate, ChatSession, ChatNotification

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id', 'is_active', 'created_at', 'message_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'session_id')
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'truncated_message', 'intent', 'confidence_display', 
                   'reply_type', 'language_display', 'escalated_to_human', 'timestamp')
    list_filter = ('intent', 'reply_type', 'input_language', 'escalated_to_human', 
                   'timestamp', 'sentiment')
    search_fields = ('user__username', 'message', 'reply', 'intent')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'session')
        }),
        ('Message Content', {
            'fields': ('message', 'reply', 'reply_type', 'reply_metadata')
        }),
        ('Analysis', {
            'fields': ('intent', 'confidence', 'sentiment', 'sentiment_score')
        }),
        ('Language', {
            'fields': ('input_language', 'reply_language')
        }),
        ('Escalation', {
            'fields': ('escalated_to_human', 'escalation_reason')
        }),
        ('Timestamps', {
            'fields': ('timestamp',)
        }),
    )
    
    def truncated_message(self, obj):
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    truncated_message.short_description = 'Message'
    
    def confidence_display(self, obj):
        if obj.confidence is None:
            return '-'
        color = 'green' if obj.confidence >= 0.8 else 'orange' if obj.confidence >= 0.6 else 'red'
        return format_html(
            '<span style="color: {};">{:.1%}</span>',
            color,
            obj.confidence
        )
    confidence_display.short_description = 'Confidence'
    
    def language_display(self, obj):
        if obj.input_language == obj.reply_language:
            return obj.get_input_language_display()
        return f"{obj.get_input_language_display()} → {obj.get_reply_language_display()}"
    language_display.short_description = 'Language'

@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_log_info', 'rating_display', 'is_helpful', 'timestamp')
    list_filter = ('rating', 'is_helpful', 'timestamp')
    search_fields = ('user__username', 'comments')
    readonly_fields = ('timestamp',)
    
    def chat_log_info(self, obj):
        return f"Chat on {obj.chat_log.timestamp.strftime('%Y-%m-%d %H:%M')}"
    chat_log_info.short_description = 'Chat Log'
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating
        color = 'green' if obj.rating >= 4 else 'orange' if obj.rating >= 3 else 'red'
        return format_html(
            '<span style="color: {};">{} ({})</span>',
            color,
            stars,
            obj.rating
        )
    rating_display.short_description = 'Rating'

@admin.register(QuickReplyTemplate)
class QuickReplyTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'intent', 'button_count', 'is_active', 'created_at')
    list_filter = ('intent', 'is_active', 'created_at')
    search_fields = ('name', 'intent')
    readonly_fields = ('created_at',)
    
    def button_count(self, obj):
        return len(obj.buttons) if obj.buttons else 0
    button_count.short_description = 'Buttons'

@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_sent', 
                   'scheduled_at', 'sent_at')
    list_filter = ('notification_type', 'is_sent', 'scheduled_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('sent_at',)
    date_hierarchy = 'scheduled_at'
    
    actions = ['mark_as_sent', 'schedule_for_now']
    
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_sent=True, sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as sent.')
    mark_as_sent.short_description = 'Mark selected notifications as sent'
    
    def schedule_for_now(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(scheduled_at=timezone.now())
        self.message_user(request, f'{updated} notifications scheduled for now.')
    schedule_for_now.short_description = 'Schedule selected notifications for now'
