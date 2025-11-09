"""
Google AI (Gemini) Chatbot Integration for SmartGriev
Provides ChatGPT-like conversational AI
"""

import os
import json
from typing import Dict, List, Optional
import requests
from django.conf import settings

class GoogleAIChatbot:
    """Google Gemini AI Chatbot"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_AI_API_KEY', settings.GOOGLE_AI_API_KEY if hasattr(settings, 'GOOGLE_AI_API_KEY') else None)
        # Using v1beta API with gemini-2.5-flash (verified available)
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        self.system_prompt = """You are a friendly, helpful AI assistant for SmartGriev - a civic complaint system in India. You talk like a real human having a natural conversation.

🎯 CRITICAL LANGUAGE RULES (FOLLOW STRICTLY):
1. DETECT the user's language from their message
2. Respond COMPLETELY in that SAME language - no mixing, no English words
3. If user speaks Gujarati (ગુજરાતી) → Respond ONLY in Gujarati
4. If user speaks Hindi (हिंदी) → Respond ONLY in Hindi  
5. If user speaks Marathi (मराठी) → Respond ONLY in Marathi
6. If user speaks Punjabi (ਪੰਜਾਬੀ) → Respond ONLY in Punjabi
7. If user speaks English → Respond ONLY in English
8. NEVER mix languages - use pure, natural language

💬 CONVERSATION STYLE:
- Talk naturally like a helpful friend or neighbor
- Use conversational phrases, not formal/robotic language
- Show empathy and understanding
- Keep responses short (2-3 sentences max)
- Sound like a real human, not a chatbot
- Be warm, friendly, and supportive

📋 YOUR ROLE:
- Help citizens report civic problems (roads, water, garbage, electricity, etc.)
- Listen to their complaints with empathy
- Ask clarifying questions if needed
- Provide helpful suggestions
- Make the complaint process easy and friendly

EXAMPLES OF NATURAL RESPONSES:

Gujarati: "હા, મને સમજાયું. રસ્તા પર ખાડા છે એ ખરેખર મુશ્કેલી છે. તમે ક્યાં રહો છો? હું તમારી ફરિયાદ નોંધી લઈશ."

Hindi: "जी हाँ, मैं समझ गया। पानी की समस्या बहुत परेशान करने वाली है। आप कहाँ रहते हैं? मैं आपकी शिकायत दर्ज कर लूंगा।"

Remember: Sound like a real person having a natural conversation, not a formal system!"""

    def chat(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Send message to Google AI and get response
        
        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with 'response', 'success', and 'error' keys
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Google AI API key not configured',
                'response': 'Sorry, the chatbot is not configured properly. Please contact support.'
            }
        
        try:
            # Build conversation context
            messages = self._build_conversation(user_message, conversation_history)
            
            # Call Google AI API
            headers = {
                'Content-Type': 'application/json',
            }
            
            payload = {
                "contents": messages
            }
            
            # Add API key to URL
            url = f"{self.api_url}?key={self.api_key}"
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)  # Increased timeout
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response text
                if 'candidates' in data and len(data['candidates']) > 0:
                    candidate = data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        reply = candidate['content']['parts'][0]['text']
                        
                        return {
                            'success': True,
                            'response': reply,
                            'model': 'gemini-2.5-flash',
                            'error': None
                        }
                
                return {
                    'success': False,
                    'error': 'Invalid response format from Google AI',
                    'response': 'Sorry, I encountered an error. Please try again.'
                }
            else:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', error_msg)
                except:
                    pass
                
                return {
                    'success': False,
                    'error': error_msg,
                    'response': 'Sorry, I encountered an error. Please try again.'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'response': 'Sorry, the request took too long. Please try again.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f'Sorry, an error occurred: {str(e)}'
            }
    
    def _build_conversation(self, user_message: str, history: List[Dict] = None) -> List[Dict]:
        """Build conversation format for Google AI"""
        messages = []
        
        # Add system prompt as first message
        messages.append({
            "role": "user",
            "parts": [{"text": self.system_prompt}]
        })
        messages.append({
            "role": "model",
            "parts": [{"text": "Understood. I'll help users with SmartGriev in their preferred language - Gujarati, Hindi, Marathi, Punjabi, English, or any Indian language they speak."}]
        })
        
        # Add conversation history
        if history:
            for msg in history[-10:]:  # Last 10 messages
                # Support both old format (type/message) and new format (role/content)
                msg_role = msg.get('role') or msg.get('type')
                msg_text = msg.get('content') or msg.get('message') or msg.get('reply', '')
                
                if msg_role in ['user', 'user']:
                    messages.append({
                        "role": "user",
                        "parts": [{"text": msg_text}]
                    })
                elif msg_role in ['assistant', 'bot', 'model']:
                    messages.append({
                        "role": "model",
                        "parts": [{"text": msg_text}]
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })
        
        return messages

# Global chatbot instance
chatbot = GoogleAIChatbot()

def get_chatbot_response(message: str, conversation_history: List[Dict] = None) -> Dict:
    """
    Get chatbot response (wrapper function)
    
    Args:
        message: User's message
        conversation_history: Previous conversation
        
    Returns:
        Response dictionary
    """
    return chatbot.chat(message, conversation_history)
