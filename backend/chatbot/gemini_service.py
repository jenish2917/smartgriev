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
        
        # Use latest Gemini 2.5 Flash (stable and fast)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Conversation history storage
        self.conversations = {}
        
        # Supported languages
        self.languages = {
            'en': 'English',
            'hi': 'Hindi',
            'bn': 'Bengali',
            'te': 'Telugu',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
        }
        
        # System prompt for complaint handling
        self.system_prompt = """You are a helpful AI assistant for SmartGriev, a civic grievance redressal system in India.

Your role:
1. Help citizens file complaints in their native language
2. Extract key information: issue type, location, description, urgency
3. Be empathetic and professional
4. Ask clarifying questions if needed
5. Confirm details before creating the complaint

Complaint categories:
- Infrastructure (roads, water supply, electricity, drainage)
- Health & Sanitation (garbage, cleanliness, hospitals)
- Law & Order (crime, safety, police)
- Education (schools, teachers, facilities)
- Transportation (buses, traffic, parking)
- Environment (pollution, trees, parks)
- Others

Guidelines:
- Always be polite and empathetic
- Ask one question at a time
- Keep responses concise (2-3 sentences max)
- Acknowledge the citizen's concern
- Extract location, urgency level (low/medium/high/urgent)
- If complaint is about a person, ask for more details
- Once you have enough info, summarize and ask for confirmation

Important: Respond in the same language as the user's message."""

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
        """Get greeting in user's language"""
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
            'pa': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡੀ ਸ਼ਿਕਾਇਤ ਦਰਜ ਕਰਨ ਵਿੱਚ ਮਦਦ ਕਰਨ ਲਈ ਇੱਥੇ ਹਾਂ। ਤੁਸੀਂ ਕਿਹੜੀ ਸਮੱਸਿਆ ਦੀ ਰਿਪੋਰਟ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ?"
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
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            bot_response = response.text
            
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
