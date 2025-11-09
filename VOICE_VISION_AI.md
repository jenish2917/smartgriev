# Voice & Vision AI - Feature 10 Documentation

## Overview

Feature 10 adds **Voice & Vision AI capabilities** to SmartGriev using Google Gemini 1.5 Pro. This feature enables citizens to submit complaints using:
- 📸 **Image uploads** with AI-powered visual analysis
- 🎥 **Video uploads** with frame-by-frame analysis
- 🎙️ **Voice recordings** with speech-to-text in 12 Indian languages
- 🌐 **Multimodal input** combining text, image, audio, and video

## Features

### 1. Image Analysis
- Automatic issue detection from images
- Severity assessment
- Object detection
- Location context identification
- Department suggestion based on visual content

### 2. Video Analysis
- Video upload and processing
- Key frame extraction
- Timeline-based observations
- Comprehensive visual analysis
- Automated issue classification

### 3. Voice Transcription
- Speech-to-text in **12 Indian languages**
- Automatic language detection
- Emotion detection from voice tone
- Urgency level assessment
- Department classification from speech content

### 4. Multimodal Analysis
- Combine text + image + audio + video
- Cross-modal information fusion
- Enhanced complaint understanding
- Intelligent department routing

## Supported Languages (Audio)

1. English
2. Hindi (हिंदी)
3. Bengali (বাংলা)
4. Telugu (తెలుగు)
5. Marathi (मराठी)
6. Tamil (தமிழ்)
7. Gujarati (ગુજરાતી)
8. Kannada (ಕನ್ನಡ)
9. Malayalam (മലയാളം)
10. Punjabi (ਪੰਜਾਬੀ)
11. Urdu (اردو)
12. Assamese (অসমীয়া)
13. Odia (ଓଡ଼ିଆ)

## API Endpoints

### 1. Image Analysis
```http
POST /api/complaints/analyze/image/
Content-Type: multipart/form-data

Parameters:
- image (file): Image file (jpg, png, webp, heic, heif)
- context (text, optional): Additional context about the complaint
```

**Response:**
```json
{
  "success": true,
  "issue_type": "Pothole",
  "severity": "High",
  "description": "Large pothole on main road causing traffic hazard",
  "detected_objects": ["road", "pothole", "vehicle", "damage"],
  "location_context": "main road intersection",
  "suggested_department": "Roads",
  "urgency": "high",
  "raw_analysis": "...",
  "metadata": {
    "format": "JPEG",
    "width": 1920,
    "height": 1080,
    "file_size_mb": 2.5
  }
}
```

### 2. Multi-Image Analysis
```http
POST /api/complaints/analyze/multi-image/
Content-Type: multipart/form-data

Parameters:
- images (files): Multiple image files (max 5)
- context (text, optional): Additional context
```

### 3. Video Analysis
```http
POST /api/complaints/analyze/video/
Content-Type: multipart/form-data

Parameters:
- video (file): Video file (mp4, avi, mov, mkv, webm, max 100MB)
- context (text, optional): Additional context
```

**Response:**
```json
{
  "success": true,
  "issue_type": "Garbage Accumulation",
  "severity": "Medium",
  "description": "Large pile of uncollected garbage visible throughout video",
  "detected_objects": ["garbage", "waste", "street", "building"],
  "location_context": "residential street",
  "suggested_department": "Waste Management",
  "urgency": "medium",
  "key_observations": [
    "Garbage pile visible from 0:00-0:15",
    "Multiple waste bins overflowing",
    "Street appears neglected"
  ]
}
```

### 4. Audio Transcription
```http
POST /api/complaints/analyze/audio/transcribe/
Content-Type: multipart/form-data

Parameters:
- audio (file): Audio file (mp3, wav, m4a, flac, aac, ogg, opus, webm)
- language (text, optional): Language code (en, hi, ta, etc.)
- context (text, optional): Additional context
```

**Response:**
```json
{
  "success": true,
  "text": "हमारे इलाके में तीन दिन से पानी नहीं आ रहा है",
  "language": "hi",
  "language_name": "Hindi",
  "confidence": 0.95,
  "issue_summary": "No water supply in the area for 3 days",
  "detected_emotion": "frustrated",
  "urgency_level": "high"
}
```

### 5. Voice Complaint Analysis
```http
POST /api/complaints/analyze/audio/complete/
Content-Type: multipart/form-data

Parameters:
- audio (file): Audio file
- language (text, optional): Language code
```

**Response:**
```json
{
  "success": true,
  "transcription": "हमारे इलाके में तीन दिन से पानी नहीं आ रहा है",
  "language": "hi",
  "language_name": "Hindi",
  "issue_type": "Water Shortage",
  "description": "No water supply in residential area for 3 days",
  "sentiment": "negative",
  "emotion": "frustrated",
  "urgency": "high",
  "suggested_department": "Water Supply",
  "location_mentioned": "residential area",
  "key_points": [
    "No water for 3 days",
    "Residential area affected",
    "Urgent issue"
  ],
  "confidence": 0.95
}
```

### 6. Multimodal Analysis
```http
POST /api/complaints/analyze/multimodal/
Content-Type: multipart/form-data

Parameters:
- text (text, optional): Text description
- image (file, optional): Image file
- audio (file, optional): Audio file
- video (file, optional): Video file
- language (text, optional): Language code for audio

Note: At least one input modality required
```

**Response:**
```json
{
  "success": true,
  "modalities_processed": ["image", "audio"],
  "image_analysis": { ... },
  "audio_analysis": { ... },
  "combined_analysis": {
    "issue_type": "Broken Streetlight",
    "description": "Streetlight not functioning at night causing safety concerns",
    "severity": "Medium",
    "urgency": "medium",
    "suggested_department": "Streetlights",
    "transcription": "...",
    "visual_evidence": ["streetlight", "pole", "darkness"]
  }
}
```

## File Limits

### Images
- **Supported formats:** JPG, JPEG, PNG, WebP, HEIC, HEIF
- **Max file size:** 20 MB per image
- **Max images (multi-image):** 5 images

### Videos
- **Supported formats:** MP4, AVI, MOV, MKV, WebM
- **Max file size:** 100 MB
- **Max duration:** Recommended < 5 minutes

### Audio
- **Supported formats:** MP3, WAV, M4A, FLAC, AAC, OGG, Opus, WebM
- **Max file size:** 25 MB
- **Max duration:** 10 minutes (600 seconds)

## Technology Stack

### Backend Services
- **Gemini 1.5 Pro Vision:** Image and video analysis
- **Gemini 1.5 Pro:** Audio transcription and analysis
- **Python Pillow:** Image validation
- **Google Generative AI SDK:** API integration

### Key Components
1. **`vision_service.py`** - Image/video analysis with Gemini Vision
2. **`audio_service.py`** - Speech-to-text and voice analysis
3. **`voice_vision_views.py`** - REST API endpoints
4. **URL routing** - Integrated into complaints app

## Usage Examples

### Python Client Example
```python
import requests

# Image analysis
with open('pothole.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/complaints/analyze/image/',
        files={'image': f},
        data={'context': 'Main road pothole'},
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
    result = response.json()
    print(f"Issue: {result['issue_type']}")
    print(f"Department: {result['suggested_department']}")

# Voice complaint analysis
with open('complaint.mp3', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/complaints/analyze/audio/complete/',
        files={'audio': f},
        data={'language': 'hi'},
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
    result = response.json()
    print(f"Transcription: {result['transcription']}")
    print(f"Issue: {result['issue_type']}")

# Multimodal complaint
with open('image.jpg', 'rb') as img, open('audio.mp3', 'rb') as audio:
    response = requests.post(
        'http://localhost:8000/api/complaints/analyze/multimodal/',
        files={
            'image': img,
            'audio': audio
        },
        data={
            'text': 'Additional context',
            'language': 'en'
        },
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
    result = response.json()
    print(f"Combined analysis: {result['combined_analysis']}")
```

### cURL Examples
```bash
# Image analysis
curl -X POST http://localhost:8000/api/complaints/analyze/image/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@pothole.jpg" \
  -F "context=Pothole on main road"

# Audio transcription
curl -X POST http://localhost:8000/api/complaints/analyze/audio/transcribe/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "audio=@complaint.mp3" \
  -F "language=hi"

# Video analysis
curl -X POST http://localhost:8000/api/complaints/analyze/video/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "video=@complaint_video.mp4"
```

## Configuration

### Required Settings
```python
# backend/smartgriev/settings.py

# Google AI API Key (Gemini)
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', 'your-api-key-here')
GEMINI_API_KEY = GOOGLE_AI_API_KEY  # Alias for compatibility
```

### Environment Variables
```bash
# .env file
GOOGLE_AI_API_KEY=your-gemini-api-key-here
```

### Get API Key
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add to environment variables or settings.py

## Testing

Run the comprehensive test suite:
```bash
cd /path/to/SmartGriev
python test_voice_vision.py
```

**Expected output:**
```
============================================================
SMARTGRIEV - VOICE & VISION AI TESTS (FEATURE 10)
============================================================

✅ PASS: Configuration
✅ PASS: Vision Service
✅ PASS: Audio Service
✅ PASS: Image Validation
✅ PASS: Audio Validation
✅ PASS: API Endpoints
✅ PASS: Response Parsing
✅ PASS: Prompt Generation

Total: 8/8 tests passed

🎉 All Voice & Vision AI tests passed!
```

## Error Handling

### Common Errors

#### 1. Missing API Key
```json
{
  "error": "Vision service initialization failed",
  "message": "GOOGLE_AI_API_KEY not found in environment variables or Django settings"
}
```
**Solution:** Set `GOOGLE_AI_API_KEY` in settings.py or environment

#### 2. File Too Large
```json
{
  "success": false,
  "error": "Image too large: 25.5MB (max: 20MB)"
}
```
**Solution:** Compress image or video before upload

#### 3. Unsupported Format
```json
{
  "success": false,
  "error": "Unsupported image format: .gif"
}
```
**Solution:** Convert to supported format (JPG, PNG, WebP, etc.)

#### 4. Processing Failed
```json
{
  "success": false,
  "error": "Video processing failed"
}
```
**Solution:** Check file integrity, try smaller file, or different format

## Performance Considerations

### Response Times
- **Image analysis:** 2-5 seconds
- **Video analysis:** 10-30 seconds (depends on length)
- **Audio transcription:** 5-15 seconds (depends on length)
- **Multimodal analysis:** Sum of individual modalities

### Cost Optimization
- Gemini 1.5 Pro pricing: ~$0.35-0.70 per 1M tokens
- Images: ~258 tokens per image
- Audio: Varies by duration
- Video: Depends on length (uses frame sampling)

### Best Practices
1. **Image compression:** Resize images to < 5MB before upload
2. **Video optimization:** Trim videos to essential segments
3. **Audio quality:** Use clear recordings with minimal background noise
4. **Batch processing:** Process multiple images together for efficiency
5. **Caching:** Cache analysis results to avoid re-processing

## Frontend Integration

### Web Speech API (Browser)
```javascript
// Voice recording
const recognition = new webkitSpeechRecognition();
recognition.lang = 'hi-IN';  // Hindi
recognition.start();

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  console.log('Transcribed:', transcript);
};
```

### Image Capture
```javascript
// Capture from camera
<input type="file" accept="image/*" capture="environment">

// Multiple images
<input type="file" accept="image/*" multiple>
```

### Video Recording
```javascript
// Record video
<input type="file" accept="video/*" capture="environment">
```

## Security

### Authentication
- All endpoints require authentication (`IsAuthenticated` permission)
- Use JWT tokens in Authorization header

### File Validation
- File type checking
- Size limit enforcement
- Format validation
- Malicious file detection

### Rate Limiting
- Consider implementing rate limiting for API calls
- Prevent abuse of expensive AI operations

## Future Enhancements

### Planned Features
1. **Real-time analysis:** Stream processing for live video
2. **Offline support:** On-device AI models for basic analysis
3. **Language expansion:** Support for more regional languages
4. **Advanced vision:** Object detection with bounding boxes
5. **Sentiment analysis:** Enhanced emotion detection
6. **Location extraction:** Automatic location identification from images

## Troubleshooting

### Issue: Services not initializing
**Check:**
- API key is set correctly
- `google-generativeai` package installed
- Django settings loaded properly

### Issue: Poor transcription accuracy
**Try:**
- Use clear audio recordings
- Minimize background noise
- Specify correct language code
- Ensure audio quality is good

### Issue: Video analysis timeout
**Solutions:**
- Reduce video length
- Lower video resolution
- Use MP4 format (most efficient)
- Check network connection

## Support

For issues or questions:
1. Check test suite output: `python test_voice_vision.py`
2. Review error logs in Django admin
3. Verify API key and configuration
4. Check file format and size limits

## License

This feature uses Google Gemini AI API. Review Google's terms of service and pricing at:
- https://ai.google.dev/pricing
- https://ai.google.dev/terms

---

**Feature 10 Status:** ✅ Complete and tested (8/8 tests passed)
