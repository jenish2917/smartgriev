from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db import models
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.conf import settings
import uuid
import json
import re

from .models import ChatLog, ChatFeedback, QuickReplyTemplate, ChatSession, ChatNotification
from .serializers import (
    ChatMessageSerializer, ChatHistorySerializer, ChatFeedbackSerializer,
    QuickReplyTemplateSerializer, ChatSessionSerializer, ChatNotificationSerializer
)

# Import for ML/NLP processing (lazy loading to avoid import errors)
def get_sentiment_analyzer():
    """Lazy loading of sentiment analyzer"""
    try:
        from transformers import pipeline
        return pipeline('sentiment-analysis')
    except ImportError:
        return None

def get_nlp_model():
    """Lazy loading of spacy model"""
    try:
        import spacy
        return spacy.load('en_core_web_sm')
    except (ImportError, OSError):
        return None

# Translation support (mock implementation - replace with actual translation service)
def translate_text(text, target_language):
    """Mock translation function - replace with actual translation API"""
    # For demo purposes, return original text with language indicator
    if target_language != 'en':
        return f"[{target_language.upper()}] {text}"
    return text

def detect_language(text):
    """Mock language detection - replace with actual language detection"""
    # Simple heuristic for demo
    if any(char in text for char in 'हिंदी'):
        return 'hi'
    return 'en'

class ChatSessionView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Create new chat session
        session = ChatSession.objects.create(
            user=request.user,
            session_id=uuid.uuid4(),
            context={'user_preferences': {}, 'conversation_history': []}
        )
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_object(self):
        session_id = self.kwargs.get('session_id')
        return ChatSession.objects.get(session_id=session_id, user=self.request.user)

class ChatMessageView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        message = serializer.validated_data['message']
        
        # Language detection
        detected_language = detect_language(message)
        preferred_language = serializer.validated_data.get('preferred_language', 'en')
        
        # Get or create session
        session = None
        session_id = serializer.validated_data.get('session_id')
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id, user=user)
            except ChatSession.DoesNotExist:
                pass
        
        if not session:
            session = ChatSession.objects.create(
                user=user,
                session_id=uuid.uuid4(),
                context={'conversation_history': [], 'user_preferences': {'language': preferred_language}}
            )
        
        # Update session context
        context = session.context
        context['conversation_history'] = context.get('conversation_history', [])[-5:]  # Keep last 5 messages
        context['conversation_history'].append({
            'message': message,
            'timestamp': timezone.now().isoformat(),
            'type': 'user'
        })
        
        # Enhanced intent recognition with context
        intent, confidence, reply = self.process_message_with_context(message, context, user)
        
        # Sentiment analysis
        sentiment_result = None
        sentiment_analyzer = get_sentiment_analyzer()
        if sentiment_analyzer:
            try:
                sentiment_result = sentiment_analyzer(message)[0]
            except Exception:
                pass
        
        # Generate quick replies based on intent
        quick_replies = self.get_quick_replies_for_intent(intent)
        
        # Translate reply if needed
        if preferred_language != 'en':
            reply = translate_text(reply, preferred_language)
        
        # Determine reply type
        reply_type = 'quick_reply' if quick_replies else 'text'
        reply_metadata = {
            'quick_replies': quick_replies,
            'session_id': str(session.session_id),
            'context_used': bool(context['conversation_history'])
        }
        
        # Check if escalation is needed
        escalated = self.should_escalate(message, intent, confidence)
        if escalated:
            reply = self.get_escalation_message(preferred_language)
            reply_type = 'escalation'
            reply_metadata['escalation_reason'] = 'Low confidence or complex query'
        
        # Update context with bot reply
        context['conversation_history'].append({
            'reply': reply,
            'intent': intent,
            'timestamp': timezone.now().isoformat(),
            'type': 'bot'
        })
        session.context = context
        session.save()
        
        # Save chat log
        serializer.save(
            user=user,
            session=session,
            reply=reply,
            intent=intent,
            confidence=confidence,
            input_language=detected_language,
            reply_language=preferred_language,
            reply_type=reply_type,
            reply_metadata=reply_metadata,
            sentiment=sentiment_result['label'] if sentiment_result else None,
            sentiment_score=sentiment_result['score'] if sentiment_result else None,
            escalated_to_human=escalated
        )

    def process_message_with_context(self, message, context, user):
        """Enhanced message processing with context awareness"""
        message_lower = message.lower()
        conversation_history = context.get('conversation_history', [])
        
        # Personalized greeting
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return 'greeting', 0.9, f"Hello {user.first_name or user.username}! How can I assist you with your grievances today?"
        
        # Context-aware responses
        recent_intents = [msg.get('intent') for msg in conversation_history[-3:] if msg.get('type') == 'bot']
        
        # Complaint filing
        if any(word in message_lower for word in ['file', 'submit', 'register', 'complaint', 'grievance']):
            if 'complaint_filing' in recent_intents:
                return 'complaint_filing_followup', 0.8, "I see you're continuing with filing a complaint. Do you need help with uploading documents or selecting the right department?"
            return 'complaint_filing', 0.8, "I'll help you file a complaint. Please provide: 1) Issue description, 2) Location, 3) Category. Would you like me to guide you step by step?"
        
        # Status checking
        elif any(word in message_lower for word in ['status', 'track', 'progress', 'update']):
            return 'complaint_status', 0.8, "To check your complaint status, I can help you find your complaint ID. Do you remember when you filed it or the complaint number?"
        
        # Department information
        elif any(word in message_lower for word in ['department', 'office', 'contact', 'who', 'where']):
            return 'department_info', 0.7, "I can help you find the right department. What type of issue are you facing? (e.g., water, electricity, roads, sanitation)"
        
        # Help and FAQ
        elif any(word in message_lower for word in ['help', 'how', 'what', 'guide']):
            return 'help', 0.7, "I'm here to help! You can: 📝 File new complaints, 📊 Check complaint status, 🏢 Find departments, 📞 Get contact information. What would you like to do?"
        
        # Thank you
        elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return 'gratitude', 0.9, "You're welcome! Is there anything else I can help you with today?"
        
        # Default response with context
        else:
            if len(conversation_history) > 0:
                return 'general_contextual', 0.5, "I understand you're continuing our conversation. Could you please be more specific about what you need help with regarding your grievance?"
            return 'general', 0.5, "I'm here to help you with filing complaints, checking status, and finding the right department. What would you like to know?"

    def get_quick_replies_for_intent(self, intent):
        """Generate quick reply buttons based on intent"""
        quick_replies_map = {
            'greeting': [
                {'text': '📝 File Complaint', 'action': 'file_complaint'},
                {'text': '📊 Check Status', 'action': 'check_status'},
                {'text': '❓ Get Help', 'action': 'get_help'}
            ],
            'complaint_filing': [
                {'text': '🏠 Housing Issue', 'action': 'category_housing'},
                {'text': '🚰 Water Problem', 'action': 'category_water'},
                {'text': '⚡ Electricity', 'action': 'category_electricity'},
                {'text': '🛣️ Road Issue', 'action': 'category_road'}
            ],
            'complaint_status': [
                {'text': '🔢 Enter Complaint ID', 'action': 'enter_id'},
                {'text': '📅 Search by Date', 'action': 'search_date'},
                {'text': '📱 Recent Complaints', 'action': 'recent_complaints'}
            ],
            'department_info': [
                {'text': '🏢 Municipal Office', 'action': 'dept_municipal'},
                {'text': '💧 Water Department', 'action': 'dept_water'},
                {'text': '⚡ Electricity Board', 'action': 'dept_electricity'}
            ],
            'help': [
                {'text': '📋 Filing Guide', 'action': 'guide_filing'},
                {'text': '📞 Contact Support', 'action': 'contact_support'},
                {'text': '❓ FAQ', 'action': 'faq'}
            ]
        }
        return quick_replies_map.get(intent, [])

    def should_escalate(self, message, intent, confidence):
        """Determine if the query should be escalated to human agent"""
        # Escalate if confidence is very low
        if confidence < 0.3:
            return True
        
        # Escalate for complex legal or urgent issues
        escalation_keywords = ['legal', 'lawyer', 'court', 'urgent', 'emergency', 'complaint against officer']
        if any(keyword in message.lower() for keyword in escalation_keywords):
            return True
        
        return False

    def get_escalation_message(self, language):
        """Get escalation message in appropriate language"""
        message = "I understand this is a complex issue. Let me connect you with a human support agent who can better assist you. Please hold on."
        return translate_text(message, language)

class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ChatLog.objects.filter(user=self.request.user).order_by('-timestamp')
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(message__icontains=search) | Q(reply__icontains=search)
            )
        
        # Filter by intent
        intent = self.request.query_params.get('intent')
        if intent:
            queryset = queryset.filter(intent=intent)
        
        # Filter by date range
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        if from_date:
            queryset = queryset.filter(timestamp__gte=from_date)
        if to_date:
            queryset = queryset.filter(timestamp__lte=to_date)
            
        return queryset

class ChatFeedbackView(generics.CreateAPIView):
    serializer_class = ChatFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_stats(request):
    """Get chat statistics for the user"""
    user = request.user
    total_chats = ChatLog.objects.filter(user=user).count()
    
    # Intent distribution
    intent_stats = ChatLog.objects.filter(user=user).values('intent').annotate(
        count=Count('intent')
    ).order_by('-count')
    
    # Average confidence
    avg_confidence = ChatLog.objects.filter(user=user).aggregate(
        avg_confidence=Avg('confidence')
    )['avg_confidence']
    
    # Feedback stats
    feedback_stats = ChatFeedback.objects.filter(user=user).aggregate(
        avg_rating=Avg('rating'),
        helpful_count=Count('id', filter=Q(is_helpful=True)),
        total_feedback=Count('id')
    )
    
    return Response({
        'total_chats': total_chats,
        'intent_distribution': list(intent_stats),
        'average_confidence': avg_confidence,
        'feedback_stats': feedback_stats,
        'escalation_rate': ChatLog.objects.filter(user=user, escalated_to_human=True).count() / max(total_chats, 1) * 100
    })

class ChatNotificationView(generics.ListCreateAPIView):
    serializer_class = ChatNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatNotification.objects.filter(user=self.request.user).order_by('-scheduled_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
