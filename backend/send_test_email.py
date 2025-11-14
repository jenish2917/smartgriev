"""
Send test email to kancha user
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from authentication.models import User
from complaints.models import Complaint
from notifications.email_service import email_service

# Get kancha user
user = User.objects.get(username='kancha@123')
complaint = Complaint.objects.filter(user=user).first()

print(f"\n📧 Sending test email to: {user.email}")
print(f"   Complaint: #{complaint.id} - {complaint.title}")

# Test complaint created email
print("\n1️⃣  Sending 'Complaint Created' email...")
result1 = email_service.send_complaint_created_email(
    user=user,
    complaint=complaint,
    language='en'
)
print(f"   Result: {'✅ SUCCESS' if result1.get('success') else '❌ FAILED'}")
if not result1.get('success'):
    print(f"   Error: {result1.get('error')}")

# Test status update email
print("\n2️⃣  Sending 'Complaint Resolved' email...")
result2 = email_service.send_status_update_email(
    user=user,
    complaint=complaint,
    old_status='pending',
    new_status='resolved',
    language='en'
)
print(f"   Result: {'✅ SUCCESS' if result2.get('success') else '❌ FAILED'}")
if not result2.get('success'):
    print(f"   Error: {result2.get('error')}")

print(f"\n✅ Done! Check inbox at: {user.email}\n")
