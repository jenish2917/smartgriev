# Email Notifications Implementation

## Overview
Implemented automatic email notifications for complaint registration and status updates (especially when resolved).

## Changes Made

### 1. Updated Signal Handlers (`backend/notifications/signals.py`)

**Added Features:**
- ✅ Email notification when complaint is created
- ✅ Email notification when complaint status changes (especially resolved)
- ✅ Track previous status to detect changes using `pre_save` signal
- ✅ Support for user language preferences
- ✅ Logging for email success/failure

**Key Changes:**
```python
# Import email service
from .email_service import email_service

# Store previous status
_complaint_previous_status = {}

@receiver(pre_save, sender=Complaint)
def store_previous_status(sender, instance, **kwargs):
    """Store previous status before save to detect changes"""
    
@receiver(post_save, sender=Complaint)
def send_complaint_notification(sender, instance, created, **kwargs):
    """Send notifications via email, SMS, and in-app"""
```

**Email Triggers:**
1. **Complaint Created** (`created=True`):
   - Sends "Complaint Registered" email
   - Includes complaint details, ID, tracking link
   - Multilingual support

2. **Status Changed** (`old_status != new_status`):
   - Sends "Status Update" email
   - Highlights the status change (pending → resolved)
   - Includes updated complaint information

### 2. Added FRONTEND_URL Setting (`backend/smartgriev/settings.py`)

```python
# Frontend URL for email links
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
```

This enables clickable links in emails to view complaints on the frontend.

### 3. Email Templates

**Existing Templates Used:**
- `backend/notifications/templates/notifications/email/complaint_created.html`
  - Professional HTML design
  - Responsive layout
  - Complaint details card
  - "View Complaint" button
  - Multilingual subject support

- `backend/notifications/templates/notifications/email/status_update.html`
  - Status change notification
  - Color-coded status badges
  - Old vs New status comparison
  - Action buttons

### 4. Email Service (`backend/notifications/email_service.py`)

**Already Existing Methods:**
- `send_complaint_created_email()` - Sends complaint registration confirmation
- `send_status_update_email()` - Sends status change notifications
- Multilingual support (English, Hindi, Bengali, Telugu, etc.)

### 5. Test Scripts

**Created:**
1. `backend/test_email_notifications.py` - Comprehensive email system test
2. `backend/send_test_email.py` - Quick test for specific user

**Run Tests:**
```bash
cd backend
python send_test_email.py
```

## Email Configuration

**Required Environment Variables (.env):**
```properties
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Gmail App Password
DEFAULT_FROM_EMAIL=SmartGriev <your-email@gmail.com>
FRONTEND_URL=http://localhost:5173
```

### Gmail Setup:
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character password
3. Use this password in `EMAIL_HOST_PASSWORD` (no spaces)

## User Preferences

Email notifications respect user preferences:

**Model:** `NotificationPreference`
- `email_enabled` - Master email toggle (default: True)
- `notify_complaint_created` - Complaint registration emails
- `notify_status_changed` - Status update emails
- `notify_resolved` - Resolution emails

Users can manage these in their account settings.

## Email Flow

### Complaint Registration:
```
1. User submits complaint via chatbot
2. Complaint saved to database
3. post_save signal triggered
4. Email service sends registration email
5. User receives email with:
   - Complaint ID
   - Title & Description
   - Department assigned
   - Tracking link
```

### Status Change (Resolution):
```
1. Admin/Officer changes complaint status
2. pre_save stores old status
3. Complaint saved with new status
4. post_save detects status change
5. Email service sends update email
6. User receives email with:
   - Status change notification
   - Old vs New status
   - Resolution details (if resolved)
   - View complaint link
```

## Testing Results

**Test Run Output:**
```bash
📧 Sending test email to: kanchachina@gmail.com
   Complaint: #57 - URGENT Water Leak at 123 Main St, Apt 4B

1️⃣  Sending 'Complaint Created' email...
   Result: ✅ SUCCESS

2️⃣  Sending 'Complaint Resolved' email...
   Result: ✅ SUCCESS
```

## Logging

**Email events are logged:**
```python
logger.info(f"[EMAIL] Sending complaint created email to {user.email}")
logger.info(f"[EMAIL] ✅ Complaint created email sent successfully")
logger.error(f"[EMAIL] ❌ Failed to send email: {error}")
```

**View logs:** `backend/logs/django.log`

## Notification Model Tracking

Each notification tracks delivery status:
```python
notification.sent_via_email = True  # Email sent
notification.sent_via_sms = True    # SMS sent (if enabled)
notification.sent_via_push = True   # Push notification (if enabled)
```

## Multilingual Support

Email subjects and content adapt to user's language preference:

**Supported Languages:**
- English (en)
- Hindi (hi)
- Bengali (bn)
- Telugu (te)
- Marathi (mr)
- Tamil (ta)
- Gujarati (gu)
- Kannada (kn)
- Malayalam (ml)
- Punjabi (pa)
- Urdu (ur)
- Assamese (as)
- Odia (or)

## Security Features

✅ **Email Privacy:**
- BCC support for bulk emails
- No email addresses exposed
- Secure SMTP TLS connection

✅ **Rate Limiting:**
- Prevents spam
- Handles failures gracefully

✅ **Error Handling:**
- Failed emails logged
- Doesn't break complaint flow
- Retry mechanism available

## Future Enhancements

**Planned:**
1. ✉️ Email digest (daily/weekly summary)
2. 📧 Rich HTML templates with images
3. 📊 Email delivery analytics
4. 🔔 Reminder emails for pending complaints
5. 👥 CC admin/officer on important updates
6. 📎 Attach complaint images to email
7. 🌐 Dynamic template selection based on status
8. ⏰ Quiet hours support

## Files Modified

1. **backend/notifications/signals.py**
   - Added email notifications
   - Status change detection
   - Language preference support

2. **backend/smartgriev/settings.py**
   - Added FRONTEND_URL setting

3. **backend/send_test_email.py** (NEW)
   - Quick email testing script

4. **backend/test_email_notifications.py** (NEW)
   - Comprehensive test suite

## Verification Steps

**To verify emails are working:**

1. **Check email configuration:**
```bash
cd backend
python manage.py shell
>>> from notifications.email_service import email_service
>>> print(f"Enabled: {email_service.enabled}")
>>> print(f"From: {email_service.from_email}")
```

2. **Create a test complaint:**
   - Go to chatbot
   - Submit a new complaint
   - Check user's email inbox

3. **Update complaint status:**
   - Login to admin panel
   - Change complaint status to "resolved"
   - Check user's email inbox

4. **Run test script:**
```bash
cd backend
python send_test_email.py
```

## Troubleshooting

**Email not sending:**
1. Check .env file has correct credentials
2. Verify Gmail App Password (16 chars, no spaces)
3. Check email user has email address
4. Verify user's email_enabled preference
5. Check logs: `backend/logs/django.log`

**Gmail issues:**
- Enable 2FA first
- Use App Password, not regular password
- Check "Less secure apps" setting
- Verify email quota not exceeded

**Template errors:**
- Ensure FRONTEND_URL is set
- Check complaint has required fields
- Verify template files exist

---

**Status:** ✅ Implemented and Tested
**Date:** November 14, 2025
**Tested with:** kancha@123 (kanchachina@gmail.com)
**Email Provider:** Gmail SMTP
