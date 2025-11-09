"""
Gemini AI-powered chatbot service for SmartGriev
Handles natural language complaint submission in 8 Indian languages
"""

import os
import json
import google.generativeai as genai
from django.conf import settings
from deep_translator import GoogleTranslator
from datetime import datetime

class GeminiChatbotService:
    """Advanced chatbot powered by Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini API"""
        # Try to get API key from settings first, then environment
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in settings or environment variables")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Flash (cost-optimized: $0.35/M tokens)
        # Auto-switch to Pro for complex queries (token count > 10k)
        self.flash_model = genai.GenerativeModel('gemini-1.5-flash')
        self.pro_model = genai.GenerativeModel('gemini-1.5-pro')
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

DEPARTMENTS:
1. Water Supply - Water shortage, leakage, quality issues
2. Electricity - Power cuts, faulty meters, line issues  
3. Roads - Potholes, damaged roads, construction delays
4. Sanitation - Garbage collection, cleanliness, drainage
5. Streetlights - Non-functional lights, damaged poles
6. Waste Management - Waste disposal, recycling
7. Parks & Gardens - Maintenance, cleanliness
8. Building Permits - Construction violations
9. Fire Safety - Fire hazards, safety concerns
10. Other - Miscellaneous civic issues

FEW-SHOT EXAMPLES (Learn from these):

Example 1 - Water Department:
User: "हमारे इलाके में 3 दिन से पानी नहीं आ रहा है"
Department: water
Urgency: high
Location: (ask for specific area)
Response: "मुझे समझ आ गया। यह एक गंभीर समस्या है। कृपया अपना क्षेत्र का नाम बताएं?"

Example 2 - Electricity:
User: "Power cut from 2 days in Sector 15"
Department: electricity
Urgency: high  
Location: Sector 15
Response: "I understand the inconvenience. I'll help file this complaint. Can you specify the exact locality in Sector 15?"

Example 3 - Roads:
User: "రోడ్డు మీద పెద్ద గుంట ఉంది, ప్రమాదం కాబోతోంది"
Department: roads
Urgency: urgent
Location: (ask for exact location)
Response: "నేను అర్థం చేసుకున్నాను. ఇది తక్షణ శ్రద్ధ అవసరం. దయచేసి ఖచ్చితమైన ప్రదేశం చెప్పండి?"

Example 4 - Sanitation:
User: "Garbage not collected for 1 week, very bad smell"
Department: sanitation
Urgency: high
Location: (ask for address)
Response: "I apologize for this inconvenience. Let me help you file this complaint. Can you provide your street address?"

Example 5 - Streetlights:
User: "પોઈન્ટ રોડ પર સ્ટ્રીટલાઈટ કામ નથી કરતી, રાત્રે અંધારું રહે છે"
Department: streetlights
Urgency: medium
Location: પોઈન્ટ રોડ (Point Road)
Response: "હું સમજ્યો. આ સુરક્ષા સમસ્યા છે. કયા વિસ્તારમાં છે? પોઈન્ટ રોડ પર ક્યાં?"

GUIDELINES:
✅ Respond in the SAME language as user
✅ Be empathetic and professional
✅ Ask ONE question at a time (max 2-3 sentences)
✅ Extract: issue type, location, urgency (low/medium/high/urgent)
✅ Classify into correct department
✅ Confirm details before finalizing

⚠️ Keep responses concise
⚠️ Don't ask already answered questions
⚠️ For RTL languages (Urdu), maintain proper text direction

Respond naturally and helpfully."""

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
            # Initialize conversation if not exists
            if session_id not in self.conversations:
                self.start_conversation(session_id, user_language)
            
            conversation = self.conversations[session_id]
            
            # Detect if message is in non-English language and translate for processing
            translated_message = user_message
            detected_language = user_language
            
            if user_language != 'en':
                try:
                    translator = GoogleTranslator(source='auto', target='en')
                    translated_message = translator.translate(user_message)
                except Exception as e:
                    print(f"Translation error: {e}")
                    translated_message = user_message
            
            # Build conversation context
            prompt = self._build_prompt(conversation, user_message, translated_message)
            
            # Auto-switch to Pro model for complex queries (>10k tokens)
            token_estimate = len(prompt) // 4  # Rough estimate: 4 chars ≈ 1 token
            selected_model = self.pro_model if token_estimate > 10000 else self.flash_model
            
            # Generate response using Gemini (Flash or Pro)
            response = selected_model.generate_content(prompt)
            bot_response = response.text
            
            # Classify department using keywords
            department = self._classify_department(translated_message)
            
            # Translate response back to user's language if needed
            if user_language != 'en':
                try:
                    translator = GoogleTranslator(source='en', target=user_language)
                    bot_response = translator.translate(bot_response)
                except Exception as e:
                    print(f"Translation error: {e}")
            
            # Update conversation history
            conversation['history'].append({
                'user': user_message,
                'bot': bot_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Extract complaint information using AI
            complaint_data = self._extract_complaint_data(conversation)
            conversation['complaint_data'] = complaint_data
            
            # Detect intent
            intent = self._detect_intent(user_message, translated_message)
            
            return {
                'response': bot_response,
                'intent': intent,
                'complaint_data': complaint_data,
                'conversation_complete': self._is_conversation_complete(complaint_data),
                'language': user_language
            }
            
        except Exception as e:
            print(f"Gemini chat error: {e}")
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
        
        # Add current user message
        prompt += f"User's message: {user_message}\n"
        if user_message != translated_message:
            prompt += f"(Translated to English: {translated_message})\n"
        
        prompt += "\nRespond to the user in their language. If you have enough information to create the complaint, ask for confirmation and provide a summary."
        
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
            print(f"Data extraction error: {e}")
        
        return complaint_data
    
    def _detect_intent(self, original_message: str, translated_message: str) -> str:
        """Detect user intent from message"""
        
        message = translated_message.lower()
        
        # Intent patterns
        if any(word in message for word in ['hello', 'hi', 'hey', 'namaste', 'help']):
            return 'greeting'
        elif any(word in message for word in ['yes', 'ok', 'confirm', 'correct', 'right']):
            return 'confirmation'
        elif any(word in message for word in ['no', 'wrong', 'change', 'modify']):
            return 'correction'
        elif any(word in message for word in ['status', 'track', 'check', 'update']):
            return 'status_check'
        elif any(word in message for word in ['thank', 'thanks', 'bye', 'goodbye']):
            return 'closing'
        else:
            return 'complaint_filing'
    
    def _is_conversation_complete(self, complaint_data: dict) -> bool:
        """Check if we have enough information to create complaint"""
        
        required_fields = ['title', 'description', 'category', 'location']
        
        return all(
            field in complaint_data and 
            complaint_data[field] and 
            complaint_data[field] != ""
            for field in required_fields
        )
    
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


# Singleton instance
gemini_chatbot = GeminiChatbotService()
