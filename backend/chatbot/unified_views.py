"""
Unified chatbot views for frontend integration
Provides /chat/, /voice/, /vision/ endpoints with location support
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
import uuid
import os
from .gemini_service import gemini_chatbot
from .civicai_voice_assistant import civic_ai
from .models import ChatSession, ChatLog
from complaints.ai_processor import AdvancedAIProcessor

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow guests to chat
def unified_chat(request):
    """
    Unified chat endpoint with location support
    
    POST data:
    - message: User message (required)
    - language: User's preferred language (default: 'en')
    - latitude: Optional GPS latitude
    - longitude: Optional GPS longitude
    - session_id: Optional session ID for context
    
    Returns:
    - response: AI response
    - session_id: Session identifier
    - intent: Detected intent
    - complaint_data: Extracted complaint data if applicable
    """
    
    message = request.data.get('message', '').strip()
    language = request.data.get('language', 'en')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    session_id = request.data.get('session_id')
    
    if not message:
        return Response({
            'error': 'Message is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Add location context to message if provided
    location_context = ""
    if latitude and longitude:
        try:
            lat = float(latitude)
            lng = float(longitude)
            location_context = f"\n[User Location: Latitude {lat}, Longitude {lng}]"
        except (ValueError, TypeError):
            logger.warning(f"Invalid location data: lat={latitude}, lng={longitude}")
    
    try:
        # Check if Gemini chatbot is available
        if gemini_chatbot is None:
            logger.error("Gemini chatbot not initialized")
            return Response({
                'error': 'AI service temporarily unavailable. Please try again later.',
                'session_id': session_id
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Initialize conversation if this is a new session
        if session_id not in gemini_chatbot.conversations:
            logger.info(f"Starting new conversation for session: {session_id}")
            gemini_chatbot.start_conversation(session_id, language)
        
        # Get response from Gemini with location context
        enhanced_message = message + location_context if location_context else message
        
        logger.info(f"Processing message in language: {language}, session: {session_id}")
        logger.info(f"Enhanced message: {enhanced_message[:100]}...")
        
        result = gemini_chatbot.chat(
            session_id=session_id,
            user_message=enhanced_message,
            user_language=language
        )
        
        logger.info(f"Gemini response: {result.get('response', '')[:100]}...")
        logger.info(f"Intent: {result.get('intent')}, Complete: {result.get('conversation_complete')}")
        logger.info(f"Complaint data: {result.get('complaint_data')}")
        
        # Save chat log if user is authenticated
        if request.user.is_authenticated:
            try:
                # Get or create chat session
                chat_session, created = ChatSession.objects.get_or_create(
                    user=request.user,
                    session_id=session_id,
                    defaults={'is_active': True}
                )
                
                # Save chat log with location
                chat_log = ChatLog.objects.create(
                    user=request.user,
                    session=chat_session,
                    message=message,
                    reply=result['response'],
                    intent=result.get('intent', 'unknown'),
                    input_language=language,
                    reply_language=language
                )
                
                # Store location if provided
                if latitude and longitude:
                    chat_log.location_latitude = float(latitude)
                    chat_log.location_longitude = float(longitude)
                    chat_log.save()
                    
            except Exception as e:
                logger.error(f"Error saving chat log: {e}")
        
        return Response({
            'session_id': session_id,
            'response': result['response'],
            'intent': result.get('intent', 'unknown'),
            'complaint_data': result.get('complaint_data'),
            'conversation_complete': result.get('conversation_complete', False),
            'auto_submit': result.get('auto_submit', False),  # CRITICAL: Pass auto_submit flag to frontend
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return Response({
            'error': f'Chat processing failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def unified_voice(request):
    """
    Unified voice endpoint for audio transcription and processing
    
    POST data (multipart/form-data):
    - audio: Audio file (required)
    - language: Language code (default: 'en')
    - latitude: Optional GPS latitude
    - longitude: Optional GPS longitude
    
    Returns:
    - response: AI response
    - transcription: Transcribed text
    - language: Detected language
    """
    
    audio_file = request.FILES.get('audio')
    language = request.data.get('language', 'en')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if not audio_file:
        return Response({
            'error': 'Audio file is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Save audio file temporarily
        file_name = f"voice_{uuid.uuid4()}{os.path.splitext(audio_file.name)[1]}"
        file_path = default_storage.save(f'temp/{file_name}', ContentFile(audio_file.read()))
        audio_url = default_storage.url(file_path)
        
        # Process with CivicAI voice assistant
        ai_response = civic_ai.process_voice_complaint(
            audio_url=audio_url,
            transcribed_text=None,  # Let CivicAI transcribe
            caller_id=request.user.username if request.user.is_authenticated else None
        )
        
        # Clean up temp file
        try:
            default_storage.delete(file_path)
        except Exception as e:
            logger.warning(f"Failed to delete temp file {file_path}: {e}")
        
        if not ai_response.get('success'):
            return Response({
                'error': ai_response.get('error', 'Voice processing failed')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add location context if provided
        location_info = ""
        if latitude and longitude:
            location_info = f" Location: ({latitude}, {longitude})"
        
        return Response({
            'response': ai_response['reply_text'] + location_info,
            'transcription': ai_response.get('transcribed_text', ai_response.get('summary_text', '')),
            'language': ai_response.get('original_language', language),
            'confidence': ai_response.get('confidence_score', 0),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        return Response({
            'error': f'Voice processing failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def unified_vision(request):
    """
    Unified vision endpoint for image analysis
    
    POST data (multipart/form-data):
    - image: Image file (required)
    - message: Optional text message to accompany image
    - language: User's preferred language (default: 'en')
    - latitude: Optional GPS latitude
    - longitude: Optional GPS longitude
    
    Returns:
    - response: AI response about the image
    - description: Image description
    - complaint_detected: Whether a complaint was detected
    """
    
    image_file = request.FILES.get('image')
    message = request.data.get('message', '')
    language = request.data.get('language', 'en')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if not image_file:
        return Response({
            'error': 'Image file is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Save image temporarily
        file_name = f"image_{uuid.uuid4()}{os.path.splitext(image_file.name)[1]}"
        file_path = default_storage.save(f'temp/{file_name}', ContentFile(image_file.read()))
        full_path = default_storage.path(file_path)
        
        # Use Gemini vision model for image analysis with language support
        try:
            import google.generativeai as genai
            from PIL import Image
            
            # Load image
            img = Image.open(full_path)
            
            # Get language name
            language_names = {
                'en': 'English', 'hi': 'Hindi', 'gu': 'Gujarati', 
                'bn': 'Bengali', 'te': 'Telugu', 'mr': 'Marathi',
                'ta': 'Tamil', 'kn': 'Kannada', 'ml': 'Malayalam',
                'pa': 'Punjabi', 'ur': 'Urdu', 'as': 'Assamese', 'or': 'Odia'
            }
            language_name = language_names.get(language, 'English')
            
            # Create vision model
            vision_model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Build prompt with language instruction
            vision_prompt = f"""Analyze this image for civic issues or complaints.

Describe what you see in the image. If it shows any civic problem (pothole, garbage, broken infrastructure, etc.), identify it clearly.

**IMPORTANT**: You MUST respond in {language_name} only. Do not use any other language.

User's message: {message if message else 'Please analyze this image for any civic issues.'}

Provide:
1. Brief description of what's in the image
2. Any civic issues/problems you detect
3. Urgency level if there's a problem"""
            
            # Generate response
            response = vision_model.generate_content([vision_prompt, img])
            description = response.text
            
            # Detect issues from response
            issue_keywords = ['pothole', 'garbage', 'ખાડો', 'કચરો', 'damaged', 'broken', 'leak', 'problem']
            detected_issues = [word for word in issue_keywords if word.lower() in description.lower()]
            
        except Exception as e:
            logger.error(f"Gemini vision error: {e}")
            # Fallback to simple description
            description = f"Image uploaded successfully. Please describe the issue you're reporting."
            detected_issues = []
        
        # Clean up temp file
        try:
            default_storage.delete(file_path)
        except Exception as e:
            logger.warning(f"Failed to delete temp file {file_path}: {e}")
        
        # Build response
        location_context = ""
        if latitude and longitude:
            location_context = f"\nLocation: Latitude {latitude}, Longitude {longitude}"
        
        # Build AI response in user's language
        response_text = description
        if message:
            response_text = f"{description}"
        response_text += location_context
        
        complaint_detected = len(detected_issues) > 0 or any(
            keyword in description.lower() 
            for keyword in ['damage', 'broken', 'dirty', 'issue', 'problem', 'leak', 'pothole']
        )
        
        return Response({
            'response': response_text,
            'description': description,
            'complaint_detected': complaint_detected,
            'detected_issues': detected_issues,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Vision processing error: {e}")
        return Response({
            'error': f'Vision processing failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def chatbot_health(request):
    """Health check endpoint for chatbot services"""
    return Response({
        'status': 'healthy',
        'services': {
            'chat': 'operational',
            'voice': 'operational',
            'vision': 'operational',
        }
    }, status=status.HTTP_200_OK)
