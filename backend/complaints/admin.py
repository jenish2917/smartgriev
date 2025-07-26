from django.contrib import admin
from .models import Department, Complaint, AuditTrail

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'officer')
    list_filter = ('zone',)
    search_fields = ('name', 'zone', 'officer__username')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'department', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'department', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'department__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('sentiment',)

@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'action', 'by_user', 'timestamp')
    list_filter = ('timestamp', 'by_user')
    search_fields = ('complaint__title', 'action', 'by_user__username')
    date_hierarchy = 'timestamp'
