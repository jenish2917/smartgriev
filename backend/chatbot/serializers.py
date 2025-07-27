from rest_framework import serializers
from .models import ChatLog, ChatFeedback, QuickReplyTemplate, ChatSession, ChatNotification
from django.contrib.auth import get_user_model

User = get_user_model()

class QuickReplyTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickReplyTemplate
        fields = ('id', 'name', 'intent', 'buttons')

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ('id', 'session_id', 'created_at', 'is_active', 'context')
        read_only_fields = ('session_id', 'created_at')

class ChatMessageSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(required=False)
    preferred_language = serializers.CharField(max_length=2, required=False, default='en')
    quick_replies = QuickReplyTemplateSerializer(read_only=True, many=True)
    
    class Meta:
        model = ChatLog
        fields = ('id', 'message', 'reply', 'timestamp', 'intent', 'confidence', 
                 'input_language', 'reply_language', 'reply_type', 'reply_metadata',
                 'sentiment', 'sentiment_score', 'session_id', 'preferred_language', 
                 'quick_replies', 'escalated_to_human')
        read_only_fields = ('reply', 'timestamp', 'intent', 'confidence', 
                          'input_language', 'reply_language', 'reply_type', 
                          'reply_metadata', 'sentiment', 'sentiment_score',
                          'escalated_to_human')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        session_id = validated_data.pop('session_id', None)
        preferred_language = validated_data.pop('preferred_language', 'en')
        
        # Handle session management
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id, user=validated_data['user'])
                validated_data['session'] = session
            except ChatSession.DoesNotExist:
                pass
        
        validated_data['input_language'] = preferred_language
        validated_data['reply_language'] = preferred_language
        
        return super().create(validated_data)

class ChatHistorySerializer(serializers.ModelSerializer):
    feedback = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatLog
        fields = ('id', 'message', 'reply', 'timestamp', 'intent', 'confidence',
                 'input_language', 'reply_language', 'reply_type', 'reply_metadata',
                 'sentiment', 'sentiment_score', 'escalated_to_human', 'feedback')
    
    def get_feedback(self, obj):
        try:
            feedback = obj.feedback
            return {
                'rating': feedback.rating,
                'is_helpful': feedback.is_helpful,
                'comments': feedback.comments
            }
        except ChatFeedback.DoesNotExist:
            return None

class ChatFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatFeedback
        fields = ('id', 'chat_log', 'rating', 'is_helpful', 'comments', 'timestamp')
        read_only_fields = ('timestamp',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ChatNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatNotification
        fields = ('id', 'notification_type', 'title', 'message', 'scheduled_at', 
                 'sent_at', 'is_sent', 'metadata')
        read_only_fields = ('sent_at', 'is_sent')
