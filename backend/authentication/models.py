from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    language = models.CharField(max_length=10, default='en')
    is_officer = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class OTPVerification(models.Model):
    """OTP verification model for user authentication"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_verifications')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, default='login')
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_type}"


class LoginSession(models.Model):
    """Track user login sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_sessions')
    session_token = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Session for {self.user.username}"
