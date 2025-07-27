from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from complaints.models import Complaint, AuditTrail
from chatbot.models import ChatLog
from .models import RealTimeMetrics, UserActivity
from .tasks import update_real_time_metrics, check_alert_rules

User = get_user_model()

@receiver(post_save, sender=Complaint)
def update_complaint_metrics(sender, instance, created, **kwargs):
    """Update real-time metrics when complaint is created or updated"""
    if created:
        # Trigger async task to update metrics
        update_real_time_metrics.delay('complaint_count', 'daily')
        
        # Clear dashboard cache
        cache.delete_pattern('dashboard_stats_*')
    else:
        # Status change
        if hasattr(instance, '_old_status') and instance._old_status != instance.status:
            update_real_time_metrics.delay('resolution_rate', 'daily')
            cache.delete_pattern('dashboard_stats_*')

@receiver(post_save, sender=ChatLog)
def update_chatbot_metrics(sender, instance, created, **kwargs):
    """Update chatbot effectiveness metrics"""
    if created:
        update_real_time_metrics.delay('chatbot_effectiveness', 'daily')

@receiver(post_save, sender=AuditTrail)
def update_activity_metrics(sender, instance, created, **kwargs):
    """Track audit trail activities"""
    if created:
        update_real_time_metrics.delay('department_performance', 'daily')

# Track model changes for metrics
@receiver(post_save, sender=Complaint)
def track_complaint_change(sender, instance, **kwargs):
    """Track the old status for comparison"""
    if instance.pk:
        try:
            old_instance = Complaint.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Complaint.DoesNotExist:
            instance._old_status = None
