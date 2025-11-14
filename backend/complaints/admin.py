from django.contrib import admin
from .models import Department, Complaint, AuditTrail

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'email', 'phone', 'is_active', 'officer')
    list_filter = ('zone', 'is_active')
    search_fields = ('name', 'zone', 'email', 'description', 'officer__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'zone', 'description', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'officer')
        }),
        ('Government Integration (Future)', {
            'fields': ('department_code', 'api_endpoint', 'api_key'),
            'classes': ('collapse',),
            'description': 'API integration for direct government portal connectivity'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'department', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'department', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'department__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('sentiment',)

# AuditTrail is unregistered - automatically logged, view-only through API
# @admin.register(AuditTrail)
# class AuditTrailAdmin(admin.ModelAdmin):
#     list_display = ('complaint', 'action', 'by_user', 'timestamp')
#     list_filter = ('timestamp', 'by_user')
#     search_fields = ('complaint__title', 'action', 'by_user__username')
#     date_hierarchy = 'timestamp'
