"""
Gemini AI-powered chatbot service for SmartGriev
Handles natural language complaint submission in 8 Indian languages
"""

import os
import json
import logging
import google.generativeai as genai
from django.conf import settings
from deep_translator import GoogleTranslator
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiChatbotService:
    """Advanced chatbot powered by Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini API"""
        # Try to get API key from settings first, then environment
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in settings or environment variables")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.0 Flash (latest stable version)
        # Configure with safety settings to allow civic complaints
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        # Use Gemini 2.5 Flash (stable, latest version with good quota)
        self.flash_model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=safety_settings
        )
        self.pro_model = genai.GenerativeModel(
            'gemini-2.5-pro',
            safety_settings=safety_settings
        )
        self.model = self.flash_model  # Default to Flash
        
        # Conversation history storage
        self.conversations = {}
        
        # Supported languages (12 Indian languages - from PDF spec)
        self.languages = {
            'en': 'English',
            'hi': 'Hindi (हिंदी)',
            'bn': 'Bengali (বাংলা)',
            'te': 'Telugu (తెలుగు)',
            'mr': 'Marathi (मराठी)',
            'ta': 'Tamil (தமிழ்)',
            'gu': 'Gujarati (ગુજરાતી)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)',
            'ur': 'Urdu (اردو)',        # RTL support
            'as': 'Assamese (অসমীয়া)',  # New
            'or': 'Odia (ଓଡ଼ିଆ)',        # New
        }
        
        # Department keywords in 12 Indian languages (for classification)
        self.department_keywords = {
            'water': ['water', 'पानी', 'জল', 'నీరు', 'पाणी', 'தண்ணீர்', 'પાણી', 'ನೀರು', 'വെള്ളം', 'ਪਾਣੀ', 'پانی', 'পানী', 'ପାଣି'],
            'electricity': ['electricity', 'light', 'बिजली', 'বিদ্যুৎ', 'విద్యుత్', 'वीज', 'மின்சாரம்', 'વીજળી', 'ವಿದ್ಯುತ್', 'വൈദ്യുതി', 'ਬਿਜਲੀ', 'بجلی', 'বিদ্যুৎ', 'ବିଦ୍ୟୁତ'],
            'roads': ['road', 'pothole', 'सड़क', 'রাস্তা', 'రోడ్డు', 'रस्ता', 'சாலை', 'રસ્તો', 'ರಸ್ತೆ', 'റോഡ്', 'ਸੜਕ', 'سڑک', 'ৰাস্তা', 'ରାସ୍ତା'],
            'sanitation': ['garbage', 'waste', 'कचरा', 'আবর্জনা', 'చెత్త', 'कचरा', 'குப்பை', 'કચરો', 'ಕಸ', 'മാലിന്യം', 'ਕੂੜਾ', 'کچرا', 'আবৰ্জনা', 'ଅଳିଆ'],
            'streetlights': ['streetlight', 'lamp', 'बत्ती', 'বাতি', 'దీపం', 'दिवा', 'விளக்கு', 'દીવો', 'ದೀಪ', 'വിളക്ക്', 'ਬੱਤੀ', 'بتی', 'লাইট', 'ବତୀ'],
        }
        
        # System prompt with few-shot learning (5 examples per department)
        self.system_prompt = """You are SmartGriev AI - a helpful assistant for India's civic grievance system.

ROLE: Help citizens file complaints in 12 Indian languages (English, Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Assamese, Odia)

YOUR TASK - CONVERSATION FLOW:
1. **Greet** the user warmly in their language
2. **Understand** their complaint - ask clarifying questions
3. **Extract** ALL REQUIRED information (MANDATORY - DO NOT skip any):
   ✓ Issue type (what is the problem?) - REQUIRED
   ✓ Complete Location (area, landmark, address) - REQUIRED - minimum 5 characters
   ✓ Urgency level (low/medium/high/urgent) - REQUIRED
   ✓ Detailed Description (full explanation) - REQUIRED - minimum 20 characters
   ✓ Title (brief summary) - REQUIRED
4. **Confirm** ALL details - show complete summary and ask: "Would you like to add or change anything?"
5. **Auto-Submit** - If user confirms (says "no", "that's all", "submit", "ok", "correct", or similar), AUTOMATICALLY submit the complaint WITHOUT requiring any button click

⚠️ CRITICAL RULES:
- NEVER show submit buttons or forms - this is a pure conversation
- ALWAYS ask for missing information naturally
- After collecting all info, summarize and ask for confirmation
- If user says "no changes", "looks good", "submit it", "that's all", etc. → tell them complaint is being submitted
- Make the confirmation question clear: "Would you like to add or modify anything, or shall I submit this complaint?"
- Be smart about user intent - "no", "nope", "all good", "submit", "go ahead" all mean confirmation

DEPARTMENTS:
1. Water Supply - Water shortage, leakage, quality issues, supply disruption
2. Electricity - Power cuts, faulty meters, line issues, transformer problems
3. Roads - Potholes, damaged roads, construction delays, maintenance
4. Sanitation - Garbage collection, cleanliness, drainage, waste management
5. Streetlights - Non-functional lights, damaged poles, insufficient lighting
6. Waste Management - Waste disposal, recycling, landfill issues
7. Parks & Gardens - Maintenance, cleanliness, encroachment
8. Building Permits - Construction violations, illegal buildings
9. Fire Safety - Fire hazards, safety concerns, blocked exits
10. Other - Miscellaneous civic issues

CONVERSATION EXAMPLES:

**Example 1 - Water Complaint (Hindi):**
User: "पानी नहीं आ रहा है"
Assistant: "मुझे खेद है। कितने समय से पानी नहीं आ रहा है? और आप किस इलाके में रहते हैं?"
User: "3 दिन से, सेक्टर 15 में"
Assistant: "समझा। यह बहुत गंभीर है। क्या आपका पूरा क्षेत्र प्रभावित है या सिर्फ आपका घर?"
User: "पूरा क्षेत्र"
Assistant: "ठीक है। मैं आपकी शिकायत दर्ज कर रहा हूं:
- समस्या: जल आपूर्ति बंद
- स्थान: सेक्टर 15
- अवधि: 3 दिन
- गंभीरता: उच्च
क्या ये विवरण सही हैं?"

**Example 2 - Electricity (English):**
User: "Power cut since morning"
Assistant: "I understand. That's very inconvenient. Which area are you in?"
User: "Rajaji Nagar, Bangalore"
Assistant: "Thank you. Just to confirm:
- Issue: Power outage
- Location: Rajaji Nagar, Bangalore  
- Duration: Since morning
- Urgency: High
Is this correct? Any other details you'd like to add?"

**Example 3 - Roads (Telugu):**
User: "రోడ్డు మీద పెద్ద గుంట ఉంది"
Assistant: "నేను అర్థం చేసుకున్నాను. ఇది ప్రమాదకరం. ఖచ్చితంగా ఎక్కడ ఉంది?"
User: "MG రోడ్, హైదరాబాద్"
Assistant: "ధన్యవాదాలు. ఇది ఎంత పెద్దది? ఏదైనా ప్రమాదం జరిగిందా?"

**Example 4 - Garbage (Gujarati):**
User: "કચરો 1 અઠવાડિયાથી નથી ઉપાડવામાં આવ્યો"
Assistant: "માફ કરશો. આ ખૂબ ખરાબ છે. તમારું સરનામું શું છે?"
User: "સ્ટેશન રોડ, અમદાવાદ"
Assistant: "સમજાયું. શું ખરાબ ગંધ આવે છે? સ્વાસ્થ્ય સમસ્યા છે?"

GUIDELINES FOR EFFECTIVE CONVERSATION:
✅ **BE EMPATHETIC**: Show you care about their problem
✅ **ASK ONE QUESTION AT A TIME**: Don't overwhelm with multiple questions
✅ **KEEP RESPONSES SHORT**: 2-3 sentences maximum
✅ **USE THEIR LANGUAGE**: Always respond in same language as user
✅ **EXTRACT INFORMATION GRADUALLY**: 
   - First: What is the problem?
   - Then: Where is it?
   - Then: How serious/urgent?
   - Finally: Confirm all details
✅ **CLASSIFY CORRECTLY**: Choose the right department based on keywords
✅ **BE CONVERSATIONAL**: Natural, friendly tone - not robotic

⚠️ IMPORTANT RULES:
- DON'T ask questions user already answered
- DON'T use complex/technical language
- DON'T give long responses
- DON'T ask for unnecessary details
- DO confirm before finalizing complaint

URGENCY LEVELS:
- **URGENT**: Life/safety risk (fire, major water burst, live wire)
- **HIGH**: Severe inconvenience (no water 2+ days, power cut, major pothole)
- **MEDIUM**: Moderate issue (garbage not collected, streetlight out)
- **LOW**: Minor issue (small pothole, park maintenance)

Respond naturally, empathetically, and helpfully. Build trust with the citizen."""

    def start_conversation(self, session_id: str, user_language: str = 'en') -> str:
        """Start a new conversation"""
        self.conversations[session_id] = {
            'history': [],
            'language': user_language,
            'complaint_data': {},
            'started_at': datetime.now().isoformat()
        }
        
        greeting = self._get_greeting(user_language)
        return greeting
    
    def _get_greeting(self, language: str) -> str:
        """Get greeting in user's language (12 Indian languages)"""
        greetings = {
            'en': "Hello! I'm here to help you file a complaint. What issue would you like to report?",
            'hi': "नमस्ते! मैं आपकी शिकायत दर्ज करने में मदद करने के लिए यहां हूं। आप किस समस्या की रिपोर्ट करना चाहेंगे?",
            'bn': "হ্যালো! আমি আপনার অভিযোগ দায়ের করতে সাহায্য করতে এখানে আছি। আপনি কোন সমস্যা রিপোর্ট করতে চান?",
            'te': "హలో! నేను మీ ఫిర్యాదును దాఖలు చేయడంలో సహాయం చేయడానికి ఇక్కడ ఉన్నాను. మీరు ఏ సమస్యను నివేదించాలనుకుంటున్నారు?",
            'mr': "नमस्कार! मी तुमची तक्रार नोंदवण्यासाठी येथे आहे. तुम्हाला कोणत्या समस्येची तक्रार करायची आहे?",
            'ta': "வணக்கம்! உங்கள் புகாரை பதிவு செய்ய நான் இங்கே இருக்கிறேன். எந்த பிரச்சினையை புகாரளிக்க விரும்புகிறீர்கள்?",
            'gu': "નમસ્તે! હું તમારી ફરિયાદ નોંધવામાં મદદ કરવા અહીં છું. તમે કઈ સમસ્યાની જાણ કરવા માંગો છો?",
            'kn': "ನಮಸ್ಕಾರ! ನಿಮ್ಮ ದೂರು ದಾಖಲಿಸಲು ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ. ನೀವು ಯಾವ ಸಮಸ್ಯೆಯನ್ನು ವರದಿ ಮಾಡಲು ಬಯಸುತ್ತೀರಿ?",
            'ml': "ഹലോ! നിങ്ങളുടെ പരാതി ഫയൽ ചെയ്യാൻ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്. നിങ്ങൾ ഏത് പ്രശ്നമാണ് റിപ്പോർട്ട് ചെയ്യാൻ ആഗ്രഹിക്കുന്നത്?",
            'pa': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡੀ ਸ਼ਿਕਾਇਤ ਦਰਜ ਕਰਨ ਵਿੱਚ ਮਦਦ ਕਰਨ ਲਈ ਇੱਥੇ ਹਾਂ। ਤੁਸੀਂ ਕਿਹੜੀ ਸਮੱਸਿਆ ਦੀ ਰਿਪੋਰਟ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ?",
            'ur': "السلام علیکم! میں آپ کی شکایت درج کرنے میں مدد کے لیے یہاں ہوں۔ آپ کس مسئلے کی اطلاع دینا چاہتے ہیں؟",  # RTL
            'as': "নমস্কাৰ! মই আপোনাৰ অভিযোগ দাখিল কৰাত সহায় কৰিবলৈ ইয়াত আছো। আপুনি কোনটো সমস্যা প্ৰতিবেদন কৰিব বিচাৰে?",  # Assamese
            'or': "ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କ ଅଭିଯୋଗ ଦାଖଲ କରିବାରେ ସାହାଯ୍ୟ କରିବାକୁ ଏଠାରେ ଅଛି। ଆପଣ କେଉଁ ସମସ୍ୟାର ରିପୋର୍ଟ କରିବାକୁ ଚାହୁଁଛନ୍ତି?",  # Odia
        }
        return greetings.get(language, greetings['en'])
    
    def chat(self, session_id: str, user_message: str, user_language: str = 'en') -> dict:
        """
        Process user message and generate response
        
        Returns:
            dict with response, intent, entities, and complaint_data
        """
        try:
            logger.info(f"[CHAT] Session: {session_id}, Language: {user_language}")
            logger.info(f"[CHAT] User message: {user_message[:100]}...")
            
            # Initialize conversation if not exists
            if session_id not in self.conversations:
                logger.info(f"[CHAT] Starting new conversation for session: {session_id}")
                self.start_conversation(session_id, user_language)
            
            conversation = self.conversations[session_id]
            
            # Gemini 2.0 supports multi-language natively, no translation needed for input
            # Just pass the message as-is and let Gemini understand it
            translated_message = user_message  # Keep original for classification
            detected_language = user_language
            
            # For department classification, we can do a simple translation if needed
            # But for chatbot response, let Gemini handle it natively
            if user_language != 'en':
                try:
                    # Only translate for keyword-based department classification
                    translator = GoogleTranslator(source='auto', target='en')
                    translated_message = translator.translate(user_message)
                    logger.info(f"[CHAT] Translated to English: {translated_message[:100]}...")
                except Exception as e:
                    logger.error(f"[CHAT] Translation error: {e}")
                    translated_message = user_message
            
            # Build conversation context with explicit language instruction
            prompt = self._build_prompt(conversation, user_message, translated_message)
            logger.info(f"[CHAT] Prompt length: {len(prompt)} chars")
            
            # Auto-switch to Pro model for complex queries (>10k tokens)
            token_estimate = len(prompt) // 4  # Rough estimate: 4 chars ≈ 1 token
            selected_model = self.pro_model if token_estimate > 10000 else self.flash_model
            logger.info(f"[CHAT] Using model: {'Pro' if selected_model == self.pro_model else 'Flash'}")
            
            # Generate response using Gemini (Flash or Pro)
            logger.info(f"[CHAT] Calling Gemini API...")
            try:
                response = selected_model.generate_content(prompt)
                bot_response = response.text
                logger.info(f"[CHAT] Gemini response: {bot_response[:200]}...")
            except Exception as api_error:
                logger.error(f"[CHAT] Gemini API error: {type(api_error).__name__}: {str(api_error)}")
                # Check if it's a safety filter issue
                if hasattr(api_error, 'message') and 'safety' in str(api_error).lower():
                    bot_response = "I understand you want to report a civic issue. Could you please provide more details about the problem, location, and urgency?"
                else:
                    raise  # Re-raise other errors to be caught by outer exception handler
            
            # Classify department using keywords (use translated text for this)
            department = self._classify_department(translated_message)
            logger.info(f"[CHAT] Classified department: {department}")
            
            # Gemini 2.0 responds natively in the user's language based on the prompt
            # No need to translate the response back - it should already be in the correct language
            
            # Update conversation history
            conversation['history'].append({
                'user': user_message,
                'bot': bot_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Extract complaint information using AI
            logger.info(f"[CHAT] Extracting complaint data...")
            complaint_data = self._extract_complaint_data(conversation)
            conversation['complaint_data'] = complaint_data
            logger.info(f"[CHAT] Extracted complaint data: {complaint_data}")
            
            # Detect intent
            intent = self._detect_intent(user_message, translated_message)
            logger.info(f"[CHAT] Detected intent: {intent}")
            logger.info(f"[CHAT] User message for intent detection: '{user_message}'")
            logger.info(f"[CHAT] Translated message for intent detection: '{translated_message}'")
            
            # Check if conversation is complete
            is_complete = self._is_conversation_complete(complaint_data)
            logger.info(f"[CHAT] Conversation complete: {is_complete}")
            
            # Check if user confirmed submission after info is complete
            should_auto_submit = (
                is_complete and 
                intent == 'submit_confirmation'
            )
            logger.info(f"[CHAT] Auto-submit triggered: {should_auto_submit}")
            
            return {
                'response': bot_response,
                'intent': intent,
                'complaint_data': complaint_data,
                'conversation_complete': is_complete,
                'auto_submit': should_auto_submit,  # New flag for frontend
                'language': user_language
            }
            
        except Exception as e:
            logger.error(f"[CHAT ERROR] {type(e).__name__}: {str(e)}", exc_info=True)
            return {
                'response': "I apologize, but I'm having trouble processing your request. Please try again.",
                'intent': 'error',
                'complaint_data': {},
                'conversation_complete': False,
                'error': str(e)
            }
    
    def _classify_department(self, message: str) -> str:
        """
        Classify complaint into department using keyword matching
        Supports 12 Indian languages
        """
        message_lower = message.lower()
        
        # Score each department
        department_scores = {}
        for dept, keywords in self.department_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                department_scores[dept] = score
        
        # Return department with highest score, default to 'other'
        if department_scores:
            return max(department_scores, key=department_scores.get)
        return 'other'
    
    def _build_prompt(self, conversation: dict, user_message: str, translated_message: str) -> str:
        """Build prompt for Gemini with conversation history"""
        
        # Start with system prompt
        prompt = self.system_prompt + "\n\n"
        
        # Add conversation history
        if conversation['history']:
            prompt += "Previous conversation:\n"
            for turn in conversation['history'][-5:]:  # Last 5 turns
                prompt += f"User: {turn['user']}\n"
                prompt += f"Assistant: {turn['bot']}\n"
            prompt += "\n"
        
        # Add current complaint data if any
        if conversation['complaint_data']:
            prompt += f"Current complaint information: {json.dumps(conversation['complaint_data'], indent=2)}\n\n"
        
        # Add current user message with language instruction
        language_name = self.languages.get(conversation['language'], 'English')
        language_code = conversation['language']
        
        prompt += f"User's message (in {language_name}): {user_message}\n"
        if user_message != translated_message:
            prompt += f"(English translation for context: {translated_message})\n"
        
        # Strong language enforcement
        if language_code == 'gu':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Gujarati (ગુજરાતી). DO NOT use English, Hindi, or any other language. Use Gujarati script exclusively. Every single word must be in Gujarati."
        elif language_code == 'ml':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Malayalam (മലയാളം). DO NOT use English, Hindi, Gujarati, or any other language. Use Malayalam script exclusively. Every single word must be in Malayalam."
        elif language_code == 'hi':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Hindi (हिंदी). DO NOT use English or any other language. Use Devanagari script exclusively. Every single word must be in Hindi."
        elif language_code == 'bn':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Bengali (বাংলা). DO NOT use English or any other language. Use Bengali script exclusively. Every single word must be in Bengali."
        elif language_code == 'te':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Telugu (తెలుగు). DO NOT use English or any other language. Use Telugu script exclusively. Every single word must be in Telugu."
        elif language_code == 'mr':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Marathi (मराठी). DO NOT use English or any other language. Use Devanagari script exclusively. Every single word must be in Marathi."
        elif language_code == 'ta':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Tamil (தமிழ்). DO NOT use English or any other language. Use Tamil script exclusively. Every single word must be in Tamil."
        elif language_code == 'kn':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Kannada (ಕನ್ನಡ). DO NOT use English or any other language. Use Kannada script exclusively. Every single word must be in Kannada."
        elif language_code == 'pa':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Punjabi (ਪੰਜਾਬੀ). DO NOT use English or any other language. Use Gurmukhi script exclusively. Every single word must be in Punjabi."
        elif language_code == 'ur':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Urdu (اردو). DO NOT use English or any other language. Use Urdu script exclusively. Every single word must be in Urdu."
        elif language_code == 'as':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Assamese (অসমীয়া). DO NOT use English or any other language. Use Assamese script exclusively. Every single word must be in Assamese."
        elif language_code == 'or':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in Odia (ଓଡ଼ିଆ). DO NOT use English or any other language. Use Odia script exclusively. Every single word must be in Odia."
        elif language_code != 'en':
            prompt += f"\n**CRITICAL INSTRUCTION**: You MUST respond ONLY in {language_name}. DO NOT use English or any other language. Use {language_name} script exclusively. Every single word must be in {language_name}."
        else:
            prompt += f"\n**IMPORTANT**: Respond in {language_name}."
        
        if self._is_conversation_complete(conversation.get('complaint_data', {})):
            prompt += f" If you have enough information to create the complaint, ask for confirmation and provide a summary in {language_name}."
        
        return prompt
    
    def _extract_complaint_data(self, conversation: dict) -> dict:
        """Extract structured complaint data from conversation"""
        
        complaint_data = conversation.get('complaint_data', {})
        
        # Analyze conversation to extract data
        full_conversation = "\n".join([
            f"User: {turn['user']}\nBot: {turn['bot']}"
            for turn in conversation['history']
        ])
        
        # Use Gemini to extract structured data
        try:
            extraction_prompt = f"""Analyze this conversation and extract complaint information in JSON format:

{full_conversation}

Extract:
- title: Brief title of the complaint (max 100 chars)
- description: Detailed description
- category: One of (Infrastructure, Health & Sanitation, Law & Order, Education, Transportation, Environment, Others)
- location: Where the issue is (address, area, landmark)
- urgency: One of (low, medium, high, urgent)
- has_enough_info: true/false if we have enough information to file the complaint

Return ONLY valid JSON, no explanation."""

            response = self.model.generate_content(extraction_prompt)
            extracted = json.loads(response.text.strip('```json\n').strip('```').strip())
            
            # Update complaint data with extracted info
            for key, value in extracted.items():
                if value and value != "":
                    complaint_data[key] = value
                    
        except Exception as e:
            logger.error(f"Data extraction error: {e}")
        
        return complaint_data
    
    def _detect_intent(self, original_message: str, translated_message: str) -> str:
        """Detect user intent from message"""
        
        message = translated_message.lower()
        logger.info(f"[INTENT] Detecting intent for message: '{message}'")
        
        # Intent patterns
        if any(word in message for word in ['hello', 'hi', 'hey', 'namaste', 'help', 'start']):
            logger.info(f"[INTENT] Matched: greeting")
            return 'greeting'
        
        # Confirmation patterns - user wants to submit (expanded list)
        # Handle "no" when asked about modifications/changes
        elif any(phrase in message for phrase in [
            'no change', 'no modification', 'looks good', 'looks fine', 'all good', 
            'thats all', "that's all", 'submit', 'file it', 'go ahead', 'proceed',
            'correct', 'yes submit', 'yes please', 'confirm', 'ok submit', 'okay',
            'nothing else', 'no more', 'no addition', 'all set', 'ready', 
            'nope', 'nah', 'done', 'perfect', 'good to go', 'submit it', 'submit this',
            'submit the complaint', 'file the complaint', 'create complaint'
        ]) or message.strip() == 'no':  # Simple "no" when asked if they want changes
            logger.info(f"[INTENT] Matched: submit_confirmation (message.strip()='{message.strip()}')")
            return 'submit_confirmation'
        
        # Just "yes", "ok", "right" - could be answering a question, not confirming submission
        elif message.strip() in ['yes', 'ok', 'correct', 'right', 'yeah', 'yep']:
            logger.info(f"[INTENT] Matched: confirmation")
            return 'confirmation'
        
        # Modification/correction request
        elif any(word in message for word in ['change', 'modify', 'edit', 'update', 'wait', 'wrong', 'actually']):
            logger.info(f"[INTENT] Matched: correction")
            return 'correction'
        
        elif any(word in message for word in ['status', 'track', 'check my complaint', 'complaint status']):
            logger.info(f"[INTENT] Matched: status_check")
            return 'status_check'
        
        elif any(word in message for word in ['thank', 'thanks', 'bye', 'goodbye']):
            logger.info(f"[INTENT] Matched: closing")
            return 'closing'
        
        else:
            logger.info(f"[INTENT] Matched: complaint_filing (default)")
            return 'complaint_filing'
    
    def _is_conversation_complete(self, complaint_data: dict) -> bool:
        """Check if we have enough information to create complaint"""
        
        # All required fields that must be collected before submission
        required_fields = ['title', 'description', 'category', 'location', 'urgency']
        
        # Check all required fields are present and not empty
        for field in required_fields:
            if field not in complaint_data or not complaint_data[field] or complaint_data[field] == "":
                return False
        
        # Additional validation for minimum description length
        if len(complaint_data.get('description', '')) < 20:
            return False
        
        # Validate location has meaningful content
        if len(complaint_data.get('location', '')) < 5:
            return False
        
        return True
    
    def get_conversation_summary(self, session_id: str) -> dict:
        """Get summary of conversation and extracted complaint data"""
        
        if session_id not in self.conversations:
            return {'error': 'Conversation not found'}
        
        conversation = self.conversations[session_id]
        
        return {
            'session_id': session_id,
            'language': conversation['language'],
            'started_at': conversation['started_at'],
            'message_count': len(conversation['history']),
            'complaint_data': conversation['complaint_data'],
            'ready_to_submit': self._is_conversation_complete(conversation['complaint_data'])
        }
    
    def end_conversation(self, session_id: str):
        """End conversation and clean up"""
        if session_id in self.conversations:
            del self.conversations[session_id]


# Singleton instance with graceful error handling
try:
    gemini_chatbot = GeminiChatbotService()
    logger.info("Gemini chatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini chatbot: {e}")
    gemini_chatbot = None
