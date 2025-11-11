# Frontend-Backend Alignment Verification

## ✅ Registration Flow - FULLY ALIGNED

### Backend API Endpoint
**URL:** `POST /api/auth/register/`  
**Serializer:** `UserSerializer` in `backend/authentication/serializers.py`

**Expected Fields:**
```python
{
    'username': str (required),
    'email': str (required),
    'password': str (required),
    'confirm_password': str (required for validation),
    'first_name': str (required),
    'last_name': str (required),
    'mobile': str (optional),
    'address': str (optional),
    'language': str (optional, default='en')
}
```

### Frontend Register Component
**File:** `frontend/src/pages/Register.tsx`

**Form Fields:**
```typescript
{
    firstName: string,      // → first_name
    lastName: string,       // → last_name  
    email: string,          // → email
    username: string,       // → username
    password: string,       // → password
    confirmPassword: string, // → confirm_password
    phone: string           // → mobile (optional)
}
```

**API Call:**
```typescript
await axios.post(API_URLS.REGISTER(), {
    username: formData.username,
    email: formData.email,
    password: formData.password,
    confirm_password: formData.confirmPassword,
    first_name: formData.firstName,
    last_name: formData.lastName,
    mobile: formData.phone || '',
    address: '',
    language: 'en'
});
```

**✅ STATUS:** **PERFECT MATCH!**

---

## ✅ Login Flow - FULLY ALIGNED

### Backend API Endpoint
**URL:** `POST /api/auth/token/`  
**View:** `TokenObtainPairView` (JWT authentication)

**Expected Fields:**
```python
{
    'username': str (required - can be email or username),
    'password': str (required)
}
```

**Response:**
```python
{
    'access': str (JWT access token),
    'refresh': str (JWT refresh token),
    'user': {
        'id': int,
        'username': str,
        'email': str,
        'first_name': str,
        'last_name': str,
        'mobile': str,
        'is_officer': bool,
        ...
    }
}
```

### Frontend Login Component
**File:** `frontend/src/pages/Login.tsx`

**Form Fields:**
```typescript
{
    email: string,    // Sent as 'username' to backend
    password: string  // → password
}
```

**API Call:**
```typescript
await axios.post(API_URLS.LOGIN(), {
    username: formData.email,  // Backend expects 'username' field
    password: formData.password
});
```

**Token Storage:**
```typescript
localStorage.setItem('token', response.data.access);
localStorage.setItem('user', JSON.stringify(response.data.user));
```

**✅ STATUS:** **PERFECT MATCH!**

---

## 🗄️ Database Schema - User Model

### Backend User Model
**File:** `backend/authentication/models.py`

**Fields:**
```python
class User(AbstractUser):
    # From AbstractUser:
    username = CharField (required, unique)
    email = EmailField (required, unique)
    password = CharField (hashed)
    first_name = CharField
    last_name = CharField
    
    # Custom fields:
    mobile = CharField (max_length=15, optional)
    address = TextField (optional)
    language = CharField (choices=LANGUAGE_CHOICES, default='en')
    preferred_language = CharField (for backward compatibility)
    voice_language_preference = CharField
    accessibility_mode = BooleanField (default=False)
    high_contrast_mode = BooleanField (default=False)
    text_size_preference = CharField
    is_officer = BooleanField (default=False)
```

**Supported Languages:**
- English (en)
- Hindi (hi) - हिन्दी
- Bengali (bn) - বাংলা
- Telugu (te) - తెలుగు
- Marathi (mr) - मराठी
- Tamil (ta) - தமிழ்
- Gujarati (gu) - ગુજરાતી
- Kannada (kn) - ಕನ್ನಡ
- Malayalam (ml) - മലയാളം
- Punjabi (pa) - ਪੰਜਾਬੀ
- Odia (or) - ଓଡ଼ିଆ
- Assamese (as) - অসমীয়া

### Frontend Matches All Required Fields ✅

---

## 🔐 Authentication Flow Summary

### 1. User Registration
```
Frontend (Register.tsx)
    ↓ POST /api/auth/register/
    ↓ {username, email, password, confirm_password, first_name, last_name, mobile}
Backend (UserRegistrationView)
    ↓ Validates password match
    ↓ Validates unique email/username
    ↓ Creates User in database
    ↓ Returns user object
Frontend
    ↓ Shows success message
    ↓ Redirects to /login after 2 seconds
```

**✅ No OTP in frontend** - Registration completes immediately and redirects to login

### 2. User Login
```
Frontend (Login.tsx)
    ↓ POST /api/auth/token/
    ↓ {username: email, password}
Backend (TokenObtainPairView - JWT)
    ↓ Authenticates user
    ↓ Generates JWT tokens
    ↓ Returns {access, refresh, user}
Frontend
    ↓ Stores token in localStorage
    ↓ Stores user data in localStorage
    ↓ Dispatches 'userChange' event
    ↓ Redirects to /dashboard
```

---

## 🔍 Key Findings

### ✅ What's Working:
1. **Registration form fields** match backend serializer exactly
2. **Login authentication** uses correct JWT token endpoint
3. **Field mapping** is consistent (firstName → first_name, etc.)
4. **Password validation** happens on both frontend and backend
5. **Error handling** properly displays backend validation errors
6. **Token storage** correctly saves JWT access token
7. **User data** properly stored in localStorage

### 📝 Important Notes:
1. **No OTP verification** in frontend registration flow
   - Backend has OTP functionality (`auth_service.py`, `OTPVerification` model)
   - Frontend registration completes without OTP
   - This is intentional for simpler user flow

2. **Email field doubles as username**
   - Login form has one field labeled "Email / Username"
   - Sent to backend as `username` parameter
   - Backend accepts both email and username for login

3. **Mobile field is optional**
   - Backend: `mobile` field is optional
   - Frontend: phone field is optional (empty string if not provided)

4. **Language defaults to English**
   - Frontend always sends `language: 'en'`
   - Backend supports 12 Indian languages
   - Could be enhanced with language selector in frontend

---

## 🎯 E2E Testing Implications

### For Test File: `01-authentication.spec.ts`

**Required Form Fields for Registration:**
```typescript
await page.fill('input[name="firstName"]', 'Test');
await page.fill('input[name="lastName"]', 'User');
await page.fill('input[name="email"]', 'test@example.com');
await page.fill('input[name="username"]', 'testuser123');
await page.fill('input[name="password"]', 'SecurePass123!');
await page.fill('input[name="confirmPassword"]', 'SecurePass123!');
await page.fill('input[name="phone"]', '+919876543210'); // Optional
```

**After Registration:**
- No OTP verification screen
- Success message appears
- Automatic redirect to `/login` after 2 seconds
- User can immediately login with credentials

**For Login:**
```typescript
await page.fill('input[name="email"]', 'test@example.com'); // or username
await page.fill('input[name="password"]', 'SecurePass123!');
await page.locator('button[type="submit"]').click();
// Redirects to /dashboard on success
```

---

## ✅ Conclusion

**Frontend and Backend are FULLY ALIGNED!** 

All registration and authentication flows match the backend API expectations perfectly. The E2E tests just need to:

1. Use correct routes: `/register` (not `/signup`) and `/login`
2. Fill correct form fields: `firstName`, `lastName`, `username`, `email`, `password`, `confirmPassword`
3. Expect direct registration → login flow (no OTP intermediate step)
4. Wait for redirect to `/dashboard` after successful login

**No frontend changes needed** - the implementation is correct!
