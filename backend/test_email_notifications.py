"""
Test Email Notification System
Tests complaint registration and resolution emails
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from authentication.models import User
from complaints.models import Complaint
from notifications.email_service import email_service
from notifications.models import NotificationPreference

def test_email_configuration():
    """Test basic email configuration"""
    print("\n" + "="*80)
    print("TESTING EMAIL CONFIGURATION")
    print("="*80 + "\n")
    
    if email_service.enabled:
        print("✅ Email service is ENABLED")
        print(f"   From Email: {email_service.from_email}")
        print(f"   SMTP Host: {os.getenv('EMAIL_HOST')}")
        print(f"   SMTP User: {os.getenv('EMAIL_HOST_USER')}")
    else:
        print("❌ Email service is DISABLED")
        print("   Please configure EMAIL_HOST, EMAIL_HOST_USER, and EMAIL_HOST_PASSWORD in .env")
        return False
    
    return True

def test_complaint_created_email():
    """Test complaint creation email"""
    print("\n" + "="*80)
    print("TESTING COMPLAINT CREATED EMAIL")
    print("="*80 + "\n")
    
    # Find a user with email
    user = User.objects.filter(email__isnull=False).exclude(email='').first()
    
    if not user:
        print("❌ No user found with email address")
        return
    
    print(f"Using test user: {user.username} ({user.email})")
    
    # Ensure user has email preferences enabled
    prefs, created = NotificationPreference.objects.get_or_create(user=user)
    if not prefs.email_enabled:
        prefs.email_enabled = True
        prefs.save()
        print(f"   Enabled email notifications for user")
    
    # Find a recent complaint or create test data
    complaint = Complaint.objects.filter(user=user).first()
    
    if not complaint:
        print("❌ No complaint found for this user")
        print("   Please create a complaint via the chatbot first")
        return
    
    print(f"\nUsing complaint:")
    print(f"   ID: #{complaint.id}")
    print(f"   Title: {complaint.title}")
    print(f"   Status: {complaint.status}")
    print(f"   Created: {complaint.created_at}")
    
    # Send test email
    print(f"\n📧 Sending complaint created email to {user.email}...")
    
    result = email_service.send_complaint_created_email(
        user=user,
        complaint=complaint,
        language=user.language_preference if hasattr(user, 'language_preference') else 'en'
    )
    
    if result.get('success'):
        print(f"✅ Email sent successfully!")
        print(f"   Recipients: {result.get('recipients')}")
        print(f"   Message: {result.get('message')}")
    else:
        print(f"❌ Email failed to send")
        print(f"   Error: {result.get('error')}")

def test_status_update_email():
    """Test status update email"""
    print("\n" + "="*80)
    print("TESTING STATUS UPDATE EMAIL (RESOLVED)")
    print("="*80 + "\n")
    
    # Find a user with email
    user = User.objects.filter(email__isnull=False).exclude(email='').first()
    
    if not user:
        print("❌ No user found with email address")
        return
    
    print(f"Using test user: {user.username} ({user.email})")
    
    # Find a complaint
    complaint = Complaint.objects.filter(user=user).first()
    
    if not complaint:
        print("❌ No complaint found for this user")
        return
    
    print(f"\nUsing complaint:")
    print(f"   ID: #{complaint.id}")
    print(f"   Title: {complaint.title}")
    print(f"   Current Status: {complaint.status}")
    
    # Send test email simulating status change
    print(f"\n📧 Sending status update email (pending → resolved)...")
    
    result = email_service.send_status_update_email(
        user=user,
        complaint=complaint,
        old_status='pending',
        new_status='resolved',
        language=user.language_preference if hasattr(user, 'language_preference') else 'en'
    )
    
    if result.get('success'):
        print(f"✅ Email sent successfully!")
        print(f"   Recipients: {result.get('recipients')}")
    else:
        print(f"❌ Email failed to send")
        print(f"   Error: {result.get('error')}")

def main():
    """Run all email tests"""
    print("\n" + "🎯"*40)
    print("EMAIL NOTIFICATION SYSTEM TEST")
    print("🎯"*40)
    
    # Test 1: Email configuration
    if not test_email_configuration():
        print("\n❌ Email service not configured. Exiting...")
        return
    
    # Test 2: Complaint created email
    test_complaint_created_email()
    
    # Test 3: Status update email
    test_status_update_email()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\n💡 TIP: Check your email inbox (including spam folder)")
    print("   Email sent from:", email_service.from_email)
    print("\n")

if __name__ == '__main__':
    main()
