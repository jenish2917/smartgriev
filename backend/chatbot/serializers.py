from rest_framework import serializers
from .models import ChatLog, ChatFeedback, QuickReplyTemplate, ChatSession, ChatNotification, QuickReplyButton

class QuickReplyButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickReplyButton
        fields = ('text', 'action')

class QuickReplyTemplateSerializer(serializers.ModelSerializer):
    buttons = QuickReplyButtonSerializer(many=True, read_only=True)

    class Meta:
        model = QuickReplyTemplate
        fields = ('id', 'name', 'intent', 'buttons')

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ('id', 'session_id', 'created_at', 'is_active', 'context')
        read_only_fields = ('session_id', 'created_at')

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatLog
        fields = ('id', 'message', 'reply', 'timestamp', 'intent', 'confidence', 
                 'input_language', 'reply_language', 'reply_type', 
                 'sentiment', 'sentiment_score', 'escalated_to_human')
        read_only_fields = ('reply', 'timestamp', 'intent', 'confidence', 
                          'input_language', 'reply_language', 'reply_type', 
                          'sentiment', 'sentiment_score',
                          'escalated_to_human')

class ChatHistorySerializer(serializers.ModelSerializer):
    feedback = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatLog
        fields = ('id', 'message', 'reply', 'timestamp', 'intent', 'confidence',
                 'input_language', 'reply_language', 'reply_type',
                 'sentiment', 'sentiment_score', 'escalated_to_human', 'feedback')
    
    def get_feedback(self, obj):
        if hasattr(obj, 'feedback'):
            return {
                'rating': obj.feedback.rating,
                'is_helpful': obj.feedback.is_helpful,
                'comments': obj.feedback.comments
            }
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
                 'sent_at', 'is_sent')
        read_only_fields = ('sent_at', 'is_sent')