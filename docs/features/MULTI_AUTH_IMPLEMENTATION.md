# Multi-Method Authentication Implementation

## Overview
Implemented triple authentication methods for SmartGriev platform:
1. **Email/Username + Password** (Traditional)
2. **Mobile Number + OTP** (SMS-based)
3. **Gmail OAuth** (Social login) - Pending backend

## ✅ Completed Changes

### Frontend Changes

#### 1. LoginPage.tsx
- **Added**: Login method selector with tabs (Email/Username | Mobile OTP)
- **Added**: State management for `loginMethod`, `mobile`, `otp`, `otpSent`
- **Added**: Handler functions:
  - `handleEmailLogin()` - Original email/username+password login
  - `handleSendOTP()` - Sends OTP to mobile number
  - `handleOTPLogin()` - Verifies OTP and authenticates
  - `handleGmailLogin()` - Redirects to Google OAuth endpoint
- **Added**: Conditional UI rendering:
  - Email tab: Username/password inputs
  - Mobile tab: Mobile number input → OTP input (two-step flow)
  - Gmail button: Google logo + "Continue with Gmail"

#### 2. RegisterPage.tsx
- **Added**: Registration method selector (Email | Mobile OTP)
- **Added**: State management for `registerMethod`, `mobile`, `otp`, `otpSent`
- **Added**: Handler functions:
  - `handleSubmit()` - Original email registration
  - `handleSendOTP()` - Sends OTP for mobile registration
  - `handleOTPRegister()` - Verifies OTP and creates account
  - `handleGmailRegister()` - Redirects to Google OAuth
- **Added**: Conditional UI:
  - Email tab: Full registration form (name, email, password, etc.)
  - Mobile tab: Mobile number → Send OTP → Enter OTP → Verify
  - Gmail button: Quick registration via Google account

#### 3. auth.ts API Client
- **Added**: `sendOTP(mobileNumber: string)` - POST to `/api/auth/send-otp/`
- **Added**: `verifyOTP(mobileNumber: string, otp: string)` - POST to `/api/auth/verify-otp/`
- **Returns**: Standard `AuthResponse` with `{access, refresh, user}`

### Backend Changes

#### 1. verification_views.py
- **Added**: `SendOTPView` class
  - Accepts: `mobile_number` in POST body
  - Generates: 6-digit random OTP
  - Creates: Temporary user if not exists (inactive until verified)
  - Stores: OTP in `OTPVerification` model with 10-minute expiry
  - Returns: Success message (+ debug OTP in development mode)
  - TODO: Integrate SMS service (Twilio/AWS SNS)

- **Added**: `VerifyOTPView` class
  - Accepts: `mobile_number` and `otp` in POST body
  - Validates: OTP not expired, attempts < max_attempts
  - Activates: Temporary user account
  - Marks: `mobile_verified = True` on user model
  - Generates: JWT tokens (access + refresh)
  - Returns: `{access, refresh, user}` response

#### 2. urls.py
- **Added**: `path('send-otp/', SendOTPView.as_view())`
- **Added**: `path('verify-otp/', VerifyOTPView.as_view())`

#### 3. Models (Existing)
- **Uses**: `OTPVerification` model with fields:
  - `user` - ForeignKey to User
  - `phone_number` - Mobile number
  - `otp_code` - 6-digit code
  - `otp_type` - Type ('login_register')
  - `is_verified` - Boolean flag
  - `attempts` - Counter (max 3)
  - `expires_at` - 10-minute expiry
  - `created_at`, `verified_at` - Timestamps

## 🔧 Technical Details

### Mobile OTP Flow
1. **User enters mobile number** → Frontend validates 10 digits
2. **Click "Send OTP"** → `authApi.sendOTP(mobile)`
3. **Backend generates OTP** → Creates temp user if new
4. **OTP stored in DB** → Expires in 10 minutes
5. **SMS sent** (TODO: integrate service) → User receives OTP
6. **User enters OTP** → Frontend validates 6 digits
7. **Click "Verify"** → `authApi.verifyOTP(mobile, otp)`
8. **Backend validates** → Checks expiry, attempts
9. **User activated** → `is_active=True`, `mobile_verified=True`
10. **JWT tokens generated** → User logged in automatically

### Gmail OAuth Flow (Pending)
1. **User clicks "Continue with Gmail"**
2. **Redirect to** → `${API_URL}/api/auth/google/`
3. **Backend handles OAuth** → django-allauth or similar
4. **Google authenticates** → User grants permissions
5. **Callback to backend** → Extract user info (email, name)
6. **Create/update user** → Find by email or create new
7. **Generate JWT tokens** → Return to frontend
8. **Frontend stores tokens** → User logged in

## 📋 Pending Implementation

### High Priority
- [ ] **Google OAuth Backend**
  - Install `django-allauth` or `python-social-auth`
  - Configure Google OAuth credentials (Client ID, Secret)
  - Create OAuth callback endpoint
  - Handle user creation/linking
  - Generate JWT tokens after OAuth

- [ ] **SMS Service Integration**
  - Choose provider (Twilio, AWS SNS, MSG91)
  - Add credentials to settings
  - Implement `send_otp_sms()` function
  - Handle delivery failures gracefully
  - Add rate limiting per mobile number

### Medium Priority
- [ ] **Security Enhancements**
  - Add rate limiting per IP for OTP requests
  - Implement CAPTCHA for suspicious activity
  - Add device fingerprinting
  - Log authentication attempts
  - Block repeated failed OTP verifications

- [ ] **User Experience**
  - Add "Resend OTP" cooldown timer (60 seconds)
  - Show OTP expiry countdown
  - Add phone number formatting (e.g., +91 98765-43210)
  - Email notification on new device login
  - Option to link multiple auth methods

### Low Priority
- [ ] **Translations**
  - Add translation keys for new UI elements
  - Translate error messages
  - Support international phone formats

- [ ] **Testing**
  - Unit tests for OTP generation/validation
  - Integration tests for auth flows
  - E2E tests for login/registration

## 🔐 Security Considerations

### Implemented
✅ OTP expires in 10 minutes
✅ Max 3 attempts per OTP
✅ Temporary users inactive until verified
✅ JWT tokens for session management
✅ Throttling on verification endpoints

### Recommended
⚠️ Add IP-based rate limiting (prevent OTP bombing)
⚠️ Implement CAPTCHA after failed attempts
⚠️ Hash OTP codes in database (currently plaintext)
⚠️ Add device trust mechanism
⚠️ Implement session management (logout all devices)

## 📊 API Endpoints Summary

| Endpoint | Method | Auth | Request Body | Response |
|----------|--------|------|--------------|----------|
| `/api/auth/send-otp/` | POST | None | `{mobile_number}` | `{message, debug_otp?}` |
| `/api/auth/verify-otp/` | POST | None | `{mobile_number, otp}` | `{access, refresh, user}` |
| `/api/auth/google/` | GET | None | - | OAuth redirect (PENDING) |
| `/api/auth/login/` | POST | None | `{username, password}` | `{access, refresh, user}` |
| `/api/auth/register/` | POST | None | `{username, email, password, ...}` | `{access, refresh, user}` |

## 🎯 Usage Examples

### Mobile OTP Login
```typescript
// Send OTP
const response = await authApi.sendOTP('9876543210');
console.log(response.message); // "OTP sent successfully to 9876543210"

// Verify OTP
const authResponse = await authApi.verifyOTP('9876543210', '123456');
setAuth(authResponse.user, authResponse.access, authResponse.refresh);
navigate('/dashboard');
```

### Gmail OAuth Login
```typescript
// Redirect to Google OAuth
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
window.location.href = `${API_URL}/api/auth/google/`;

// Backend handles callback and redirects back with tokens
```

## 🚀 Deployment Checklist

### Before Production
- [ ] Set up SMS service credentials
- [ ] Configure Google OAuth app
- [ ] Add production CORS origins
- [ ] Enable HTTPS for OAuth callbacks
- [ ] Set DEBUG=False (no debug_otp in response)
- [ ] Configure rate limiting rules
- [ ] Set up monitoring/alerts for auth failures
- [ ] Test all flows in staging environment

### Environment Variables
```bash
# SMS Service (example with Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://yourapp.com/api/auth/google/callback/

# Security
OTP_EXPIRY_MINUTES=10
OTP_MAX_ATTEMPTS=3
OTP_RATE_LIMIT=3/hour
```

## 📝 Notes

- OTP is logged to console in development mode (DEBUG=True)
- Temporary users created with username `temp_{last10digits}`
- Mobile number field required in User model
- JWT tokens expire based on `SIMPLE_JWT` settings
- OAuth requires HTTPS in production

## 🎉 Benefits

1. **Reduced Friction**: No password needed for mobile users
2. **Security**: OTP-based auth more secure than passwords
3. **Convenience**: Social login for quick onboarding
4. **Flexibility**: Users choose preferred auth method
5. **Mobile-First**: Optimized for Indian mobile users
6. **Accessibility**: Support for users without email

---

**Status**: Frontend complete ✅ | Backend OTP complete ✅ | Gmail OAuth pending ⏳
**Date**: 2025-01-XX
**Developer**: GitHub Copilot
