"""
Management command to check and auto-escalate unresolved complaints
Run this as a cron job or scheduled task every day
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from complaints.models import Complaint
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check for complaints unresolved for 2-3 days and auto-escalate them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=2,
            help='Number of days to consider a complaint unresolved (default: 2)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be escalated without actually doing it',
        )

    def handle(self, *args, **options):
        days_threshold = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'Checking for unresolved complaints (>{days_threshold} days)...\n'
            f'{"="*60}\n'
        ))

        # Calculate the cutoff date
        cutoff_date = timezone.now() - timedelta(days=days_threshold)
        
        # Find complaints that are:
        # 1. Created more than X days ago
        # 2. Still in 'pending' or 'in_progress' status
        # 3. Not already escalated recently
        unresolved_complaints = Complaint.objects.filter(
            created_at__lte=cutoff_date,
            status__in=['pending', 'in_progress'],
        ).exclude(
            # Exclude if already escalated in last 24 hours
            escalated_at__gte=timezone.now() - timedelta(hours=24)
        )

        total_found = unresolved_complaints.count()
        
        if total_found == 0:
            self.stdout.write(self.style.SUCCESS(
                '✅ No unresolved complaints found. All complaints are being handled well!'
            ))
            return

        self.stdout.write(self.style.WARNING(
            f'⚠️  Found {total_found} unresolved complaints\n'
        ))

        escalated_count = 0
        
        for complaint in unresolved_complaints:
            days_pending = (timezone.now() - complaint.created_at).days
            
            self.stdout.write(
                f'\n📋 Complaint ID: {complaint.id}\n'
                f'   Title: {complaint.title}\n'
                f'   Status: {complaint.status}\n'
                f'   Days pending: {days_pending}\n'
                f'   Category: {complaint.category or "Not assigned"}\n'
                f'   Department: {complaint.department or "Not assigned"}\n'
            )

            if dry_run:
                self.stdout.write(self.style.WARNING(
                    '   [DRY RUN] Would escalate this complaint\n'
                ))
                continue

            # Auto-escalate the complaint
            try:
                self.escalate_complaint(complaint, days_pending)
                escalated_count += 1
                self.stdout.write(self.style.SUCCESS(
                    '   ✅ Successfully escalated!\n'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'   ❌ Error escalating: {str(e)}\n'
                ))
                logger.error(f'Error escalating complaint {complaint.id}: {str(e)}')

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'Summary:\n'
            f'  Total found: {total_found}\n'
            f'  Escalated: {escalated_count}\n'
            f'  Failed: {total_found - escalated_count}\n'
            f'{"="*60}\n'
        ))

    def escalate_complaint(self, complaint, days_pending):
        """
        Escalate a complaint by:
        1. Increasing priority
        2. Changing urgency level
        3. Adding escalation note
        4. Notifying authorities
        5. Updating timestamps
        """
        
        # Increase priority
        priority_levels = ['low', 'medium', 'high', 'urgent']
        current_priority = complaint.priority or 'medium'
        current_index = priority_levels.index(current_priority) if current_priority in priority_levels else 1
        new_priority = priority_levels[min(current_index + 1, len(priority_levels) - 1)]
        
        # Increase urgency
        urgency_levels = ['low', 'medium', 'high', 'critical']
        current_urgency = complaint.urgency_level or 'medium'
        current_urgency_index = urgency_levels.index(current_urgency) if current_urgency in urgency_levels else 1
        new_urgency = urgency_levels[min(current_urgency_index + 1, len(urgency_levels) - 1)]
        
        # Create escalation note
        escalation_note = (
            f"⚠️ AUTO-ESCALATED (Day {days_pending})\n"
            f"This complaint has been unresolved for {days_pending} days.\n"
            f"Priority increased: {current_priority} → {new_priority}\n"
            f"Urgency increased: {current_urgency} → {new_urgency}\n"
            f"Automated escalation by SmartGriev AI System.\n"
            f"Timestamp: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Update complaint
        complaint.priority = new_priority
        complaint.urgency_level = new_urgency
        complaint.escalated_at = timezone.now()
        complaint.escalation_count = (complaint.escalation_count or 0) + 1
        
        # Add note to description or comments
        if hasattr(complaint, 'admin_notes'):
            complaint.admin_notes = f"{complaint.admin_notes or ''}\n\n{escalation_note}"
        elif hasattr(complaint, 'internal_notes'):
            complaint.internal_notes = f"{complaint.internal_notes or ''}\n\n{escalation_note}"
        
        complaint.save()
        
        # Send notifications
        self.send_escalation_notifications(complaint, days_pending, escalation_note)
        
        logger.info(f'Escalated complaint {complaint.id} after {days_pending} days')

    def send_escalation_notifications(self, complaint, days_pending, escalation_note):
        """Send email notifications about escalation"""
        
        try:
            # Notify user
            if complaint.user and hasattr(complaint.user, 'email') and complaint.user.email:
                send_mail(
                    subject=f'SmartGriev: Your Complaint #{complaint.id} Has Been Escalated',
                    message=(
                        f'Dear {complaint.user.get_full_name() or complaint.user.username},\n\n'
                        f'Your complaint has been automatically escalated due to pending resolution.\n\n'
                        f'Complaint Details:\n'
                        f'  ID: {complaint.id}\n'
                        f'  Title: {complaint.title}\n'
                        f'  Status: {complaint.status}\n'
                        f'  Days Pending: {days_pending}\n'
                        f'  New Priority: {complaint.priority}\n'
                        f'  New Urgency: {complaint.urgency_level}\n\n'
                        f'We apologize for the delay. Your complaint is now receiving higher priority attention.\n\n'
                        f'Track your complaint: http://yoursite.com/my-complaints\n\n'
                        f'Thank you for your patience.\n'
                        f'SmartGriev Team'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[complaint.user.email],
                    fail_silently=True,
                )
            
            # Notify department officials
            if complaint.department and hasattr(complaint.department, 'email'):
                send_mail(
                    subject=f'URGENT: Complaint #{complaint.id} Auto-Escalated',
                    message=(
                        f'ATTENTION: Complaint requires immediate attention\n\n'
                        f'{escalation_note}\n\n'
                        f'Complaint Details:\n'
                        f'  ID: {complaint.id}\n'
                        f'  Title: {complaint.title}\n'
                        f'  Category: {complaint.category}\n'
                        f'  User: {complaint.user}\n'
                        f'  Created: {complaint.created_at.strftime("%Y-%m-%d %H:%M")}\n'
                        f'  Days Pending: {days_pending}\n\n'
                        f'Please take immediate action.\n'
                        f'SmartGriev Auto-Escalation System'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[complaint.department.email],
                    fail_silently=True,
                )
                
        except Exception as e:
            logger.warning(f'Failed to send escalation notification: {str(e)}')
