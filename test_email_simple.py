"""
Simple Email Test - Direct SMTP test without Django models
Tests if email credentials work
"""
import sys
import os
import django

# Setup Django environment
sys.path.append(r'd:\SmartGriev\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings


def test_simple_email():
    """Send a simple test email"""
    print("\n" + "="*60)
    print("SIMPLE EMAIL TEST")
    print("="*60)
    
    print(f"\n📧 Email Configuration:")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   User: {settings.EMAIL_HOST_USER}")
    print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
    
    test_email = settings.EMAIL_HOST_USER
    
    print(f"\n📨 Sending test email to: {test_email}")
    print("   Subject: SmartGriev - Email Test")
    print("   Please wait...")
    
    try:
        # Send simple text email
        result = send_mail(
            subject='SmartGriev - Email Test',
            message='This is a test email from SmartGriev notification system. If you received this, email notifications are working correctly!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if result == 1:
            print(f"\n✅ SUCCESS! Email sent successfully!")
            print(f"\n🔍 CHECK YOUR INBOX: {test_email}")
            print("   - Check spam/junk folder if not in inbox")
            print("   - Email should arrive within 1-2 minutes")
            print("\n✨ Email notification system is working!")
            return True
        else:
            print(f"\n❌ FAILED: Email not sent (result: {result})")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("\nIf you see 'Authentication failed' or 'Username and Password not accepted':")
        print("   Your Gmail password 'jenish_12345' might not work directly.")
        print("   Gmail requires an 'App Password' for SMTP access.")
        print("\n📝 How to fix:")
        print("   1. Go to: https://myaccount.google.com/apppasswords")
        print("   2. Enable 2-Factor Authentication (if not already enabled)")
        print("   3. Generate an 'App Password' for 'Mail'")
        print("   4. Copy the 16-character password (e.g., 'abcd efgh ijkl mnop')")
        print("   5. Update EMAIL_HOST_PASSWORD in .env with this App Password")
        print("   6. Remove spaces: 'abcdefghijklmnop'")
        print("\nIf you see 'Connection refused' or 'Network error':")
        print("   - Check if antivirus/firewall is blocking SMTP port 587")
        print("   - Try disabling VPN temporarily")
        print("   - Ensure internet connection is stable")
        
        return False


if __name__ == '__main__':
    print("\n" + "🧪"*30)
    print("SmartGriev Email Notification Test")
    print("🧪"*30)
    
    print("\n⚠️  This will send a real email to:")
    print(f"   {settings.EMAIL_HOST_USER}")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    success = test_simple_email()
    
    if success:
        print("\n" + "="*60)
        print("🎉 EMAIL TEST PASSED!")
        print("="*60)
        print("\nNotification system is ready to use.")
        print("Users will receive emails for:")
        print("   - Complaint created")
        print("   - Status updates")
        print("   - Password reset")
        print("   - Welcome messages")
    else:
        print("\n" + "="*60)
        print("❌ EMAIL TEST FAILED")
        print("="*60)
        print("\nPlease fix the email configuration before using notifications.")
