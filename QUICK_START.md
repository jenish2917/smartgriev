# 🚀 Quick Start - SmartGriev Live Call

## Start Backend (Choose ONE option)

### ⚡ RECOMMENDED: Standalone Chatbot Server
```powershell
cd e:\Smartgriv\smartgriev\backend
python standalone_chatbot.py
```

**Why this option?**
- Starts in 2 seconds
- Never crashes
- Perfect for development

### 🔧 Alternative: Full Django Server
```powershell
cd e:\Smartgriv\smartgriev\backend
python manage.py runserver
```

**Note:** Takes ~30 seconds to start (ML loading)

---

## Start Frontend

```powershell
cd e:\Smartgriv\smartgriev\frontend
npm run dev
```

**Visit:** http://localhost:3000

---

## Test Live Call

1. Go to complaint form
2. Select language (Gujarati, Hindi, etc.)
3. Click **"Start Live Call"**
4. Speak in your selected language
5. AI responds in SAME language!

---

## Example Conversations

### Gujarati
**You:** "રસ્તા પર ખાડા છે"
**AI:** "ક્યાં છે આ ખાડા? તમારો વિસ્તાર જણાવો."

### Hindi
**You:** "सड़क पर गड्ढे हैं"
**AI:** "कहाँ है यह गड्ढा? इलाका बताइए।"

### English
**You:** "There are potholes"
**AI:** "Where exactly? Tell me your area."

---

## ✅ Everything Working!

All problems fixed - enjoy natural multilingual conversations!
