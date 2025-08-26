# SmartGriev Notification System - Optional Dependencies

The SmartGriev notification system is designed to work with optional dependencies for advanced features. The system will gracefully degrade functionality if these dependencies are not installed.

## Core Notification Features (Always Available)
- Email notifications (using Django's built-in email)
- Webhook notifications
- Basic notification queue processing

## Optional Features and Dependencies

### 🔥 Firebase Push Notifications
**Dependency:** `firebase-admin>=6.2.0`
**Features:** Send push notifications to mobile apps
**Configuration:** Requires Firebase project setup and service account key

```bash
pip install firebase-admin
```

### 📱 SMS Notifications via Twilio
**Dependency:** `twilio>=8.5.0`
**Features:** Send SMS notifications to mobile numbers
**Configuration:** Requires Twilio account and API credentials

```bash
pip install twilio
```

### 🔄 Real-time In-App Notifications
**Dependencies:** 
- `channels>=4.0.0`
- `channels-redis>=4.1.0`
- `asgiref>=3.7.0`

**Features:** Real-time WebSocket notifications
**Configuration:** Requires Redis and WebSocket setup

```bash
pip install channels channels-redis
```

### 📊 Error Monitoring with Sentry
**Dependency:** `sentry-sdk[django]>=1.29.0`
**Features:** Production error tracking and monitoring
**Configuration:** Requires Sentry DSN configuration

```bash
pip install sentry-sdk[django]
```

### 📧 Enhanced Email Features
**Dependencies:**
- `django-anymail>=10.0.0` - Multiple email provider support
- `premailer>=3.10.0` - CSS inlining for emails

**Features:** Advanced email providers (SendGrid, Mailgun, etc.)

```bash
pip install django-anymail premailer
```

## Installation Options

### Minimal Installation (Core Features Only)
```bash
pip install -r requirements/base.txt
```

### Full Installation (All Optional Features)
```bash
pip install -r requirements/base.txt
pip install -r requirements/optional.txt
```

### Selective Installation
Choose only the features you need:
```bash
# For push notifications only
pip install firebase-admin

# For SMS notifications only
pip install twilio

# For real-time notifications only
pip install channels channels-redis
```

## Configuration

### Environment Variables
Add these to your `.env` file only if you're using the corresponding features:

```env
# Firebase (for push notifications)
FIREBASE_CREDENTIALS_PATH=/path/to/service-account-key.json

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Sentry (for error monitoring)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Redis (for real-time notifications)
REDIS_URL=redis://localhost:6379/0
```

## Graceful Degradation

The system is designed to handle missing dependencies gracefully:

1. **Missing Firebase**: Push notifications will be logged as failed with "Firebase Admin SDK not installed"
2. **Missing Twilio**: SMS notifications will be logged as failed with "Twilio SDK not installed"
3. **Missing Channels**: In-app notifications will be logged as failed with "Channels not installed"
4. **Missing Sentry**: Error tracking will be disabled, but the application will continue to work

## Development vs Production

### Development Environment
For development, you typically only need:
```bash
pip install -r requirements/development.txt
```

### Production Environment
For production, install all features:
```bash
pip install -r requirements/production.txt
pip install -r requirements/optional.txt
```

## Testing Without Optional Dependencies

You can test the notification system without installing optional dependencies. The system will:
- Process email notifications normally
- Log failed attempts for unsupported channels
- Continue processing the notification queue
- Maintain all analytics and reporting features

This allows for development and testing of the core complaint management system without requiring external service accounts or complex setup.
