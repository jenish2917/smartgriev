"""
Google AI (Gemini) Integration for SmartGriev
Provides AI chatbot capabilities using Google's Gemini API
"""

import os
import logging
from typing import Generator, Dict, Any, List
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    logger.warning("Google GenerativeAI library not available. Install with: pip install google-generativeai")


class GoogleAIChatbot:
    """Chatbot service using Google's Gemini API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, 'GOOGLE_AI_API_KEY', None)
        
        if GOOGLE_AI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.chat = None
            logger.info("Google AI (Gemini) initialized successfully")
        else:
            self.model = None
            logger.warning("Google AI not initialized. Check API key and installation.")
    
    def create_system_prompt(self, language: str = "en") -> str:
        """Create system prompt for the chatbot"""
        prompts = {
            "en": """You are an AI assistant for SmartGriev, an Indian government grievance management system. 
Your role is to help citizens file complaints, check status, and get information about public services.

Guidelines:
- Be polite, professional, and empathetic
- Provide clear, concise responses in 2-3 sentences
- Ask clarifying questions when needed
- Guide users through the complaint filing process
- Recognize urgency and escalate critical issues
- Support both English and Hindi languages
- Be aware of Indian government procedures and departments
- Help users understand what information they need to provide for complaints
- Suggest relevant departments based on the complaint type""",
            
            "hi": """आप स्मार्टग्रीव के लिए एक AI सहायक हैं, जो भारत सरकार की शिकायत प्रबंधन प्रणाली है।
आपकी भूमिका नागरिकों को शिकायत दर्ज करने, स्थिति जांचने और सार्वजनिक सेवाओं के बारे में जानकारी प्राप्त करने में मदद करना है।

दिशानिर्देश:
- विनम्र, पेशेवर और सहानुभूतिपूर्ण रहें
- 2-3 वाक्यों में स्पष्ट, संक्षिप्त उत्तर प्रदान करें
- आवश्यकता पड़ने पर स्पष्टीकरण के प्रश्न पूछें
- शिकायत दर्ज करने की प्रक्रिया में उपयोगकर्ताओं का मार्गदर्शन करें
- महत्वपूर्ण मुद्दों को पहचानें"""
        }
        return prompts.get(language, prompts["en"])
    
    def chat_stream(self, message: str, conversation_history: List[Dict] = None, language: str = "en") -> Generator[str, None, None]:
        """
        Stream chatbot responses using Google Gemini
        
        Args:
            message: User's message
            conversation_history: Previous conversation messages
            language: Language code (en or hi)
            
        Yields:
            Chunks of the AI response
        """
        if not self.model:
            # Fallback response if Google AI not available
            yield "I'm sorry, the AI service is currently unavailable. Please try again later."
            return
        
        try:
            # Create chat session with context
            if not self.chat or conversation_history is None or len(conversation_history) == 0:
                # Start new chat with system prompt
                system_prompt = self.create_system_prompt(language)
                self.chat = self.model.start_chat(history=[])
                
                # Send system prompt first
                self.chat.send_message(system_prompt)
            
            # Send user message and stream response
            response = self.chat.send_message(message, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Google AI chat error: {str(e)}")
            yield f"I encountered an error: {str(e)}. Please try again."
    
    def chat_complete(self, message: str, conversation_history: List[Dict] = None, language: str = "en") -> str:
        """
        Get complete chatbot response (non-streaming)
        
        Args:
            message: User's message
            conversation_history: Previous conversation messages
            language: Language code (en or hi)
            
        Returns:
            Complete AI response
        """
        if not self.model:
            return "AI service is currently unavailable. Please try again later."
        
        try:
            # Prepare full conversation context
            system_prompt = self.create_system_prompt(language)
            
            # Build conversation history
            conversation = []
            if conversation_history:
                for entry in conversation_history[-5:]:  # Last 5 messages
                    role = "user" if entry.get('sender') == 'user' else "model"
                    conversation.append({
                        "role": role,
                        "parts": [entry.get('text', entry.get('message', ''))]
                    })
            
            # Create chat and get response
            chat = self.model.start_chat(history=conversation)
            response = chat.send_message(f"{system_prompt}\n\nUser: {message}")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Google AI chat error: {str(e)}")
            return f"I encountered an error. Please try again. Error: {str(e)}"
    
    def analyze_complaint(self, text: str) -> Dict[str, Any]:
        """
        Analyze complaint text using AI
        
        Args:
            text: Complaint description
            
        Returns:
            Dictionary with analysis results
        """
        if not self.model:
            return {
                "category": "general",
                "priority": "medium",
                "department": "general",
                "summary": text[:100]
            }
        
        try:
            prompt = f"""Analyze this complaint and provide structured information:

Complaint: {text}

Provide:
1. Category (roads, water, electricity, garbage, healthcare, education, police, other)
2. Priority (low, medium, high, urgent)
3. Suggested Department
4. Brief summary (1 sentence)
5. Urgency level (1-5)

Format as JSON."""
            
            response = self.model.generate_content(prompt)
            
            # Parse response (simplified - you can add better JSON parsing)
            return {
                "category": "general",
                "priority": "medium",
                "department": "general",
                "summary": text[:100],
                "ai_analysis": response.text
            }
            
        except Exception as e:
            logger.error(f"Complaint analysis error: {str(e)}")
            return {
                "category": "general",
                "priority": "medium",
                "department": "general",
                "summary": text[:100]
            }


# Singleton instance
_google_ai_chatbot = None

def get_google_ai_chatbot() -> GoogleAIChatbot:
    """Get or create GoogleAIChatbot singleton instance"""
    global _google_ai_chatbot
    if _google_ai_chatbot is None:
        _google_ai_chatbot = GoogleAIChatbot()
    return _google_ai_chatbot
