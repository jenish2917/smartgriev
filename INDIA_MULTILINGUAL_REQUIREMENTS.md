# SmartGriev - India Multi-Lingual AI-Powered Complaint System
**Generated:** November 7, 2025  
**Target Audience:** Indian Citizens (22 Official Languages + English)  
**Priority:** CRITICAL for Production Deployment in India  
**Core Innovation:** AI Chatbot-Driven Complaint Submission (No Traditional Forms)

---

## 🚀 Revolutionary Approach: AI-First Complaint System

### **🤖 Conversational AI Interface (Gemini API)**
**NO TRADITIONAL FORMS - 100% Chatbot Interaction**

SmartGriev prioritizes **user convenience** by eliminating traditional complaint forms entirely. Citizens interact with an intelligent AI chatbot powered by **Google Gemini API** that:

#### **Key Features:**
1. **Natural Conversation** - Users describe problems in their own words
2. **Multi-Lingual Chat** - AI understands and responds in 8+ Indian languages
3. **Context-Aware** - AI asks relevant follow-up questions automatically
4. **Smart Extraction** - AI extracts complaint details (category, location, priority) from conversation
5. **Voice + Text Support** - Citizens can speak or type in their preferred language
6. **Instant Validation** - Real-time guidance and clarification requests
7. **Automatic Classification** - AI categorizes complaints using ML models

#### **How It Works:**
```
User: "मेरे इलाके में पानी नहीं आ रहा है" (No water in my area)
AI: "मैं समझ गया। कृपया बताएं - आपका क्षेत्र कौन सा है?"
User: "Sector 15, Noida"
AI: "धन्यवाद! पानी की समस्या कब से है?"
User: "3 दिन से"
AI: "आपकी शिकायत दर्ज कर ली गई है। शिकायत संख्या: #12345"
```

**No Forms. No Fields. Just Natural Conversation.**

---

## 🇮🇳 India-Specific Requirements

### 🌐 Multi-Lingual Support (CRITICAL)

#### **Supported Languages - Phase 1 (Immediate)**
1. **Hindi** (हिन्दी) - Primary language, 528M speakers
2. **English** - Administrative language
3. **Bengali** (বাংলা) - 97M speakers
4. **Telugu** (తెలుగు) - 82M speakers
5. **Marathi** (मराठी) - 83M speakers
6. **Tamil** (தமிழ்) - 69M speakers
7. **Gujarati** (ગુજરાતી) - 56M speakers
8. **Kannada** (ಕನ್ನಡ) - 44M speakers

#### **Supported Languages - Phase 2 (Next Sprint)**
9. Malayalam (മലയാളം)
10. Odia (ଓଡ଼ିଆ)
11. Punjabi (ਪੰਜਾਬੀ)
12. Assamese (অসমীয়া)
13. Urdu (اردو)
14. Sanskrit (संस्कृत)
15. Konkani (कोंकणी)

### 🎯 Core Requirements for Indian Context

#### 1. **Voice-First Approach**
- ✅ Audio complaint submission (already implemented)
- ⚠️ **NEW:** Support for regional language voice input via Gemini API
- ⚠️ **NEW:** Automatic language detection in audio
- ⚠️ **NEW:** Multi-lingual speech-to-text (Google Cloud Speech + Gemini)
- ⚠️ **NEW:** Voice responses in user's preferred language
- ✅ **AI Chatbot:** Natural conversation-based complaint submission (Gemini API)

#### 2. **Low-Literacy Friendly**
- ✅ **AI Chatbot:** No forms to fill - just talk to the AI
- ⚠️ **NEW:** Icon-based navigation
- ⚠️ **NEW:** Visual complaint categories (pictures)
- ⚠️ **NEW:** Voice guidance for all major actions
- ⚠️ **NEW:** Simple, clear UI with minimal text
- ⚠️ **NEW:** Tutorial videos in regional languages
- ✅ **AI Chatbot:** AI explains everything in simple language

#### 3. **Mobile-First Design**
- ✅ Responsive design (already implemented)
- ⚠️ **NEW:** Offline complaint creation (PWA)
- ⚠️ **NEW:** Low-bandwidth mode (compressed images)
- ⚠️ **NEW:** SMS notifications (for non-smartphone users)
- ⚠️ **NEW:** USSD integration for feature phones

#### 4. **Government Integration**
- ⚠️ **NEW:** Aadhaar authentication support
- ⚠️ **NEW:** DigiLocker integration for document uploads
- ⚠️ **NEW:** UPI payment integration (for paid services)
- ⚠️ **NEW:** Integration with state government portals
- ⚠️ **NEW:** UMANG (Unified Mobile App for New-age Governance) compatibility

#### 5. **Regional Customization**
- ⚠️ **NEW:** State-specific complaint categories
- ⚠️ **NEW:** Local government department mapping
- ⚠️ **NEW:** Regional holiday calendars
- ⚠️ **NEW:** Zone/ward-based routing
- ⚠️ **NEW:** District-level analytics

#### 6. **Accessibility**
- ⚠️ **NEW:** Screen reader support in regional languages
- ⚠️ **NEW:** High contrast mode
- ⚠️ **NEW:** Font size adjustments
- ⚠️ **NEW:** Text-to-speech for all content
- ⚠️ **NEW:** Keyboard navigation

---

## 🤖 AI Chatbot Implementation (Gemini API)

### **Architecture Overview**

```
User Input (Voice/Text in any language)
    ↓
Language Detection (Auto)
    ↓
Google Gemini API
    ↓
Natural Language Understanding
    ↓
Complaint Information Extraction
    ↓
Validation & Confirmation
    ↓
Database Storage
    ↓
AI-Generated Summary (Multi-lingual)
```

### **Gemini API Integration**

**1. Core Chatbot Service**
```python
# backend/chatbot/gemini_service.py
class GeminiChatbotService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = 'gemini-1.5-pro'  # Latest multi-lingual model
        
    def process_complaint_conversation(self, user_message, language, context):
        """
        Main chatbot handler for complaint submission
        - Understands context in 100+ languages
        - Extracts structured data from natural conversation
        - Asks intelligent follow-up questions
        - Validates and confirms details
        """
        prompt = f"""
        You are a helpful government complaint assistant for India.
        Language: {language}
        User says: {user_message}
        Context: {context}
        
        Extract:
        - Complaint category (roads, water, electricity, etc.)
        - Location details
        - Problem description
        - Urgency level
        
        If information is missing, ask clarifying questions naturally.
        Respond in the same language as user input.
        """
        
        response = gemini.generate_content(prompt)
        return response.text
```

**2. Smart Information Extraction**
```python
def extract_complaint_details(conversation_history):
    """
    AI analyzes entire conversation and extracts structured data:
    {
        'category': 'water_supply',
        'location': 'Sector 15, Noida, UP',
        'description': 'No water supply for 3 days',
        'priority': 'high',
        'confidence': 0.95
    }
    """
```

**3. Multi-Lingual Voice Integration**
```python
def handle_voice_complaint(audio_file, detected_language):
    """
    1. Speech-to-Text (Google Cloud Speech or Whisper)
    2. Send transcription to Gemini API
    3. Get AI response
    4. Convert response to speech (TTS)
    5. Play to user
    """
```

### **Key Advantages of AI Chatbot Approach**

✅ **User Convenience:**
- No complex forms to fill
- Natural conversation like talking to a person
- No need to know categories or technical terms
- AI guides through the entire process

✅ **Multi-Lingual Native Support:**
- Gemini understands 100+ languages natively
- No separate translation needed
- Code-switching support (Hindi + English mixed)
- Regional dialect understanding

✅ **Intelligent Processing:**
- Automatic complaint categorization
- Smart priority detection from urgency words
- Location extraction from natural language
- Duplicate complaint detection

✅ **Accessibility:**
- Perfect for low-literacy users
- Voice-first interface
- Simple conversational flow
- No technical jargon

### **Implementation Status**

✅ **Completed:**
- Multi-lingual translation infrastructure (8 languages)
- Backend API for language preference
- Frontend i18n configuration
- LanguageSwitcher component

⚠️ **In Progress:**
- Gemini API integration for chatbot
- Voice input/output pipeline
- Conversational UI components

🔄 **Planned:**
- Advanced context management
- Multi-turn conversation handling
- Sentiment analysis for priority detection
- Integration with existing complaint workflow

---

## 🔧 Technical Implementation Plan

### **PHASE 1: Multi-Lingual Core (Week 1-2)**

#### Backend Changes

**1. Database Schema Updates**
```python
# User Model - Add language preference
class User(AbstractUser):
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('hi', 'Hindi'),
            ('bn', 'Bengali'),
            ('te', 'Telugu'),
            ('mr', 'Marathi'),
            ('ta', 'Tamil'),
            ('gu', 'Gujarati'),
            ('kn', 'Kannada'),
        ],
        default='en'
    )
    voice_language_preference = models.CharField(max_length=10, default='en')
    accessibility_mode = models.BooleanField(default=False)
```

**2. Complaint Model Updates**
```python
class Complaint(models.Model):
    # Add language tracking
    submitted_language = models.CharField(max_length=10, default='en')
    original_text = models.TextField(blank=True)  # Original language
    translated_text = models.TextField(blank=True)  # English for processing
    auto_translated = models.BooleanField(default=False)
```

**3. Translation Service Integration**
```python
# New: backend/services/translation_service.py
class TranslationService:
    - Google Cloud Translation API
    - Bhashini (NPLT - Govt of India translation)
    - IndicTrans2 (AI4Bharat)
    - Fallback to Google Translate
```

**4. Speech-to-Text Enhancement**
```python
# Update: backend/machine_learning/audio_analyzer.py
- Add support for Indian language models
- Integrate with Bhashini Speech Recognition
- Whisper multilingual support
- Language detection pre-processing
```

#### Frontend Changes

**1. i18n Library Integration**
```json
// package.json additions
{
  "dependencies": {
    "react-i18next": "^13.5.0",
    "i18next": "^23.7.0",
    "i18next-browser-languagedetector": "^7.2.0",
    "i18next-http-backend": "^2.4.2"
  }
}
```

**2. Translation Files Structure**
```
frontend/public/locales/
├── en/
│   ├── common.json
│   ├── complaints.json
│   ├── auth.json
│   └── dashboard.json
├── hi/
│   ├── common.json
│   ├── complaints.json
│   ├── auth.json
│   └── dashboard.json
├── bn/
├── te/
├── mr/
├── ta/
├── gu/
└── kn/
```

**3. Language Switcher Component**
```tsx
// New: frontend/src/components/LanguageSwitcher.tsx
- Dropdown with language selection
- Flag icons for each language
- Persistent storage of preference
- Real-time UI update
```

**4. RTL Support (for Urdu)**
```css
/* Support right-to-left languages */
[dir="rtl"] { ... }
```

---

### **PHASE 2: Voice & Accessibility (Week 3-4)**

#### Backend Enhancements

**1. Voice Processing Pipeline**
```python
# New: backend/services/voice_service.py
class VoiceService:
    def process_voice_complaint(audio_file, language_hint=None):
        # 1. Detect language
        # 2. Transcribe in native language
        # 3. Translate to English for AI processing
        # 4. Process through AI classifier
        # 5. Return results in original language
```

**2. API Endpoints for Voice**
```python
POST /api/voice/transcribe/
POST /api/voice/translate/
POST /api/voice/detect-language/
GET /api/voice/supported-languages/
```

#### Frontend Enhancements

**1. Voice Input Component**
```tsx
// New: frontend/src/components/VoiceInput.tsx
- Browser speech recognition API
- Language selection before recording
- Visual waveform feedback
- Playback functionality
```

**2. Text-to-Speech Integration**
```tsx
// New: frontend/src/services/ttsService.ts
- Read out notifications
- Complaint status updates
- Form field assistance
```

---

### **PHASE 3: Government Integration (Week 5-6)**

#### Aadhaar Integration

```python
# New: backend/authentication/aadhaar_auth.py
class AadhaarAuthService:
    def initiate_ekyc(aadhaar_number)
    def verify_otp(request_id, otp)
    def fetch_user_details(request_id)
```

#### DigiLocker Integration

```python
# New: backend/services/digilocker_service.py
class DigiLockerService:
    def authorize_user()
    def fetch_documents(doc_type)
    def attach_to_complaint(complaint_id, document_uri)
```

#### State Portal Integration

```python
# New: backend/integrations/government_portal.py
class StatePortalIntegration:
    def sync_complaint_to_portal(complaint)
    def fetch_status_updates()
    def map_department_codes()
```

---

### **PHASE 4: Mobile & Offline Support (Week 7-8)**

#### Progressive Web App (PWA)

**1. Service Worker**
```javascript
// New: frontend/public/service-worker.js
- Cache critical assets
- Offline complaint submission queue
- Background sync when online
```

**2. Manifest Configuration**
```json
// frontend/public/manifest.json
{
  "name": "SmartGriev - नागरिक शिकायत प्रणाली",
  "short_name": "SmartGriev",
  "description": "AI-Powered Civic Grievance Management",
  "lang": "hi",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#1890ff",
  "background_color": "#ffffff"
}
```

#### SMS Integration

```python
# New: backend/notifications/sms_service.py
class SMSService:
    def send_complaint_confirmation(mobile, complaint_id, language)
    def send_status_update(mobile, status, language)
    def send_otp(mobile, otp)
```

**SMS Templates (Hindi Example)**
```
शिकायत दर्ज हो गई है। 
संदर्भ संख्या: {complaint_id}
स्थिति देखने के लिए: smartgriev.gov.in
```

---

## 📋 Revised TODO - Complete Roadmap

### 🔴 PHASE 1: Multi-Lingual Foundation (2 weeks)

#### Week 1: Backend Multi-Lingual Setup

- [ ] **Day 1-2: Database Schema Updates**
  - [ ] Add `preferred_language` to User model
  - [ ] Add `submitted_language` to Complaint model
  - [ ] Create migration and test
  - [ ] Update user registration API
  - [ ] Update profile API

- [ ] **Day 3-4: Translation Service**
  - [ ] Integrate Bhashini API (Government of India)
  - [ ] Add Google Cloud Translation as fallback
  - [ ] Create translation middleware
  - [ ] Add caching for translations
  - [ ] Write unit tests for translation service

- [ ] **Day 5: API Internationalization**
  - [ ] Add language parameter to all API responses
  - [ ] Translate error messages
  - [ ] Translate notification templates
  - [ ] Update API documentation

#### Week 2: Frontend Multi-Lingual Setup

- [ ] **Day 1-2: i18n Integration**
  - [ ] Install react-i18next
  - [ ] Setup i18n configuration
  - [ ] Create language detector
  - [ ] Implement LanguageSwitcher component
  - [ ] Add to main layout

- [ ] **Day 3-5: Translation Files**
  - [ ] Create English translation files (baseline)
  - [ ] Translate to Hindi (priority)
  - [ ] Translate to Bengali
  - [ ] Translate to Telugu
  - [ ] Translate to Marathi
  - [ ] Translate to Tamil
  - [ ] Translate to Gujarati
  - [ ] Translate to Kannada

- [ ] **Day 6-7: UI Updates**
  - [ ] Update all components to use i18n
  - [ ] Update forms with translated labels
  - [ ] Update button text and messages
  - [ ] Update validation messages
  - [ ] Test language switching

### 🔴 PHASE 2: Voice & Audio Enhancement (2 weeks)

#### Week 3: Voice Input Processing

- [ ] **Day 1-2: Speech-to-Text Service**
  - [ ] Integrate Bhashini Speech API
  - [ ] Add Whisper API support
  - [ ] Implement language detection
  - [ ] Create audio processing pipeline
  - [ ] Write tests

- [ ] **Day 3-4: Backend Voice Endpoints**
  - [ ] Create `/api/voice/transcribe/` endpoint
  - [ ] Create `/api/voice/translate/` endpoint
  - [ ] Create `/api/voice/detect-language/` endpoint
  - [ ] Add audio file validation
  - [ ] Implement rate limiting

- [ ] **Day 5: Voice Complaint Workflow**
  - [ ] Update complaint creation to handle voice
  - [ ] Add language detection to audio uploads
  - [ ] Auto-translate voice complaints
  - [ ] Update AI processor for multilingual text

#### Week 4: Voice UI & Text-to-Speech

- [ ] **Day 1-3: Voice Input Component**
  - [ ] Create VoiceRecorder component
  - [ ] Add browser speech recognition
  - [ ] Implement language selection
  - [ ] Add visual waveform display
  - [ ] Add playback functionality

- [ ] **Day 4-5: Text-to-Speech**
  - [ ] Integrate TTS service
  - [ ] Add voice feedback for buttons
  - [ ] Add complaint status voice updates
  - [ ] Add voice tutorial mode

- [ ] **Day 6-7: Testing & Optimization**
  - [ ] Test all 8 languages with voice
  - [ ] Optimize audio file sizes
  - [ ] Test on mobile devices
  - [ ] Fix bugs and edge cases

### 🟡 PHASE 3: Government Integration (2 weeks)

#### Week 5: Aadhaar & DigiLocker

- [ ] **Day 1-3: Aadhaar Integration**
  - [ ] Register with UIDAI for API access
  - [ ] Implement Aadhaar eKYC flow
  - [ ] Add OTP verification
  - [ ] Update user model with Aadhaar number
  - [ ] Add privacy compliance features

- [ ] **Day 4-5: DigiLocker Integration**
  - [ ] Register with DigiLocker
  - [ ] Implement OAuth flow
  - [ ] Add document fetching
  - [ ] Link documents to complaints
  - [ ] Test document attachment

- [ ] **Day 6-7: UI for Government Services**
  - [ ] Add Aadhaar verification button
  - [ ] Add DigiLocker document picker
  - [ ] Update registration flow
  - [ ] Add verification badges

#### Week 6: State Portal Integration

- [ ] **Day 1-3: Portal API Integration**
  - [ ] Research state portal APIs (by state)
  - [ ] Create adapter pattern for multiple states
  - [ ] Implement complaint sync
  - [ ] Add status update polling
  - [ ] Error handling for portal downtime

- [ ] **Day 4-5: Department Mapping**
  - [ ] Create state-specific department lists
  - [ ] Map local departments to system
  - [ ] Add zone/ward configuration
  - [ ] Update complaint routing logic

- [ ] **Day 6-7: Testing & Documentation**
  - [ ] Test integration with sample state
  - [ ] Document integration process
  - [ ] Create admin guide for adding states
  - [ ] Update deployment guide

### 🟡 PHASE 4: Mobile & Offline (2 weeks)

#### Week 7: PWA & Offline Support

- [ ] **Day 1-2: Service Worker Setup**
  - [ ] Create service worker
  - [ ] Configure caching strategy
  - [ ] Implement offline queue
  - [ ] Add background sync

- [ ] **Day 3-4: PWA Manifest**
  - [ ] Create manifest.json
  - [ ] Add icons for all sizes
  - [ ] Configure install prompt
  - [ ] Test installation on mobile

- [ ] **Day 5-7: Offline Features**
  - [ ] Enable offline complaint creation
  - [ ] Add offline indicator
  - [ ] Sync when back online
  - [ ] Test offline scenarios

#### Week 8: SMS & Low-Bandwidth Mode

- [ ] **Day 1-3: SMS Integration**
  - [ ] Choose SMS gateway (MSG91/Twilio)
  - [ ] Create SMS service
  - [ ] Add templates for all languages
  - [ ] Implement OTP via SMS
  - [ ] Add status notifications via SMS

- [ ] **Day 4-5: Low-Bandwidth Mode**
  - [ ] Implement image compression
  - [ ] Add data saver mode
  - [ ] Optimize API responses
  - [ ] Add bandwidth detection

- [ ] **Day 6-7: USSD Menu (Optional)**
  - [ ] Design USSD flow
  - [ ] Implement basic complaint submission
  - [ ] Add status checking
  - [ ] Test with telecom providers

### 🟢 PHASE 5: Accessibility & Testing (1 week)

#### Week 9: Accessibility Features

- [ ] **Day 1-2: Screen Reader Support**
  - [ ] Add ARIA labels in all languages
  - [ ] Test with NVDA/JAWS
  - [ ] Add alt text for images
  - [ ] Ensure keyboard navigation

- [ ] **Day 3-4: Visual Accessibility**
  - [ ] Add high contrast theme
  - [ ] Implement font size controls
  - [ ] Test color blindness modes
  - [ ] Add focus indicators

- [ ] **Day 5: Icon-Based Navigation**
  - [ ] Create icon library for common actions
  - [ ] Add visual complaint categories
  - [ ] Reduce text density
  - [ ] Add tooltips

- [ ] **Day 6-7: Comprehensive Testing**
  - [ ] Test all languages end-to-end
  - [ ] Test voice features in 8 languages
  - [ ] Test on various devices
  - [ ] Accessibility audit
  - [ ] Performance testing

### 🟢 PHASE 6: Frontend Testing Suite (1 week)

#### Week 10: Automated Testing

- [ ] **Day 1-2: Setup Testing Framework**
  - [ ] Install Vitest & React Testing Library
  - [ ] Configure test environment
  - [ ] Setup i18n for tests
  - [ ] Create test utilities

- [ ] **Day 3-5: Write Unit Tests**
  - [ ] Authentication components (15 tests)
  - [ ] Complaint components (20 tests)
  - [ ] Dashboard components (10 tests)
  - [ ] Voice components (10 tests)
  - [ ] Language switcher (5 tests)
  - [ ] Services & API calls (15 tests)

- [ ] **Day 6-7: Integration Tests**
  - [ ] Complete user flows (5 tests)
  - [ ] Multi-language switching (3 tests)
  - [ ] Voice complaint submission (3 tests)
  - [ ] Offline/online sync (3 tests)

### 🟢 PHASE 7: Deployment & DevOps (1 week)

#### Week 11: Production Preparation

- [ ] **Day 1-2: Docker & CI/CD**
  - [ ] Create Dockerfile for backend
  - [ ] Create Dockerfile for frontend
  - [ ] Setup docker-compose
  - [ ] Configure GitHub Actions
  - [ ] Add automated testing in CI

- [ ] **Day 3-4: Cloud Deployment**
  - [ ] Choose cloud provider (AWS/Azure/GCP)
  - [ ] Setup PostgreSQL database
  - [ ] Configure Redis for caching
  - [ ] Setup CDN for static files
  - [ ] Configure domain & SSL

- [ ] **Day 5: Monitoring & Logging**
  - [ ] Setup Sentry for error tracking
  - [ ] Add application logging
  - [ ] Setup uptime monitoring
  - [ ] Configure alerts
  - [ ] Add analytics (Google Analytics/Matomo)

- [ ] **Day 6-7: Final Testing & Launch**
  - [ ] Load testing (500+ concurrent users)
  - [ ] Security audit
  - [ ] Backup & recovery testing
  - [ ] Create runbook for operations
  - [ ] Soft launch with beta users

---

## 🎯 Updated Success Metrics for India

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Language Coverage** | 8+ languages | Phase 1 complete |
| **Voice Recognition Accuracy** | 90%+ | Across all 8 languages |
| **Translation Quality** | 85%+ | BLEU score |
| **Mobile Usage** | 80%+ | Of total traffic |
| **Offline Functionality** | 100% | Complaint creation works offline |
| **Low-Literacy Usability** | 90%+ | Users can submit without assistance |
| **SMS Delivery** | 95%+ | Status updates within 5 mins |
| **Aadhaar Verification** | <30 sec | eKYC completion time |
| **Government Portal Sync** | 99%+ | Successful syncs |
| **Accessibility Score** | WCAG 2.1 AA | Automated audit |
| **Page Load (3G)** | <5 sec | Time to interactive |
| **API Response Time** | <300ms | 95th percentile |

---

## 📦 Additional Dependencies Required

### Backend Dependencies

```txt
# Translation & NLP
bhashini-api==1.0.0              # Government of India translation
google-cloud-translate==3.12.1   # Fallback translation
indicnlp-transliteration==0.3.0  # Indic language support
indic-nlp-library==0.92          # Language processing

# Speech Recognition
google-cloud-speech==2.21.0      # Speech-to-text
pydub==0.25.1                    # Audio processing

# Government Integration
aadhaar-py==1.1.0                # Aadhaar eKYC
digilocker-sdk==1.0.0            # DigiLocker integration

# SMS & Notifications
twilio==8.10.0                   # SMS service
msg91-python==1.0.0              # Indian SMS gateway

# Caching & Performance
django-redis==5.4.0              # Redis caching
django-silk==5.0.4               # Performance profiling
```

### Frontend Dependencies

```json
{
  "dependencies": {
    "react-i18next": "^13.5.0",
    "i18next": "^23.7.0",
    "i18next-browser-languagedetector": "^7.2.0",
    "i18next-http-backend": "^2.4.2",
    "react-speech-recognition": "^3.10.0",
    "wavesurfer.js": "^7.4.4",
    "workbox-webpack-plugin": "^7.0.0",
    "pwacompat": "^2.0.17"
  }
}
```

---

## 🚀 Quick Start Guide (Revised)

### For Developers

```bash
# Backend setup with new dependencies
cd backend
pip install -r requirements/india-specific.txt
python manage.py migrate
python manage.py load_indian_departments  # Load Indian dept data
python manage.py createsuperuser

# Frontend setup with i18n
cd frontend
npm install
npm run generate-translations  # Generate missing translations
npm run dev

# Run both with docker-compose
docker-compose -f docker-compose.india.yml up
```

### Environment Variables (Updated)

```env
# backend/.env
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant

# Translation Services
BHASHINI_API_KEY=your_bhashini_key
BHASHINI_USER_ID=your_user_id
GOOGLE_TRANSLATE_API_KEY=your_google_key

# Speech Services
GOOGLE_CLOUD_SPEECH_KEY=path/to/service-account.json

# Government Integration
AADHAAR_API_KEY=your_aadhaar_key
AADHAAR_ENVIRONMENT=sandbox  # or production
DIGILOCKER_CLIENT_ID=your_client_id
DIGILOCKER_CLIENT_SECRET=your_client_secret

# SMS Services
MSG91_AUTH_KEY=your_msg91_key
MSG91_SENDER_ID=SMARTG
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# Defaults
DEFAULT_LANGUAGE=hi  # Hindi as default for India
SUPPORTED_LANGUAGES=en,hi,bn,te,mr,ta,gu,kn
```

---

## 🎓 Training & Documentation Needs

### User Manuals Required (Each Language)

1. **Citizen Guide**
   - How to register
   - How to submit complaint (text/voice/image)
   - How to track status
   - How to use voice features
   - How to enable offline mode

2. **Officer Guide**
   - How to review complaints
   - How to assign tasks
   - How to update status
   - How to generate reports

3. **Admin Guide**
   - System configuration
   - Department management
   - User management
   - Analytics & reporting

### Video Tutorials (Each Language)

1. First-time setup (2 mins)
2. Submit complaint via voice (3 mins)
3. Track complaint status (2 mins)
4. Enable offline mode (1 min)

---

## 🔒 Compliance & Legal

### Data Protection

- [ ] **Digital Personal Data Protection Act, 2023** compliance
- [ ] User consent for data collection
- [ ] Right to data deletion
- [ ] Data localization (India servers)
- [ ] Encryption at rest and in transit

### Government Compliance

- [ ] **CERT-In guidelines** for cybersecurity
- [ ] **MEITY standards** for government apps
- [ ] **Accessibility guidelines** (GIGW)
- [ ] **STQC certification** (optional but recommended)

---

## 📞 Support & Community

### Multi-Channel Support

- [ ] **Helpline** (IVR in all languages)
- [ ] **WhatsApp chatbot** (multi-lingual)
- [ ] **Email support** (auto-translate)
- [ ] **Community forums** (language-specific)

---

## ✅ Definition of Done (Revised)

### For Production Deployment in India

**Functional Requirements:**
- ✅ All features work in 8+ Indian languages
- ✅ Voice complaint submission in all languages
- ✅ Aadhaar authentication working
- ✅ SMS notifications in regional languages
- ✅ Offline mode functional
- ✅ Works on 3G networks (<5 sec load time)
- ✅ Accessible to users with disabilities

**Testing Requirements:**
- ✅ 100% backend test coverage maintained
- ✅ 70%+ frontend test coverage
- ✅ End-to-end tests in all languages
- ✅ Load tested with 1000+ concurrent users
- ✅ Security audit passed

**Deployment Requirements:**
- ✅ Docker containers ready
- ✅ CI/CD pipeline configured
- ✅ Monitoring & logging setup
- ✅ Backup & recovery tested
- ✅ Documentation complete

**Compliance Requirements:**
- ✅ Data protection compliance
- ✅ Accessibility audit passed
- ✅ Government integration tested
- ✅ Privacy policy published
- ✅ Terms of service in all languages

---

## 📊 Updated Project Timeline

| Phase | Duration | Completion |
|-------|----------|-----------|
| **Current Status** | - | 85% |
| **Phase 1: Multi-Lingual** | 2 weeks | 0% |
| **Phase 2: Voice & Audio** | 2 weeks | 0% |
| **Phase 3: Government Integration** | 2 weeks | 0% |
| **Phase 4: Mobile & Offline** | 2 weeks | 0% |
| **Phase 5: Accessibility** | 1 week | 0% |
| **Phase 6: Frontend Testing** | 1 week | 0% |
| **Phase 7: Deployment** | 1 week | 0% |
| **TOTAL** | **11 weeks** | **~12% (India-ready)** |

---

## 🎯 Priority Matrix

### MUST HAVE (Block Production)
1. Hindi + English multi-lingual support
2. Voice input with language detection
3. SMS notifications
4. Mobile-responsive design
5. Basic offline support

### SHOULD HAVE (High Value)
1. 8 languages support
2. Aadhaar authentication
3. DigiLocker integration
4. PWA with offline mode
5. Screen reader support

### NICE TO HAVE (Enhancement)
1. USSD menu for feature phones
2. State portal integration
3. WhatsApp bot
4. Advanced analytics
5. Video tutorials

---

**Next Immediate Action:** Choose which phase to start first!

**Recommended:** Start with **Phase 1 (Multi-Lingual Foundation)** as it's the foundation for everything else.

Would you like me to begin implementing Phase 1? 🚀
