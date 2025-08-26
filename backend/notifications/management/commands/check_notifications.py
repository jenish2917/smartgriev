"""
Management command to check notification system dependencies and capabilities
"""

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Check notification system dependencies and capabilities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about each dependency',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('SmartGriev Notification System - Dependency Check')
        )
        self.stdout.write('=' * 60)
        
        # Check core capabilities
        self.stdout.write('\n📧 Core Capabilities (Always Available):')
        self.stdout.write('  ✅ Email notifications')
        self.stdout.write('  ✅ Webhook notifications')
        self.stdout.write('  ✅ Notification queue processing')
        
        # Check optional dependencies
        self.stdout.write('\n🔧 Optional Dependencies:')
        
        # Firebase
        firebase_available = self._check_firebase()
        status = '✅' if firebase_available else '❌'
        self.stdout.write(f'  {status} Firebase (Push notifications)')
        if verbose and not firebase_available:
            self.stdout.write('      Install: pip install firebase-admin')
        
        # Twilio
        twilio_available = self._check_twilio()
        status = '✅' if twilio_available else '❌'
        self.stdout.write(f'  {status} Twilio (SMS notifications)')
        if verbose and not twilio_available:
            self.stdout.write('      Install: pip install twilio')
        
        # Channels
        channels_available = self._check_channels()
        status = '✅' if channels_available else '❌'
        self.stdout.write(f'  {status} Channels (Real-time notifications)')
        if verbose and not channels_available:
            self.stdout.write('      Install: pip install channels channels-redis')
        
        # Sentry
        sentry_available = self._check_sentry()
        status = '✅' if sentry_available else '❌'
        self.stdout.write(f'  {status} Sentry (Error monitoring)')
        if verbose and not sentry_available:
            self.stdout.write('      Install: pip install sentry-sdk[django]')
        
        # Configuration check
        self.stdout.write('\n⚙️  Configuration Status:')
        
        # Email configuration
        email_configured = self._check_email_config()
        status = '✅' if email_configured else '⚠️'
        self.stdout.write(f'  {status} Email backend configured')
        
        if firebase_available:
            firebase_configured = self._check_firebase_config()
            status = '✅' if firebase_configured else '⚠️'
            self.stdout.write(f'  {status} Firebase credentials configured')
        
        if twilio_available:
            twilio_configured = self._check_twilio_config()
            status = '✅' if twilio_configured else '⚠️'
            self.stdout.write(f'  {status} Twilio credentials configured')
        
        if sentry_available:
            sentry_configured = self._check_sentry_config()
            status = '✅' if sentry_configured else '⚠️'
            self.stdout.write(f'  {status} Sentry DSN configured')
        
        # Summary
        total_features = 4  # Firebase, Twilio, Channels, Sentry
        available_features = sum([
            firebase_available, twilio_available, 
            channels_available, sentry_available
        ])
        
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'  Available features: {available_features}/{total_features}')
        
        if available_features == total_features:
            self.stdout.write(
                self.style.SUCCESS('  🎉 All notification features are available!')
            )
        elif available_features > 0:
            self.stdout.write(
                self.style.WARNING('  ⚡ Partial functionality - some features available')
            )
        else:
            self.stdout.write(
                self.style.WARNING('  📦 Basic functionality only - consider installing optional dependencies')
            )
        
        self.stdout.write('\nFor installation instructions, see: notifications/README.md')

    def _check_firebase(self):
        """Check if Firebase Admin SDK is available"""
        try:
            import firebase_admin
            return True
        except ImportError:
            return False

    def _check_twilio(self):
        """Check if Twilio SDK is available"""
        try:
            from twilio.rest import Client
            return True
        except ImportError:
            return False

    def _check_channels(self):
        """Check if Django Channels is available"""
        try:
            from channels.layers import get_channel_layer
            return True
        except ImportError:
            return False

    def _check_sentry(self):
        """Check if Sentry SDK is available"""
        try:
            import sentry_sdk
            return True
        except ImportError:
            return False

    def _check_email_config(self):
        """Check if email is properly configured"""
        return hasattr(settings, 'EMAIL_BACKEND') and settings.EMAIL_BACKEND

    def _check_firebase_config(self):
        """Check if Firebase is properly configured"""
        return (
            hasattr(settings, 'FIREBASE_CREDENTIALS_PATH') and 
            settings.FIREBASE_CREDENTIALS_PATH
        )

    def _check_twilio_config(self):
        """Check if Twilio is properly configured"""
        return (
            hasattr(settings, 'TWILIO_ACCOUNT_SID') and 
            hasattr(settings, 'TWILIO_AUTH_TOKEN') and
            settings.TWILIO_ACCOUNT_SID and 
            settings.TWILIO_AUTH_TOKEN
        )

    def _check_sentry_config(self):
        """Check if Sentry is properly configured"""
        return hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN
