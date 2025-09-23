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
from django.db import models
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.backends import BaseBackend

import pyotp
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

# Get user model reference
UserModel = get_user_model()

class OTPVerification(models.Model):
    """OTP verification for phone and email"""
    
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='otp_verifications')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(
        max_length=20,
        choices=[
            ('registration', 'Registration'),
            ('login', 'Login'),
            ('password_reset', 'Password Reset'),
            ('phone_verification', 'Phone Verification'),
            ('email_verification', 'Email Verification'),
        ]
    )
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'otp_type']),
            models.Index(fields=['email', 'otp_type']),
            models.Index(fields=['created_at']),
        ]
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.is_expired() and not self.is_verified and self.attempts < self.max_attempts
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # 10 minutes expiry
        super().save(*args, **kwargs)

class LoginSession(models.Model):
    """Track user login sessions"""
    
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='login_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    device_info = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]

@dataclass
class OTPResult:
    """Result of OTP operations"""
    success: bool
    message: str
    otp_id: Optional[int] = None
    expires_in: Optional[int] = None

class AdvancedAuthService:
    """
    Advanced authentication service with OTP verification
    Supports multiple authentication methods and security features
    """
    
    def __init__(self):
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.otp_length = 6
        self.otp_expiry = timedelta(minutes=10)
    
    async def register_user(
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
                await self.send_phone_otp(user, phone_number, 'registration')
            if email:
                await self.send_email_otp(user, email, 'registration')
            
            return True, "User registered successfully. Please verify your contact details.", user
            
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False, "Registration failed. Please try again.", None
    
    async def send_phone_otp(self, user: Any, phone_number: str, otp_type: str) -> OTPResult:
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
            await self.send_sms(phone_number, otp_code, otp_type)
            
            return OTPResult(
                success=True,
                message=f"OTP sent to {phone_number}",
                otp_id=otp_record.id,
                expires_in=600  # 10 minutes
            )
            
        except Exception as e:
            logger.error(f"Phone OTP failed: {e}")
            return OTPResult(
                success=False,
                message="Failed to send OTP. Please try again."
            )
    
    async def send_email_otp(self, user: Any, email: str, otp_type: str) -> OTPResult:
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
            await self.send_email(email, otp_code, otp_type)
            
            return OTPResult(
                success=True,
                message=f"OTP sent to {email}",
                otp_id=otp_record.id,
                expires_in=600  # 10 minutes
            )
            
        except Exception as e:
            logger.error(f"Email OTP failed: {e}")
            return OTPResult(
                success=False,
                message="Failed to send OTP. Please try again."
            )
    
    def generate_otp(self) -> str:
        """Generate secure OTP"""
        return ''.join(random.choices(string.digits, k=self.otp_length))
    
    async def send_sms(self, phone_number: str, otp_code: str, otp_type: str):
        """Send SMS using SMS provider (implement with your chosen provider)"""
        # Example with Twilio (uncomment and configure)
        """
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = f"Your SmartGriev {otp_type} OTP is: {otp_code}. Valid for 10 minutes. Do not share with anyone."
        
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        """
        
        # For now, just log the OTP (remove in production)
        logger.info(f"SMS OTP for {phone_number}: {otp_code}")
    
    async def send_email(self, email: str, otp_code: str, otp_type: str):
        """Send OTP email"""
        subject = f"SmartGriev {otp_type.title()} OTP"
        message = f"""
        Dear User,
        
        Your OTP for {otp_type} is: {otp_code}
        
        This OTP is valid for 10 minutes only.
        Do not share this OTP with anyone.
        
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
    
    async def verify_otp(self, otp_id: int, otp_code: str) -> Tuple[bool, str]:
        """Verify OTP code"""
        try:
            otp_record = OTPVerification.objects.get(id=otp_id)
            
            # Check if OTP is still valid
            if not otp_record.is_valid():
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
                return False, f"Invalid OTP. {otp_record.max_attempts - otp_record.attempts} attempts remaining"
                
        except OTPVerification.DoesNotExist:
            return False, "Invalid OTP record"
        except Exception as e:
            logger.error(f"OTP verification failed: {e}")
            return False, "OTP verification failed"
    
    async def authenticate_user(
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