# SmartGriev - Unified Implementation Strategy
**Version**: 3.0 (Merged Specification)  
**Last Updated**: November 9, 2025  
**Status**: Master Blueprint for Implementation

---

## 📋 Executive Summary

This document merges the comprehensive PDF specification (Document 11) with the current PROJECT_STATUS.md to create a unified implementation roadmap for SmartGriev - an AI-powered civic grievance redressal system for India.

**Key Integration Points:**
- ✅ **Current Working**: Twilio Verify OTP, Basic Authentication, Complaint System, Frontend UI
- 🔄 **To Enhance**: Gemini AI Integration, PostgreSQL Migration, Next.js 14, 12 Languages
- 🆕 **New Features**: MapMyIndia GIS, Voice/Vision AI, WebSockets, Advanced Analytics

---

## 🎯 Core Principles from Both Documents

### From PDF Specification:
1. **Trust Blue (#2563EB)** + **Success Green (#059669)** as brand colors
2. **Gemini 1.5 Flash** primary, DistilBERT fallback
3. **PostgreSQL 15 + PostGIS** for production
4. **Next.js 14 App Router** with [lang] prefixed routes
5. **12 Indian Languages** with RTL support for Urdu
6. **MapMyIndia** for location services
7. **JWT 15min access + 7 day refresh** in httpOnly cookies

### From Current Implementation:
1. **Twilio Verify** for OTP authentication (✅ Working)
2. **Futuristic Glassmorphism** UI design
3. **Django REST Framework** backend
4. **Vite + React + TypeScript** frontend
5. **8 Languages** currently supported
6. **SQLite** database (to migrate to PostgreSQL)

---

## 🎨 Design System - Unified Color Palette

### Brand Colors (From PDF Spec)
```typescript
primary: {
  main: '#2563EB',     // Trust Blue - Main brand color
  light: '#60A5FA',
  dark: '#1E40AF',
}
secondary: {
  main: '#059669',     // Success Green - Secondary brand
  light: '#34D399',
  dark: '#047857',
}
```

### Futuristic Accents (From Current Design)
```typescript
futuristic: {
  purple: '#6C63FF',   // Glassmorphism purple
  cyan: '#4ECDC4',     // Tech cyan
  pink: '#FF6584',     // Alert pink
  yellow: '#FFD93D',   // Warning yellow
  lime: '#7BE495',     // Active green
}
```

### Government Colors (From PDF Spec)
```typescript
government: {
  ashokaChakra: '#000080',  // Navy blue
  saffron: '#FF9933',       // Tricolor saffron
  white: '#FFFFFF',         // Tricolor white
  green: '#138808',         // Tricolor green
}
```

### Status Colors (Merged)
```typescript
status: {
  success: '#059669',    // Brand green
  warning: '#F59E0B',    // Amber
  error: '#EF4444',      // Red
  info: '#2563EB',       // Brand blue
  pending: '#F59E0B',    // Amber
  inProgress: '#2563EB', // Blue
  resolved: '#059669',   // Green
  rejected: '#EF4444',   // Red
}
```

---

## 🏗️ Architecture - Unified Stack

### Frontend Stack (Target)
```
Next.js 14 App Router (from Vite migration)
├── TypeScript 5.3 (strict mode)
├── Tailwind CSS 3.4 + CSS Variables
├── shadcn/ui components
├── Zustand (global state)
├── SWR (data fetching)
├── next-i18next (12 languages)
├── next/image (AVIF/WebP)
└── next/font (Noto Sans variants)
```

**Current**: Vite + React 18 + Ant Design  
**Migration Path**: Incremental - keep Vite during development, prepare Next.js for production

### Backend Stack (Enhanced)
```
Django 4.2.7 + DRF
├── djangorestframework-simplejwt (✅ JWT tokens)
├── PostgreSQL 15 + PostGIS 3.3 (from SQLite)
├── Redis (caching + Celery broker)
├── Celery (async tasks)
├── django-channels (WebSockets)
├── google-generativeai (Gemini 1.5)
├── twilio (✅ OTP - Already working)
└── python-decouple (env management)
```

### Database Schema (Enhanced)

#### Users Table (UUID Primary Key)
```sql
CREATE TABLE users_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name JSONB,  -- Multilingual: {"en": "John Doe", "hi": "जॉन डो"}
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),  -- Encrypted with pgcrypto
    location GEOMETRY(Point, 4326),  -- PostGIS
    preferred_language VARCHAR(10) DEFAULT 'en',
    notification_preferences JSONB,  -- Email/SMS/Push preferences
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_location ON users_user USING GIST (location);
CREATE INDEX idx_users_preferences ON users_user USING GIN (notification_preferences);
```

#### Complaints Table (Enhanced with Gemini)
```sql
CREATE TABLE complaints_complaint (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    complaint_number VARCHAR(50) UNIQUE,  -- Format: BC-{YEAR}-{CITY}-{DEPT}-{SEQ}
    user_id UUID REFERENCES users_user(id),
    title VARCHAR(255),
    description TEXT,
    department VARCHAR(50),
    sub_category VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 3,  -- 1=emergency, 5=general
    location GEOMETRY(Point, 4326),
    location_confidence DECIMAL(3,2),  -- 0.0-1.0
    gemini_raw_response JSONB,  -- Full Gemini classification result
    gemini_confidence DECIMAL(3,2),
    status_history JSONB,  -- Array of status changes
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_complaints_status ON complaints_complaint(status) WHERE status = 'pending';
CREATE INDEX idx_complaints_user_date ON complaints_complaint(user_id, created_at DESC);
CREATE INDEX idx_complaints_location ON complaints_complaint USING GIST (location);
CREATE INDEX idx_complaints_gemini ON complaints_complaint USING GIN (gemini_raw_response);
```

#### Municipal Corporations (PostGIS Jurisdictions)
```sql
CREATE TABLE integrations_corporation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE,  -- BOM, DEL, BLR, etc.
    name JSONB,  -- Multilingual names
    jurisdiction GEOMETRY(MultiPolygon, 4326),  -- Geographic boundary
    api_config JSONB,  -- Encrypted API credentials
    contact_info JSONB
);

-- Spatial Index
CREATE INDEX idx_corp_jurisdiction ON integrations_corporation USING GIST (jurisdiction);
```

---

## 🔐 Authentication Architecture (Twilio + JWT)

### Current Implementation (✅ Working)
```
Twilio Verify Service
├── Account SID: [Set in .env]
├── Auth Token: [Set in .env]
├── Verify Service SID: [Set in .env]
└── Provider: twilio_verify
```

### Enhanced JWT Flow (To Implement)
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_COOKIE': 'access_token',  # httpOnly cookie
    'AUTH_COOKIE_REFRESH': 'refresh_token',
    'AUTH_COOKIE_SECURE': True,
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_SAMESITE': 'Lax',
}
```

### Authentication Flow
```
1. User enters mobile: +919510007247
2. Backend sends OTP via Twilio Verify
3. User enters OTP: 596463
4. Backend verifies with Twilio
5. ✅ On success: Generate JWT tokens
   - Access Token (15 min) in httpOnly cookie
   - Refresh Token (7 days) in httpOnly cookie
6. Frontend stores user data in Zustand
7. Auto-refresh before access token expires
```

### Google OAuth Integration (Future)
```typescript
// NextAuth.js configuration
providers: [
  GoogleProvider({
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  }),
  CredentialsProvider({
    name: 'OTP',
    credentials: {
      phone: { label: "Phone", type: "text" },
      otp: { label: "OTP", type: "text" }
    },
    async authorize(credentials) {
      // Verify OTP with Django backend
      const res = await fetch(`${API_URL}/auth/verify-otp/`, {
        method: 'POST',
        body: JSON.stringify(credentials),
      });
      // Return user + JWT tokens
    }
  })
]
```

---

## 🤖 AI Architecture - Gemini Integration

### Gemini Configuration
```python
# backend/smartgriev/settings.py
GEMINI_CONFIG = {
    'API_KEY': os.getenv('GEMINI_API_KEY'),
    'PRIMARY_MODEL': 'gemini-1.5-flash',  # Default classifier
    'PRO_MODEL': 'gemini-1.5-pro',        # Complex cases
    'EMBEDDING_MODEL': 'embedding-001',    # Semantic search
    'COST_LIMITS': {
        'flash_per_million': 0.35,  # $0.35/M tokens
        'pro_per_million': 7.00,    # $7/M tokens
        'monthly_cap': 500,         # $500/month
    },
    'SWITCHING_RULES': {
        'token_threshold': 300,      # Switch to Pro if >300 tokens
        'mixed_language': True,      # Switch to Pro for mixed languages
        'image_analysis': True,      # Always use Pro for images
    }
}
```

### System Prompt (12 Languages)
```python
SYSTEM_PROMPT = """
You are BharatConnect AI, a municipal complaint classifier for India.

RULES:
1. Output ONLY valid JSON (no markdown, no explanation)
2. Detect language: en, hi, bn, te, mr, ta, gu, kn, ml, pa, ur, as, or
3. Extract location: address, pincode, landmark
4. Priority: 1=emergency (health/safety), 5=general
5. Confidence: 0.0-1.0 based on text clarity

DEPARTMENTS:
water, electricity, roads, sanitation, waste, streetlights, parks, building, fire, other

DEPARTMENT KEYWORDS (12 Languages):
water: पानी(hi), पाणी(mr), నీరు(te), தண்ணீர்(ta), ನೀರು(kn), വെള്ളം(ml), পানি(bn), પાણી(gu), ਪਾਣੀ(pa), پانی(ur)
electricity: बिजली(hi), वीज(mr), విద్యుత్(te), மின்சாரம்(ta), ವಿದ್ಯುತ್(kn), വൈദ്യുതി(ml), বিদ্যুৎ(bn), વીજળી(gu), ਬਿਜਲੀ(pa), بجلی(ur)
roads: सड़क(hi), रस्ता(mr), రోడ్డు(te), சாலை(ta), ರಸ್ತೆ(kn), റോഡ്(ml), রাস্তা(bn), રસ્તો(gu), ਸੜਕ(pa), سڑک(ur)
... (continue for all departments)

OUTPUT FORMAT:
{
  "department": "string",
  "sub_category": "detailed issue description",
  "priority": 1-5,
  "confidence": 0.0-1.0,
  "language": "ISO 639-1 code",
  "entities": {
    "location": "extracted address",
    "pincode": "6-digit postal code",
    "landmark": "nearby landmark"
  },
  "reasoning": "brief explanation"
}
"""
```

### Classification Flow
```python
# backend/complaints/services/gemini_classifier.py
class GeminiClassifier:
    def classify(self, text: str, user_context: dict) -> dict:
        # 1. Sanitization
        text = self.sanitize_pii(text)[:500]  # Remove PII, limit to 500 chars
        
        # 2. Semantic Cache Check (pgvector)
        cached = self.check_cache(text, threshold=0.95)
        if cached:
            return cached
        
        # 3. Select Model (Flash vs Pro)
        model = self.select_model(text)
        
        # 4. Build Prompt
        prompt = self.build_prompt(text, user_context)
        
        # 5. Call Gemini API
        try:
            response = model.generate_content(prompt)
            result = self.parse_json(response.text)
        except Exception as e:
            # Fallback to DistilBERT
            return self.fallback_classifier(text)
        
        # 6. Confidence Calibration
        result['confidence'] = self.calibrate_confidence(
            result['confidence'], 
            result['department']
        )
        
        # 7. Store in Cache
        self.store_cache(text, result, ttl=86400)  # 24 hours
        
        return result
```

### DistilBERT Fallback
```python
# Local model for offline/fallback
from transformers import DistilBertForSequenceClassification

class FallbackClassifier:
    def __init__(self):
        self.model = DistilBertForSequenceClassification.from_pretrained(
            'models/complaint-classifier-distilbert'
        )
        self.accuracy = 0.75  # 75% accuracy
        self.inference_time = 0.2  # 200ms
    
    def classify(self, text: str) -> dict:
        # Fast local classification
        inputs = self.tokenizer(text, return_tensors='pt')
        outputs = self.model(**inputs)
        department = self.label_mapping[outputs.logits.argmax()]
        confidence = outputs.logits.softmax(dim=-1).max().item()
        
        return {
            'department': department,
            'confidence': confidence * 0.9,  # Reduce confidence for fallback
            'fallback': True
        }
```

---

## 🌐 Internationalization - 12 Languages

### Supported Languages (Enhanced)
```typescript
const languages = [
  { code: 'en', name: 'English', native: 'English', dir: 'ltr', font: 'Inter' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', dir: 'ltr', font: 'Noto Sans Devanagari' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা', dir: 'ltr', font: 'Noto Sans Bengali' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు', dir: 'ltr', font: 'Noto Sans Telugu' },
  { code: 'mr', name: 'Marathi', native: 'मराठी', dir: 'ltr', font: 'Noto Sans Devanagari' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்', dir: 'ltr', font: 'Noto Sans Tamil' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી', dir: 'ltr', font: 'Noto Sans Gujarati' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', dir: 'ltr', font: 'Noto Sans Kannada' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം', dir: 'ltr', font: 'Noto Sans Malayalam' },
  { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ', dir: 'ltr', font: 'Noto Sans Gurmukhi' },
  { code: 'ur', name: 'Urdu', native: 'اردو', dir: 'rtl', font: 'Noto Nastaliq Urdu' },  // NEW - RTL
  { code: 'as', name: 'Assamese', native: 'অসমীয়া', dir: 'ltr', font: 'Noto Sans Bengali' },  // NEW
  { code: 'or', name: 'Odia', native: 'ଓଡ଼ିଆ', dir: 'ltr', font: 'Noto Sans Oriya' },  // NEW
];
```

### Translation Workflow
```
1. English source in /locales/en/common.json
2. Gemini batch translation:
   POST /api/v1/translations/batch
   {
     "source": "en",
     "targets": ["hi", "bn", "te", ...],
     "content": { "login": "Login", "register": "Register" }
   }
3. Human review via Django admin interface
4. Publish to /public/locales/{lng}/
5. Frontend loads via next-i18next HTTP backend
```

### RTL Support (Urdu)
```css
/* globals.css */
[dir="rtl"] {
  direction: rtl;
}

[dir="rtl"] .flex {
  flex-direction: row-reverse;
}

[dir="rtl"] .text-left {
  text-align: right;
}

/* Use logical properties */
margin-inline-start: 16px;  /* Instead of margin-left */
padding-inline-end: 8px;    /* Instead of padding-right */
```

---

## 📍 Location & GIS - MapMyIndia Integration

### MapMyIndia API Configuration
```python
# backend/smartgriev/settings.py
MAPMYINDIA_CONFIG = {
    'API_KEY': os.getenv('MAPMYINDIA_API_KEY'),
    'BASE_URL': 'https://atlas.mapmyindia.com/api',
    'ENDPOINTS': {
        'geocode': '/places/geocode',
        'reverse_geocode': '/places/geoplace',
        'place_search': '/places/search',
        'directions': '/directions',
    }
}
```

### Location Services
```python
# backend/complaints/services/location.py
class LocationService:
    def forward_geocode(self, address: str) -> dict:
        """Convert address to coordinates"""
        response = requests.get(
            f"{BASE_URL}/places/geocode",
            params={'address': address},
            headers={'Authorization': f'Bearer {API_KEY}'}
        )
        return {
            'lat': response.json()['lat'],
            'lng': response.json()['lng'],
            'confidence': self.calculate_confidence(response)
        }
    
    def reverse_geocode(self, lat: float, lng: float) -> dict:
        """Convert coordinates to address"""
        response = requests.get(
            f"{BASE_URL}/places/geoplace",
            params={'lat': lat, 'lng': lng},
            headers={'Authorization': f'Bearer {API_KEY}'}
        )
        return response.json()
    
    def generate_plus_code(self, lat: float, lng: float) -> str:
        """Generate Open Location Code (Plus Code)"""
        from openlocationcode import openlocationcode as olc
        return olc.encode(lat, lng, codeLength=10)  # e.g., 7FG5+RW5
```

### PostGIS Spatial Queries
```sql
-- Find municipal corporation for a complaint location
SELECT code, name 
FROM integrations_corporation
WHERE ST_Within(
    ST_SetSRID(ST_MakePoint(72.8777, 19.0760), 4326),  -- Mumbai coords
    jurisdiction
);

-- Find complaints within 500m radius
SELECT * 
FROM complaints_complaint
WHERE ST_DWithin(
    location,
    ST_SetSRID(ST_MakePoint(72.8777, 19.0760), 4326),
    500  -- meters
);

-- Auto-assign ward based on location
SELECT ward_number, ward_name
FROM spatial_wards
WHERE ST_Within(complaint_location, geom);
```

### Location Confidence Scoring
```python
def calculate_location_confidence(gps_accuracy, has_pincode, has_landmark) -> float:
    """
    High: GPS <10m + pincode match = 0.95
    Medium: GPS 10-50m + landmark = 0.70
    Low: Manual address only = 0.40
    """
    if gps_accuracy < 10 and has_pincode:
        return 0.95
    elif gps_accuracy < 50 and has_landmark:
        return 0.70
    else:
        return 0.40
```

---

## 🔔 Notifications - Multi-Channel System

### Notification Channels
```python
# backend/notifications/models.py
class Notification(models.Model):
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('inapp', 'In-App'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.JSONField()  # Multilingual: {"en": "...", "hi": "..."}
    body = models.JSONField()   # Multilingual
    channel = models.CharField(max_length=10, choices=CHANNELS)
    complaint = models.ForeignKey(Complaint, null=True)
    read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
```

### Celery Tasks
```python
# backend/notifications/tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_notification(self, notification_id):
    notification = Notification.objects.get(id=notification_id)
    
    try:
        if notification.channel == 'email':
            send_email_notification(notification)
        elif notification.channel == 'sms':
            send_sms_notification(notification)  # Twilio
        elif notification.channel == 'push':
            send_push_notification(notification)  # FCM
        elif notification.channel == 'inapp':
            send_websocket_notification(notification)
        
        notification.sent = True
        notification.save()
    except Exception as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
```

### Email Templates (MJML)
```xml
<!-- notifications/templates/complaint_submitted.mjml -->
<mjml>
  <mj-body>
    <mj-section background-color="#2563EB">
      <mj-column>
        <mj-text font-size="24px" color="#ffffff">
          {{title.{{lang}}}}
        </mj-text>
      </mj-column>
    </mj-section>
    <mj-section>
      <mj-text>
        {{body.{{lang}}}}
      </mj-text>
      <mj-button href="{{tracking_url}}">
        Track Complaint
      </mj-button>
    </mj-section>
  </mj-body>
</mjml>
```

### Notification Triggers
```python
# Automatic triggers
TRIGGERS = {
    'complaint_submitted': ['email', 'sms', 'inapp'],
    'status_changed': ['email', 'push', 'inapp'],
    'municipal_update': ['email', 'inapp'],
    'resolution_request': ['email', 'sms', 'push'],
    'complaint_resolved': ['email', 'sms', 'inapp'],
}
```

---

## 🎤 Voice & Vision AI

### Voice Input (Web Speech API)
```typescript
// frontend/components/VoiceInput.tsx
import { useState, useEffect } from 'react';

export function VoiceInput({ onTranscript }) {
  const [recognition, setRecognition] = useState(null);
  
  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'hi-IN';  // Hindi
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        onTranscript(transcript);
      };
      
      setRecognition(recognition);
    }
  }, []);
  
  const startListening = () => {
    recognition?.start();
  };
  
  return (
    <button onClick={startListening}>
      🎤 Speak in Hindi
    </button>
  );
}
```

### Vision API (Gemini 1.5 Pro)
```python
# backend/complaints/services/vision_analyzer.py
import google.generativeai as genai

class VisionAnalyzer:
    def analyze_image(self, image_path: str) -> dict:
        """Analyze complaint image with Gemini 1.5 Pro"""
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        prompt = """
        Analyze this civic complaint image.
        Identify:
        1. Type of issue (pothole, garbage, leakage, etc.)
        2. Severity (1-5)
        3. Suggested department
        4. Visible location markers
        
        Output JSON only.
        """
        
        response = model.generate_content([prompt, image_data])
        return json.loads(response.text)
```

---

## 🔌 Real-Time Features - WebSockets

### Django Channels Configuration
```python
# backend/smartgriev/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from complaints.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

### WebSocket Consumer
```python
# backend/complaints/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ComplaintConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.group_name = f'user_{self.user_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def complaint_status_changed(self, event):
        await self.send_json({
            'type': 'status_change',
            'complaint_id': event['complaint_id'],
            'old_status': event['old_status'],
            'new_status': event['new_status'],
            'timestamp': event['timestamp']
        })
```

### Frontend WebSocket Client
```typescript
// frontend/lib/websocket.ts
import { useEffect } from 'react';

export function useComplaintWebSocket(userId: string) {
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/complaints/user_${userId}/`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'status_change') {
        // Update UI
        toast.success(`Complaint ${data.complaint_id} status changed to ${data.new_status}`);
      }
    };
    
    return () => ws.close();
  }, [userId]);
}
```

---

## 📊 Analytics & Observability

### OpenTelemetry Tracing
```python
# backend/smartgriev/middleware.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

tracer_provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)
tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(tracer_provider)

class TracingMiddleware:
    def __call__(self, request):
        with trace.get_tracer(__name__).start_as_current_span(
            f"{request.method} {request.path}",
            attributes={
                'user.id': request.user.id,
                'http.method': request.method,
                'http.url': request.path,
            }
        ) as span:
            response = self.get_response(request)
            span.set_attribute('http.status_code', response.status_code)
            return response
```

### Prometheus Metrics
```python
# backend/complaints/metrics.py
from prometheus_client import Counter, Histogram, Gauge

complaints_total = Counter(
    'complaints_total',
    'Total complaints submitted',
    ['department', 'status']
)

gemini_latency = Histogram(
    'gemini_classification_latency_seconds',
    'Gemini API latency',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

gemini_cost = Counter(
    'gemini_cost_dollars',
    'Total Gemini API cost',
    ['model']
)
```

### Grafana Dashboards
```json
{
  "dashboard": {
    "title": "SmartGriev - Municipal Health",
    "panels": [
      {
        "title": "Complaints by Department",
        "type": "graph",
        "targets": [{
          "expr": "sum(rate(complaints_total[5m])) by (department)"
        }]
      },
      {
        "title": "Average Resolution Time",
        "type": "singlestat",
        "targets": [{
          "expr": "avg(complaint_resolution_time_hours)"
        }]
      },
      {
        "title": "AI Classification Confidence",
        "type": "heatmap",
        "targets": [{
          "expr": "histogram_quantile(0.95, gemini_confidence_bucket)"
        }]
      }
    ]
  }
}
```

---

## 🚀 Performance Optimization

### 4-Layer Caching Strategy

#### Layer 1: Browser (Service Worker)
```typescript
// frontend/public/sw.js
const CACHE_NAME = 'smartgriev-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
```

#### Layer 2: CDN (Cloudflare ISR)
```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, s-maxage=300, stale-while-revalidate=600',
          },
        ],
      },
    ];
  },
};
```

#### Layer 3: Redis (Django Cache)
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'smartgriev',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Usage
from django.core.cache import cache

@cache_page(60 * 5)  # Cache for 5 minutes
def complaint_list(request):
    complaints = Complaint.objects.all()
    return Response(serializer.data)
```

#### Layer 4: Database (Materialized Views)
```sql
-- Materialized view for analytics
CREATE MATERIALIZED VIEW analytics_daily_stats AS
SELECT 
    DATE(created_at) as date,
    department,
    COUNT(*) as total_complaints,
    AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))/3600) as avg_resolution_hours
FROM complaints_complaint
WHERE resolved_at IS NOT NULL
GROUP BY date, department;

-- Refresh schedule (cron job)
REFRESH MATERIALIZED VIEW CONCURRENTLY analytics_daily_stats;
```

---

## 🧪 Testing Strategy

### Test Pyramid
```
E2E Tests (10%)
├── Login → File Complaint → Track → Resolve
├── Voice Input → Classification → Notification
└── Admin Panel → Complaint Management

Integration Tests (20%)
├── API Endpoints with real DB
├── Gemini API mocked responses
├── Twilio OTP flow
└── WebSocket connections

Unit Tests (70%)
├── Django models & serializers
├── React components
├── Gemini classifier logic
└── Location services
```

### Test Configuration
```python
# backend/pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = smartgriev.settings_test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

### Load Testing (k6)
```javascript
// tests/load/complaint_submission.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up
    { duration: '5m', target: 1000 },  // Peak load
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% < 500ms
  },
};

export default function () {
  let response = http.post('http://localhost:8000/api/v1/complaints/', {
    title: 'Load test complaint',
    description: 'Testing system under load',
  });
  
  check(response, {
    'status is 201': (r) => r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

---

## 🔒 Security Hardening

### OWASP Top 10 Mitigation

#### 1. Injection Prevention
```python
# Always use ORM, never raw SQL
# BAD
Complaint.objects.raw(f"SELECT * FROM complaints WHERE id = {user_input}")

# GOOD
Complaint.objects.filter(id=user_input)
```

#### 2. Authentication & Session Management
```python
# settings.py
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JS access
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True

# Rate limiting
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='5/15m', method='POST')
def login_view(request):
    # Max 5 login attempts per 15 minutes
    pass
```

#### 3. XSS Prevention
```typescript
// React auto-escapes, but for raw HTML:
import DOMPurify from 'dompurify';

function SafeHtml({ html }) {
  const clean = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
```

#### 4. CSP Headers
```python
# settings.py
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # Minimize unsafe-inline
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = (
    "'self'",
    "https://generativelanguage.googleapis.com",
    "https://apis.mapmyindia.com",
)
```

### Encryption Implementation
```python
# Sensitive field encryption with pgcrypto
from django.db import models
from django.contrib.postgres.fields import CITextField

class User(models.Model):
    email = CITextField()  # Case-insensitive
    phone = models.CharField(max_length=20)  # Encrypted
    
    class Meta:
        db_table = 'users_user'
    
    def save(self, *args, **kwargs):
        # Encrypt phone before saving
        from cryptography.fernet import Fernet
        key = settings.ENCRYPTION_KEY
        f = Fernet(key)
        self.phone = f.encrypt(self.phone.encode())
        super().save(*args, **kwargs)
```

---

## 🌍 Production Deployment

### Infrastructure Stack

```
┌─────────────────────────────────────────────────────────┐
│                    CLOUDFLARE                           │
│  DDoS Protection | WAF | CDN | DNS | SSL               │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴─────────────────┐
        │                                   │
┌───────▼────────┐              ┌──────────▼──────────┐
│   VERCEL       │              │    AWS (Mumbai)     │
│  Next.js App   │              │  ap-south-1         │
│  Global CDN    │              │                     │
│  ISR + Edge    │              │  ┌───────────────┐  │
└────────────────┘              │  │  ECS Fargate  │  │
                                │  │  Django API   │  │
                                │  └───────┬───────┘  │
                                │          │          │
                                │  ┌───────▼───────┐  │
                                │  │ RDS PostgreSQL│  │
                                │  │  Multi-AZ     │  │
                                │  │  db.r5.large  │  │
                                │  └───────────────┘  │
                                │                     │
                                │  ┌───────────────┐  │
                                │  │ ElastiCache   │  │
                                │  │ Redis Cluster │  │
                                │  └───────────────┘  │
                                │                     │
                                │  ┌───────────────┐  │
                                │  │  S3 + CF      │  │
                                │  │  Media Files  │  │
                                │  └───────────────┘  │
                                └─────────────────────┘
```

### Environment Variables (.env.production)
```bash
# Django
DJANGO_SECRET_KEY=<from-aws-secrets-manager>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.smartgriev.in
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000

# Database
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/smartgriev
DATABASE_CONN_MAX_AGE=600

# Redis
REDIS_URL=redis://elasticache-endpoint:6379/0

# Twilio (✅ Already configured)
TWILIO_ACCOUNT_SID=<your-twilio-account-sid>
TWILIO_AUTH_TOKEN=<your-twilio-auth-token>
TWILIO_VERIFY_SERVICE_SID=<your-twilio-verify-service-sid>

# Gemini AI
GEMINI_API_KEY=<from-secrets-manager>

# MapMyIndia
MAPMYINDIA_API_KEY=<from-secrets-manager>

# AWS
AWS_ACCESS_KEY_ID=<from-secrets-manager>
AWS_SECRET_ACCESS_KEY=<from-secrets-manager>
AWS_STORAGE_BUCKET_NAME=smartgriev-media
AWS_S3_REGION_NAME=ap-south-1

# Monitoring
SENTRY_DSN=<sentry-project-dsn>
```

### Deployment Commands
```bash
# Backend (AWS ECS)
docker build -t smartgriev-api:latest .
docker tag smartgriev-api:latest <ecr-repo>:latest
docker push <ecr-repo>:latest
aws ecs update-service --cluster smartgriev --service api --force-new-deployment

# Frontend (Vercel)
vercel deploy --prod

# Database Migration
python manage.py migrate --no-input

# Static Files
python manage.py collectstatic --no-input
aws s3 sync staticfiles/ s3://smartgriev-static/
```

---

## 📋 Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2) ✅ CURRENT
- [x] Basic Django backend with DRF
- [x] Vite + React + TypeScript frontend
- [x] Twilio Verify OTP authentication
- [x] SQLite database
- [x] Basic complaint CRUD
- [x] 8 languages support

### Phase 2: Enhancement (Weeks 3-4)
- [ ] Implement djangorestframework-simplejwt
- [ ] Add JWT httpOnly cookie authentication
- [ ] Enhance complaint model with status_history
- [ ] Add complaint number format: BC-{YEAR}-{CITY}-{DEPT}-{SEQ}
- [ ] Integrate Gemini 1.5 Flash for classification
- [ ] Add DistilBERT fallback classifier
- [ ] Expand to 12 languages (add Urdu, Assamese, Odia, Punjabi)
- [ ] Implement RTL support for Urdu

### Phase 3: Database Migration (Weeks 5-6)
- [ ] Setup PostgreSQL 15 with PostGIS
- [ ] Create migration scripts from SQLite
- [ ] Implement UUID primary keys
- [ ] Add JSONB fields for multilingual content
- [ ] Create GIN and GiST indexes
- [ ] Setup PgBouncer connection pooling
- [ ] Implement pgcrypto for sensitive fields

### Phase 4: Location & GIS (Week 7)
- [ ] Integrate MapMyIndia API
- [ ] Implement forward/reverse geocoding
- [ ] Add Plus Code generation
- [ ] Create PostGIS spatial queries
- [ ] Implement ward auto-assignment
- [ ] Add location confidence scoring

### Phase 5: Frontend Migration (Weeks 8-9)
- [ ] Setup Next.js 14 with App Router
- [ ] Migrate pages to [lang] prefixed routes
- [ ] Implement Zustand for state management
- [ ] Setup SWR for data fetching
- [ ] Configure next/image and next/font
- [ ] Add Tailwind CSS with CSS variables
- [ ] Integrate shadcn/ui components

### Phase 6: Real-Time & Notifications (Week 10)
- [ ] Setup django-channels with Redis
- [ ] Implement WebSocket consumers
- [ ] Add Socket.IO client in frontend
- [ ] Create multi-channel notification system
- [ ] Setup Celery for async tasks
- [ ] Implement MJML email templates
- [ ] Add Firebase Cloud Messaging for push

### Phase 7: Voice & Vision (Week 11)
- [ ] Integrate Web Speech API for voice input
- [ ] Implement Gemini 1.5 Pro vision API
- [ ] Add image analysis for complaints
- [ ] Support video uploads with frame extraction
- [ ] Multi-language voice support (Hindi, English, etc.)

### Phase 8: Analytics & Monitoring (Week 12)
- [ ] Setup OpenTelemetry tracing
- [ ] Configure Prometheus metrics
- [ ] Create Grafana dashboards
- [ ] Implement structured JSON logging
- [ ] Add Sentry error tracking
- [ ] Setup Helicone for Gemini monitoring

### Phase 9: Testing & Security (Week 13)
- [ ] Write unit tests (80% coverage goal)
- [ ] Create integration tests
- [ ] Implement E2E tests with Playwright
- [ ] Add k6 load testing scripts
- [ ] Security audit (OWASP Top 10)
- [ ] Implement rate limiting
- [ ] Add CSP headers

### Phase 10: Production Deployment (Week 14)
- [ ] Setup AWS infrastructure (ECS, RDS, ElastiCache)
- [ ] Deploy Next.js on Vercel
- [ ] Configure Cloudflare CDN and WAF
- [ ] Setup CI/CD pipeline (GitHub Actions)
- [ ] Implement monitoring and alerts
- [ ] Performance optimization (caching, CDN)
- [ ] Go live! 🚀

---

## 🎯 Success Metrics

### Technical Metrics
- **API Latency**: p95 < 500ms
- **Page Load**: p95 < 2s
- **AI Classification**: 
  - Accuracy > 85% (with Gemini)
  - Confidence > 0.7 for 90% of cases
- **Test Coverage**: > 80%
- **Uptime**: 99.9% SLA

### Business Metrics
- **User Adoption**: 10,000 registered users in 3 months
- **Complaint Resolution**: Average 48 hours
- **User Satisfaction**: > 4.5/5 rating
- **Municipal Efficiency**: 30% reduction in resolution time

### Cost Metrics
- **Gemini API**: < $500/month
- **AWS Infrastructure**: < $300/month
- **Twilio SMS**: < $100/month (with current volume)
- **Total Operating Cost**: < $1000/month

---

## 📚 References

### Documentation
- Django: https://docs.djangoproject.com/
- Next.js: https://nextjs.org/docs
- Gemini API: https://ai.google.dev/docs
- PostGIS: https://postgis.net/documentation/
- MapMyIndia: https://www.mapmyindia.com/api/
- Twilio Verify: https://www.twilio.com/docs/verify

### Best Practices
- OWASP Top 10: https://owasp.org/Top10/
- Web.dev Performance: https://web.dev/performance/
- WCAG 2.1 AA: https://www.w3.org/WAI/WCAG21/quickref/

---

## 📞 Support & Contact

**Project Owner**: Jenish Barvaliya  
**Email**: jenishbarvaliya.it22@scet.ac.in  
**Mobile**: +91 9510007247  
**GitHub**: https://github.com/jenish2917/smartgriev

---

## 📊 Appendix A: Cost Calculation Sheet

### Monthly Operating Costs (10,000 complaints/day projection)

| Component | Unit Cost | Monthly Usage | Monthly Cost |
|-----------|-----------|---------------|--------------|
| **AI Services** |
| Gemini 1.5 Flash (90%) | $0.35/M tokens | ~150M tokens | $52.50 |
| Gemini 1.5 Pro (10%) | $7.00/M tokens | ~15M tokens | $105.00 |
| **Compute & Storage** |
| AWS ECS Fargate (2 tasks) | $0.04/hour | 1440 hours | $57.60 |
| RDS PostgreSQL (db.r5.large) | $0.168/hour | 720 hours | $120.96 |
| ElastiCache Redis (cache.r5.large) | $0.126/hour | 720 hours | $90.72 |
| S3 Storage | $0.023/GB | ~500GB | $11.50 |
| CloudFront Data Transfer | $0.085/GB | ~300GB | $25.50 |
| **Communication** |
| Twilio Verify (OTP) | $0.05/verification | 5000/month | $250.00 |
| AWS SES (Email) | $0.10/1000 | 50000 emails | $5.00 |
| **Platform** |
| Vercel Pro | Fixed | - | $20.00 |
| Cloudflare Pro | Fixed | - | $20.00 |
| **TOTAL** | | | **$758.78/month** |

**Break-even Point**: 15,000 active users (assuming ₹50/user/year subscription)

### Cost Optimization Strategies
1. **Gemini Caching**: 24-hour semantic cache = 40% cost reduction
2. **Reserved Instances**: 1-year RDS reservation = 30% savings
3. **S3 Lifecycle**: Move old media to Glacier after 90 days = 70% storage savings
4. **CDN Optimization**: Cloudflare caching = 50% origin request reduction

---

## 🧪 Appendix B: Load Testing Scripts (k6)

### Complaint Submission Test
```javascript
// tests/load/complaint_submission.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Warm up
    { duration: '5m', target: 1000 },  // Peak load
    { duration: '2m', target: 0 },     // Cool down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const payload = JSON.stringify({
    description: 'मेरी गली में पानी नहीं आ रहा है। कृपया जल्दी ठीक करें।',
    location: { lat: 19.0760, lng: 72.8777 },
    address: { pincode: '400001', landmark: 'CST Station' },
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.JWT_TOKEN}`,
    },
  };

  const res = http.post(
    'https://api.smartgriev.in/api/v1/complaints/',
    payload,
    params
  );

  check(res, {
    'status is 201': (r) => r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'has complaint_number': (r) => r.json('complaint_number') !== null,
  });

  sleep(Math.random() * 3 + 1); // Random delay 1-4 seconds
}
```

### Gemini Classification Stress Test
```javascript
// tests/load/gemini_classification.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 500, // 500 virtual users
  duration: '10m',
  thresholds: {
    'gemini_latency': ['p(95)<2000'],
    'gemini_cost': ['count<100'], // Max $100 during test
  },
};

const complaints = [
  'सड़क पर बड़ा गड्ढा है',
  'Street light not working',
  'Garbage not collected for 3 days',
  'పాలేరు పైపు లీక్ అయింది',
  'રસ્તા પર ગટર ખુલ્લું છે',
];

export default function () {
  const text = complaints[Math.floor(Math.random() * complaints.length)];
  
  const res = http.post('https://api.smartgriev.in/api/v1/chatbot/classify', {
    text: text,
    language: 'auto',
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'confidence > 0.7': (r) => r.json('confidence') > 0.7,
  });
}
```

---

## 🔒 Appendix C: Security Audit Checklist

### Pre-Production Checklist
- [ ] `pip-audit` run and all vulnerabilities fixed
- [ ] `npm audit` passing with 0 high/critical issues
- [ ] Dependabot enabled for auto-dependency updates
- [ ] Sentry DSN configured and error tracking active
- [ ] CSP header deployed and tested
- [ ] Rate limiting active on all endpoints
- [ ] JWT secret rotated and stored in AWS Secrets Manager
- [ ] Database backups tested (restore within 15 minutes)
- [ ] Penetration testing completed (quarterly schedule set)
- [ ] Bug bounty program documented
- [ ] GDPR/CCPA data deletion process implemented
- [ ] Incident response plan reviewed and shared with team
- [ ] 2FA enforced for admin accounts
- [ ] API keys rotated every 90 days
- [ ] HTTPS enforced (HSTS header active)
- [ ] XSS protection tested (DOMPurify implemented)
- [ ] SQL injection tests passed (ORM-only queries)
- [ ] CORS configured with strict origins
- [ ] File upload validation (type, size, malware scan)
- [ ] Audit logs enabled for admin actions

### Monthly Security Tasks
- [ ] Review access logs for anomalies
- [ ] Update dependencies (npm, pip)
- [ ] Rotate API keys
- [ ] Review user permissions
- [ ] Check backup integrity
- [ ] Test disaster recovery plan

### Quarterly Security Tasks
- [ ] Penetration testing by third-party
- [ ] Security training for team
- [ ] Review and update incident response plan
- [ ] Audit all third-party integrations
- [ ] Review and update privacy policy

---

## 🚀 Appendix D: Deployment Runbook

### Production Deployment Steps

#### Pre-Deployment
1. **Code Review**: All PRs approved by 2+ reviewers
2. **Tests Passing**: 
   ```bash
   pytest --cov=. --cov-report=html
   npm run test
   npm run test:e2e
   ```
3. **Staging Verification**: Test on staging environment
4. **Database Backup**: 
   ```bash
   pg_dump smartgriev_prod > backup_$(date +%Y%m%d).sql
   ```
5. **Notify Team**: Announce deployment in #deployments Slack

#### Deployment
```bash
# 1. Merge to main branch
git checkout main
git merge --no-ff feature/new-feature
git push origin main

# 2. GitHub Actions auto-triggers deployment

# 3. Backend (AWS ECS)
docker build -t smartgriev-api:${GIT_SHA} .
docker tag smartgriev-api:${GIT_SHA} ${ECR_REPO}:latest
docker push ${ECR_REPO}:${GIT_SHA}
aws ecs update-service \
  --cluster smartgriev-prod \
  --service api \
  --force-new-deployment

# 4. Run Migrations (via ECS task)
aws ecs run-task \
  --cluster smartgriev-prod \
  --task-definition migrate \
  --overrides '{"containerOverrides": [{"name": "migrate", "command": ["python", "manage.py", "migrate"]}]}'

# 5. Frontend (Vercel)
vercel deploy --prod

# 6. Health Check
curl https://api.smartgriev.in/health
# Expected: {"status": "ok", "version": "3.0"}
```

#### Post-Deployment
1. **Monitor Sentry**: Check for new errors (5 min)
2. **Monitor Metrics**: Watch Grafana dashboards (15 min)
3. **Smoke Test**: Run critical user journeys
4. **Verify Twilio**: Test OTP flow with real mobile
5. **Announce Success**: Update #deployments Slack

#### Rollback Procedure
```bash
# If errors detected, rollback immediately

# Backend Rollback
aws ecs update-service \
  --cluster smartgriev-prod \
  --service api \
  --task-definition api:${PREVIOUS_VERSION}

# Frontend Rollback
vercel rollback

# Database Rollback (if migrations failed)
psql smartgriev_prod < backup_20251109.sql
```

---

## 🔄 Appendix E: Feedback & Improvement Loop

### AI Model Improvement
```python
# backend/complaints/services/feedback_collector.py
class FeedbackCollector:
    def collect_user_correction(self, complaint_id, correct_dept):
        """When user corrects AI classification"""
        complaint = Complaint.objects.get(id=complaint_id)
        
        Feedback.objects.create(
            complaint=complaint,
            gemini_prediction=complaint.gemini_raw_response['department'],
            user_correction=correct_dept,
            confidence_score=complaint.gemini_raw_response['confidence'],
            created_at=timezone.now()
        )
        
        # If corrections exceed threshold, trigger retraining
        monthly_corrections = Feedback.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        if monthly_corrections > 1000:
            self.trigger_model_retraining()
    
    def trigger_model_retraining(self):
        """Retrain DistilBERT fallback model monthly"""
        from celery import current_app
        current_app.send_task(
            'ml_tasks.retrain_classifier',
            kwargs={'feedback_count': 1000}
        )
```

### User Satisfaction Tracking
```python
# Post-resolution survey
class ResolutionFeedback(models.Model):
    complaint = models.OneToOneField(Complaint)
    satisfaction_rating = models.IntegerField(1, 5)  # 1-5 stars
    resolution_time_satisfied = models.BooleanField()
    would_recommend = models.BooleanField()
    comments = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Alert if low rating
        if self.satisfaction_rating <= 2:
            notify_admin.delay(
                f"Low satisfaction: {self.complaint.complaint_number}"
            )
```

---

## 🎯 Appendix F: Municipal Integration Spec

### Adapter Pattern for Multiple Municipalities
```python
# backend/integrations/base.py
from abc import ABC, abstractmethod

class MunicipalAdapter(ABC):
    """Base class for all municipal integrations"""
    
    @abstractmethod
    def submit_complaint(self, complaint) -> str:
        """Submit complaint and return municipal tracking ID"""
        pass
    
    @abstractmethod
    def get_status(self, municipal_id) -> dict:
        """Fetch complaint status from municipal portal"""
        pass
    
    @abstractmethod
    def get_ward(self, location) -> str:
        """Determine ward from GPS coordinates"""
        pass

# backend/integrations/mumbai.py
class MumbaiMCGMAdapter(MunicipalAdapter):
    API_URL = "https://portal.mcgm.gov.in/api"
    
    def submit_complaint(self, complaint):
        """Submit to MCGM Water Department"""
        payload = {
            "complainant_name": complaint.user.full_name,
            "complainant_mobile": complaint.user.phone,
            "complaint_location": {
                "ward": self.get_ward(complaint.location),
                "address": complaint.address,
                "pincode": complaint.pincode,
            },
            "complaint_details": complaint.description,
            "department": self.map_department(complaint.department),
            "priority": complaint.priority,
        }
        
        response = requests.post(
            f"{self.API_URL}/complaints/submit",
            json=payload,
            headers={"Authorization": f"Bearer {settings.MCGM_API_KEY}"},
            timeout=30
        )
        
        return response.json()['complaint_id']
    
    def get_status(self, municipal_id):
        """Poll MCGM for status updates"""
        response = requests.get(
            f"{self.API_URL}/complaints/{municipal_id}",
            headers={"Authorization": f"Bearer {settings.MCGM_API_KEY}"}
        )
        return {
            'status': response.json()['status'],
            'last_updated': response.json()['updated_at'],
            'notes': response.json()['notes']
        }
    
    def map_department(self, dept):
        """Map SmartGriev dept to MCGM dept codes"""
        mapping = {
            'water': 'HYD_WAT',
            'roads': 'ROA_MTN',
            'sanitation': 'SWM_CLN',
        }
        return mapping.get(dept, 'GENERAL')
```

---

## 💬 Appendix G: Sample Gemini Prompts

### System Prompt for Classification
```python
SYSTEM_PROMPT = """
You are BharatConnect AI, an expert municipal complaint classifier for Indian cities.

RULES:
1. Output ONLY valid JSON (no markdown, no explanation)
2. Detect language automatically from these: en, hi, bn, te, mr, ta, gu, kn, ml, pa, ur, as, or
3. Extract precise location details
4. Assign priority: 1=emergency (health/safety threat), 2=urgent, 3=normal, 4=low, 5=general inquiry
5. Confidence score: 0.0-1.0 based on text clarity

DEPARTMENTS:
water, electricity, roads, sanitation, waste, streetlights, parks, building, fire, other

DEPARTMENT KEYWORDS (12 Languages):
water: water, पानी(hi), পানি(bn), నీరు(te), पाणी(mr), தண்ணீர்(ta), પાણી(gu), ನೀರು(kn), വെള്ളം(ml), ਪਾਣੀ(pa), پانی(ur), পানী(as), ପାଣି(or)
electricity: electricity, बिजली(hi), বিদ্যুৎ(bn), విద్యుత్(te), वीज(mr), மின்சாரம்(ta), વીજળી(gu), ವಿದ್ಯುತ್(kn), വൈദ്യുതി(ml), ਬਿਜਲੀ(pa), بجلی(ur), বিদ্যুৎ(as), ବିଦ୍ୟୁତ୍(or)
roads: road, सड़क(hi), রাস্তা(bn), రోడ్డు(te), रस्ता(mr), சாலை(ta), રસ્તો(gu), ರಸ್ತೆ(kn), റോഡ്(ml), ਸੜਕ(pa), سڑک(ur), পথ(as), ରାସ୍ତା(or)

EXAMPLES (Few-Shot Learning):
Input: "मेरी गली में 3 दिन से पानी नहीं आ रहा। क्षेत्र: बांद्रा पूर्व, मुंबई - 400051"
Output: {"department": "water", "sub_category": "No water supply for 3 days", "priority": 2, "confidence": 0.95, "language": "hi", "entities": {"location": "Bandra East, Mumbai", "pincode": "400051", "landmark": ""}}

Input: "Big pothole near CST Station causing accidents"
Output: {"department": "roads", "sub_category": "Large pothole causing safety hazard", "priority": 2, "confidence": 0.92, "language": "en", "entities": {"location": "", "pincode": "", "landmark": "CST Station"}}

OUTPUT FORMAT:
{
  "department": "string",
  "sub_category": "detailed issue description",
  "priority": 1-5,
  "confidence": 0.0-1.0,
  "language": "ISO 639-1 code",
  "entities": {
    "location": "extracted address",
    "pincode": "6-digit postal code or empty",
    "landmark": "nearby landmark or empty"
  },
  "reasoning": "brief explanation in English"
}
"""
```

### User Prompt Template
```python
def build_user_prompt(text: str, context: dict = None) -> str:
    prompt = f"Classify this complaint:\n\n{text}"
    
    if context:
        if context.get('previous_complaints'):
            prompt += f"\n\nUser's previous complaints: {context['previous_complaints']}"
        
        if context.get('location_hint'):
            prompt += f"\n\nUser's city: {context['location_hint']}"
    
    return prompt
```

---

## 📊 Appendix H: Real-Time Dashboard Features

### Municipal Officer Dashboard (Real-Time)
```typescript
// Features for admin panel
interface DashboardMetrics {
  // Real-time counters (WebSocket)
  pendingComplaints: number;
  inProgressComplaints: number;
  resolvedToday: number;
  averageResolutionTime: string; // "2.5 hours"
  
  // Charts
  departmentBreakdown: {
    water: number;
    roads: number;
    electricity: number;
    // ...
  };
  
  // Live feed
  recentComplaints: Complaint[];
  highPriorityAlerts: Complaint[];
  
  // AI metrics
  aiAccuracy: number; // 0.85 = 85%
  geminiCostToday: number; // $12.50
}

// WebSocket implementation
const ws = new WebSocket('wss://api.smartgriev.in/ws/dashboard/');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  
  if (update.type === 'new_complaint') {
    showNotification(update.complaint);
    updateMetrics();
  }
};
```

---

## ⚠️ Appendix I: Critical Challenges & Mitigation

### Challenge 1: Municipal API Integration
**Problem**: Most Indian municipalities lack APIs  
**Mitigation**:
- Manual submission fallback (PDF generation + email to municipal officer)
- Scraping municipal portals (with rate limiting)
- Direct database integration where permitted
- Build relationships with municipal IT departments

### Challenge 2: Gemini API Costs Exceeding Budget
**Problem**: $500/month cap could be exceeded  
**Mitigation**:
- Aggressive caching (24-hour TTL semantic cache)
- Switch to DistilBERT fallback when budget 80% consumed
- User prompt optimization (limit to 500 chars)
- Batch processing during off-peak hours

### Challenge 3: Low Internet Connectivity in Rural Areas
**Problem**: Users can't upload images/videos  
**Mitigation**:
- Progressive Web App (PWA) with offline mode
- Image compression (WebP format, max 500KB)
- SMS-based complaint filing (premium feature)
- Voice notes instead of text (smaller file size)

### Challenge 4: Language Detection Accuracy
**Problem**: Hinglish and code-mixing confuse models  
**Mitigation**:
- Gemini excels at mixed language understanding
- Manual language selector as fallback
- User correction feedback loop improves over time

### Challenge 5: Scalability During Viral Events
**Problem**: 10x traffic spike when issue goes viral  
**Mitigation**:
- Auto-scaling ECS tasks (2-10 instances)
- CloudFront CDN absorbs read traffic
- Read replicas for database
- Celery queue absorbs spikes

---

## ✅ Appendix J: Getting Started Checklist (This Week)

### Day 1-2: Environment Setup
- [ ] Clone repository
- [ ] Setup PostgreSQL 15 locally
- [ ] Install Python 3.11+ and Node.js 20+
- [ ] Create virtual environment
- [ ] Install backend dependencies: `pip install -r requirements.txt`
- [ ] Install frontend dependencies: `npm install`
- [ ] Setup `.env` file with Twilio credentials
- [ ] Setup `.env` with Gemini API key
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`

### Day 3-4: Core Features Testing
- [ ] Test Twilio OTP flow (✅ Already working!)
- [ ] Test Gemini classification with sample complaints
- [ ] Test complaint CRUD operations
- [ ] Test multilingual UI (switch between Hindi/English)
- [ ] Test location picker (GPS + manual)

### Day 5-7: Local Development
- [ ] Run backend: `python manage.py runserver 8000`
- [ ] Run frontend: `npm run dev`
- [ ] Test end-to-end flow: Register → Login → File Complaint → Track
- [ ] Fix any bugs found
- [ ] Write tests for critical paths
- [ ] Document setup process for team

---

## 🎛️ Appendix K: YAML & Configuration Files

### docker-compose.yml (Production)
```yaml
version: '3.8'

services:
  # Django Backend
  web:
    build: ./backend
    command: gunicorn smartgriev.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker
  celery_worker:
    build: ./backend
    command: celery -A smartgriev worker -l info -Q default,high,low
    env_file:
      - .env.production
    depends_on:
      - redis
      - db

  # Celery Beat (Scheduler)
  celery_beat:
    build: ./backend
    command: celery -A smartgriev beat -l info
    env_file:
      - .env.production
    depends_on:
      - redis

  # PostgreSQL Database
  db:
    image: postgis/postgis:15-3.3
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: smartgriev
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### GitHub Actions CI/CD
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test
          npm run test:e2e

  deploy:
    needs: [backend-tests, frontend-tests]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy Backend to AWS ECS
        run: |
          # Deploy steps here
          
      - name: Deploy Frontend to Vercel
        run: |
          npx vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## 🔄 Appendix L: Circuit Breaker Pattern

### Gemini API Circuit Breaker
```python
# backend/complaints/services/circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta
import redis

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, using fallback
    HALF_OPEN = "half_open"  # Testing recovery

class GeminiCircuitBreaker:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.failure_threshold = 5  # Open after 5 failures
        self.timeout = 300  # 5 minutes
        self.half_open_requests = 10  # Test 10% of traffic
    
    def call(self, func, *args, **kwargs):
        state = self.get_state()
        
        if state == CircuitState.OPEN:
            # Check if timeout expired
            if self.should_attempt_reset():
                self.set_state(CircuitState.HALF_OPEN)
            else:
                # Use fallback
                return self.fallback()
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            if self.get_state() == CircuitState.OPEN:
                return self.fallback()
            raise
    
    def on_failure(self):
        failures = self.redis_client.incr('gemini:failures')
        if failures >= self.failure_threshold:
            self.set_state(CircuitState.OPEN)
            logger.error(f"Circuit breaker OPEN after {failures} failures")
    
    def on_success(self):
        self.redis_client.delete('gemini:failures')
        if self.get_state() == CircuitState.HALF_OPEN:
            self.set_state(CircuitState.CLOSED)
            logger.info("Circuit breaker CLOSED - Gemini API recovered")
    
    def fallback(self):
        """Use DistilBERT local model"""
        from .fallback_classifier import DistilBERTClassifier
        return DistilBERTClassifier().classify()
```

---

## 📈 Appendix M: Success Metrics & KPIs

### Technical Metrics (DevOps)
| Metric | Target | Measurement |
|--------|--------|-------------|
| API Latency (p95) | < 500ms | Prometheus |
| API Latency (p99) | < 1000ms | Prometheus |
| Page Load Time (p95) | < 2s | Lighthouse CI |
| Uptime | 99.9% | Uptime Robot |
| Error Rate | < 0.1% | Sentry |
| Test Coverage | > 80% | Codecov |
| Build Time | < 5min | GitHub Actions |
| Deployment Frequency | Daily | GitHub Insights |

### AI/ML Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Classification Accuracy | > 85% | User corrections |
| Gemini Confidence (avg) | > 0.75 | Database |
| Fallback Rate | < 10% | Prometheus |
| API Cost/Day | < $20 | Helicone |
| Cache Hit Rate | > 40% | Redis INFO |

### Business Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Monthly Active Users | 10,000 | Analytics |
| Complaint Submissions/Day | 500 | Database |
| Average Resolution Time | < 48hrs | Database |
| User Satisfaction | > 4.5/5 | Post-resolution survey |
| Complaint Completion Rate | > 80% | Database |
| Returning Users (30-day) | > 60% | Analytics |

### Cost Metrics
| Metric | Target | Actual |
|--------|--------|--------|
| Monthly Operating Cost | < $1000 | $758.78 |
| Cost per Complaint | < $0.50 | $0.25 |
| Cost per User (Annual) | < $10 | $9.10 |

---

**Last Updated**: November 9, 2025  
**Document Version**: 3.0 - COMPLETE  
**Status**: Ready for Implementation 🚀  
**All Sections Merged**: ✅ PDF Spec + Current Project
