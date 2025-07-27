from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AnalyticsDashboard, RealTimeMetrics, UserActivity,
    PerformanceMetrics, AlertRule, AlertInstance
)

@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'dashboard_type', 'user', 'is_active', 'created_at')
    list_filter = ('dashboard_type', 'is_active', 'created_at')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(RealTimeMetrics)
class RealTimeMetricsAdmin(admin.ModelAdmin):
    list_display = ('metric_type', 'time_period', 'department', 'timestamp_display')
    list_filter = ('metric_type', 'time_period', 'timestamp')
    search_fields = ('metric_type',)
    readonly_fields = ('timestamp',)
    
    def timestamp_display(self, obj):
        return format_html(
            '<span title="{}">{}</span>',
            obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            obj.timestamp.strftime('%m/%d %H:%M')
        )
    timestamp_display.short_description = 'Timestamp'

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'endpoint', 'response_code', 'duration_display', 'timestamp')
    list_filter = ('activity_type', 'response_code', 'timestamp')
    search_fields = ('user__username', 'activity_type', 'endpoint')
    readonly_fields = ('timestamp',)
    
    def duration_display(self, obj):
        if obj.duration:
            if obj.duration < 1:
                return f'{obj.duration * 1000:.0f}ms'
            return f'{obj.duration:.2f}s'
        return '-'
    duration_display.short_description = 'Duration'

@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = ('metric_name', 'metric_value', 'server_node', 'timestamp')
    list_filter = ('metric_name', 'server_node', 'timestamp')
    search_fields = ('metric_name',)
    readonly_fields = ('timestamp',)

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'metric_type', 'condition_display', 'is_active', 'created_by', 'created_at')
    list_filter = ('metric_type', 'condition_type', 'is_active', 'created_at')
    search_fields = ('name', 'metric_type')
    readonly_fields = ('created_at',)
    
    def condition_display(self, obj):
        return f'{obj.condition_type} {obj.comparison_operator} {obj.threshold_value}'
    condition_display.short_description = 'Condition'

@admin.register(AlertInstance)
class AlertInstanceAdmin(admin.ModelAdmin):
    list_display = ('rule', 'triggered_value', 'severity_display', 'is_resolved', 'triggered_at')
    list_filter = ('severity', 'is_resolved', 'triggered_at')
    search_fields = ('rule__name', 'message')
    readonly_fields = ('triggered_at',)
    
    def severity_display(self, obj):
        colors = {'low': 'green', 'medium': 'orange', 'high': 'red'}
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.severity, 'black'),
            obj.severity.upper()
        )
    severity_display.short_description = 'Severity'
