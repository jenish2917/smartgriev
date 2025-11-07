from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, Count, Avg, Prefetch
from django.utils import timezone
import uuid
from .models import ChatLog, ChatFeedback, QuickReplyTemplate, ChatSession, ChatNotification
from .serializers import (
    ChatMessageSerializer, ChatHistorySerializer, ChatFeedbackSerializer,
    QuickReplyTemplateSerializer, ChatSessionSerializer, ChatNotificationSerializer
)
from .utils import (
    get_sentiment_analyzer, get_nlp_model, translate_text, detect_language, 
    process_message_with_context, get_quick_replies_for_intent, should_escalate, 
    get_escalation_message, manage_conversation_flow, analyze_sentiment,
    extract_entities, detect_intent, analyze_complaint_urgency, extract_complaint_category
)

class ChatSessionView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = self.request.user
        message = serializer.validated_data['message']
        session_id = self.request.data.get('session_id')
        preferred_language = self.request.data.get('preferred_language', 'en')

        session = self._get_or_create_session(user, session_id, preferred_language)
        context = self._update_session_context(session, message)

        # Use enhanced conversation flow management
        conversation_data = manage_conversation_flow(
            message, 
            context.get('conversation_history', []),
            {'user': user, 'language': preferred_language}
        )

        # Extract enhanced data
        intent = conversation_data['intent']
        sentiment = conversation_data['sentiment']
        urgency = conversation_data['urgency']
        category = conversation_data['category']
        entities = conversation_data['entities']
        quick_replies = conversation_data['quick_replies']
        needs_escalation = conversation_data['needs_escalation']
        reply = conversation_data['message']

        # Set confidence based on intent detection
        confidence = 0.9 if intent != 'unknown' else 0.3

        # Apply language translation if needed
        if preferred_language != 'en':
            reply = translate_text(reply, preferred_language)

        # Determine reply type and metadata
        reply_type, reply_metadata, escalated = self._determine_reply_type_enhanced(
            quick_replies, session, context, message, intent, confidence, 
            preferred_language, needs_escalation, urgency, category
        )

        # Update session context with enhanced data
        self._update_bot_response_in_context_enhanced(
            session, reply, intent, sentiment, urgency, category, entities
        )
        
        serializer.save(
            user=user,
            session=session,
            reply=reply,
            intent=intent,
            confidence=confidence,
            input_language=detect_language(message),
            reply_language=preferred_language,
            reply_type=reply_type,
            sentiment=sentiment,
            sentiment_score=confidence,  # Use confidence as sentiment score
            escalated_to_human=escalated
        )

    def _get_or_create_session(self, user, session_id, preferred_language):
        if session_id:
            try:
                return ChatSession.objects.get(session_id=session_id, user=user)
            except ChatSession.DoesNotExist:
                pass
        return ChatSession.objects.create(
            user=user,
            session_id=uuid.uuid4(),
            context={'conversation_history': [], 'user_preferences': {'language': preferred_language}}
        )

    def _update_session_context(self, session, message):
        context = session.context
        context['conversation_history'] = context.get('conversation_history', [])[-5:]
        context['conversation_history'].append({
            'message': message,
            'timestamp': timezone.now().isoformat(),
            'type': 'user'
        })
        return context

    def _get_sentiment(self, message):
        sentiment_analyzer = get_sentiment_analyzer()
        if sentiment_analyzer:
            try:
                return sentiment_analyzer(message)[0]
            except Exception:
                pass
        return None

    def _determine_reply_type_enhanced(self, quick_replies, session, context, message, intent, confidence, preferred_language, needs_escalation, urgency, category):
        """Enhanced reply type determination with urgency and escalation logic"""
        reply_type = 'quick_reply' if quick_replies else 'text'
        reply_metadata = {
            'quick_replies': quick_replies,
            'session_id': str(session.session_id),
            'context_used': bool(context['conversation_history']),
            'urgency': urgency,
            'category': category,
            'intent': intent
        }
        
        escalated = False
        
        # Enhanced escalation logic
        if needs_escalation or urgency in ['high', 'critical'] or confidence < 0.5:
            escalated = True
            reply_type = 'escalation'
            reply_metadata['escalation_reason'] = self._get_escalation_reason(needs_escalation, urgency, confidence)
            
            # Get escalation message in preferred language
            escalation_message = get_escalation_message(preferred_language)
            reply_metadata['escalation_message'] = escalation_message
        
        return reply_type, reply_metadata, escalated

    def _get_escalation_reason(self, needs_escalation, urgency, confidence):
        """Determine specific escalation reason"""
        reasons = []
        if needs_escalation:
            reasons.append('negative_sentiment')
        if urgency in ['high', 'critical']:
            reasons.append(f'{urgency}_urgency')
        if confidence < 0.5:
            reasons.append('low_confidence')
        return ', '.join(reasons)

    def _update_bot_response_in_context_enhanced(self, session, reply, intent, sentiment, urgency, category, entities):
        """Enhanced context update with additional metadata"""
        context = session.context
        context['conversation_history'].append({
            'reply': reply,
            'intent': intent,
            'sentiment': sentiment,
            'urgency': urgency,
            'category': category,
            'entities': entities,
            'timestamp': timezone.now().isoformat(),
            'type': 'bot'
        })
        
        # Update session metadata
        context['last_intent'] = intent
        context['last_category'] = category
        context['last_urgency'] = urgency
        
        session.context = context
        session.save()

class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ChatLog.objects.filter(user=self.request.user).prefetch_related(
            Prefetch('feedback', queryset=ChatFeedback.objects.all(), to_attr='feedback')
        ).order_by('-timestamp')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(message__icontains=search) | Q(reply__icontains=search)
            )
        intent = self.request.query_params.get('intent')
        if intent:
            queryset = queryset.filter(intent=intent)
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
    user = request.user
    total_chats = ChatLog.objects.filter(user=user).count()
    intent_stats = ChatLog.objects.filter(user=user).values('intent').annotate(
        count=Count('intent')
    ).order_by('-count')
    avg_confidence = ChatLog.objects.filter(user=user).aggregate(
        avg_confidence=Avg('confidence')
    )['avg_confidence']
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
