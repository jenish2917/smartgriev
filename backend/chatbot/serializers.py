from rest_framework import serializers
from .models import ChatLog
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatLog
        fields = ('id', 'message', 'reply', 'timestamp', 'intent', 'confidence')
        read_only_fields = ('reply', 'timestamp', 'intent', 'confidence')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatLog
        fields = ('id', 'message', 'reply', 'timestamp', 'intent', 'confidence')
