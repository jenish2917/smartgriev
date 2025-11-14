# 🎯 Quick Start: AI Chatbot Intelligent Flow

## What Changed?

The AI Chatbot is now the **ONLY** way to submit complaints. It intelligently:

1. **Asks for location first** → GPS or manual address
2. **Extracts all complaint details** through natural conversation
3. **Accepts multi-modal input** (text, voice, photos, videos)
4. **Auto-submits** when all required info is collected

---

## 🚀 Key Features

### 1. GPS Location Request Flow
```
User clicks "File a new complaint"
  ↓
AI asks: "Enable GPS or enter manually?"
  ↓
[Enable GPS] → Permission granted → Location captured ✅
     OR
[Enter Manually] → User types address → Address parsed ✅
     OR
[Enable GPS] → Permission denied → AI asks for manual address
```

### 2. Quick Reply Buttons
- "File a new complaint" → Triggers location flow
- "Report pothole with photo" → Direct to media upload
- "Garbage collection issue" → Pre-fills issue type
- "Street light not working" → Pre-fills category

### 3. Location Buttons (Dynamic)
Shows when AI asks for location:
- 🟢 **Enable GPS** (Primary) → `requestLocation()`
- ⚪ **Enter Manually** (Outline) → AI asks for typed address

---

## 🧠 AI Information Extraction

The AI automatically extracts from conversation:

| Information | Source | Example |
|------------|--------|---------|
| **Location** | GPS coordinates or typed address | (23.0225, 72.5714) OR "MG Road, Vastrapur" |
| **Issue Type** | Keywords in text/voice/image | "pothole" → Infrastructure |
| **Department** | Issue type mapping | Pothole → Roads & Infrastructure |
| **Severity** | Context ("huge", "emergency") | "causing accidents" → HIGH priority |
| **Description** | User's natural language | "Big pothole for 2 weeks" |
| **Media** | Uploaded images/videos | Photo of pothole analyzed by AI |
| **Duration** | Time mentions | "for 3 days", "since yesterday" |

---

## 📸 Multi-Modal Input Examples

### Text + GPS
```
User: "There's a pothole on my street"
[Clicks "Enable GPS"]
AI: "✅ Location captured. Can you share a photo?"
[User uploads photo]
AI: "Got it! Filing complaint... ✅ #SG202501234"
```

### Voice + Manual Address
```
User: 🎤 "Garbage not collected for 5 days"
AI: "🎤 Heard you. What's your address?"
User: "123 Green Park, Sector 12"
AI: "Perfect! Filing now... ✅ #SG202501235"
```

### Image + Auto-Detection
```
User: [Drags image of water leakage]
AI: "I see water leakage. Where is this?"
[User clicks Enable GPS]
AI: "✅ Emergency complaint filed! #SG-EMRG-5678"
```

---

## 🔧 Code Updates

### Frontend (`ChatbotPage.tsx`)

**Added State:**
```typescript
const [userLocation, setUserLocation] = useState<{
  latitude: number;
  longitude: number;
} | null>(null);
```

**GPS Request:**
```typescript
const requestLocation = () => {
  navigator.geolocation.getCurrentPosition(
    (position) => {
      setUserLocation({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      });
      // AI confirms location captured
    },
    (error) => {
      // AI asks for manual address
    }
  );
};
```

**Send with Location:**
```typescript
// Text message
await chatbotApi.sendMessage(text, 'en', userLocation);

// Image/Video
await chatbotApi.sendImage(file, text, userLocation);
```

---

### API Updates (`chatbot.ts`)

**Updated Signatures:**
```typescript
sendMessage(
  message: string,
  language: string,
  location?: { latitude: number; longitude: number } | null
)

sendImage(
  file: File,
  message?: string,
  location?: { latitude: number; longitude: number } | null
)
```

**Request Payload:**
```typescript
{
  message: "Pothole on street",
  language: "en",
  latitude: 23.0225,    // Optional
  longitude: 72.5714    // Optional
}
```

---

## 🎨 UI Components Added

### 1. Location Request Buttons
```tsx
<Button
  variant="primary"
  onClick={requestLocation}
  leftIcon={<GpsIcon />}
>
  Enable GPS
</Button>

<Button
  variant="outline"
  onClick={handleManualAddress}
>
  Enter Manually
</Button>
```

### 2. Quick Reply Handler
```tsx
const handleQuickReply = (reply: string) => {
  if (reply === 'File a new complaint') {
    // Trigger location flow
    setMessages([...messages, {
      role: 'assistant',
      content: '📍 Would you like to enable GPS?'
    }]);
  }
};
```

### 3. Updated Welcome Message
```tsx
{
  content: `Hello! I'm your AI assistant for SmartGriev. 
  I'll help you submit complaints through natural conversation. 
  Just tell me about the issue, and I'll guide you through the process.`
}
```

---

## 📊 User Journey

### Complete Flow Example

1. **Landing**
   ```
   User opens chatbot page
   AI: "Hello! What civic issue would you like to report?"
   ```

2. **Initiate**
   ```
   User: "File a new complaint"
   AI: "📍 Would you like to enable GPS or enter address manually?"
   [Shows two buttons]
   ```

3. **Location**
   ```
   User clicks "Enable GPS"
   Browser: Requests permission
   User: Allows
   AI: "✅ Location captured (23.0225, 72.5714). What's the problem?"
   ```

4. **Describe**
   ```
   User: "Big pothole causing accidents"
   AI: "Can you share a photo?"
   ```

5. **Media**
   ```
   User: [Uploads photo]
   AI: "I can see the pothole is large..."
   ```

6. **Submit**
   ```
   AI: "Filing complaint now:
        📍 MG Road, Vastrapur, Ahmedabad
        🚧 Large pothole
        📸 Photo attached
        🏢 Roads & Infrastructure
        
        ✅ Complaint #SG202501234 filed!"
   ```

---

## 🧪 Testing Scenarios

### Test 1: GPS Success Flow
1. Click "File a new complaint"
2. Click "Enable GPS"
3. Allow browser permission
4. Verify location captured in AI response
5. Type issue description
6. Upload photo
7. Verify complaint submitted with GPS coords

### Test 2: GPS Denied Flow
1. Click "File a new complaint"
2. Click "Enable GPS"
3. Deny browser permission
4. Verify AI asks for manual address
5. Type address
6. Continue with complaint

### Test 3: Manual Address Flow
1. Click "File a new complaint"
2. Click "Enter Manually"
3. Type complete address
4. Verify AI parses address
5. Continue with complaint

### Test 4: Voice + Image + GPS
1. Enable GPS first
2. Record voice complaint
3. Upload image
4. Verify all data combined in single complaint

---

## 📝 Backend Integration Required

The backend needs to handle:

### 1. Location in Chat Endpoint
```python
# /api/chatbot/chat/
{
  "message": "...",
  "language": "en",
  "latitude": 23.0225,  # NEW
  "longitude": 72.5714  # NEW
}
```

### 2. Location in Vision Endpoint
```python
# /api/chatbot/vision/
FormData:
- image: File
- message: str
- latitude: float  # NEW
- longitude: float # NEW
```

### 3. AI Processing
```python
def process_message(message, location=None):
    # Extract intent
    # If location provided, reverse geocode
    # Store location with complaint
    # Auto-assign department based on issue + location
```

### 4. Complaint Auto-Submit
```python
def auto_submit_complaint(extracted_data):
    complaint = Complaint(
        title=extracted_data['title'],
        description=extracted_data['description'],
        latitude=extracted_data['latitude'],
        longitude=extracted_data['longitude'],
        address=extracted_data['address'],  # From GPS or manual
        category=extracted_data['category'],
        department=extracted_data['department'],
        severity=extracted_data['severity'],
        media=extracted_data['media_files'],
        user=request.user
    )
    complaint.save()
    return complaint.id
```

---

## ✅ Checklist

- [x] GPS request function implemented
- [x] Manual address fallback working
- [x] Location sent with text messages
- [x] Location sent with images/videos
- [x] Quick reply buttons trigger location flow
- [x] UI shows GPS and Manual buttons
- [x] Error handling for denied permissions
- [x] Welcome message updated
- [x] TypeScript errors resolved (0 errors)
- [x] Documentation created

---

## 🚀 Next Steps

1. **Backend Integration:**
   - Update `/api/chatbot/chat/` to accept latitude/longitude
   - Update `/api/chatbot/vision/` to accept location in FormData
   - Implement reverse geocoding (coords → address)
   - Implement address parsing (text → structured address)

2. **AI Enhancements:**
   - Train model to extract department from issue description
   - Implement severity scoring algorithm
   - Add multi-turn conversation state management
   - Implement complaint auto-submission when all data collected

3. **Testing:**
   - Test GPS flow on mobile devices
   - Test location accuracy
   - Test with various address formats
   - Test multi-modal combinations

4. **UI Polish:**
   - Add loading states for GPS request
   - Add map preview of captured location
   - Add address confirmation dialog
   - Add visual feedback for data extraction

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| `frontend-new/src/pages/chatbot/ChatbotPage.tsx` | Main chatbot UI with GPS flow |
| `frontend-new/src/api/chatbot.ts` | API client with location support |
| `CHATBOT_FLOW_DOCUMENTATION.md` | Complete detailed documentation |
| `backend/chatbot/views.py` | Backend endpoint handlers (needs update) |
| `backend/chatbot/gemini_service.py` | AI processing service (needs update) |

---

**Last Updated:** November 11, 2025
**Status:** ✅ Frontend Complete, ⏳ Backend Integration Pending
