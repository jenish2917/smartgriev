from django.contrib import admin
from .models import ChatLog

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'reply', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'message', 'reply')
    date_hierarchy = 'timestamp'
    readonly_fields = ('reply',)
