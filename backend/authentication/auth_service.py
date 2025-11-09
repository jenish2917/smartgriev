# Advanced Authentication Service with OTP Verification
# Supports email, mobile, and Google authentication

import random
import string
import asyncio
import logging
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

# Import models
from .models import User, OTPVerification, LoginSession

logger = logging.getLogger(__name__)


@dataclass
class OTPResult:
    """Result of OTP operations"""
    success: bool
    message: str
    data: Optional[Dict] = None


class AdvancedAuthService:
    """
    Advanced authentication service with OTP support
    """
    
    def __init__(self):
        """Initialize the authentication service"""
        self.otp_length = 6
        self.otp_expiry_minutes = 10
        self.max_otp_attempts = 3
        
        logger.info("AdvancedAuthService initialized")
    
    def generate_otp(self) -> str:
        """Generate a random 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=self.otp_length))
    
    def register_user(
        self, 
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        password: str = None,
        first_name: str = "",
        last_name: str = "",
        **kwargs
    ) -> Tuple[bool, str, Optional[Any]]:
        """Register a new user with OTP verification"""
        try:
            # Validate input
            if not phone_number and not email:
                return False, "Either phone number or email is required", None
            
            # Check if user already exists
            if phone_number and User.objects.filter(mobile=phone_number).exists():
                return False, "Phone number already registered", None
            
            if email and User.objects.filter(email=email).exists():
                return False, "Email already registered", None
            
            # Create user
            username = phone_number or email.split('@')[0]
            user = User.objects.create_user(
                username=username,
                email=email,
                mobile=phone_number or "",
                first_name=first_name,
                last_name=last_name,
                **kwargs
            )
            
            if password:
                user.set_password(password)
                user.save()
            
            # Send verification OTP
            if phone_number:
                self.send_phone_otp(user, phone_number, 'registration')
            if email:
                self.send_email_otp(user, email, 'registration')
            
            return True, "User registered successfully. Please verify your contact details.", user
            
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False, "Registration failed. Please try again.", None
    
    def send_phone_otp(self, user: Any, phone_number: str, otp_type: str) -> OTPResult:
        """Send OTP to phone number"""
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            
            # Create OTP record
            otp_record = OTPVerification.objects.create(
                user=user,
                phone_number=phone_number,
                otp_code=otp_code,
                otp_type=otp_type
            )
            
            # Send SMS (integrate with your SMS provider)
            # For now, just log the OTP (in production, integrate with Twilio/other SMS service)
            logger.info(f"SMS OTP for {phone_number}: {otp_code}")
            
            # In production, uncomment and configure:
            # self._send_sms(phone_number, otp_code, otp_type)
            
            return OTPResult(
                success=True,
                message=f"OTP sent to {phone_number}",
                data={"otp_id": otp_record.id}
            )
            
        except Exception as e:
            logger.error(f"Failed to send phone OTP: {e}")
            return OTPResult(
                success=False,
                message="Failed to send OTP"
            )
    
    def send_email_otp(self, user: Any, email: str, otp_type: str) -> OTPResult:
        """Send OTP to email"""
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            
            # Create OTP record
            otp_record = OTPVerification.objects.create(
                user=user,
                email=email,
                otp_code=otp_code,
                otp_type=otp_type
            )
            
            # Send email
            self._send_email(email, otp_code, otp_type)
            
            return OTPResult(
                success=True,
                message=f"OTP sent to {email}",
                data={"otp_id": otp_record.id}
            )
            
        except Exception as e:
            logger.error(f"Failed to send email OTP: {e}")
            return OTPResult(
                success=False,
                message="Failed to send OTP"
            )
    
    def _send_sms(self, phone_number: str, otp_code: str, otp_type: str):
        """
        Send SMS using Twilio (configure in production)
        """
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = f"Your SmartGriev {otp_type} OTP is: {otp_code}. Valid for 10 minutes. Do not share with anyone."
        
        try:
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            logger.info(f"SMS sent successfully to {phone_number}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            raise
    
    def _send_email(self, email: str, otp_code: str, otp_type: str):
        """Send OTP email"""
        subject = f"SmartGriev {otp_type.title()} OTP"
        message = f"""
        Dear User,
        
        Your SmartGriev {otp_type} OTP is: {otp_code}
        
        This OTP is valid for 10 minutes. Please do not share this with anyone.
        
        If you did not request this OTP, please ignore this email.
        
        Regards,
        SmartGriev Team
        Government of India
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    
    def verify_otp(self, user_id: int, otp_code: str, otp_type: str) -> Tuple[bool, str]:
        """Verify OTP code"""
        try:
            # Find the latest OTP record
            otp_record = OTPVerification.objects.filter(
                user_id=user_id,
                otp_type=otp_type,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not otp_record:
                return False, "No OTP found or already verified"
            
            # Check if OTP is expired or max attempts exceeded
            if otp_record.is_expired() or otp_record.attempts >= otp_record.max_attempts:
                return False, "OTP has expired or exceeded maximum attempts"
            
            # Increment attempts
            otp_record.attempts += 1
            otp_record.save()
            
            # Verify OTP
            if otp_record.otp_code == otp_code:
                otp_record.is_verified = True
                otp_record.verified_at = timezone.now()
                otp_record.save()
                
                return True, "OTP verified successfully"
            else:
                return False, "Invalid OTP code"
                
        except Exception as e:
            logger.error(f"OTP verification failed: {e}")
            return False, "OTP verification failed"
    
    def authenticate_user(
        self, 
        identifier: str,  # phone/email/username
        password: str,
        request_ip: str = None
    ) -> Tuple[bool, str, Optional[Any]]:
        """Authenticate user with multiple login methods"""
        try:
            # Find user by phone, email, or username
            user = None
            if identifier.isdigit() and len(identifier) >= 10:
                user = User.objects.filter(mobile=identifier).first()
            elif '@' in identifier:
                user = User.objects.filter(email=identifier).first()
            else:
                user = User.objects.filter(username=identifier).first()
            
            if not user:
                return False, "User not found", None
            
            # Verify password
            if not user.check_password(password):
                return False, "Invalid credentials", None
            
            # Update last login
            user.last_login = timezone.now()
            user.save()
            
            return True, "Login successful", user
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False, "Authentication failed", None

# Initialize global auth service
auth_service = AdvancedAuthService()