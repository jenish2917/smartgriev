from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from complaints.models import Complaint, AuditTrail
from .tasks import send_notification_async

@receiver(post_save, sender=Complaint)
def complaint_notification_handler(sender, instance, created, **kwargs):
    """Handle notifications for complaint events"""
    if created:
        # New complaint created
        send_notification_async.delay(
            event='complaint_created',
            complaint_id=instance.id,
            context={'complaint': instance}
        )
    else:
        # Complaint updated - check if status changed
        if hasattr(instance, '_old_status') and instance._old_status != instance.status:
            send_notification_async.delay(
                event='status_changed',
                complaint_id=instance.id,
                context={
                    'complaint': instance,
                    'old_status': instance._old_status,
                    'new_status': instance.status
                }
            )

@receiver(post_save, sender=AuditTrail)
def audit_trail_notification_handler(sender, instance, created, **kwargs):
    """Handle notifications for audit trail events"""
    if created and 'comment' in instance.action:
        send_notification_async.delay(
            event='comment_added',
            complaint_id=instance.complaint.id,
            context={
                'complaint': instance.complaint,
                'comment': instance.action,
                'by_user': instance.by_user
            }
        )

# Track old status for comparison
@receiver(pre_save, sender=Complaint)
def track_complaint_status_change(sender, instance, **kwargs):
    """Track the old status for comparison"""
    if instance.pk:
        try:
            old_instance = Complaint.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Complaint.DoesNotExist:
            instance._old_status = None
