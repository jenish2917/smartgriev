"""
Signal handlers for automatic notifications
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from complaints.models import Complaint
from .models import Notification, NotificationPreference
from .sms_service import sms_service

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Complaint)
def send_complaint_notification(sender, instance, created, **kwargs):
    """Send notification when complaint is created or status changes"""
    
    if not instance.user:
        return
    
    try:
        # Get user preferences
        preferences, _ = NotificationPreference.objects.get_or_create(
            user=instance.user
        )
        
        if created:
            # New complaint created
            title = "Complaint Registered"
            message = f"Your complaint '{instance.title}' has been successfully registered with ID #{instance.id}"
            notification_type = 'complaint_created'
            
            # Create notification
            notification = Notification.objects.create(
                user=instance.user,
                title=title,
                message=message,
                notification_type=notification_type,
                complaint=instance,
                priority='medium'
            )
            
            # Send SMS if enabled
            if preferences.sms_enabled and preferences.notify_complaint_created:
                sms_result = sms_service.send_complaint_created_sms(instance.user, instance)
                if sms_result.get('success'):
                    notification.sent_via_sms = True
                    notification.save()
        
        else:
            # Status changed
            if instance.status in ['in_progress', 'resolved', 'rejected']:
                title = f"Complaint Status: {instance.status.replace('_', ' ').title()}"
                message = f"Your complaint #{instance.id} status has been updated to: {instance.status.replace('_', ' ').title()}"
                notification_type = 'status_changed'
                
                # Create notification
                notification = Notification.objects.create(
                    user=instance.user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    complaint=instance,
                    priority='high' if instance.status == 'resolved' else 'medium'
                )
                
                # Send SMS if enabled
                if preferences.sms_enabled and preferences.notify_status_changed:
                    sms_result = sms_service.send_status_update_sms(
                        instance.user, 
                        instance, 
                        instance.status
                    )
                    if sms_result.get('success'):
                        notification.sent_via_sms = True
                        notification.save()
    
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
