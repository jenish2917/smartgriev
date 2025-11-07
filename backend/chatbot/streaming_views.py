"""
Streaming Chatbot Views with ChatGPT-style responses
Implements Server-Sent Events (SSE) for real-time streaming
"""

import json
import logging
import os
from typing import Generator, Dict, Any
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import uuid

from .models import ChatLog, ChatSession
from .utils import (
    detect_language, detect_intent, analyze_sentiment,
    extract_entities, analyze_complaint_urgency, extract_complaint_category
)

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq library not available. Install with: pip install groq")


class StreamingChatbotService:
    """Service for streaming chatbot responses using Groq API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if GROQ_AVAILABLE and self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Groq client not initialized. Streaming will use fallback responses.")
    
    def create_system_prompt(self, language: str = "en") -> str:
        """Create system prompt for the chatbot"""
        prompts = {
            "en": """You are an AI assistant for SmartGriev, an Indian government grievance management system. 
Your role is to help citizens file complaints, check status, and get information about public services.

Guidelines:
- Be polite, professional, and empathetic
- Provide clear, concise responses
- Ask clarifying questions when needed
- Guide users through the complaint filing process
- Recognize urgency and escalate critical issues
- Support both English and Hindi languages
- Be aware of Indian government procedures and departments""",
            
            "hi": """आप स्मार्टग्रीव के लिए एक AI सहायक हैं, जो भारत सरकार की शिकायत प्रबंधन प्रणाली है।
आपकी भूमिका नागरिकों को शिकायत दर्ज करने, स्थिति जांचने और सार्वजनिक सेवाओं के बारे में जानकारी प्राप्त करने में मदद करना है।

दिशानिर्देश:
- विनम्र, पेशेवर और सहानुभूतिपूर्ण रहें
- स्पष्ट, संक्षिप्त उत्तर प्रदान करें
- आवश्यकता पड़ने पर स्पष्टीकरण के प्रश्न पूछें
- शिकायत दर्ज करने की प्रक्रिया में उपयोगकर्ताओं का मार्गदर्शन करें
- तात्कालिकता को पहचानें और महत्वपूर्ण मुद्दों को बढ़ाएं
- अंग्रेजी और हिंदी दोनों भाषाओं का समर्थन करें"""
        }
        return prompts.get(language, prompts["en"])
    
    def prepare_conversation_context(self, conversation_history: list) -> list:
        """Prepare conversation history for API call"""
        messages = []
        for entry in conversation_history[-10:]:  # Last 10 messages for context
            if entry.get('type') == 'user':
                messages.append({
                    "role": "user",
                    "content": entry.get('message', '')
                })
            elif entry.get('type') == 'bot':
                messages.append({
                    "role": "assistant",
                    "content": entry.get('reply', '')
                })
        return messages
    
    def stream_response(self, message: str, conversation_history: list = None, 
                       language: str = "en") -> Generator[str, None, None]:
        """Stream chatbot response token by token"""
        
        if not self.client:
            # Fallback to non-streaming response
            yield self._generate_fallback_response(message, language)
            return
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self.create_system_prompt(language)}
            ]
            
            # Add conversation history
            if conversation_history:
                messages.extend(self.prepare_conversation_context(conversation_history))
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Stream response from Groq
            stream = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # High-quality model for government use
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield self._generate_fallback_response(message, language)
    
    def _generate_fallback_response(self, message: str, language: str) -> str:
        """Generate fallback response when API is unavailable"""
        intent = detect_intent(message)
        
        responses = {
            "greeting": "Hello! I'm here to help you with your complaints and inquiries. How can I assist you today?",
            "complaint_filing": "I'll help you file a complaint. Could you please tell me what type of issue you're experiencing?",
            "complaint_status": "I can help you check your complaint status. Do you have your complaint ID?",
            "help": "I can assist you with filing complaints, checking status, or answering questions. What would you like to know?",
            "gratitude": "You're welcome! Is there anything else I can help you with?",
            "farewell": "Thank you for contacting us. Have a great day!",
        }
        
        response = responses.get(intent, "I understand. Could you please provide more details so I can better assist you?")
        
        # Translate if needed
        if language == "hi":
            from .utils import translate_text
            response = translate_text(response, "hi")
        
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stream_chat_message(request):
    """
    Streaming endpoint for chatbot messages
    Returns Server-Sent Events (SSE) for real-time streaming
    """
    try:
        # Extract request data
        message = request.data.get('message', '')
        session_id = request.data.get('session_id')
        preferred_language = request.data.get('preferred_language', 'en')
        
        if not message:
            return StreamingHttpResponse(
                _error_stream("Message is required"),
                content_type='text/event-stream'
            )
        
        # Get or create session
        session = _get_or_create_session(request.user, session_id, preferred_language)
        conversation_history = session.context.get('conversation_history', [])
        
        # Update context with user message
        conversation_history.append({
            'message': message,
            'timestamp': timezone.now().isoformat(),
            'type': 'user'
        })
        
        # Analyze message
        intent = detect_intent(message)
        sentiment = analyze_sentiment(message)
        urgency = analyze_complaint_urgency(message)
        category = extract_complaint_category(message)
        entities = extract_entities(message)
        input_language = detect_language(message)
        
        # Create streaming service
        streaming_service = StreamingChatbotService()
        
        # Generate streaming response
        def generate():
            full_response = ""
            
            # Send metadata first
            metadata = {
                'type': 'metadata',
                'session_id': str(session.session_id),
                'intent': intent,
                'sentiment': sentiment,
                'urgency': urgency,
                'category': category,
                'entities': entities,
                'language': input_language
            }
            yield f"data: {json.dumps(metadata)}\n\n"
            
            # Stream response tokens
            for token in streaming_service.stream_response(message, conversation_history, preferred_language):
                full_response += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
            
            # Send completion signal
            completion_data = {
                'type': 'complete',
                'full_response': full_response
            }
            yield f"data: {json.dumps(completion_data)}\n\n"
            
            # Save to database
            _save_chat_log(
                user=request.user,
                session=session,
                message=message,
                reply=full_response,
                intent=intent,
                sentiment=sentiment,
                urgency=urgency,
                category=category,
                entities=entities,
                input_language=input_language,
                reply_language=preferred_language
            )
            
            # Update session context
            conversation_history.append({
                'reply': full_response,
                'intent': intent,
                'sentiment': sentiment,
                'urgency': urgency,
                'category': category,
                'timestamp': timezone.now().isoformat(),
                'type': 'bot'
            })
            session.context['conversation_history'] = conversation_history[-10:]  # Keep last 10
            session.save()
        
        return StreamingHttpResponse(
            generate(),
            content_type='text/event-stream'
        )
        
    except Exception as e:
        logger.error(f"Stream chat error: {e}")
        return StreamingHttpResponse(
            _error_stream(str(e)),
            content_type='text/event-stream'
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quick_response(request):
    """
    Generate a complete response without streaming (for quick replies)
    """
    try:
        message = request.data.get('message', '')
        session_id = request.data.get('session_id')
        preferred_language = request.data.get('preferred_language', 'en')
        
        if not message:
            return Response({'error': 'Message is required'}, status=400)
        
        # Get or create session
        session = _get_or_create_session(request.user, session_id, preferred_language)
        conversation_history = session.context.get('conversation_history', [])
        
        # Analyze message
        intent = detect_intent(message)
        sentiment = analyze_sentiment(message)
        urgency = analyze_complaint_urgency(message)
        category = extract_complaint_category(message)
        entities = extract_entities(message)
        
        # Generate response
        streaming_service = StreamingChatbotService()
        full_response = "".join(streaming_service.stream_response(message, conversation_history, preferred_language))
        
        # Save to database
        chat_log = _save_chat_log(
            user=request.user,
            session=session,
            message=message,
            reply=full_response,
            intent=intent,
            sentiment=sentiment,
            urgency=urgency,
            category=category,
            entities=entities,
            input_language=detect_language(message),
            reply_language=preferred_language
        )
        
        # Update session context
        conversation_history.append({
            'message': message,
            'timestamp': timezone.now().isoformat(),
            'type': 'user'
        })
        conversation_history.append({
            'reply': full_response,
            'intent': intent,
            'sentiment': sentiment,
            'timestamp': timezone.now().isoformat(),
            'type': 'bot'
        })
        session.context['conversation_history'] = conversation_history[-10:]
        session.save()
        
        from rest_framework.response import Response
        return Response({
            'id': chat_log.id,
            'message': message,
            'reply': full_response,
            'intent': intent,
            'sentiment': sentiment,
            'urgency': urgency,
            'category': category,
            'entities': entities,
            'session_id': str(session.session_id),
            'timestamp': chat_log.timestamp.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Quick response error: {e}")
        from rest_framework.response import Response
        return Response({'error': str(e)}, status=500)


# Helper functions
def _get_or_create_session(user, session_id, preferred_language):
    """Get existing session or create new one"""
    if session_id:
        try:
            return ChatSession.objects.get(session_id=session_id, user=user)
        except ChatSession.DoesNotExist:
            pass
    
    return ChatSession.objects.create(
        user=user,
        session_id=uuid.uuid4(),
        context={
            'conversation_history': [],
            'user_preferences': {'language': preferred_language}
        }
    )


def _save_chat_log(user, session, message, reply, intent, sentiment, urgency, 
                   category, entities, input_language, reply_language):
    """Save chat log to database"""
    return ChatLog.objects.create(
        user=user,
        session=session,
        message=message,
        reply=reply,
        intent=intent,
        confidence=0.85,  # Default confidence for streaming responses
        input_language=input_language,
        reply_language=reply_language,
        reply_type='streaming',
        sentiment=sentiment,
        sentiment_score=0.8,
        escalated_to_human=urgency in ['high', 'critical']
    )


def _error_stream(error_message: str) -> Generator[str, None, None]:
    """Generate error event for SSE"""
    error_data = {
        'type': 'error',
        'message': error_message
    }
    yield f"data: {json.dumps(error_data)}\n\n"
