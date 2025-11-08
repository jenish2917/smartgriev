from django.contrib import admin
from .models import UserActivity, ComplaintStats, DepartmentMetrics, SystemMetrics


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at', 'ip_address']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'activity_type', 'description')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'metadata')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(ComplaintStats)
class ComplaintStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_complaints', 'new_complaints', 'resolved_complaints', 'pending_complaints']
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DepartmentMetrics)
class DepartmentMetricsAdmin(admin.ModelAdmin):
    list_display = ['department', 'date', 'total_complaints', 'resolved_complaints', 'resolution_rate']
    list_filter = ['department', 'date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'total_users', 'total_complaints', 'open_complaints']
    list_filter = ['timestamp']
    date_hierarchy = 'timestamp'
    readonly_fields = ['created_at']
