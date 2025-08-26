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
from .utils import get_sentiment_analyzer, get_nlp_model, translate_text, detect_language, process_message_with_context, get_quick_replies_for_intent, should_escalate, get_escalation_message

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

        intent, confidence, reply = process_message_with_context(message, context, user)
        sentiment_result = self._get_sentiment(message)
        quick_replies = get_quick_replies_for_intent(intent)

        if preferred_language != 'en':
            reply = translate_text(reply, preferred_language)

        reply_type, reply_metadata, escalated = self._determine_reply_type(quick_replies, session, context, message, intent, confidence, preferred_language)

        self._update_bot_response_in_context(session, reply, intent)
        
        serializer.save(
            user=user,
            session=session,
            reply=reply,
            intent=intent,
            confidence=confidence,
            input_language=detect_language(message),
            reply_language=preferred_language,
            reply_type=reply_type,
            sentiment=sentiment_result.get('label') if sentiment_result else None,
            sentiment_score=sentiment_result.get('score') if sentiment_result else None,
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

    def _determine_reply_type(self, quick_replies, session, context, message, intent, confidence, preferred_language):
        reply_type = 'quick_reply' if quick_replies else 'text'
        reply_metadata = {
            'quick_replies': quick_replies,
            'session_id': str(session.session_id),
            'context_used': bool(context['conversation_history'])
        }
        escalated = should_escalate(message, intent, confidence)
        if escalated:
            reply = get_escalation_message(preferred_language)
            reply_type = 'escalation'
            reply_metadata['escalation_reason'] = 'Low confidence or complex query'
        return reply_type, reply_metadata, escalated

    def _update_bot_response_in_context(self, session, reply, intent):
        context = session.context
        context['conversation_history'].append({
            'reply': reply,
            'intent': intent,
            'timestamp': timezone.now().isoformat(),
            'type': 'bot'
        })
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
