"""
Celery Tasks for Auto-Escalation
Schedule these tasks to run automatically
"""

from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


@shared_task(name='auto_escalate_complaints')
def auto_escalate_complaints_task(days=3, send_notifications=True):
    """
    Celery task to auto-escalate complaints
    
    Args:
        days: Number of days after which to escalate
        send_notifications: Whether to send email notifications
    """
    logger.info(f'Starting auto-escalation task for complaints older than {days} days')
    
    try:
        options = {
            'days': days,
            'send_notifications': send_notifications,
        }
        
        call_command('auto_escalate_complaints', **options)
        logger.info('Auto-escalation task completed successfully')
        return f'Auto-escalation completed for complaints older than {days} days'
        
    except Exception as e:
        logger.error(f'Auto-escalation task failed: {str(e)}')
        raise


@shared_task(name='daily_escalation_check')
def daily_escalation_check():
    """
    Daily escalation check (runs every 24 hours)
    Checks complaints older than 3 days
    """
    return auto_escalate_complaints_task(days=3, send_notifications=True)


@shared_task(name='urgent_escalation_check')
def urgent_escalation_check():
    """
    Urgent escalation check (runs every 12 hours)
    Checks complaints older than 2 days
    """
    return auto_escalate_complaints_task(days=2, send_notifications=True)
