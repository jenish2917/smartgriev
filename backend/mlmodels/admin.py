from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import MLModel, ModelPrediction

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'get_framework', 'version', 
                   'accuracy_display', 'languages_display', 
                   'is_active', 'created_at')
    list_filter = ('model_type', 'version', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'model_type', 'version')
        }),
        ('Model Files', {
            'fields': ('model_path', 'config_path', 'vocab_path')
        }),
        ('Configuration', {
            'fields': ('supported_languages', 'accuracy', 'is_active', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_framework(self, obj):
        return obj.get_framework_display()
    get_framework.short_description = 'Framework'

    def accuracy_display(self, obj):
        color = 'green' if obj.accuracy >= 0.9 else 'orange' if obj.accuracy >= 0.8 else 'red'
        return format_html(
            '<span style="color: {};">{:.1%}</span>',
            color,
            obj.accuracy
        )
    accuracy_display.short_description = 'Accuracy'

    def languages_display(self, obj):
        return format_html(
            '<span title="{}">{} languages</span>',
            ', '.join(obj.supported_languages),
            len(obj.supported_languages)
        )
    languages_display.short_description = 'Languages'

    def save_model(self, request, obj, form, change):
        if not change:  # New model
            import os
            model_path = os.path.join(settings.MODELS_ROOT, obj.model_path)
            if os.path.exists(model_path):
                obj.model_size = os.path.getsize(model_path)
        super().save_model(request, obj, form, change)

@admin.register(ModelPrediction)
class ModelPredictionAdmin(admin.ModelAdmin):
    list_display = ('model', 'truncated_input', 'languages_display', 
                   'confidence_display', 'processing_time_display', 
                   'timestamp')
    list_filter = ('model', 'timestamp')
    search_fields = ('input_text', 'prediction')
    readonly_fields = ('timestamp',)
    
    def truncated_input(self, obj):
        return (obj.input_text[:50] + '...') if len(obj.input_text) > 50 else obj.input_text
    truncated_input.short_description = 'Input Text'
    
    def languages_display(self, obj):
        if obj.output_language:
            return f'{obj.input_language} → {obj.output_language}'
        return obj.input_language
    languages_display.short_description = 'Languages'
    
    def confidence_display(self, obj):
        color = 'green' if obj.confidence >= 0.9 else 'orange' if obj.confidence >= 0.7 else 'red'
        return format_html(
            '<span style="color: {};">{:.1%}</span>',
            color,
            obj.confidence
        )
    confidence_display.short_description = 'Confidence'
    
    def processing_time_display(self, obj):
        if obj.processing_time < 1:
            return f'{obj.processing_time * 1000:.0f}ms'
        return f'{obj.processing_time:.2f}s'
    processing_time_display.short_description = 'Processing Time'
