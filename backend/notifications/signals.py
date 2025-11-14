"""
Signal handlers for automatic notifications
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from complaints.models import Complaint
from .models import Notification, NotificationPreference
from .sms_service import sms_service
from .email_service import email_service

logger = logging.getLogger(__name__)

# Store previous status to detect changes
_complaint_previous_status = {}


@receiver(pre_save, sender=Complaint)
def store_previous_status(sender, instance, **kwargs):
    """Store previous status before save to detect changes"""
    if instance.pk:
        try:
            old_instance = Complaint.objects.get(pk=instance.pk)
            _complaint_previous_status[instance.pk] = old_instance.status
        except Complaint.DoesNotExist:
            _complaint_previous_status[instance.pk] = None


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
        
        # Get user's language preference
        user_language = instance.user.language_preference if hasattr(instance.user, 'language_preference') else 'en'
        
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
            
            # Send Email if user has email
            if instance.user.email and preferences.email_enabled:
                logger.info(f"[EMAIL] Sending complaint created email to {instance.user.email}")
                email_result = email_service.send_complaint_created_email(
                    user=instance.user,
                    complaint=instance,
                    language=user_language
                )
                if email_result.get('success'):
                    notification.sent_via_email = True
                    logger.info(f"[EMAIL] ✅ Complaint created email sent successfully")
                else:
                    logger.error(f"[EMAIL] ❌ Failed to send email: {email_result.get('error')}")
                notification.save()
            
            # Send SMS if enabled
            if preferences.sms_enabled and preferences.notify_complaint_created:
                sms_result = sms_service.send_complaint_created_sms(instance.user, instance)
                if sms_result.get('success'):
                    notification.sent_via_sms = True
                    notification.save()
        
        else:
            # Check if status changed
            old_status = _complaint_previous_status.get(instance.pk)
            
            # Status changed
            if old_status and old_status != instance.status:
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
                
                # Send Email for status updates (especially resolved)
                if instance.user.email and preferences.email_enabled:
                    logger.info(f"[EMAIL] Sending status update email to {instance.user.email} (Status: {old_status} → {instance.status})")
                    email_result = email_service.send_status_update_email(
                        user=instance.user,
                        complaint=instance,
                        old_status=old_status,
                        new_status=instance.status,
                        language=user_language
                    )
                    if email_result.get('success'):
                        notification.sent_via_email = True
                        logger.info(f"[EMAIL] ✅ Status update email sent successfully")
                    else:
                        logger.error(f"[EMAIL] ❌ Failed to send email: {email_result.get('error')}")
                    notification.save()
                
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
            
            # Clean up stored status
            if instance.pk in _complaint_previous_status:
                del _complaint_previous_status[instance.pk]
    
    except Exception as e:
        logger.error(f"Error sending notification: {e}", exc_info=True)
