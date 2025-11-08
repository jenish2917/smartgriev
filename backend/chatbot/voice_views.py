"""
CivicAI Voice Complaint API Views
RESTful endpoints for voice-based complaint submission
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
import logging

from .civicai_voice_assistant import civic_ai
from complaints.models import Complaint
from complaints.serializers import ComplaintSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def voice_complaint_submit(request):
    """
    Submit complaint via voice with automatic language detection and processing
    
    Expected payload:
    {
        "transcribed_text": "મારા એરિયા માં પાણી નથી આવતું છેલ્લા 2 દિવસ થી.",
        "audio_url": "https://...",  // Optional
        "caller_id": "user_phone_number"  // Optional
    }
    
    Returns:
    {
        "success": true,
        "summary_text": "No water supply in area for 2 days",
        "original_language": "gu",
        "reply_text": "હું તમારી ફરિયાદ પાણી વિભાગ માં મોકલી રહ્યો છું...",
        "department_tag": "water",
        "confidence_score": 0.85,
        "complaint_id": 123,
        "tracking_number": "COMP-000123"
    }
    """
    try:
        # Get request data
        transcribed_text = request.data.get('transcribed_text', '').strip()
        audio_url = request.data.get('audio_url')
        caller_id = request.data.get('caller_id')
        
        if not transcribed_text:
            return Response({
                'success': False,
                'error': 'Transcribed text is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process with CivicAI
        ai_response = civic_ai.process_voice_complaint(
            audio_url=audio_url,
            transcribed_text=transcribed_text,
            caller_id=caller_id
        )
        
        if not ai_response.get('success'):
            return Response(ai_response, status=status.HTTP_400_BAD_REQUEST)
        
        # Create complaint in database
        complaint_data = {
            'title': f"{ai_response['department_name']} Issue - Voice Call",
            'description': ai_response['summary_text'],
            'priority': 'medium',
            'urgency_level': 'medium',
            'category': ai_response['department_name'],
            # Store original voice data
            'ai_processed_text': transcribed_text,
            'department_classification': ai_response['department_tag'],
            'ai_confidence_score': ai_response['confidence_score'],
        }
        
        # Create complaint
        serializer = ComplaintSerializer(data=complaint_data)
        if serializer.is_valid():
            complaint = serializer.save()
            
            # Add complaint info to response
            ai_response['complaint_id'] = complaint.id
            ai_response['tracking_number'] = f"COMP-{complaint.id:06d}"
            ai_response['status'] = complaint.status
            
            logger.info(f"Voice complaint created: {complaint.id} ({ai_response['department_tag']})")
            
            return Response(ai_response, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Complaint creation failed: {serializer.errors}")
            ai_response['warning'] = 'AI processed successfully but complaint not saved'
            ai_response['db_errors'] = serializer.errors
            return Response(ai_response, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Voice complaint submission failed: {str(e)}")
        return Response({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def voice_chat(request):
    """
    Interactive voice chat endpoint for guided complaint submission
    
    Provides natural conversation flow with language detection and responses
    """
    try:
        user_message = request.data.get('message', '').strip()
        session_state = request.data.get('session_state', 'greeting')
        
        if not user_message:
            return Response({
                'success': False,
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Detect language
        language = civic_ai.detect_language(user_message)
        
        # Generate response based on session state
        if session_state == 'greeting':
            reply = civic_ai.GREETINGS.get(language, civic_ai.GREETINGS['en'])
            next_state = 'collecting_complaint'
            
        elif session_state == 'collecting_complaint':
            # Process the complaint
            ai_response = civic_ai.process_voice_complaint(
                transcribed_text=user_message
            )
            reply = ai_response.get('reply_text', 'Thank you for your complaint.')
            next_state = 'completed'
            
        else:
            reply = "Thank you. Your complaint has been recorded."
            next_state = 'completed'
        
        return Response({
            'success': True,
            'reply': reply,
            'language': language,
            'language_name': civic_ai.SUPPORTED_LANGUAGES.get(language, 'Unknown'),
            'next_state': next_state
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Voice chat failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def voice_languages(request):
    """
    Get list of supported languages
    """
    return Response({
        'success': True,
        'supported_languages': [
            {'code': code, 'name': name}
            for code, name in civic_ai.SUPPORTED_LANGUAGES.items()
        ],
        'departments': [
            {'code': code, 'name': name}
            for code, name in civic_ai.DEPARTMENTS.items()
        ]
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def voice_health(request):
    """
    Health check for voice assistant service
    """
    return Response({
        'success': True,
        'status': 'healthy',
        'service': 'CivicAI Voice Assistant',
        'version': '1.0.0',
        'supported_languages': len(civic_ai.SUPPORTED_LANGUAGES),
        'supported_departments': len(civic_ai.DEPARTMENTS)
    }, status=status.HTTP_200_OK)
