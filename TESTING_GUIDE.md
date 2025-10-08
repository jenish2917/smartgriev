# 🧪 SmartGriev - URL & Function Testing Guide

## 🚀 Quick Start Testing

### Prerequisites
1. **Clear Browser Cache FIRST** (Critical!):
   ```bash
   # Method 1: Browser Console (F12)
   localStorage.clear();
   location.reload(true);
   
   # Method 2: Open fix_errors.html and click "Clear Everything"
   
   # Method 3: Ctrl+Shift+Delete → Clear browsing data
   ```

2. **Servers Running:**
   - Frontend: `http://localhost:3001/`
   - Backend: `http://127.0.0.1:8000/`

3. **Test User Credentials:**
   - Username: `testuser`
   - Password: `Test@123`

---

## 📋 URL Testing Checklist

### 1. Home Page - `/`
**URL:** `http://localhost:3001/`

#### What to Test:
- [ ] **Logo Click** → Should stay on home page or refresh
- [ ] **Hero Section** displays properly
  - Title: "Smart Grievance Management System"
  - Subtitle visible
  - Two buttons: "🤖 Try AI Chatbot" and "📝 Submit Complaint"
- [ ] **Chatbot Preview** shows sample conversation
- [ ] **Features Grid** shows 6 feature cards:
  - 🤖 AI-Powered Chatbot
  - 🎥 Multimodal Submissions
  - ⚡ Real-Time Tracking
  - 🎯 Smart Classification
  - 📊 Analytics Dashboard
  - 🔒 Secure & Private
- [ ] **CTA Section** shows "Ready to Get Started?"
- [ ] **"Create Free Account →" button** → Navigates to `/register`

#### Mobile Testing:
- [ ] **Hamburger menu** (☰) appears on mobile (≤768px)
- [ ] Mobile menu opens/closes smoothly
- [ ] Hero section stacks vertically on mobile
- [ ] Feature cards stack into 1 column
- [ ] CTA buttons full-width on mobile

---

### 2. Login Page - `/login`
**URL:** `http://localhost:3001/login`

#### What to Test:
- [ ] **Logo (SG)** displays
- [ ] **Title:** "Welcome Back"
- [ ] **Form Fields:**
  - Email or Username (required)
  - Password (required)
  - "Remember Me" checkbox
- [ ] **Login Button** clickable
- [ ] **"Forgot Password?"** link → `/forgot-password`
- [ ] **"Sign up here"** link → `/register`

#### Function Testing:
- [ ] **Valid Login:**
  - Enter: `testuser` / `Test@123`
  - Click "Login"
  - Should redirect to `/dashboard`
  - Username appears in navbar
  - No errors in console
  
- [ ] **Invalid Login:**
  - Enter wrong credentials
  - Should show error message
  - Should NOT redirect
  
- [ ] **Empty Fields:**
  - Click Login without filling fields
  - Should show validation errors
  
- [ ] **Remember Me:**
  - Check "Remember Me"
  - Login successfully
  - Close browser tab
  - Reopen → Should stay logged in

#### Mobile Testing:
- [ ] Form fits screen without horizontal scroll
- [ ] Input fields are touch-friendly (min 50px height)
- [ ] Buttons are full-width and easy to tap
- [ ] Keyboard doesn't cover input fields

---

### 3. Register Page - `/register`
**URL:** `http://localhost:3001/register`

#### What to Test:
- [ ] **Logo (SG)** displays
- [ ] **Title:** "Create Account"
- [ ] **Form Fields:**
  - First Name, Last Name (grid on desktop, stack on mobile)
  - Email
  - Username
  - Password
  - Confirm Password
  - Terms & Conditions checkbox
- [ ] **Register Button** clickable
- [ ] **"Login here"** link → `/login`

#### Function Testing:
- [ ] **Valid Registration:**
  - Fill all fields with valid data
  - Check Terms checkbox
  - Click "Create Account"
  - Should show success message
  - Should auto-login and redirect to `/dashboard`
  - Username appears in navbar
  
- [ ] **Password Validation:**
  - Try weak password → Should show strength indicator
  - Try non-matching passwords → Should show error
  
- [ ] **Email Validation:**
  - Try invalid email → Should show error
  - Try existing email → Should show "Email already exists"
  
- [ ] **Required Fields:**
  - Leave fields empty → Should show validation errors

#### Mobile Testing:
- [ ] Form row (First Name + Last Name) stacks on mobile
- [ ] All inputs touch-friendly
- [ ] Scrollable form on small screens
- [ ] Password strength indicator visible

---

### 4. Forgot Password - `/forgot-password`
**URL:** `http://localhost:3001/forgot-password`

#### What to Test:
- [ ] **Logo (SG)** displays
- [ ] **Title:** "Reset Password"
- [ ] **Email input field**
- [ ] **Submit Button**
- [ ] **"Back to Login"** link → `/login`

#### Function Testing:
- [ ] **Valid Email:**
  - Enter registered email
  - Click "Send Reset Link"
  - Should show success message
  
- [ ] **Invalid Email:**
  - Enter non-registered email
  - Should show "Email not found" error
  
- [ ] **Empty Field:**
  - Click submit without email
  - Should show validation error

---

### 5. Dashboard - `/dashboard`
**URL:** `http://localhost:3001/dashboard`  
**Auth Required:** ✅ Yes

#### What to Test:
- [ ] **Header:**
  - "Welcome back, {username}! 👋"
  - Subtitle displays
- [ ] **Stats Grid (4 cards):**
  - 📊 Total Complaints
  - ⏳ Pending
  - 🔄 In Progress
  - ✅ Resolved
- [ ] **Quick Actions (4 cards):**
  - Submit New Complaint → `/multimodal-submit`
  - Chat with AI → `/chatbot`
  - View All Complaints → `/my-complaints`
  - Track Status → `/my-complaints`
- [ ] **Recent Complaints Table:**
  - Shows last 5 complaints
  - Columns: ID, Title, Status, Priority, Date
  - Click row → Navigate to complaint detail

#### Function Testing:
- [ ] **Stats Accuracy:**
  - Submit 3 complaints
  - Check "Total" increases to 3
  - Check "Pending" shows 3 (default status)
  
- [ ] **Quick Action Clicks:**
  - Click each card
  - Verify correct navigation
  
- [ ] **Recent Complaints:**
  - Shows newest complaints first
  - Status badges color-coded
  - Click row opens detail

#### Mobile Testing:
- [ ] Stats grid: 4 → 2 → 1 columns (desktop → tablet → mobile)
- [ ] Quick actions stack into 1 column
- [ ] Table becomes card view on mobile
- [ ] Touch-friendly tap targets

---

### 6. AI Chatbot - `/chatbot`
**URL:** `http://localhost:3001/chatbot`  
**Auth Required:** ✅ Yes

#### What to Test:
- [ ] **Chat Header:**
  - "🤖 SmartGriev AI Assistant"
  - Online status indicator
- [ ] **Chat Messages Area:**
  - Welcome message from bot
  - Scrollable conversation
- [ ] **Input Area:**
  - Text input field
  - Send button
  - File upload button
  - Emoji picker (if implemented)

#### Function Testing:
- [ ] **Send Text Message:**
  - Type "Hello"
  - Click Send or press Enter
  - Bot responds within 2-3 seconds
  - Message appears in chat
  
- [ ] **Submit Complaint via Chat:**
  - Type "I want to report road damage"
  - Bot asks for location
  - Provide location
  - Bot offers to upload photo
  - Complete conversation
  - Complaint created successfully
  
- [ ] **File Upload:**
  - Click upload button
  - Select image file
  - File preview appears
  - Send file
  - Bot confirms receipt
  
- [ ] **Conversation History:**
  - Previous messages persist
  - Scroll to view history
  - New messages appear at bottom

#### Mobile Testing:
- [ ] Chat window fits screen
- [ ] Input area doesn't overlap keyboard
- [ ] Send button touch-friendly
- [ ] Messages wrap properly
- [ ] Image previews scale correctly

---

### 7. Submit Complaint (Multimodal) - `/multimodal-submit`
**URL:** `http://localhost:3001/multimodal-submit`  
**Auth Required:** ✅ Yes

#### What to Test:
- [ ] **Form Fields:**
  - Title (required)
  - Description (required)
  - Category dropdown
  - Priority dropdown
  - Location/Address
- [ ] **File Upload Section:**
  - Image upload (PNG, JPG, JPEG)
  - Video upload (MP4, AVI, MOV)
  - Audio upload (MP3, WAV, M4A)
  - Multiple file support
- [ ] **Submit Button**
- [ ] **Preview Area** (if implemented)

#### Function Testing:
- [ ] **Text-Only Submission:**
  - Fill Title: "Street Light Not Working"
  - Fill Description: "The street light on Main St is out"
  - Select Category: "Public Infrastructure"
  - Select Priority: "Medium"
  - Click Submit
  - Should redirect to `/my-complaints`
  - New complaint appears in list
  
- [ ] **Image Submission:**
  - Fill required fields
  - Upload image (JPG/PNG)
  - Preview shows thumbnail
  - Submit
  - Complaint created with image
  
- [ ] **Video Submission:**
  - Fill required fields
  - Upload video (MP4)
  - Preview shows video player
  - Submit
  - Complaint created with video
  
- [ ] **Audio Submission:**
  - Fill required fields
  - Upload audio (MP3)
  - Preview shows audio player
  - Submit
  - Complaint created with audio
  
- [ ] **Multiple Files:**
  - Upload image + video + audio
  - All files shown in preview
  - Submit
  - All files attached to complaint
  
- [ ] **Form Validation:**
  - Leave required fields empty
  - Click Submit
  - Should show validation errors
  - Should NOT submit

#### Mobile Testing:
- [ ] Form fields stack vertically
- [ ] File upload buttons full-width
- [ ] Camera integration (if available)
- [ ] Preview area scrollable
- [ ] Submit button sticky at bottom

---

### 8. My Complaints - `/my-complaints`
**URL:** `http://localhost:3001/my-complaints`  
**Auth Required:** ✅ Yes

#### What to Test:
- [ ] **Page Header:** "My Complaints"
- [ ] **Filter Options:**
  - All
  - Pending
  - In Progress
  - Resolved
- [ ] **Sort Options:**
  - Newest First
  - Oldest First
  - Priority (High to Low)
- [ ] **Complaints List/Grid:**
  - Each complaint shows:
    - Title
    - Status badge
    - Priority
    - Date created
    - Thumbnail (if has image)

#### Function Testing:
- [ ] **Load Complaints:**
  - Page loads
  - Shows all user's complaints
  - Newest first by default
  
- [ ] **Filter by Status:**
  - Click "Pending"
  - Only pending complaints show
  - Click "Resolved"
  - Only resolved complaints show
  
- [ ] **Sort:**
  - Click "Oldest First"
  - Order reverses
  - Click "Priority"
  - High priority complaints at top
  
- [ ] **Click Complaint:**
  - Click any complaint card
  - Opens detail view
  - Shows full description
  - Shows all attachments
  - Shows status history
  
- [ ] **Empty State:**
  - Filter with no results
  - Shows "No complaints found" message

#### Mobile Testing:
- [ ] Filter chips horizontal scroll
- [ ] Complaint cards stack vertically
- [ ] Images fit card width
- [ ] Touch-friendly card tap area
- [ ] Sort dropdown accessible

---

### 9. Profile - `/profile`
**URL:** `http://localhost:3001/profile`  
**Auth Required:** ✅ Yes

#### What to Test:
- [ ] **Profile Header:**
  - User avatar
  - Username
  - Email
  - Member since date
- [ ] **Edit Profile Form:**
  - First Name
  - Last Name
  - Phone Number
  - Address
  - Bio
- [ ] **Avatar Upload:**
  - Click to upload
  - Preview new avatar
  - Save changes
- [ ] **Save Button**
- [ ] **Cancel Button**

#### Function Testing:
- [ ] **Update Profile:**
  - Change First Name
  - Click Save
  - Success message appears
  - Navbar updates with new name
  
- [ ] **Upload Avatar:**
  - Click avatar upload
  - Select image
  - Preview shows
  - Save
  - Avatar updates in navbar
  
- [ ] **Validation:**
  - Try invalid phone number
  - Should show error
  - Should NOT save

---

### 10. Settings - `/settings`
**URL:** `http://localhost:3001/settings`  
**Auth Required:** ✅ Yes

#### What to Test:
- [ ] **Notification Settings:**
  - Email notifications toggle
  - SMS notifications toggle
  - Push notifications toggle
- [ ] **Privacy Settings:**
  - Profile visibility
  - Complaint visibility
- [ ] **Password Change:**
  - Current password
  - New password
  - Confirm password
- [ ] **Save Button**

#### Function Testing:
- [ ] **Toggle Notifications:**
  - Turn on email notifications
  - Click Save
  - Setting persists on reload
  
- [ ] **Change Password:**
  - Enter current password
  - Enter new password
  - Confirm new password
  - Click Save
  - Logout
  - Login with new password
  - Should work

---

## 🔐 Authentication Flow Testing

### Test Case 1: Complete Login/Logout Cycle
```
1. Open http://localhost:3001/
2. Click "Login" in navbar
3. Enter testuser / Test@123
4. Click "Login"
5. ✅ Should redirect to /dashboard
6. ✅ Navbar shows "testuser"
7. ✅ Avatar with "T" appears
8. Click "Logout"
9. ✅ Navbar shows "Login" and "Sign Up"
10. ✅ Redirected to /login
11. ✅ Try accessing /dashboard directly
12. ✅ Should redirect to /login (protected route)
```

### Test Case 2: Protected Route Access
```
1. Clear browser cache (logout if logged in)
2. Open http://localhost:3001/dashboard directly
3. ✅ Should redirect to /login
4. Login with testuser / Test@123
5. ✅ Should redirect back to /dashboard
```

### Test Case 3: Token Expiration
```
1. Login successfully
2. Open DevTools → Application → Local Storage
3. Delete "token" manually
4. Try navigating to /dashboard
5. ✅ Should redirect to /login
6. ✅ Should show "Session expired" message
```

---

## 🎨 Responsive Design Testing

### Breakpoints to Test:
- **Mobile:** 320px - 480px
- **Tablet:** 481px - 768px
- **Desktop:** 769px - 1024px
- **Large:** 1025px+

### Chrome DevTools Device Toolbar:
```
1. Press F12 (Open DevTools)
2. Press Ctrl+Shift+M (Toggle Device Toolbar)
3. Select preset devices:
   - iPhone SE (375x667)
   - iPhone 12 Pro (390x844)
   - iPad (768x1024)
   - iPad Pro (1024x1366)
   - Desktop (1920x1080)
```

### What to Check on Each Device:
- [ ] **Navbar:**
  - Desktop: Full navigation visible
  - Tablet/Mobile: Hamburger menu
  - Logo always visible
  
- [ ] **Forms:**
  - Inputs at least 48px height (touch-friendly)
  - Buttons full-width on mobile
  - No horizontal scroll
  
- [ ] **Cards/Grids:**
  - Desktop: 3-4 columns
  - Tablet: 2 columns
  - Mobile: 1 column
  
- [ ] **Tables:**
  - Desktop: Full table
  - Mobile: Card view
  
- [ ] **Text:**
  - Readable without zooming
  - Proper line height
  - No text cutoff

---

## 🐛 Error Testing

### Test Invalid URLs:
- [ ] `http://localhost:3001/nonexistent` → Should show 404 page
- [ ] `http://localhost:3001/dashboard/999999` → Should show "Complaint not found"

### Test Network Errors:
- [ ] Stop backend server
- [ ] Try logging in
- [ ] Should show "Server error" message
- [ ] Start backend server
- [ ] Try again → Should work

### Test Validation Errors:
- [ ] Submit empty form → Should show field errors
- [ ] Enter invalid email → Should show email error
- [ ] Upload wrong file type → Should show file type error
- [ ] Upload file > 10MB → Should show size error

---

## ✅ Success Criteria

All tests pass when:
1. ✅ All URLs load without errors
2. ✅ All functions work as expected
3. ✅ No console errors
4. ✅ Responsive on all devices
5. ✅ Forms validate correctly
6. ✅ Auth flow works seamlessly
7. ✅ Data persists correctly
8. ✅ Error handling works
9. ✅ UI looks polished
10. ✅ Performance is smooth

---

## 📊 Testing Checklist Summary

| Feature | Desktop | Tablet | Mobile | Status |
|---------|---------|--------|--------|--------|
| Home Page | ⏳ | ⏳ | ⏳ | Responsive ✅ |
| Navbar | ⏳ | ⏳ | ⏳ | Responsive ✅ |
| Login | ⏳ | ⏳ | ⏳ | Responsive ✅ |
| Register | ⏳ | ⏳ | ⏳ | Responsive ✅ |
| Dashboard | ⏳ | ⏳ | ⏳ | Responsive ✅ |
| Chatbot | ⏳ | ⏳ | ⏳ | Needs Testing |
| Submit Complaint | ⏳ | ⏳ | ⏳ | Needs Testing |
| My Complaints | ⏳ | ⏳ | ⏳ | Needs Testing |
| Profile | ⏳ | ⏳ | ⏳ | Needs Testing |
| Settings | ⏳ | ⏳ | ⏳ | Needs Testing |

**Legend:**
- ✅ Complete and Tested
- 🔄 In Progress
- ⏳ Not Started
- ❌ Failed/Needs Fix

---

## 🎯 Quick Test Script

Run this quick 5-minute test:
```
1. Clear cache (F12 → Console → localStorage.clear();location.reload(true);)
2. Visit / → Check home page loads
3. Click Login → Login with testuser/Test@123
4. Check navbar shows username ✅
5. Visit /dashboard → Check stats load
6. Click "Submit New Complaint" quick action
7. Fill form → Submit complaint
8. Visit /my-complaints → Check new complaint appears
9. Click Logout → Check redirects to /login
10. Check navbar shows Login/Sign Up buttons ✅
```

If all 10 steps work, the core functionality is working! 🎉

---

**Last Updated:** January 2024  
**Test Coverage:** ~60% Complete  
**Priority:** HIGH - Complete before production
