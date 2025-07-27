from celery import shared_task
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import RealTimeMetrics, AlertRule, AlertInstance, UserActivity
from complaints.models import Complaint, Department
from chatbot.models import ChatLog
import json

@shared_task
def update_real_time_metrics(metric_type, time_period):
    """Update real-time metrics for dashboard"""
    now = timezone.now()
    
    if metric_type == 'complaint_count':
        if time_period == 'daily':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            count = Complaint.objects.filter(created_at__gte=today_start).count()
            
            metric, created = RealTimeMetrics.objects.get_or_create(
                metric_type='complaint_count',
                time_period='daily',
                timestamp__date=now.date(),
                defaults={'metric_value': {'count': count}}
            )
            if not created:
                metric.metric_value = {'count': count}
                metric.save()
    
    elif metric_type == 'resolution_rate':
        if time_period == 'daily':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            total = Complaint.objects.filter(created_at__gte=today_start).count()
            resolved = Complaint.objects.filter(
                created_at__gte=today_start, 
                status='resolved'
            ).count()
            
            rate = (resolved / max(total, 1)) * 100
            
            metric, created = RealTimeMetrics.objects.get_or_create(
                metric_type='resolution_rate',
                time_period='daily',
                timestamp__date=now.date(),
                defaults={'metric_value': {'rate': rate, 'total': total, 'resolved': resolved}}
            )
            if not created:
                metric.metric_value = {'rate': rate, 'total': total, 'resolved': resolved}
                metric.save()
    
    elif metric_type == 'chatbot_effectiveness':
        if time_period == 'daily':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            total_chats = ChatLog.objects.filter(timestamp__gte=today_start).count()
            escalated = ChatLog.objects.filter(
                timestamp__gte=today_start,
                escalated_to_human=True
            ).count()
            
            effectiveness = (1 - (escalated / max(total_chats, 1))) * 100
            
            metric, created = RealTimeMetrics.objects.get_or_create(
                metric_type='chatbot_effectiveness',
                time_period='daily',
                timestamp__date=now.date(),
                defaults={'metric_value': {
                    'effectiveness': effectiveness,
                    'total_chats': total_chats,
                    'escalated': escalated
                }}
            )
            if not created:
                metric.metric_value = {
                    'effectiveness': effectiveness,
                    'total_chats': total_chats,
                    'escalated': escalated
                }
                metric.save()
    
    elif metric_type == 'department_performance':
        # Calculate department performance metrics
        departments = Department.objects.annotate(
            total_complaints=Count('complaints'),
            resolved_complaints=Count('complaints', filter=Q(complaints__status='resolved')),
            pending_complaints=Count('complaints', filter=Q(complaints__status='pending'))
        )
        
        performance_data = []
        for dept in departments:
            resolution_rate = (dept.resolved_complaints / max(dept.total_complaints, 1)) * 100
            performance_data.append({
                'department_id': dept.id,
                'department_name': dept.name,
                'total_complaints': dept.total_complaints,
                'resolved_complaints': dept.resolved_complaints,
                'pending_complaints': dept.pending_complaints,
                'resolution_rate': resolution_rate
            })
        
        metric, created = RealTimeMetrics.objects.get_or_create(
            metric_type='department_performance',
            time_period=time_period,
            timestamp__date=now.date(),
            defaults={'metric_value': {'departments': performance_data}}
        )
        if not created:
            metric.metric_value = {'departments': performance_data}
            metric.save()

@shared_task
def check_alert_rules():
    """Check all active alert rules and trigger alerts if conditions are met"""
    active_rules = AlertRule.objects.filter(is_active=True)
    
    for rule in active_rules:
        # Get latest metric for this rule
        latest_metric = RealTimeMetrics.objects.filter(
            metric_type=rule.metric_type
        ).order_by('-timestamp').first()
        
        if not latest_metric:
            continue
        
        # Check if rule condition is met
        metric_value = latest_metric.metric_value
        
        # Extract numeric value based on metric type
        if rule.metric_type == 'complaint_count':
            current_value = metric_value.get('count', 0)
        elif rule.metric_type == 'resolution_rate':
            current_value = metric_value.get('rate', 0)
        elif rule.metric_type == 'chatbot_effectiveness':
            current_value = metric_value.get('effectiveness', 0)
        else:
            continue
        
        # Check condition
        triggered = False
        if rule.comparison_operator == '>' and current_value > rule.threshold_value:
            triggered = True
        elif rule.comparison_operator == '<' and current_value < rule.threshold_value:
            triggered = True
        elif rule.comparison_operator == '>=' and current_value >= rule.threshold_value:
            triggered = True
        elif rule.comparison_operator == '<=' and current_value <= rule.threshold_value:
            triggered = True
        elif rule.comparison_operator == '==' and current_value == rule.threshold_value:
            triggered = True
        
        if triggered:
            # Check if alert already exists for this rule in the last hour
            recent_alert = AlertInstance.objects.filter(
                rule=rule,
                triggered_at__gte=timezone.now() - timedelta(hours=1)
            ).exists()
            
            if not recent_alert:
                # Create new alert instance
                alert = AlertInstance.objects.create(
                    rule=rule,
                    triggered_value=current_value,
                    message=f"{rule.name}: {rule.metric_type} is {current_value} (threshold: {rule.threshold_value})",
                    severity='high' if abs(current_value - rule.threshold_value) > (rule.threshold_value * 0.2) else 'medium'
                )
                
                # Send notifications
                send_alert_notifications.delay(alert.id)

@shared_task
def send_alert_notifications(alert_id):
    """Send notifications for triggered alerts"""
    try:
        alert = AlertInstance.objects.get(id=alert_id)
        
        # Send email notifications
        if 'email' in alert.rule.notification_channels:
            from django.core.mail import send_mail
            send_mail(
                subject=f'Alert: {alert.rule.name}',
                message=alert.message,
                from_email='alerts@smartgriev.com',
                recipient_list=[alert.rule.created_by.email],
                fail_silently=True
            )
        
        # Send webhook notifications
        if 'webhook' in alert.rule.notification_channels:
            import requests
            webhook_url = alert.rule.metadata.get('webhook_url')
            if webhook_url:
                try:
                    requests.post(webhook_url, json={
                        'alert_id': alert.id,
                        'rule_name': alert.rule.name,
                        'message': alert.message,
                        'severity': alert.severity,
                        'triggered_at': alert.triggered_at.isoformat()
                    }, timeout=10)
                except Exception as e:
                    print(f"Failed to send webhook: {e}")
        
    except AlertInstance.DoesNotExist:
        pass

@shared_task
def generate_daily_reports():
    """Generate daily analytics reports"""
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    today = timezone.now().date()
    
    # Get statistics for today
    daily_stats = {
        'total_complaints': Complaint.objects.filter(created_at__date=today).count(),
        'resolved_complaints': Complaint.objects.filter(
            updated_at__date=today, 
            status='resolved'
        ).count(),
        'pending_complaints': Complaint.objects.filter(status='pending').count(),
    }
    
    # Send to admin users
    admin_users = User.objects.filter(is_superuser=True, email__isnull=False)
    
    for admin in admin_users:
        try:
            subject = f'SmartGriev Daily Report - {today}'
            text_content = f"""
            Daily Report for {today}:
            - New Complaints: {daily_stats['total_complaints']}
            - Resolved Today: {daily_stats['resolved_complaints']}
            - Pending Complaints: {daily_stats['pending_complaints']}
            """
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='reports@smartgriev.com',
                to=[admin.email]
            )
            msg.send()
            
        except Exception as e:
            print(f"Failed to send daily report to {admin.email}: {e}")

@shared_task
def cleanup_old_metrics():
    """Clean up old metrics data"""
    cutoff_date = timezone.now() - timedelta(days=90)
    
    # Delete old metrics
    deleted_count = RealTimeMetrics.objects.filter(timestamp__lt=cutoff_date).delete()[0]
    
    # Delete old user activity
    UserActivity.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # Delete resolved alerts older than 30 days
    old_alerts_cutoff = timezone.now() - timedelta(days=30)
    AlertInstance.objects.filter(
        is_resolved=True,
        resolved_at__lt=old_alerts_cutoff
    ).delete()
    
    return f"Cleaned up {deleted_count} old metric records"
