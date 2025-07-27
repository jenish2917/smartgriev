from celery import shared_task
from django.template import Context, Template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from .models import (
    NotificationRule, NotificationTemplate, NotificationQueue,
    NotificationPreference, NotificationDeliveryLog
)
from complaints.models import Complaint
import json
import requests

@shared_task
def send_notification_async(event, complaint_id, context=None):
    """Process notification rules and send notifications"""
    try:
        complaint = Complaint.objects.get(id=complaint_id)
        
        # Find matching notification rules
        rules = NotificationRule.objects.filter(
            trigger_event=event,
            is_active=True
        )
        
        for rule in rules:
            # Check if conditions are met
            if check_rule_conditions(rule, complaint, context):
                # Determine recipients
                recipients = get_rule_recipients(rule, complaint)
                
                for recipient in recipients:
                    # Check user preferences
                    if should_send_to_user(recipient, rule):
                        # Create notification queue entry
                        create_notification_queue_entry(rule, recipient, complaint, context)
        
    except Complaint.DoesNotExist:
        pass

def check_rule_conditions(rule, complaint, context):
    """Check if rule conditions are met"""
    conditions = rule.conditions
    
    if not conditions:
        return True
    
    # Check status conditions
    if 'status' in conditions:
        if complaint.status not in conditions['status']:
            return False
    
    # Check priority conditions
    if 'priority' in conditions:
        if complaint.priority not in conditions['priority']:
            return False
    
    # Check department conditions
    if 'department' in conditions:
        if complaint.department.id not in conditions['department']:
            return False
    
    return True

def get_rule_recipients(rule, complaint):
    """Get recipients based on rule configuration"""
    recipients = []
    
    if rule.recipient_type == 'complaint_user':
        recipients.append(complaint.user)
    elif rule.recipient_type == 'department_officer':
        if complaint.department and complaint.department.officer:
            recipients.append(complaint.department.officer)
    elif rule.recipient_type == 'all_officers':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        recipients.extend(User.objects.filter(is_officer=True))
    elif rule.recipient_type == 'admin_users':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        recipients.extend(User.objects.filter(is_superuser=True))
    elif rule.recipient_type == 'custom':
        recipients.extend(rule.custom_recipients.all())
    
    return recipients

def should_send_to_user(user, rule):
    """Check if notification should be sent to user based on preferences"""
    try:
        prefs = user.notification_preferences
        
        # Check if channel is enabled
        if rule.template.channel == 'email' and not prefs.email_enabled:
            return False
        elif rule.template.channel == 'sms' and not prefs.sms_enabled:
            return False
        elif rule.template.channel == 'push' and not prefs.push_enabled:
            return False
        elif rule.template.channel == 'in_app' and not prefs.in_app_enabled:
            return False
        
        # Check notification type preferences
        if rule.template.notification_type == 'complaint_status' and not prefs.complaint_updates:
            return False
        elif rule.template.notification_type == 'system_alert' and not prefs.system_alerts:
            return False
        elif rule.template.notification_type == 'marketing' and not prefs.marketing_messages:
            return False
        
        # Check frequency limits
        recent_notifications = NotificationQueue.objects.filter(
            recipient=user,
            rule=rule,
            created_at__gte=timezone.now() - timezone.timedelta(hours=rule.max_frequency_hours)
        ).count()
        
        if recent_notifications > 0:
            return False
        
        return True
        
    except:
        # Default to sending if preferences don't exist
        return True

def create_notification_queue_entry(rule, recipient, complaint, context):
    """Create a notification queue entry"""
    template = rule.template
    
    # Prepare template context
    template_context = {
        'user': recipient,
        'complaint': complaint,
        'department': complaint.department,
    }
    if context:
        template_context.update(context)
    
    # Render subject and body
    subject = render_template(template.subject_template, template_context)
    body = render_template(template.body_template, template_context)
    html_body = render_template(template.html_template, template_context) if template.html_template else ''
    
    # Determine recipient address
    recipient_address = get_recipient_address(recipient, template.channel)
    
    if not recipient_address:
        return  # Skip if no valid address
    
    # Calculate scheduled time
    scheduled_at = timezone.now()
    if rule.delay_minutes > 0:
        scheduled_at += timezone.timedelta(minutes=rule.delay_minutes)
    
    # Create queue entry
    NotificationQueue.objects.create(
        rule=rule,
        recipient=recipient,
        subject=subject,
        body=body,
        html_body=html_body,
        channel=template.channel,
        recipient_address=recipient_address,
        scheduled_at=scheduled_at,
        context_data=template_context
    )

def render_template(template_string, context):
    """Render Django template string with context"""
    if not template_string:
        return ''
    
    template = Template(template_string)
    return template.render(Context(context))

def get_recipient_address(user, channel):
    """Get recipient address for the specified channel"""
    if channel == 'email':
        return user.email
    elif channel == 'sms':
        return user.mobile
    elif channel == 'push':
        # Get the most recent active device token
        device = user.push_devices.filter(is_active=True).order_by('-last_used').first()
        return device.device_token if device else None
    elif channel == 'in_app':
        return str(user.id)  # Use user ID for in-app notifications
    
    return None

@shared_task
def process_notification_queue():
    """Process pending notifications in the queue"""
    pending_notifications = NotificationQueue.objects.filter(
        status='pending',
        scheduled_at__lte=timezone.now()
    ).order_by('scheduled_at')[:100]  # Process in batches
    
    for notification in pending_notifications:
        try:
            notification.status = 'processing'
            notification.save()
            
            # Send notification based on channel
            success = send_notification(notification)
            
            if success:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
            else:
                notification.status = 'failed'
                notification.retry_count += 1
                
                # Retry logic
                if notification.retry_count < 3:
                    notification.status = 'pending'
                    notification.scheduled_at = timezone.now() + timezone.timedelta(minutes=notification.retry_count * 5)
            
            notification.save()
            
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()

def send_notification(notification):
    """Send notification via the specified channel"""
    try:
        if notification.channel == 'email':
            return send_email_notification(notification)
        elif notification.channel == 'sms':
            return send_sms_notification(notification)
        elif notification.channel == 'push':
            return send_push_notification(notification)
        elif notification.channel == 'in_app':
            return send_in_app_notification(notification)
        elif notification.channel == 'webhook':
            return send_webhook_notification(notification)
        
        return False
        
    except Exception as e:
        log_delivery_attempt(notification, False, str(e))
        return False

def send_email_notification(notification):
    """Send email notification"""
    try:
        msg = EmailMultiAlternatives(
            subject=notification.subject,
            body=notification.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[notification.recipient_address]
        )
        
        if notification.html_body:
            msg.attach_alternative(notification.html_body, "text/html")
        
        msg.send()
        log_delivery_attempt(notification, True)
        return True
        
    except Exception as e:
        log_delivery_attempt(notification, False, str(e))
        return False

def send_sms_notification(notification):
    """Send SMS notification via Twilio"""
    try:
        from twilio.rest import Client
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        message = client.messages.create(
            body=notification.body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=notification.recipient_address
        )
        
        notification.provider_message_id = message.sid
        notification.save()
        
        log_delivery_attempt(notification, True)
        return True
        
    except Exception as e:
        log_delivery_attempt(notification, False, str(e))
        return False

def send_push_notification(notification):
    """Send push notification"""
    try:
        # Firebase Cloud Messaging implementation
        import firebase_admin
        from firebase_admin import messaging
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification.subject,
                body=notification.body,
            ),
            token=notification.recipient_address,
        )
        
        response = messaging.send(message)
        notification.provider_message_id = response
        notification.save()
        
        log_delivery_attempt(notification, True)
        return True
        
    except Exception as e:
        log_delivery_attempt(notification, False, str(e))
        return False

def send_in_app_notification(notification):
    """Send in-app notification via WebSocket"""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        group_name = f"notifications_{notification.recipient.id}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification',
                'title': notification.subject,
                'message': notification.body,
                'category': notification.rule.template.notification_type,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        log_delivery_attempt(notification, True)
        return True
        
    except Exception as e:
        log_delivery_attempt(notification, False, str(e))
        return False

def send_webhook_notification(notification):
    """Send webhook notification"""
    try:
        webhook_url = notification.context_data.get('webhook_url')
        if not webhook_url:
            return False
        
        payload = {
            'notification_id': str(notification.notification_id),
            'subject': notification.subject,
            'body': notification.body,
            'recipient': notification.recipient.username,
            'timestamp': timezone.now().isoformat(),
            'context': notification.context_data
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        notification.provider_message_id = str(response.status_code)
        notification.save()
        
        log_delivery_attempt(notification, response.status_code < 400, 
                           f"HTTP {response.status_code}")
        return response.status_code < 400
        
    except Exception as e:
        log_delivery_attempt(notification, False, str(e))
        return False

def log_delivery_attempt(notification, success, error_message=None):
    """Log delivery attempt"""
    NotificationDeliveryLog.objects.create(
        notification=notification,
        attempt_number=notification.retry_count + 1,
        provider_name=notification.channel,
        success=success,
        error_message=error_message or '',
        provider_response={'success': success}
    )

@shared_task
def update_notification_analytics():
    """Update notification analytics daily"""
    from django.db.models import Count, Avg
    from .models import NotificationAnalytics
    
    today = timezone.now().date()
    
    # Get analytics for each template
    templates = NotificationTemplate.objects.filter(is_active=True)
    
    for template in templates:
        # Calculate metrics for today
        notifications = NotificationQueue.objects.filter(
            rule__template=template,
            created_at__date=today
        )
        
        sent_count = notifications.filter(status='sent').count()
        delivered_count = notifications.filter(delivery_status='delivered').count()
        failed_count = notifications.filter(status='failed').count()
        opened_count = notifications.filter(opened_at__isnull=False).count()
        clicked_count = notifications.filter(clicked_at__isnull=False).count()
        
        # Calculate rates
        delivery_rate = (delivered_count / max(sent_count, 1)) * 100
        open_rate = (opened_count / max(delivered_count, 1)) * 100
        click_rate = (clicked_count / max(opened_count, 1)) * 100
        
        # Update or create analytics record
        analytics, created = NotificationAnalytics.objects.get_or_create(
            template=template,
            date=today,
            defaults={
                'sent_count': sent_count,
                'delivered_count': delivered_count,
                'failed_count': failed_count,
                'opened_count': opened_count,
                'clicked_count': clicked_count,
                'delivery_rate': delivery_rate,
                'open_rate': open_rate,
                'click_rate': click_rate
            }
        )
        
        if not created:
            analytics.sent_count = sent_count
            analytics.delivered_count = delivered_count
            analytics.failed_count = failed_count
            analytics.opened_count = opened_count
            analytics.clicked_count = clicked_count
            analytics.delivery_rate = delivery_rate
            analytics.open_rate = open_rate
            analytics.click_rate = click_rate
            analytics.save()
