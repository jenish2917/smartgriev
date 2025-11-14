from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    # Language choices for India
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi - हिन्दी'),
        ('bn', 'Bengali - বাংলা'),
        ('te', 'Telugu - తెలుగు'),
        ('mr', 'Marathi - मराठी'),
        ('ta', 'Tamil - தமிழ்'),
        ('gu', 'Gujarati - ગુજરાતી'),
        ('kn', 'Kannada - ಕನ್ನಡ'),
        ('ml', 'Malayalam - മലയാളം'),
        ('pa', 'Punjabi - ਪੰਜਾਬੀ'),
        ('or', 'Odia - ଓଡ଼ିଆ'),
        ('as', 'Assamese - অসমীয়া'),
    ]

    mobile = models.CharField(max_length=15, blank=True, null=True, db_index=True)
    address = models.TextField(blank=True, null=True)

    # Multi-lingual preferences
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text='Preferred language for UI and communications'
    )
    preferred_language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text='Primary language preference (same as language, for backward compatibility)'
    )
    voice_language_preference = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text='Preferred language for voice input/output'
    )

    # Accessibility settings
    accessibility_mode = models.BooleanField(
        default=False,
        help_text='Enable accessibility features like screen reader support'
    )
    high_contrast_mode = models.BooleanField(
        default=False,
        help_text='Enable high contrast visual theme'
    )
    text_size_preference = models.CharField(
        max_length=10,
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('xlarge', 'Extra Large')],
        default='medium',
        help_text='Preferred text size'
    )

    # User role
    is_officer = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def get_display_language(self):
        """Get the language name in both English and native script"""
        return dict(self.LANGUAGE_CHOICES).get(self.language, 'English')


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


class VerificationToken(models.Model):
    """Token model for email verification, password reset, and other verification purposes"""
    TOKEN_TYPES = [
        ('email', 'Email Verification'),
        ('mobile', 'Mobile Verification'),
        ('password', 'Password Reset'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=255, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES, default='email')
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.token_type} token for {self.user.username}"
