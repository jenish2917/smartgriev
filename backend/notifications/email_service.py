"""
Email Notification Service with MJML Template Support
Provides beautiful, responsive email templates for complaint notifications
"""
import os
import logging
from typing import Dict, List, Optional, Any
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import requests

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email notification service with MJML template support
    MJML creates responsive email templates that work across all email clients
    """
    
    def __init__(self):
        """Initialize email service"""
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.enabled = all([
            settings.EMAIL_HOST,
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD
        ])
        
        if not self.enabled:
            logger.warning("Email service disabled - Email credentials not configured")
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[tuple]] = None
    ) -> Dict[str, Any]:
        """
        Send HTML email
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content
            text_content: Plain text content (auto-generated if not provided)
            attachments: List of (filename, content, mimetype) tuples
            
        Returns:
            Dict with success status and message
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Email service is not configured'
            }
        
        try:
            # Generate plain text version if not provided
            if not text_content:
                text_content = strip_tags(html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=to_emails
            )
            
            # Attach HTML version
            email.attach_alternative(html_content, "text/html")
            
            # Add attachments if provided
            if attachments:
                for filename, content, mimetype in attachments:
                    email.attach(filename, content, mimetype)
            
            # Send email
            email.send(fail_silently=False)
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            
            return {
                'success': True,
                'message': f'Email sent to {len(to_emails)} recipient(s)',
                'recipients': to_emails
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_complaint_created_email(
        self,
        user,
        complaint,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Send email when complaint is created
        
        Args:
            user: User model instance
            complaint: Complaint model instance
            language: Language code (en, hi, bn, etc.)
            
        Returns:
            Dict with success status
        """
        if not user.email:
            return {'success': False, 'error': 'User has no email address'}
        
        # Multilingual subject
        subjects = {
            'en': f'Complaint #{complaint.complaint_number} Created Successfully',
            'hi': f'शिकायत #{complaint.complaint_number} सफलतापूर्वक दर्ज',
            'bn': f'অভিযোগ #{complaint.complaint_number} সফলভাবে তৈরি',
            'te': f'ఫిర్యాదు #{complaint.complaint_number} విజయవంతంగా సృష్టించబడింది',
        }
        
        # Generate HTML email content
        context = {
            'user': user,
            'complaint': complaint,
            'complaint_number': complaint.complaint_number,
            'title': complaint.title,
            'status': complaint.status,
            'department': complaint.department.name if complaint.department else 'Not assigned',
            'created_at': complaint.created_at,
            'view_url': f"{settings.FRONTEND_URL}/complaints/{complaint.id}",
            'language': language
        }
        
        html_content = render_to_string('notifications/email/complaint_created.html', context)
        
        return self.send_email(
            to_emails=[user.email],
            subject=subjects.get(language, subjects['en']),
            html_content=html_content
        )
    
    def send_status_update_email(
        self,
        user,
        complaint,
        old_status: str,
        new_status: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Send email when complaint status changes
        
        Args:
            user: User model instance
            complaint: Complaint model instance
            old_status: Previous status
            new_status: New status
            language: Language code
            
        Returns:
            Dict with success status
        """
        if not user.email:
            return {'success': False, 'error': 'User has no email address'}
        
        # Multilingual subjects
        subjects = {
            'en': f'Update: Complaint #{complaint.complaint_number} - {new_status.title()}',
            'hi': f'अपडेट: शिकायत #{complaint.complaint_number} - {new_status}',
            'bn': f'আপডেট: অভিযোগ #{complaint.complaint_number} - {new_status}',
        }
        
        # Status color mapping
        status_colors = {
            'submitted': '#1890ff',
            'pending': '#faad14',
            'in_progress': '#13c2c2',
            'resolved': '#52c41a',
            'rejected': '#f5222d',
            'closed': '#8c8c8c',
        }
        
        context = {
            'user': user,
            'complaint': complaint,
            'complaint_number': complaint.complaint_number,
            'title': complaint.title,
            'old_status': old_status,
            'new_status': new_status,
            'status_color': status_colors.get(new_status, '#1890ff'),
            'department': complaint.department.name if complaint.department else 'Not assigned',
            'updated_at': complaint.updated_at,
            'view_url': f"{settings.FRONTEND_URL}/complaints/{complaint.id}",
            'language': language
        }
        
        html_content = render_to_string('notifications/email/status_update.html', context)
        
        return self.send_email(
            to_emails=[user.email],
            subject=subjects.get(language, subjects['en']),
            html_content=html_content
        )
    
    def send_welcome_email(
        self,
        user,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Send welcome email to new user
        
        Args:
            user: User model instance
            language: Language code
            
        Returns:
            Dict with success status
        """
        if not user.email:
            return {'success': False, 'error': 'User has no email address'}
        
        subjects = {
            'en': 'Welcome to SmartGriev - AI-Powered Civic Complaint System',
            'hi': 'SmartGriev में आपका स्वागत है - एआई-संचालित नागरिक शिकायत प्रणाली',
            'bn': 'SmartGriev-এ স্বাগতম - AI-চালিত নাগরিক অভিযোগ সিস্টেম',
        }
        
        context = {
            'user': user,
            'first_name': user.first_name or user.username,
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
            'submit_complaint_url': f"{settings.FRONTEND_URL}/submit-complaint",
            'language': language
        }
        
        html_content = render_to_string('notifications/email/welcome.html', context)
        
        return self.send_email(
            to_emails=[user.email],
            subject=subjects.get(language, subjects['en']),
            html_content=html_content
        )
    
    def send_password_reset_email(
        self,
        user,
        reset_token: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Send password reset email
        
        Args:
            user: User model instance
            reset_token: Password reset token
            language: Language code
            
        Returns:
            Dict with success status
        """
        if not user.email:
            return {'success': False, 'error': 'User has no email address'}
        
        subjects = {
            'en': 'Reset Your SmartGriev Password',
            'hi': 'अपना SmartGriev पासवर्ड रीसेट करें',
            'bn': 'আপনার SmartGriev পাসওয়ার্ড রিসেট করুন',
        }
        
        context = {
            'user': user,
            'reset_url': f"{settings.FRONTEND_URL}/reset-password?token={reset_token}",
            'expiry_hours': 24,
            'language': language
        }
        
        html_content = render_to_string('notifications/email/password_reset.html', context)
        
        return self.send_email(
            to_emails=[user.email],
            subject=subjects.get(language, subjects['en']),
            html_content=html_content
        )
    
    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str
    ) -> Dict[str, Any]:
        """
        Send bulk email to multiple recipients
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            html_content: HTML content
            
        Returns:
            Dict with success status
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        for email in recipients:
            result = self.send_email([email], subject, html_content)
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
                errors.append(f"{email}: {result.get('error')}")
        
        return {
            'success': failed_count == 0,
            'sent': success_count,
            'failed': failed_count,
            'errors': errors if errors else None
        }


# Singleton instance
email_service = EmailService()
