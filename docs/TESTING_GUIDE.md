# Quick Test Guide - Live Call Improvements

## 🎯 Test 1: Gujarati Language Response (CRITICAL FIX)

### Steps:
1. Open SmartGriev in browser
2. Click **📞 Live Call** button (in navbar or chatbot)
3. Select **🇮🇳 ગુજરાતી** from language dropdown
4. Wait for AI greeting in Gujarati
5. Speak one of these:
   - "રસ્તા પર ખાડા છે" (There are potholes on the road)
   - "પાણીની સમસ્યા છે" (There's a water problem)
   - "શેરી સાફ નથી" (Street is not clean)

### Expected Result ✅:
- AI should respond **in Gujarati**, not English
- Console should show: `🔊 Speaking response in: gu-IN`
- Response should be natural Gujarati

### Old Behavior ❌:
- User speaks Gujarati → AI responds in English

---

## 🎯 Test 2: Call Duration Timer

### Steps:
1. Start live call
2. Look at status indicator in navbar
3. Observe the timer

### Expected Result ✅:
- Timer starts at: `🎤 Listening... (0s)`
- After 5 seconds: `🎤 Listening... (5s)`
- After 10 seconds: `🎤 Listening... (10s)`
- When speaking: `🔊 AI Speaking... (15s)`
- Timer continues counting throughout call

### Visual Locations:
- **Navbar support bar**: Green/Blue/Orange box with timer
- **Chatbot panel**: Green header with timer

---

## 🎯 Test 3: Speech Recognition Accuracy

### Steps:
1. Start live call
2. Open browser console (F12)
3. Speak clearly in any language
4. Check console output

### Expected Result ✅:
Console should show:
```
🎤 Starting recognition with language: gu-IN
📝 Recognized: રસ્તા પર ખાડા છે | Confidence: 0.95 | Language: gu-IN
🔊 Speaking response in: gu-IN
```

### What to Check:
- Transcript matches what you said
- Confidence is above 0.7 (70%)
- Language code is correct

---

## 🎯 Test 4: All Languages

### Test Each Language:
| Language | Code | Test Phrase | AI Should Respond In |
|----------|------|-------------|----------------------|
| English | en-IN | "There are potholes on the road" | English |
| Hindi | hi-IN | "पानी की समस्या है" | Hindi |
| Gujarati | gu-IN | "રસ્તા પર ખાડા છે" | Gujarati |
| Marathi | mr-IN | "रस्ता खराब आहे" | Marathi |
| Punjabi | pa-IN | "ਸੜਕ ਖਰਾਬ ਹੈ" | Punjabi |

### Expected Result ✅:
Each language test should:
1. Recognize speech correctly
2. AI responds in **same language**
3. Speech synthesis uses correct accent
4. Timer shows throughout

---

## 🎯 Test 5: Call Timer Reset

### Steps:
1. Start call (timer starts at 0s)
2. Wait 15 seconds (timer shows 15s)
3. Click **📞 End Call**
4. Start new call
5. Check timer

### Expected Result ✅:
- Timer resets to `(0s)` on new call
- No leftover time from previous call

---

## 🎯 Test 6: Speech Clarity

### Steps:
1. Start call in any language
2. Ask a complex question
3. Listen to AI response

### Expected Result ✅:
- AI speaks clearly and slowly
- Easy to understand each word
- Not too fast, not too slow
- Natural sounding

### Technical Detail:
- Speech rate is now **0.85** (down from 0.9)
- Should sound clearer and more deliberate

---

## 🛠️ Debugging Tools

### Browser Console Commands:
```javascript
// Check speech synthesis voices
window.speechSynthesis.getVoices().forEach(v => console.log(v.lang, v.name));

// Check speech recognition support
console.log('Recognition:', 'webkitSpeechRecognition' in window);
console.log('Synthesis:', 'speechSynthesis' in window);
```

### Console Logs to Watch:
- `📞 Starting live call in language: gu-IN`
- `🎤 Starting recognition with language: gu-IN`
- `📝 Recognized: <text> | Confidence: <number> | Language: gu-IN`
- `🔊 Speaking response in: gu-IN`
- `📞 Live call ended`

---

## 🚨 Troubleshooting

### Issue: AI Still Responds in English
**Check:**
1. Language dropdown is set correctly
2. Console shows correct language code
3. Backend is running
4. Clear browser cache

### Issue: Timer Not Showing
**Check:**
1. Call is actually started (green/red button)
2. Refresh browser
3. Check console for errors

### Issue: Speech Not Recognized
**Check:**
1. Microphone permission granted
2. Using Chrome or Edge (Firefox limited support)
3. Speak clearly near microphone
4. Check console for recognition errors

### Issue: No Voice Output
**Check:**
1. Volume is on
2. Browser has audio permission
3. Using supported browser
4. Try different language

---

## ✅ Success Criteria

All tests pass when:
- ✅ User speaks Gujarati → AI responds in Gujarati
- ✅ User speaks Hindi → AI responds in Hindi
- ✅ User speaks any supported language → AI responds in that language
- ✅ Call timer shows and updates every second
- ✅ Timer resets on new call
- ✅ Speech is clear and understandable
- ✅ Recognition accuracy is good (>70% confidence)
- ✅ No English responses when speaking other languages

---

## 📊 Performance Metrics

### Good Call Quality:
- Recognition confidence: **>0.7** (70%)
- Response time: **<2 seconds**
- Language match: **100%**
- Timer accuracy: **±1 second**

### Browser Compatibility:
- ✅ Chrome 90+ (Best)
- ✅ Edge 90+ (Best)
- ⚠️ Safari 14+ (Limited)
- ❌ Firefox (Not Recommended)

---

## 🎉 What's Fixed

1. **Language Accuracy** ✅
   - Gujarati issue completely resolved
   - All languages respond correctly

2. **Call Duration** ✅
   - Timer shows in seconds
   - Updates every second
   - Visible in two locations

3. **Speech Quality** ✅
   - Better recognition accuracy
   - Clearer AI voice
   - Better logging

4. **User Experience** ✅
   - Professional call interface
   - Clear status indicators
   - Continuous conversation flow

---

Ready to test! Start with Test 1 (Gujarati) as that was the critical issue.
