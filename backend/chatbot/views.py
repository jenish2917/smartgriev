from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatLog
from .serializers import ChatMessageSerializer, ChatHistorySerializer
from transformers import pipeline
import spacy

# Load NLP models
sentiment_analyzer = pipeline('sentiment-analysis')
nlp = spacy.load('en_core_web_sm')

class ChatMessageView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Process the user message
        message = serializer.validated_data['message']
        
        # Basic intent recognition
        doc = nlp(message.lower())
        intent = 'general'
        confidence = 0.5

        if any(word.text in ['file', 'submit', 'register'] for word in doc):
            intent = 'complaint_filing'
            reply = "To file a complaint, please provide details about the issue, location, and any relevant media."
            confidence = 0.8
        elif any(word.text in ['status', 'track', 'progress'] for word in doc):
            intent = 'complaint_status'
            reply = "You can check your complaint status in the complaints section. Would you like me to help you find a specific complaint?"
            confidence = 0.8
        elif any(word.text in ['department', 'office', 'contact'] for word in doc):
            intent = 'department_info'
            reply = "I can help you find the right department for your complaint. What type of issue are you facing?"
            confidence = 0.7
        else:
            reply = "I'm here to help you with filing complaints, checking status, and finding the right department. What would you like to know?"

        # Get sentiment
        sentiment = sentiment_analyzer(message)[0]
        
        # Save chat log with all metadata
        serializer.save(
            user=self.request.user,
            reply=reply,
            intent=intent,
            confidence=confidence
        )

class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatLog.objects.filter(user=self.request.user).order_by('-timestamp')
