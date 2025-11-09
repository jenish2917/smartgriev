"""
SMS Notification Service using Twilio
"""

import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:
    """SMS notification service using Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        
        self.enabled = all([self.account_sid, self.auth_token, self.from_number])
        
        if self.enabled:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Twilio initialization error: {e}")
                self.enabled = False
        else:
            logger.warning("SMS service disabled - Twilio credentials not configured")
            self.client = None
    
    def send_sms(self, to_number: str, message: str) -> dict:
        """
        Send SMS to a phone number
        
        Args:
            to_number: Recipient phone number (with country code, e.g., +919876543210)
            message: SMS message text
            
        Returns:
            dict with success status and message
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'SMS service not configured'
            }
        
        # Validate phone number format
        if not to_number.startswith('+'):
            to_number = f'+91{to_number}'  # Default to India (+91)
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'to': to_number
            }
            
        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_complaint_created_sms(self, user, complaint):
        """Send SMS when complaint is created"""
        
        if not user.mobile:
            return {'success': False, 'error': 'User mobile number not available'}
        
        # Get user's preferred language
        language = getattr(user, 'language', 'en')
        
        # SMS templates in multiple languages
        templates = {
            'en': f"SmartGriev: Your complaint #{complaint.id} '{complaint.title[:50]}' has been registered successfully. Track status at smartgriev.com",
            'hi': f"SmartGriev: आपकी शिकायत #{complaint.id} '{complaint.title[:50]}' सफलतापूर्वक दर्ज की गई है। smartgriev.com पर स्थिति देखें",
            'bn': f"SmartGriev: আপনার অভিযোগ #{complaint.id} '{complaint.title[:50]}' সফলভাবে নিবন্ধিত হয়েছে। smartgriev.com এ স্থিতি ট্র্যাক করুন",
            'te': f"SmartGriev: మీ ఫిర్యాదు #{complaint.id} '{complaint.title[:50]}' విజయవంతంగా నమోదు చేయబడింది। smartgriev.com వద్ద స్థితిని ట్రాక్ చేయండి",
            'ta': f"SmartGriev: உங்கள் புகார் #{complaint.id} '{complaint.title[:50]}' வெற்றிகரமாக பதிவு செய்யப்பட்டது। smartgriev.com இல் நிலையைக் கண்காணிக்கவும்",
            'mr': f"SmartGriev: तुमची तक्रार #{complaint.id} '{complaint.title[:50]}' यशस्वीरित्या नोंदवली गेली आहे। smartgriev.com वर स्थिती पहा",
        }
        
        message = templates.get(language, templates['en'])
        
        return self.send_sms(user.mobile, message)
    
    def send_status_update_sms(self, user, complaint, new_status):
        """Send SMS when complaint status changes"""
        
        if not user.mobile:
            return {'success': False, 'error': 'User mobile number not available'}
        
        language = getattr(user, 'language', 'en')
        
        status_messages = {
            'in_progress': {
                'en': f"SmartGriev: Your complaint #{complaint.id} is now IN PROGRESS. We're working on it.",
                'hi': f"SmartGriev: आपकी शिकायत #{complaint.id} अब प्रगति में है। हम इस पर काम कर रहे हैं।",
                'bn': f"SmartGriev: আপনার অভিযোগ #{complaint.id} এখন চলছে। আমরা এটি নিয়ে কাজ করছি।",
            },
            'resolved': {
                'en': f"SmartGriev: Good news! Your complaint #{complaint.id} has been RESOLVED. Thank you for using SmartGriev.",
                'hi': f"SmartGriev: खुशखबरी! आपकी शिकायत #{complaint.id} हल हो गई है। SmartGriev उपयोग करने के लिए धन्यवाद।",
                'bn': f"SmartGriev: সুসংবাদ! আপনার অভিযোগ #{complaint.id} সমাধান হয়েছে। SmartGriev ব্যবহার করার জন্য ধন্যবাদ।",
            },
            'rejected': {
                'en': f"SmartGriev: Your complaint #{complaint.id} has been reviewed. Status: REJECTED. Please check details on our website.",
                'hi': f"SmartGriev: आपकी शिकायत #{complaint.id} की समीक्षा की गई है। स्थिति: अस्वीकृत। कृपया हमारी वेबसाइट पर विवरण देखें।",
                'bn': f"SmartGriev: আপনার অভিযোগ #{complaint.id} পর্যালোচনা করা হয়েছে। স্থিতি: প্রত্যাখ্যাত। আমাদের ওয়েবসাইটে বিস্তারিত দেখুন।",
            }
        }
        
        messages = status_messages.get(new_status, {})
        message = messages.get(language, messages.get('en', f"SmartGriev: Complaint #{complaint.id} status updated to {new_status}"))
        
        return self.send_sms(user.mobile, message)
    
    def send_bulk_sms(self, recipients: list, message: str) -> dict:
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of phone numbers
            message: SMS message text
            
        Returns:
            dict with results
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'SMS service not configured'
            }
        
        results = []
        success_count = 0
        failed_count = 0
        
        for phone in recipients:
            result = self.send_sms(phone, message)
            results.append({
                'phone': phone,
                'result': result
            })
            
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
        
        return {
            'success': True,
            'total': len(recipients),
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results
        }
    
    def get_sms_status(self, message_sid: str) -> dict:
        """Check status of sent SMS"""
        
        if not self.enabled:
            return {
                'success': False,
                'error': 'SMS service not configured'
            }
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'success': True,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'date_sent': message.date_sent,
                'price': message.price,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
sms_service = SMSService()
