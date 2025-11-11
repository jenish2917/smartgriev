# 🤖 AI Chatbot - Intelligent Complaint Submission Flow

## Overview

The SmartGriev AI Chatbot is the **primary and only** way to submit complaints. It uses natural language processing to guide users through a conversational complaint filing process, automatically extracting all necessary information without requiring complex forms.

## 🎯 Core Philosophy

**"Chat, Don't Fill Forms"**

Instead of a 22-field intimidating form, users simply have a conversation with the AI assistant. The AI intelligently:
- Asks contextual questions
- Extracts key information from natural language
- Requests GPS location or manual address
- Accepts multi-modal input (text, voice, images, videos)
- Auto-submits the complaint when all required info is collected

---

## 📍 Location Request Flow

### Step 1: User Initiates Complaint
**User Action:** Clicks "File a new complaint" or types complaint details

**AI Response:**
```
📍 To file your complaint, I need to know the location. 
Would you like to enable GPS for automatic location, 
or would you prefer to enter your address manually?
```

**UI Shows:** Two buttons:
- 🟢 **Enable GPS** (Primary button)
- ⚪ **Enter Manually** (Outline button)

---

### Step 2A: GPS Enabled (Success)
**User Action:** Clicks "Enable GPS" → Browser requests permission → User accepts

**System Action:**
```typescript
navigator.geolocation.getCurrentPosition(
  (position) => {
    const { latitude, longitude } = position.coords;
    // Store location: e.g., (23.0225, 72.5714)
  }
);
```

**AI Response:**
```
✅ Great! I've captured your location (23.0225, 72.5714). 
Now, please describe the issue you're facing. What's the problem?
```

**Next:** User describes the issue → AI extracts details → Auto-submits complaint

---

### Step 2B: GPS Denied or Unavailable
**User Action:** Clicks "Enable GPS" → Browser requests permission → User denies

**System Error Handling:**
```typescript
if (error.code === error.PERMISSION_DENIED) {
  // User explicitly denied permission
} else if (error.code === error.POSITION_UNAVAILABLE) {
  // GPS hardware issue or not available
} else if (error.code === error.TIMEOUT) {
  // Request took too long
}
```

**AI Response:**
```
I couldn't access your location. It looks like GPS permission was denied. 
No worries! Please type your address manually 
(street, area, city), and we'll continue.
```

**Next:** User types address → AI parses address → Continues with complaint details

---

### Step 2C: Manual Address Entry
**User Action:** Clicks "Enter Manually" button

**AI Response:**
```
No problem! Please type your complete address 
(Street, Area, Landmark, City, Pincode) 
so I can help you file the complaint.
```

**User Types:**
```
Example: "123 MG Road, Vastrapur, near ISRO Circle, Ahmedabad, Gujarat 380015"
```

**AI Processing:**
- Extracts street: "123 MG Road"
- Extracts area: "Vastrapur"
- Extracts landmark: "near ISRO Circle"
- Extracts city: "Ahmedabad"
- Extracts pincode: "380015"

**AI Response:**
```
Perfect! I've noted the address: 123 MG Road, Vastrapur, Ahmedabad 380015.
Now, what's the issue you're facing?
```

---

## 🧠 Intelligent Information Extraction

Once location is captured, the AI extracts all complaint details through natural conversation:

### Example Conversation Flow

**User:** "There's a huge pothole on my street that's causing accidents"

**AI Extracts:**
- **Issue Type:** Infrastructure → Road damage
- **Problem:** Pothole
- **Severity:** High (keyword: "huge", "causing accidents")
- **Department:** Roads & Infrastructure
- **Category:** Road Maintenance

**AI Response:**
```
I understand. A large pothole causing accidents. 
That sounds serious! 🚧

Can you share a photo of the pothole? 
This will help authorities assess the damage quickly.
```

**User:** *Uploads photo*

**AI Analyzes Image:**
- Confirms pothole visible
- Estimates size from image
- Detects road type (asphalt/concrete)
- Identifies surrounding context (traffic, residential area)

**AI Response:**
```
Got it! I can see the pothole is quite large and on a busy road. 

For my records:
📍 Location: 123 MG Road, Vastrapur, Ahmedabad
🚧 Issue: Large pothole causing safety hazard
📸 Photo: Attached
🏢 Department: Roads & Infrastructure
⚠️ Priority: High

I'm submitting this complaint now. 
You'll receive a tracking number shortly!

✅ Complaint #SG202501234 has been filed successfully.
You can track its status anytime by asking me "Check complaint status".
```

**System Action:**
- Auto-creates complaint with extracted data
- Uploads photo as evidence
- Sets priority to "High" based on severity
- Assigns to Roads & Infrastructure department
- Generates tracking number
- Sends confirmation to user's email/SMS

---

## 🎤 Multi-Modal Input Support

### 1. Voice Recording
**User Action:** Clicks mic button → Records complaint verbally

**Example Voice Input:**
```
"Hi, I want to report a streetlight issue. 
The light outside my house on Station Road has been broken for 3 days. 
It's dark at night and not safe. Can you please fix it?"
```

**AI Processing:**
- Transcribes audio to text
- Extracts:
  - Issue: Streetlight not working
  - Location: Station Road (asks for complete address if missing)
  - Duration: 3 days
  - Impact: Safety concern (darkness)
  - Department: Electricity / Street Lighting

**AI Response:**
```
🎤 I heard you! Streetlight not working on Station Road for 3 days.

I need your complete address (house number, area, pincode) 
to file this complaint. Could you provide that?
```

---

### 2. Image Upload
**User Action:** 
- Drags and drops image into chat
- OR clicks image button and selects file
- OR captures photo on mobile

**AI Vision Analysis:**
- Detects issue type (garbage pile, pothole, broken infrastructure)
- Identifies severity from visual context
- Reads text in image (signboards, labels)
- Recognizes landmarks for location context

**Example:**
```
User uploads image of garbage pile

AI Response:
"I can see a large garbage accumulation in your photo. 
It appears to be on a residential street near a park entrance.

To file this complaint:
1. Is this the correct location? (shows map based on GPS if available)
2. How long has this garbage been here?
3. Is there a regular pickup schedule that's been missed?"
```

---

### 3. Video Upload
**User Action:** Uploads video (e.g., water leakage, traffic issue)

**AI Video Analysis:**
- Extracts key frames
- Analyzes motion (flowing water, moving vehicles)
- Detects time of day from lighting
- Identifies duration of issue from video length

**Example:**
```
User uploads video of water main burst

AI Response:
"I can see water flowing rapidly in your video - 
this looks like a water main burst! 🚨

This is an emergency. I'm filing this as URGENT priority.

📍 Location: [GPS or asks for address]
💧 Issue: Water main burst
⏰ Video timestamp: Today at 2:30 PM
🚨 Priority: CRITICAL

I'm notifying the Water Supply department immediately.
Emergency ticket #SG-EMRG-5678 created.
Estimated response time: Within 2 hours.
```

---

## 🔄 Complete Conversation Examples

### Example 1: Pothole with Photo

```
User: "Hey, there's a big pothole on my street"

AI: "I can help you report that! First, I need the location. 
Would you like to enable GPS or enter the address manually?"

[User clicks "Enable GPS"]

AI: "✅ Location captured (23.0225, 72.5714). 
Can you share a photo of the pothole?"

[User uploads photo]

AI: "I can see it's a large pothole on an asphalt road. 
How long has this been here?"

User: "About 2 weeks"

AI: "Got it. Let me file this complaint for you:
📍 Location: MG Road, Vastrapur, Ahmedabad (from GPS)
🚧 Issue: Large pothole
📅 Duration: 2 weeks
📸 Photo: Attached
🏢 Department: Roads & Infrastructure

✅ Complaint #SG202501234 filed successfully!
You'll receive updates via SMS and email."
```

---

### Example 2: Voice Complaint (No GPS)

```
[User clicks mic and speaks]

User: 🎤 "The garbage truck hasn't come to our area for 5 days. 
There's waste piling up on the corner of Green Park Colony"

AI: "🎤 Transcription: 'The garbage truck hasn't come to our area for 5 days...'

I understand - garbage collection hasn't happened in 5 days at Green Park Colony.

I need your complete address. Could you type:
Street number, area name, and pincode?"

User: "House 45, Sector 12, Green Park Colony, 380058"

AI: "Perfect! Filing complaint now:
📍 45, Sector 12, Green Park Colony - 380058
🗑️ Issue: Garbage collection missed for 5 days
🏢 Department: Solid Waste Management
⏰ Reported: Today, 3:45 PM

✅ Complaint #SG202501235 created.
Collection teams have been notified.
Expected resolution: Within 24 hours."
```

---

### Example 3: Multi-Step Video Complaint

```
User: "I want to report something"

AI: "I'm here to help! What would you like to report?"

User: [Uploads video of waterlogged street]

AI: "I can see heavy waterlogging in your video. This looks like a drainage issue.
Where is this happening? Would you like to enable GPS?"

[User clicks "Enter Manually"]

AI: "Please provide the street address and area name."

User: "Station Road, near Railway Station, Sabarmati"

AI: "Thanks! How long has this waterlogging been present?"

User: "Since yesterday's rain"

AI: "Understood. Is traffic affected by this?"

User: "Yes, vehicles can't pass through"

AI: "This is serious. Filing as HIGH priority:
📍 Station Road, Sabarmati (near Railway Station)
💧 Issue: Severe waterlogging blocking traffic
📹 Video evidence: Attached
⏰ Since: Yesterday (24 hours)
🏢 Department: Drainage & Storm Water
🚨 Priority: HIGH

✅ Complaint #SG202501236 filed.
Drainage teams dispatched.
ETA: 4-6 hours for water pumping.

You'll receive updates via SMS."
```

---

## 🧩 Information Categories Auto-Extracted

The AI automatically identifies and extracts:

### 1. **Location** (REQUIRED)
- GPS coordinates (if enabled)
- OR Manual address (street, area, city, pincode)
- Landmarks from conversation or image

### 2. **Issue Type** (REQUIRED)
- Infrastructure: Potholes, roads, bridges
- Sanitation: Garbage, sewage, cleanliness
- Utilities: Water supply, electricity, street lights
- Safety: Crime, accidents, hazards
- Environment: Pollution, noise, tree cutting
- Traffic: Congestion, signals, parking
- Others: Custom categories

### 3. **Description** (REQUIRED)
- User's natural language description
- Extracted from text, voice transcription, or image analysis

### 4. **Severity/Priority**
- Keywords: "urgent", "emergency", "dangerous", "critical"
- Visual cues: Size of issue in images/videos
- Duration: "for weeks", "just happened"
- Impact: "traffic blocked", "health hazard"

**Auto-assigned Priority:**
- 🔴 **CRITICAL:** Life-threatening, major infrastructure failure
- 🟠 **HIGH:** Safety hazard, service disruption, health risk
- 🟡 **MEDIUM:** Quality of life issues, minor damage
- 🟢 **LOW:** Cosmetic issues, suggestions

### 5. **Department** (Auto-assigned by AI)
Based on issue type:
- Roads & Infrastructure
- Solid Waste Management
- Water Supply & Drainage
- Electricity Department
- Traffic Police
- Health & Sanitation
- Parks & Gardens
- Building Permissions
- Others

### 6. **Category** (Auto-tagged)
- Road Maintenance, Street Lighting, Garbage Collection, Water Leakage, etc.

### 7. **Media Attachments**
- Photos: Analyzed for visual context
- Videos: Analyzed for severity and motion
- Audio: Transcribed for text extraction

### 8. **Timestamp**
- Auto-captured submission time
- User-mentioned duration ("for 3 days") extracted

### 9. **Contact Info**
- Auto-filled from logged-in user profile
- Name, email, mobile number

---

## 🔧 Technical Implementation

### Frontend (ChatbotPage.tsx)

**State Management:**
```typescript
const [userLocation, setUserLocation] = useState<{
  latitude: number;
  longitude: number;
} | null>(null);

const [isRequestingLocation, setIsRequestingLocation] = useState(false);
```

**GPS Request Function:**
```typescript
const requestLocation = () => {
  setIsRequestingLocation(true);
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords;
      setUserLocation({ latitude, longitude });
      // AI acknowledges location
    },
    (error) => {
      // Handle denied/unavailable GPS
      // AI asks for manual address
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
};
```

**Send Message with Location:**
```typescript
const response = await chatbotApi.sendMessage(
  messageText, 
  'en', 
  userLocation // { latitude, longitude } or null
);
```

**Send Media with Location:**
```typescript
const response = await chatbotApi.sendImage(
  imageFile, 
  messageText, 
  userLocation // { latitude, longitude } or null
);
```

---

### Backend API (Expected Endpoints)

#### 1. Text Message API
```python
POST /api/chatbot/chat/
Content-Type: application/json

Request:
{
  "message": "There's a pothole on my street",
  "language": "en",
  "latitude": 23.0225,  # Optional
  "longitude": 72.5714  # Optional
}

Response:
{
  "response": "I can help you with that! Can you share a photo?",
  "extracted_info": {
    "issue_type": "infrastructure",
    "category": "road_damage",
    "department": "roads_infrastructure",
    "severity": "medium"
  },
  "complaint_id": null  # Not yet created
}
```

#### 2. Image/Video API
```python
POST /api/chatbot/vision/
Content-Type: multipart/form-data

Request (FormData):
- image: [File]
- message: "Pothole on MG Road"
- latitude: 23.0225  # Optional
- longitude: 72.5714  # Optional

Response:
{
  "response": "I can see a large pothole. Filing complaint now...",
  "description": "Large pothole on asphalt road, approximately 2ft diameter",
  "complaint_id": "SG202501234",
  "tracking_number": "SG202501234",
  "extracted_info": {
    "issue_type": "infrastructure",
    "severity": "high",
    "visual_analysis": {
      "object_detected": "pothole",
      "size_estimate": "large",
      "road_type": "asphalt"
    }
  }
}
```

#### 3. Voice API
```python
POST /api/chatbot/voice/
Content-Type: multipart/form-data

Request:
- audio: [WebM audio file]
- language: "en"

Response:
{
  "transcription": "There's a streetlight issue on Station Road",
  "response": "I heard you. Let me help file this complaint...",
  "extracted_info": {
    "issue_type": "utilities",
    "category": "street_lighting"
  }
}
```

---

## 📊 User Experience Benefits

### Traditional Form (OLD):
- ❌ 22 fields to fill
- ❌ Confusing dropdowns (department, category)
- ❌ Manual coordinate entry
- ❌ Separate image upload page
- ❌ Technical jargon
- ❌ High abandonment rate
- ⏱️ **Time:** 5-10 minutes

### AI Chatbot (NEW):
- ✅ Natural conversation
- ✅ AI auto-extracts info
- ✅ One-click GPS or simple address
- ✅ Drag-and-drop media in chat
- ✅ Plain language
- ✅ High completion rate
- ⏱️ **Time:** 30-60 seconds

---

## 🎨 UI/UX Features

### Location Request UI
```tsx
{/* GPS Request Buttons */}
<div className="flex gap-2">
  <Button
    variant="primary"
    size="sm"
    onClick={requestLocation}
    leftIcon={<GpsIcon />}
  >
    Enable GPS
  </Button>
  <Button
    variant="outline"
    size="sm"
    onClick={handleManualAddress}
  >
    Enter Manually
  </Button>
</div>
```

### Quick Reply Suggestions
```tsx
<button 
  onClick={() => handleQuickReply('File a new complaint')}
  className="quick-reply-button"
>
  File a new complaint
</button>
```

### Drag-and-Drop Overlay
```tsx
{isDragging && (
  <div className="drag-overlay">
    📸 Drop your image or video here
  </div>
)}
```

### Recording Indicator
```tsx
{isRecording && (
  <div className="recording-banner">
    🔴 Recording... Click mic to stop
  </div>
)}
```

---

## 🔐 Privacy & Security

1. **GPS Permission:** Browser-level, user must explicitly allow
2. **Location Storage:** Encrypted and associated with complaint only
3. **Media Uploads:** Scanned for inappropriate content before processing
4. **Audio Transcription:** Processed and deleted, only text stored
5. **User Data:** GDPR/DPDP compliant, can be deleted on request

---

## 🚀 Future Enhancements

1. **Real-time location tracking:** For mobile garbage trucks, ambulances
2. **Voice-only mode:** Fully hands-free complaint filing
3. **Regional language support:** Voice and text in 12 Indian languages
4. **Predictive suggestions:** "Based on your location, report streetlight?"
5. **Complaint clustering:** "3 others reported similar issue nearby"
6. **AR mode:** Point camera → AI identifies issue → Auto-files complaint
7. **Offline mode:** Queue complaints when offline, submit when online

---

## 📝 Summary

The SmartGriev AI Chatbot revolutionizes civic complaint submission by:
- **Eliminating complex forms** → Natural conversation
- **Intelligent location capture** → GPS or manual address
- **Multi-modal input** → Text, voice, images, videos
- **Auto-extraction** → No dropdowns, AI assigns department/category
- **Instant submission** → Single conversation, done!

**Result:** Citizens can report issues in 30 seconds instead of 10 minutes, leading to higher engagement and faster resolution of civic problems. 🎉
