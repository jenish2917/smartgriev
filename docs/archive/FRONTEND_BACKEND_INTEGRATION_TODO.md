# 🔗 Frontend-Backend Integration TODO List
**Critical Step-by-Step Integration Guide**

---

## 📊 AUDIT SUMMARY

### Frontend Status (React 19 + TypeScript)
- ✅ **Built**: Authentication, Dashboard, Chatbot, Complaints List, Profile
- ✅ **API Clients**: auth.ts, complaints.ts, chatbot.ts
- ✅ **State Management**: Zustand (auth, theme) + React Query
- ✅ **Location Support**: GPS request flow implemented
- ⚠️ **Not Connected**: All API calls return errors (backend mismatch)

### Backend Status (Django 5.2)
- ✅ **Endpoints**: Authentication, Complaints, Chatbot (Gemini/Voice)
- ✅ **AI Features**: Gemini chat, voice transcription, image analysis
- ✅ **Database**: Models for User, Complaint, Department, ChatLog
- ⚠️ **Endpoint Mismatch**: URLs don't match frontend expectations
- ⚠️ **Response Format**: Different from frontend TypeScript types

---

## 🚨 CRITICAL MISMATCHES FOUND

### 1. Authentication Endpoints
| Frontend Expects | Backend Has | Status |
|-----------------|-------------|--------|
| `POST /api/auth/login/` | ✅ `/api/auth/login/` | ✅ MATCH |
| `POST /api/auth/register/` | ✅ `/api/auth/register/` | ✅ MATCH |
| `GET /api/auth/user/` | ❌ `/api/auth/profile/` | ❌ MISMATCH |
| `POST /api/auth/logout/` | ❌ Not implemented | ❌ MISSING |

### 2. Complaint Endpoints
| Frontend Expects | Backend Has | Status |
|-----------------|-------------|--------|
| `GET /api/complaints/` | ✅ `/api/complaints/` | ✅ MATCH |
| `POST /api/complaints/` | ✅ `/api/complaints/` | ✅ MATCH |
| `GET /api/complaints/{id}/` | ✅ `/api/complaints/{id}/` | ✅ MATCH |
| `PATCH /api/complaints/{id}/` | ✅ `/api/complaints/{id}/` | ✅ MATCH |
| `DELETE /api/complaints/{id}/` | ✅ `/api/complaints/{id}/` | ✅ MATCH |

### 3. Chatbot Endpoints
| Frontend Expects | Backend Has | Status |
|-----------------|-------------|--------|
| `POST /api/chatbot/chat/` (with location) | ⚠️ `/api/chatbot/chat/` (no location support) | ⚠️ PARTIAL |
| `POST /api/chatbot/voice/` | ⚠️ `/api/chatbot/voice/submit/` | ❌ MISMATCH |
| `POST /api/chatbot/vision/` (image/video) | ❌ `/api/complaints/analyze/image/` | ❌ MISMATCH |
| `GET /api/chatbot/history/` | ❌ Not implemented | ❌ MISSING |

### 4. Response Format Mismatches

**Frontend Expects (User):**
```typescript
{
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  mobile_number?: string;
  address?: string;
  role: 'citizen' | 'official' | 'admin';
  language_preference: string;
  created_at: string;
}
```

**Backend Returns:**
```python
{
  "id": int,
  "username": str,
  "email": str,
  "first_name": str,
  "last_name": str,
  "phone": str,  # ❌ Should be mobile_number
  "preferred_language": str,  # ❌ Should be language_preference
  "is_verified": bool,  # ❌ Frontend expects is_email_verified
  # ❌ Missing: role, address
}
```

---

## 📋 MODULE-BY-MODULE INTEGRATION TODO

---

## MODULE 1: AUTHENTICATION 🔐

### Priority: **CRITICAL** | Status: 🟡 Partial

### Todo 1.1: Fix User Endpoint Mismatch
**File**: `backend/authentication/urls.py`
- [ ] Add alias route: `path('user/', UserProfileView.as_view(), name='current-user')`
- [ ] Keep existing `/profile/` for backward compatibility

**File**: `backend/authentication/views.py` - `UserProfileView`
- [ ] Ensure GET returns current user data (already working)

**File**: `backend/authentication/serializers.py` - `UserSerializer`
- [ ] Add field mapping:
  ```python
  mobile_number = serializers.CharField(source='phone', required=False)
  language_preference = serializers.CharField(source='preferred_language')
  ```

**Testing**:
```bash
# Frontend call
GET /api/auth/user/
Authorization: Bearer {token}

# Expected response
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "mobile_number": "+919876543210",
  "address": "123 Street, City",
  "role": "citizen",
  "language_preference": "en",
  "is_email_verified": true,
  "is_mobile_verified": false,
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

### Todo 1.2: Implement Logout Endpoint
**File**: `backend/authentication/urls.py`
- [ ] Add route: `path('logout/', LogoutView.as_view(), name='logout')`

**File**: `backend/authentication/views.py`
- [ ] Create `LogoutView`:
  ```python
  from rest_framework_simplejwt.tokens import RefreshToken
  
  class LogoutView(APIView):
      permission_classes = (permissions.IsAuthenticated,)
      
      def post(self, request):
          try:
              refresh_token = request.data.get('refresh_token')
              token = RefreshToken(refresh_token)
              token.blacklist()
              return Response({"message": "Logout successful"}, status=200)
          except Exception:
              return Response({"error": "Invalid token"}, status=400)
  ```

**Testing**:
```bash
POST /api/auth/logout/
Authorization: Bearer {token}
Content-Type: application/json

{
  "refresh_token": "..."
}
```

---

### Todo 1.3: Fix User Model Field Names
**File**: `backend/authentication/models.py` or `User` model

**Option A**: Add property aliases (non-destructive)
```python
class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    
    @property
    def mobile_number(self):
        return self.phone
    
    @property
    def language_preference(self):
        return self.preferred_language
```

**Option B**: Rename fields (requires migration)
```python
# Only if you want to standardize
python manage.py makemigrations
# Rename phone → mobile_number
# Rename preferred_language → language_preference
python manage.py migrate
```

**Recommendation**: Use **Option A** (aliases) to avoid breaking existing code.

---

### Todo 1.4: Add Role Field to User
**File**: `backend/authentication/models.py`
- [ ] Add field:
  ```python
  ROLE_CHOICES = [
      ('citizen', 'Citizen'),
      ('official', 'Official'),
      ('admin', 'Admin'),
  ]
  role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
  ```
- [ ] Run migration: `python manage.py makemigrations && python manage.py migrate`

**File**: `backend/authentication/serializers.py`
- [ ] Add `'role'` to `UserSerializer.Meta.fields`

---

### Todo 1.5: Fix Register Response
**File**: `backend/authentication/views.py` - `UserRegistrationView`
- [ ] Return JWT tokens after successful registration:
  ```python
  def create(self, request, *args, **kwargs):
      response = super().create(request, *args, **kwargs)
      user = User.objects.get(username=response.data['username'])
      
      # Generate JWT tokens
      refresh = RefreshToken.for_user(user)
      
      return Response({
          'access': str(refresh.access_token),
          'refresh': str(refresh),
          'user': UserSerializer(user).data
      }, status=status.HTTP_201_CREATED)
  ```

---

### Todo 1.6: Test Authentication Flow
- [ ] Register new user → Returns access + refresh tokens
- [ ] Login with credentials → Returns tokens + user data
- [ ] GET /api/auth/user/ with token → Returns user profile
- [ ] Logout → Blacklists token
- [ ] Verify frontend can store tokens in localStorage

---

## MODULE 2: COMPLAINTS MANAGEMENT 📝

### Priority: **HIGH** | Status: 🟢 Good Match

### Todo 2.1: Verify Complaint Response Format
**File**: `backend/complaints/serializers.py` - `ComplaintSerializer`

**Check if all frontend fields are returned**:
```python
class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'id', 'title', 'description', 'category', 'department',
            'urgency', 'status', 'latitude', 'longitude', 'address',
            'landmark', 'audio_file', 'image', 'citizen',
            'assigned_official', 'created_at', 'updated_at', 'resolved_at'
        ]
```

**Frontend expects**:
- ✅ `id`, `title`, `description`
- ✅ `category`, `department`, `urgency`, `status`
- ✅ `latitude`, `longitude`, `address`
- ✅ `created_at`, `updated_at`
- ❌ Check if `citizen` field name matches (frontend might expect `user_id`)

---

### Todo 2.2: Add Pagination Support
**File**: `backend/complaints/views.py` - `ComplaintListCreateView`
- [ ] Verify pagination is enabled:
  ```python
  from rest_framework.pagination import PageNumberPagination
  
  class ComplaintPagination(PageNumberPagination):
      page_size = 10
      page_size_query_param = 'page_size'
      max_page_size = 100
  
  class ComplaintListCreateView(generics.ListCreateAPIView):
      pagination_class = ComplaintPagination
  ```

**Frontend expects**:
```typescript
{
  count: number;
  next: string | null;
  previous: string | null;
  results: Complaint[];
}
```

---

### Todo 2.3: Fix Status Filter Query
**File**: `backend/complaints/views.py`
- [ ] Ensure `status` query param works:
  ```python
  def get_queryset(self):
      queryset = super().get_queryset()
      status_filter = self.request.query_params.get('status')
      if status_filter:
          queryset = queryset.filter(status=status_filter)
      return queryset
  ```

**Test**:
```bash
GET /api/complaints/?status=pending
GET /api/complaints/?status=resolved
```

---

### Todo 2.4: Add Search Support
**File**: `backend/complaints/views.py`
- [ ] Add search filter (already exists, verify):
  ```python
  from rest_framework import filters
  
  class ComplaintListCreateView(generics.ListCreateAPIView):
      filter_backends = [filters.SearchFilter]
      search_fields = ['title', 'description', 'address']
  ```

**Test**:
```bash
GET /api/complaints/?search=pothole
```

---

### Todo 2.5: Test Complaint CRUD Operations
- [ ] List complaints: `GET /api/complaints/`
- [ ] Create complaint: `POST /api/complaints/`
- [ ] Get single complaint: `GET /api/complaints/{id}/`
- [ ] Update complaint: `PATCH /api/complaints/{id}/`
- [ ] Delete complaint: `DELETE /api/complaints/{id}/`
- [ ] Verify permissions (user can only access their own complaints)

---

## MODULE 3: AI CHATBOT 🤖

### Priority: **CRITICAL** | Status: 🔴 Major Mismatches

### Todo 3.1: Create Unified Chat Endpoint with Location Support
**File**: `backend/chatbot/urls.py`
- [ ] Add route: `path('chat/', unified_chat_view, name='unified-chat')`

**File**: `backend/chatbot/views.py`
- [ ] Create new view:
  ```python
  from rest_framework.decorators import api_view, permission_classes
  from rest_framework.permissions import AllowAny
  from rest_framework.response import Response
  from rest_framework import status
  
  @api_view(['POST'])
  @permission_classes([AllowAny])
  def unified_chat_view(request):
      """
      Unified chat endpoint that accepts:
      - message: Text message
      - language: User language (default: 'en')
      - latitude: Optional GPS latitude
      - longitude: Optional GPS longitude
      """
      message = request.data.get('message', '').strip()
      language = request.data.get('language', 'en')
      latitude = request.data.get('latitude')
      longitude = request.data.get('longitude')
      
      if not message:
          return Response({
              'error': 'Message is required'
          }, status=status.HTTP_400_BAD_REQUEST)
      
      # Process with Gemini AI
      from .gemini_service import gemini_chatbot
      
      # Include location in context if provided
      context = {}
      if latitude and longitude:
          context['location'] = {
              'latitude': float(latitude),
              'longitude': float(longitude)
          }
      
      result = gemini_chatbot.chat(
          session_id=request.session.session_key or str(uuid.uuid4()),
          user_message=message,
          user_language=language,
          context=context
      )
      
      return Response({
          'response': result['response'],
          'intent': result.get('intent', 'general'),
          'complaint_data': result.get('complaint_data', {}),
      }, status=status.HTTP_200_OK)
  ```

---

### Todo 3.2: Create Voice Endpoint for Frontend
**File**: `backend/chatbot/urls.py`
- [ ] Add route: `path('voice/', voice_transcription_view, name='voice-chat')`

**File**: `backend/chatbot/views.py`
- [ ] Create view:
  ```python
  @api_view(['POST'])
  @permission_classes([AllowAny])
  def voice_transcription_view(request):
      """
      Voice transcription endpoint
      Expects:
      - audio: Audio file (WebM, MP3, WAV)
      - language: Target language (default: 'en')
      """
      audio_file = request.FILES.get('audio')
      language = request.data.get('language', 'en')
      
      if not audio_file:
          return Response({
              'error': 'Audio file is required'
          }, status=status.HTTP_400_BAD_REQUEST)
      
      # Use existing voice processing
      from .civicai_voice_assistant import civic_ai
      
      # Save audio temporarily
      import tempfile
      with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
          for chunk in audio_file.chunks():
              tmp.write(chunk)
          audio_path = tmp.name
      
      # Transcribe audio
      result = civic_ai.transcribe_audio(audio_path, language)
      
      # Process transcribed text with chatbot
      chat_result = gemini_chatbot.chat(
          session_id=request.session.session_key or str(uuid.uuid4()),
          user_message=result['transcription'],
          user_language=language
      )
      
      return Response({
          'transcription': result['transcription'],
          'response': chat_result['response'],
          'confidence': result.get('confidence', 0.9)
      }, status=status.HTTP_200_OK)
  ```

---

### Todo 3.3: Create Vision Endpoint for Frontend
**File**: `backend/chatbot/urls.py`
- [ ] Add route: `path('vision/', vision_analysis_view, name='vision-chat')`

**File**: `backend/chatbot/views.py`
- [ ] Create view:
  ```python
  @api_view(['POST'])
  @permission_classes([AllowAny])
  def vision_analysis_view(request):
      """
      Vision analysis endpoint for images/videos
      Expects:
      - image: Image/video file
      - message: Optional text message
      - latitude: Optional GPS latitude
      - longitude: Optional GPS longitude
      """
      image_file = request.FILES.get('image')
      message = request.data.get('message', '')
      latitude = request.data.get('latitude')
      longitude = request.data.get('longitude')
      
      if not image_file:
          return Response({
              'error': 'Image/video file is required'
          }, status=status.HTTP_400_BAD_REQUEST)
      
      # Use existing image analysis
      from complaints.voice_vision_views import ImageAnalysisView
      
      # Analyze image
      analysis_view = ImageAnalysisView()
      analysis_result = analysis_view.analyze_image(image_file)
      
      # Build context
      context = {
          'image_analysis': analysis_result,
          'user_message': message
      }
      
      if latitude and longitude:
          context['location'] = {
              'latitude': float(latitude),
              'longitude': float(longitude)
          }
      
      # Generate AI response
      prompt = f"""
      User uploaded an image. Analysis: {analysis_result.get('description', '')}
      User message: {message}
      Location: {context.get('location', 'Not provided')}
      
      Respond naturally and extract complaint information if applicable.
      """
      
      chat_result = gemini_chatbot.chat(
          session_id=request.session.session_key or str(uuid.uuid4()),
          user_message=prompt,
          user_language='en'
      )
      
      return Response({
          'description': analysis_result.get('description', ''),
          'response': chat_result['response'],
          'detected_objects': analysis_result.get('objects', []),
          'complaint_data': chat_result.get('complaint_data', {})
      }, status=status.HTTP_200_OK)
  ```

---

### Todo 3.4: Implement Chat History Endpoint
**File**: `backend/chatbot/urls.py`
- [ ] Add route: `path('history/', chat_history_view, name='chat-history')`

**File**: `backend/chatbot/views.py`
- [ ] Create view:
  ```python
  @api_view(['GET'])
  @permission_classes([IsAuthenticated])
  def chat_history_view(request):
      """Get user's chat history"""
      from .models import ChatLog
      
      logs = ChatLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
      
      history = []
      for log in logs:
          history.append({
              'id': str(log.id),
              'role': 'user',
              'content': log.message,
              'timestamp': log.timestamp.isoformat()
          })
          history.append({
              'id': f"{log.id}-reply",
              'role': 'assistant',
              'content': log.reply,
              'timestamp': log.timestamp.isoformat()
          })
      
      return Response(history, status=status.HTTP_200_OK)
  ```

---

### Todo 3.5: Update Gemini Service for Location Context
**File**: `backend/chatbot/gemini_service.py`
- [ ] Update `chat()` method signature:
  ```python
  def chat(self, session_id, user_message, user_language='en', context=None):
      context = context or {}
      
      # Add location to conversation context
      if 'location' in context:
          location_text = f"\nUser location: {context['location']['latitude']}, {context['location']['longitude']}"
          user_message = user_message + location_text
      
      # Continue with existing logic...
  ```

---

### Todo 3.6: Test Chatbot Integration
- [ ] **Text Chat**: POST /api/chatbot/chat/ → Returns AI response
- [ ] **With Location**: Include latitude/longitude → AI acknowledges location
- [ ] **Voice**: POST /api/chatbot/voice/ with audio file → Returns transcription + response
- [ ] **Vision**: POST /api/chatbot/vision/ with image → Returns analysis + response
- [ ] **History**: GET /api/chatbot/history/ → Returns past conversations

---

## MODULE 4: LOCATION & GPS 📍

### Priority: **HIGH** | Status: 🟡 Backend Exists, Frontend Integration Needed

### Todo 4.1: Add Reverse Geocoding Endpoint
**File**: `backend/complaints/location_views.py`
- [ ] Verify `reverse_geocode` function exists and works:
  ```python
  @api_view(['POST'])
  def reverse_geocode(request):
      latitude = request.data.get('latitude')
      longitude = request.data.get('longitude')
      
      # Use Google Maps API or OSM Nominatim
      address = get_address_from_coords(latitude, longitude)
      
      return Response({
          'address': address,
          'latitude': latitude,
          'longitude': longitude
      })
  ```

**File**: `backend/complaints/urls.py`
- [ ] Add route: `path('location/reverse/', reverse_geocode, name='reverse-geocode')`

---

### Todo 4.2: Add Address Parsing Endpoint
**File**: `backend/complaints/location_views.py`
- [ ] Create function:
  ```python
  @api_view(['POST'])
  def parse_address(request):
      address_text = request.data.get('address', '').strip()
      
      # Use regex or NLP to extract components
      parsed = {
          'street': '',
          'area': '',
          'city': '',
          'pincode': '',
          'raw': address_text
      }
      
      # Simple regex parsing
      import re
      
      # Extract pincode (6 digits)
      pincode_match = re.search(r'\b(\d{6})\b', address_text)
      if pincode_match:
          parsed['pincode'] = pincode_match.group(1)
      
      # Extract city (common Indian cities)
      cities = ['Ahmedabad', 'Mumbai', 'Delhi', 'Bangalore', ...]
      for city in cities:
          if city.lower() in address_text.lower():
              parsed['city'] = city
              break
      
      return Response(parsed)
  ```

---

### Todo 4.3: Create Frontend API Client
**File**: `frontend-new/src/api/location.ts`
- [ ] Create new file:
  ```typescript
  import apiClient, { handleApiError } from '@/lib/axios';
  
  export const locationApi = {
    // Reverse geocode coordinates to address
    reverseGeocode: async (lat: number, lng: number): Promise<string> => {
      try {
        const response = await apiClient.post('/api/complaints/location/reverse/', {
          latitude: lat,
          longitude: lng
        });
        return response.data.address;
      } catch (error) {
        throw new Error(handleApiError(error));
      }
    },
    
    // Parse address text into components
    parseAddress: async (address: string) => {
      try {
        const response = await apiClient.post('/api/complaints/location/parse/', {
          address
        });
        return response.data;
      } catch (error) {
        throw new Error(handleApiError(error));
      }
    }
  };
  ```

---

### Todo 4.4: Update ChatbotPage to Use Reverse Geocoding
**File**: `frontend-new/src/pages/chatbot/ChatbotPage.tsx`
- [ ] Import locationApi
- [ ] After GPS capture, fetch address:
  ```typescript
  const { latitude, longitude } = position.coords;
  setUserLocation({ latitude, longitude });
  
  // Fetch human-readable address
  try {
    const address = await locationApi.reverseGeocode(latitude, longitude);
    setMessages([...messages, {
      role: 'assistant',
      content: `✅ Location captured: ${address}. What's the issue?`
    }]);
  } catch (error) {
    setMessages([...messages, {
      role: 'assistant',
      content: `✅ Location captured (${latitude.toFixed(4)}, ${longitude.toFixed(4)}). What's the issue?`
    }]);
  }
  ```

---

## MODULE 5: PROFILE & USER MANAGEMENT 👤

### Priority: **MEDIUM** | Status: 🟡 Basic Exists, Needs Enhancement

### Todo 5.1: Add Update Profile Endpoint
**File**: `backend/authentication/views.py` - `UserProfileView`
- [ ] Ensure PATCH/PUT works:
  ```python
  class UserProfileView(generics.RetrieveUpdateAPIView):
      permission_classes = (permissions.IsAuthenticated,)
      serializer_class = UserSerializer
      
      def get_object(self):
          return self.request.user
      
      def update(self, request, *args, **kwargs):
          partial = kwargs.pop('partial', False)
          instance = self.get_object()
          serializer = self.get_serializer(instance, data=request.data, partial=partial)
          serializer.is_valid(raise_exception=True)
          self.perform_update(serializer)
          return Response(serializer.data)
  ```

---

### Todo 5.2: Add Change Password Endpoint
**File**: `backend/authentication/urls.py`
- [ ] Verify route exists: `path('change-password/', ChangePasswordView.as_view())`

**File**: `backend/authentication/views.py` - `ChangePasswordView`
- [ ] Ensure proper validation (already exists, verify it works)

---

### Todo 5.3: Create Frontend Update User Function
**File**: `frontend-new/src/api/auth.ts`
- [ ] Add methods:
  ```typescript
  updateProfile: async (data: Partial<User>): Promise<User> => {
    try {
      const response = await apiClient.patch<User>('/api/auth/user/', data);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
  
  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    try {
      await apiClient.post('/api/auth/change-password/', {
        old_password: oldPassword,
        new_password: newPassword,
        confirm_new_password: newPassword
      });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
  ```

---

### Todo 5.4: Connect ProfilePage to API
**File**: `frontend-new/src/pages/profile/ProfilePage.tsx`
- [ ] Replace mock API call with real API:
  ```typescript
  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      const updatedUser = await authApi.updateProfile(formData);
      updateUser(updatedUser);
      setIsEditing(false);
      alert('Profile updated successfully!');
    } catch (error) {
      alert(`Failed to update profile: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleChangePassword = async () => {
    // Validation...
    setIsSaving(true);
    try {
      await authApi.changePassword(
        passwordData.current_password,
        passwordData.new_password
      );
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      setIsChangingPassword(false);
      alert('Password changed successfully!');
    } catch (error) {
      alert(`Failed to change password: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };
  ```

---

## MODULE 6: CORS & SECURITY 🔒

### Priority: **CRITICAL** | Status: ⚠️ Must Configure

### Todo 6.1: Configure CORS Settings
**File**: `backend/smartgriev/settings.py`
- [ ] Install django-cors-headers: `pip install django-cors-headers`
- [ ] Add to INSTALLED_APPS:
  ```python
  INSTALLED_APPS = [
      ...
      'corsheaders',
  ]
  ```
- [ ] Add middleware:
  ```python
  MIDDLEWARE = [
      'corsheaders.middleware.CorsMiddleware',
      'django.middleware.common.CommonMiddleware',
      ...
  ]
  ```
- [ ] Configure CORS:
  ```python
  # For development
  CORS_ALLOWED_ORIGINS = [
      "http://localhost:3000",
      "http://127.0.0.1:3000",
  ]
  
  # For production (update with your domain)
  # CORS_ALLOWED_ORIGINS = [
  #     "https://yourdomain.com",
  # ]
  
  CORS_ALLOW_CREDENTIALS = True
  ```

---

### Todo 6.2: Configure JWT Settings
**File**: `backend/smartgriev/settings.py`
- [ ] Update JWT settings:
  ```python
  from datetime import timedelta
  
  SIMPLE_JWT = {
      'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
      'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
      'ROTATE_REFRESH_TOKENS': True,
      'BLACKLIST_AFTER_ROTATION': True,
      'UPDATE_LAST_LOGIN': True,
      
      'ALGORITHM': 'HS256',
      'SIGNING_KEY': SECRET_KEY,
      'AUTH_HEADER_TYPES': ('Bearer',),
      'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
  }
  ```

---

### Todo 6.3: Test CORS with Frontend
- [ ] Start backend: `python manage.py runserver 8000`
- [ ] Start frontend: `npm run dev` (port 3000)
- [ ] Open browser dev tools
- [ ] Try login from frontend
- [ ] Verify no CORS errors in console
- [ ] Verify Authorization header sent with requests

---

## MODULE 7: ERROR HANDLING & LOGGING 🐛

### Priority: **MEDIUM** | Status: 🟡 Needs Standardization

### Todo 7.1: Standardize Error Responses
**File**: `backend/smartgriev/middleware.py`
- [ ] Create custom exception handler:
  ```python
  from rest_framework.views import exception_handler
  from rest_framework.response import Response
  from rest_framework import status
  
  def custom_exception_handler(exc, context):
      response = exception_handler(exc, context)
      
      if response is not None:
          # Standardize error format
          response.data = {
              'success': False,
              'error': response.data.get('detail', str(exc)),
              'status_code': response.status_code
          }
      
      return response
  ```

**File**: `backend/smartgriev/settings.py`
- [ ] Set custom handler:
  ```python
  REST_FRAMEWORK = {
      'EXCEPTION_HANDLER': 'smartgriev.middleware.custom_exception_handler',
      ...
  }
  ```

---

### Todo 7.2: Add Request/Response Logging
**File**: `backend/smartgriev/settings.py`
- [ ] Configure logging:
  ```python
  LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'handlers': {
          'file': {
              'level': 'INFO',
              'class': 'logging.FileHandler',
              'filename': 'logs/api.log',
          },
          'console': {
              'level': 'DEBUG',
              'class': 'logging.StreamHandler',
          },
      },
      'loggers': {
          'django': {
              'handlers': ['file', 'console'],
              'level': 'INFO',
          },
          'chatbot': {
              'handlers': ['file', 'console'],
              'level': 'DEBUG',
          },
      },
  }
  ```

---

## MODULE 8: TESTING & VALIDATION ✅

### Priority: **HIGH** | Status: 🔴 Critical Before Production

### Todo 8.1: Create Integration Tests
**File**: `backend/tests/test_integration.py`
- [ ] Create test suite:
  ```python
  from django.test import TestCase
  from rest_framework.test import APIClient
  from django.contrib.auth import get_user_model
  
  User = get_user_model()
  
  class AuthenticationIntegrationTest(TestCase):
      def setUp(self):
          self.client = APIClient()
      
      def test_register_login_flow(self):
          # Register
          response = self.client.post('/api/auth/register/', {
              'username': 'testuser',
              'email': 'test@example.com',
              'password': 'testpass123',
              'first_name': 'Test',
              'last_name': 'User'
          })
          self.assertEqual(response.status_code, 201)
          self.assertIn('access', response.data)
          
          # Login
          response = self.client.post('/api/auth/login/', {
              'username': 'testuser',
              'password': 'testpass123'
          })
          self.assertEqual(response.status_code, 200)
          token = response.data['access']
          
          # Get profile
          self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
          response = self.client.get('/api/auth/user/')
          self.assertEqual(response.status_code, 200)
          self.assertEqual(response.data['username'], 'testuser')
  
  class ComplaintIntegrationTest(TestCase):
      def setUp(self):
          self.client = APIClient()
          self.user = User.objects.create_user(
              username='testuser',
              password='testpass123'
          )
          # Get token
          response = self.client.post('/api/auth/login/', {
              'username': 'testuser',
              'password': 'testpass123'
          })
          self.token = response.data['access']
          self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
      
      def test_create_complaint_flow(self):
          response = self.client.post('/api/complaints/', {
              'title': 'Test Complaint',
              'description': 'Test description',
              'category': 'infrastructure',
              'latitude': 23.0225,
              'longitude': 72.5714,
              'address': 'Test Address'
          })
          self.assertEqual(response.status_code, 201)
          self.assertIn('id', response.data)
  ```

---

### Todo 8.2: Manual E2E Testing Checklist
- [ ] **Registration Flow**:
  - [ ] Open frontend (http://localhost:3000)
  - [ ] Click "Register"
  - [ ] Fill all fields
  - [ ] Submit → Should redirect to dashboard
  - [ ] Verify token stored in localStorage

- [ ] **Login Flow**:
  - [ ] Logout
  - [ ] Click "Login"
  - [ ] Enter credentials
  - [ ] Submit → Should redirect to dashboard
  - [ ] Verify user data displayed

- [ ] **Dashboard**:
  - [ ] Verify stats cards show data
  - [ ] Verify no API errors in console

- [ ] **Chatbot Flow**:
  - [ ] Open chatbot page
  - [ ] Type "Hello" → Should get AI response
  - [ ] Click "File a new complaint"
  - [ ] Click "Enable GPS" → Browser asks permission
  - [ ] Allow → Should show location captured
  - [ ] Type issue description
  - [ ] Upload image → Should show preview
  - [ ] Verify AI responds to image
  - [ ] Check if location sent in API request (DevTools → Network)

- [ ] **Complaints List**:
  - [ ] Open complaints page
  - [ ] Verify complaints load
  - [ ] Test search bar
  - [ ] Test status filter
  - [ ] Click view complaint → Should show details

- [ ] **Profile Page**:
  - [ ] Open profile
  - [ ] Click "Edit Profile"
  - [ ] Change name
  - [ ] Click "Save" → Should update
  - [ ] Change password → Should succeed

---

## MODULE 9: DEPLOYMENT PREPARATION 🚀

### Priority: **MEDIUM** | Status: 🔴 Pre-Production

### Todo 9.1: Environment Variables
**File**: `backend/.env` (create if not exists)
```env
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=smartgriev_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Google AI
GOOGLE_API_KEY=your-gemini-api-key

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Media/Static
MEDIA_ROOT=/var/www/smartgriev/media
STATIC_ROOT=/var/www/smartgriev/static
```

**File**: `frontend-new/.env.production`
```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_NAME=SmartGriev
```

---

### Todo 9.2: Docker Configuration
**File**: `docker-compose.yml` (update)
- [ ] Ensure both frontend and backend services configured
- [ ] Add nginx for reverse proxy
- [ ] Add PostgreSQL service
- [ ] Configure volumes for persistent data

---

### Todo 9.3: CI/CD Pipeline
- [ ] Setup GitHub Actions
- [ ] Auto-run tests on push
- [ ] Auto-deploy on merge to main
- [ ] Setup staging environment

---

## 📊 INTEGRATION PRIORITY ORDER

### Week 1: Critical Path (Must Complete First)
1. ✅ **MODULE 6**: CORS & Security → Enable frontend-backend communication
2. ✅ **MODULE 1 (Todo 1.1-1.3)**: Authentication endpoints → Login/Register working
3. ✅ **MODULE 3 (Todo 3.1)**: Unified chat endpoint → Basic chatbot working
4. ⚠️ **MODULE 8 (Todo 8.2)**: Manual testing → Verify everything works

### Week 2: Core Features
5. ⚠️ **MODULE 1 (Todo 1.4-1.6)**: Complete auth (role, logout) → Full auth flow
6. ⚠️ **MODULE 2**: Verify complaints → CRUD operations working
7. ⚠️ **MODULE 3 (Todo 3.2-3.4)**: Voice & Vision endpoints → Multi-modal working
8. ⚠️ **MODULE 4**: Location services → GPS & address parsing

### Week 3: Polish & Deployment
9. ⚠️ **MODULE 5**: Profile management → User can update profile
10. ⚠️ **MODULE 7**: Error handling → Consistent error messages
11. ⚠️ **MODULE 8 (Todo 8.1)**: Automated tests → Test coverage
12. ⚠️ **MODULE 9**: Deployment prep → Production ready

---

## 🧪 TESTING COMMANDS

### Backend Tests
```bash
cd backend
python manage.py test
python manage.py test authentication
python manage.py test complaints
python manage.py test chatbot
```

### Frontend Tests (future)
```bash
cd frontend-new
npm run test
npm run test:e2e
```

### Manual API Testing
```bash
# Test login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Test chat with location
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"There is a pothole","latitude":23.0225,"longitude":72.5714}'

# Test get complaints
curl -X GET http://localhost:8000/api/complaints/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 COMPLETION CHECKLIST

### Module Completion Status
- [ ] MODULE 1: Authentication (0/6 todos)
- [ ] MODULE 2: Complaints (0/5 todos)
- [ ] MODULE 3: AI Chatbot (0/6 todos)
- [ ] MODULE 4: Location & GPS (0/4 todos)
- [ ] MODULE 5: Profile & User (0/4 todos)
- [ ] MODULE 6: CORS & Security (0/3 todos)
- [ ] MODULE 7: Error Handling (0/2 todos)
- [ ] MODULE 8: Testing (0/2 todos)
- [ ] MODULE 9: Deployment (0/3 todos)

### Total: 0/35 todos completed

---

## 🎯 SUCCESS CRITERIA

The integration is complete when:
1. ✅ User can register and login from frontend
2. ✅ User can view dashboard with real data
3. ✅ User can chat with AI (text, voice, image)
4. ✅ User can enable GPS and AI captures location
5. ✅ AI can extract complaint details from conversation
6. ✅ User can view their complaints list
7. ✅ User can update their profile
8. ✅ All API calls succeed (no 404, 500 errors)
9. ✅ No CORS errors in browser console
10. ✅ E2E tests pass

---

**Next Step**: Start with **MODULE 6 (CORS)** immediately, then **MODULE 1.1 (User endpoint)**, then test login flow end-to-end.

---

**Last Updated**: November 11, 2025  
**Status**: 🔴 Integration Not Started  
**Estimated Time**: 2-3 weeks for full integration
