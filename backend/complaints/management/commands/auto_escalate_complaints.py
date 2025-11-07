"""
Auto-Escalation Management Command
Automatically escalates or re-files unresolved complaints after 2-3 days
"""

import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from complaints.models import Complaint
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Auto-escalate unresolved complaints older than 2-3 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=3,
            help='Number of days after which to escalate (default: 3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be escalated without making changes'
        )
        parser.add_argument(
            '--send-notifications',
            action='store_true',
            help='Send email notifications to users about escalation'
        )

    def handle(self, *args, **options):
        days_threshold = options['days']
        dry_run = options['dry_run']
        send_notifications = options['send_notifications']
        
        cutoff_date = timezone.now() - timedelta(days=days_threshold)
        
        self.stdout.write(self.style.SUCCESS(
            f'🔍 Checking complaints older than {days_threshold} days (before {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")})'
        ))
        
        # Find complaints that need escalation
        complaints_to_escalate = Complaint.objects.filter(
            Q(status='pending') | Q(status='in_progress'),
            created_at__lt=cutoff_date,
            escalated=False
        ).select_related('user', 'department')
        
        total_count = complaints_to_escalate.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No complaints need escalation'))
            return
        
        self.stdout.write(self.style.WARNING(
            f'⚠️  Found {total_count} complaints that need escalation'
        ))
        
        escalated_count = 0
        failed_count = 0
        
        for complaint in complaints_to_escalate:
            try:
                days_old = (timezone.now() - complaint.created_at).days
                
                self.stdout.write(
                    f'\n📋 Complaint ID: {complaint.id}'
                    f'\n   User: {complaint.user.email}'
                    f'\n   Status: {complaint.status}'
                    f'\n   Created: {complaint.created_at.strftime("%Y-%m-%d %H:%M:%S")} ({days_old} days ago)'
                    f'\n   Category: {complaint.category or "N/A"}'
                )
                
                if not dry_run:
                    # Method 1: Escalate existing complaint
                    complaint.escalated = True
                    complaint.escalation_date = timezone.now()
                    complaint.priority = 'high'  # Increase priority
                    
                    # Add escalation note
                    escalation_note = f"Auto-escalated after {days_old} days without resolution"
                    if complaint.admin_notes:
                        complaint.admin_notes += f"\n\n{escalation_note}"
                    else:
                        complaint.admin_notes = escalation_note
                    
                    complaint.save()
                    
                    # Method 2: Create notification for admin
                    self._create_admin_notification(complaint, days_old)
                    
                    # Method 3: Send email notification
                    if send_notifications:
                        self._send_escalation_email(complaint, days_old)
                    
                    escalated_count += 1
                    self.stdout.write(self.style.SUCCESS('   ✅ Escalated successfully'))
                else:
                    self.stdout.write(self.style.WARNING('   ⏭️  Would escalate (dry-run mode)'))
                    escalated_count += 1
                    
            except Exception as e:
                failed_count += 1
                logger.error(f'Error escalating complaint {complaint.id}: {str(e)}')
                self.stdout.write(self.style.ERROR(f'   ❌ Failed: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'\n📊 ESCALATION SUMMARY'))
        self.stdout.write(f'Total complaints found: {total_count}')
        self.stdout.write(self.style.SUCCESS(f'Successfully escalated: {escalated_count}'))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'Failed: {failed_count}'))
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN MODE - No changes were made'))
        self.stdout.write('='*60 + '\n')
    
    def _create_admin_notification(self, complaint, days_old):
        """Create notification for administrators"""
        try:
            from chatbot.models import ChatNotification
            
            # Get admin users
            admin_users = User.objects.filter(is_staff=True, is_active=True)
            
            for admin in admin_users:
                ChatNotification.objects.create(
                    user=admin,
                    notification_type='escalation',
                    title=f'Complaint Auto-Escalated: #{complaint.id}',
                    message=f'Complaint from {complaint.user.email} has been auto-escalated after {days_old} days without resolution. Status: {complaint.status}, Category: {complaint.category or "N/A"}',
                    scheduled_at=timezone.now()
                )
        except Exception as e:
            logger.error(f'Error creating admin notification: {str(e)}')
    
    def _send_escalation_email(self, complaint, days_old):
        """Send escalation email to user and admins"""
        try:
            # Email to user
            user_subject = f'SmartGriev: Your Complaint #{complaint.id} Has Been Escalated'
            user_message = f"""
Dear {complaint.user.get_full_name() or complaint.user.email},

Your complaint (ID: {complaint.id}) has been automatically escalated for priority resolution.

Complaint Details:
- Filed on: {complaint.created_at.strftime('%B %d, %Y')}
- Days pending: {days_old}
- Current status: {complaint.status}
- Category: {complaint.category or 'General'}

Your complaint is now marked as HIGH PRIORITY and will receive immediate attention from our senior team.

We apologize for the delay and are committed to resolving this matter urgently.

Thank you for your patience.

Best regards,
SmartGriev Team
            """
            
            send_mail(
                user_subject,
                user_message,
                settings.DEFAULT_FROM_EMAIL,
                [complaint.user.email],
                fail_silently=True,
            )
            
            # Email to admins
            admin_emails = User.objects.filter(
                is_staff=True, 
                is_active=True,
                email__isnull=False
            ).values_list('email', flat=True)
            
            if admin_emails:
                admin_subject = f'SmartGriev: Auto-Escalation Alert - Complaint #{complaint.id}'
                admin_message = f"""
URGENT: Complaint Auto-Escalation Alert

Complaint ID: {complaint.id}
User: {complaint.user.email}
Days Pending: {days_old}
Current Status: {complaint.status}
Category: {complaint.category or 'General'}
Priority: HIGH (Auto-escalated)

This complaint requires immediate attention.

Action Required:
1. Review the complaint details
2. Contact the user
3. Provide resolution or update

Login to SmartGriev admin panel to take action.
                """
                
                send_mail(
                    admin_subject,
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL,
                    list(admin_emails),
                    fail_silently=True,
                )
        except Exception as e:
            logger.error(f'Error sending escalation email: {str(e)}')
