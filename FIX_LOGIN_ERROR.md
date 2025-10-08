# Create Test User for SmartGriev

This script helps you create a test user account to resolve the "No active account found" error.

## Quick Fix - Create User via Django Shell

### Option 1: Using Django Admin (Recommended)

1. **Start Django server:**
```bash
cd E:\Smartgriv\smartgriev\backend
python manage.py runserver
```

2. **Create superuser (if not exists):**
```bash
python manage.py createsuperuser
```
- Username: `admin`
- Email: `admin@smartgriev.com`
- Password: `admin123` (or your choice)

3. **Access Django Admin:**
- Visit: http://127.0.0.1:8000/admin
- Login with superuser credentials
- Go to **Users** → **Add User**
- Create test user:
  - Username: `testuser`
  - Email: `test@example.com`
  - Password: `Test@123`
  - **✅ Check "Active" checkbox**
  - Save

### Option 2: Using Django Shell

```bash
cd E:\Smartgriv\smartgriev\backend
python manage.py shell
```

Then run:
```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create test user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='Test@123',
    first_name='Test',
    last_name='User',
    is_active=True  # ✅ IMPORTANT: Must be True
)

print(f"✅ User created: {user.username} ({user.email})")
print(f"✅ Is active: {user.is_active}")
```

### Option 3: Using Python Script

Create file: `backend/create_test_user.py`
```python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create test user
try:
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='Test@123',
        first_name='Test',
        last_name='User',
        is_active=True
    )
    print(f"✅ User created successfully!")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Active: {user.is_active}")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:
```bash
cd E:\Smartgriv\smartgriev\backend
python create_test_user.py
```

---

## 🔧 Fix Frontend Login (Username vs Email)

The backend uses `username` field for authentication, but frontend sends `email`.

### Current Issue:
```typescript
// Frontend sends:
{
  username: formData.email,  // ❌ This might not match
  password: formData.password
}
```

### Solution 1: Update Backend to Accept Email

Edit: `backend/authentication/serializers.py`

Add custom serializer:
```python
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Allow login with email or username
        username = attrs.get('username')
        
        # Check if username is actually an email
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass
        
        return super().validate(attrs)
```

Edit: `backend/authentication/views.py`

```python
from .serializers import CustomTokenObtainPairSerializer

class UserLoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer  # ✅ Use custom serializer
```

### Solution 2: Update Frontend to Use Username

Change the input field in `Login.tsx`:
```typescript
<Input
  type="text"
  id="email"
  name="email"
  placeholder="Enter your username"  // ✅ Change placeholder
  value={formData.email}
  onChange={handleChange}
  required
/>
```

---

## 🧪 Test Your Login

### Test Credentials:
- **Username:** `testuser`
- **Email:** `test@example.com`
- **Password:** `Test@123`

### Frontend Login Form:
1. Open: http://localhost:3001/login
2. Enter:
   - **Username/Email:** `testuser` (or `test@example.com` if backend fix applied)
   - **Password:** `Test@123`
3. Click **Sign In**

---

## 📊 Verify User in Database

```bash
cd E:\Smartgriv\smartgriev\backend
python manage.py shell
```

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# List all users
for user in User.objects.all():
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Active: {user.is_active}")
    print(f"Staff: {user.is_staff}")
    print("---")

# Check specific user
user = User.objects.get(username='testuser')
print(f"✅ User found: {user.username}")
print(f"✅ Is active: {user.is_active}")
print(f"✅ Can login: {user.check_password('Test@123')}")
```

---

## 🚨 Common Issues & Fixes

### Issue 1: User exists but inactive
```python
# Activate user
user = User.objects.get(username='testuser')
user.is_active = True
user.save()
```

### Issue 2: Wrong password
```python
# Reset password
user = User.objects.get(username='testuser')
user.set_password('Test@123')
user.save()
```

### Issue 3: User doesn't exist
```python
# Create new user
User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='Test@123',
    is_active=True
)
```

### Issue 4: CORS error
Check `backend/smartgriev/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',  # ✅ Add this
]
```

---

## ✅ Complete Setup Checklist

- [ ] Django server running on http://127.0.0.1:8000
- [ ] Frontend server running on http://localhost:3001
- [ ] Test user created with `is_active=True`
- [ ] CORS configured for localhost:3001
- [ ] Backend accepts email or username for login
- [ ] Test login successful

---

## 🎯 Next Steps

1. **Create test user** using one of the methods above
2. **Restart Django server** if you made code changes
3. **Test login** at http://localhost:3001/login
4. **Check Django logs** if still getting errors

---

**Generated:** October 6, 2025  
**Issue:** "No active account found with the given credentials"  
**Status:** Solution provided - create test user and configure backend
