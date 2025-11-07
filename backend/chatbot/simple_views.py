"""
Simple ChatGPT-like chatbot views using Google AI
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .google_ai_chat import get_chatbot_response

@api_view(['POST'])
@permission_classes([AllowAny])  # Public access like ChatGPT
def simple_chat(request):
    """
    Simple chat endpoint - works like ChatGPT
    
    POST /api/chatbot/chat/
    {
        "message": "Hello, how can I file a complaint?",
        "conversation_history": [...]  // Optional
    }
    
    Returns:
    {
        "response": "Hello! To file a complaint...",
        "success": true
    }
    """
    message = request.data.get('message', '').strip()
    
    if not message:
        return Response({
            'success': False,
            'error': 'Message is required',
            'response': 'Please provide a message.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get conversation history if provided
    conversation_history = request.data.get('conversation_history', [])
    
    # Get AI response
    result = get_chatbot_response(message, conversation_history)
    
    if result['success']:
        return Response({
            'response': result['response'],
            'success': True,
            'model': result.get('model', 'gemini-2.5-flash')
        })
    else:
        return Response({
            'response': result['response'],
            'success': False,
            'error': result.get('error', 'Unknown error')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def chat_health(request):
    """Check if chatbot is working"""
    try:
        import os
        from django.conf import settings
        
        api_key = os.getenv('GOOGLE_AI_API_KEY', getattr(settings, 'GOOGLE_AI_API_KEY', None))
        
        return Response({
            'status': 'healthy',
            'api_configured': bool(api_key),
            'message': 'Chatbot is ready!' if api_key else 'API key not configured'
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
