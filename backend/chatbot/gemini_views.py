"""
Gemini-powered chatbot views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import uuid
from .gemini_service import gemini_chatbot
from .models import ChatSession, ChatLog
from complaints.models import Complaint, ComplaintCategory, Department


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow guests to chat
def gemini_chat(request):
    """
    Chat with Gemini AI assistant
    
    POST data:
    - message: User message
    - session_id: Optional session ID for context
    - language: User's preferred language (default: 'en')
    """
    
    message = request.data.get('message', '').strip()
    session_id = request.data.get('session_id')
    language = request.data.get('language', 'en')
    
    if not message:
        return Response({
            'error': 'Message is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        # Get response from Gemini
        result = gemini_chatbot.chat(
            session_id=session_id,
            user_message=message,
            user_language=language
        )
        
        # Save chat log if user is authenticated
        if request.user.is_authenticated:
            try:
                # Get or create chat session
                chat_session, created = ChatSession.objects.get_or_create(
                    user=request.user,
                    session_id=session_id,
                    defaults={'is_active': True}
                )
                
                # Save chat log
                ChatLog.objects.create(
                    user=request.user,
                    session=chat_session,
                    message=message,
                    reply=result['response'],
                    intent=result.get('intent', 'unknown'),
                    input_language=language,
                    reply_language=language
                )
            except Exception as e:
                print(f"Error saving chat log: {e}")
        
        return Response({
            'session_id': session_id,
            'response': result['response'],
            'intent': result['intent'],
            'complaint_data': result['complaint_data'],
            'conversation_complete': result['conversation_complete'],
            'language': language
        })
        
    except Exception as e:
        return Response({
            'error': f'Chat processing failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_complaint_from_chat(request):
    """
    Create a complaint from chatbot conversation
    
    POST data:
    - session_id: Chat session ID
    - confirm: Set to true to confirm and create complaint
    """
    
    session_id = request.data.get('session_id')
    confirm = request.data.get('confirm', False)
    
    if not session_id:
        return Response({
            'error': 'session_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get conversation summary
        summary = gemini_chatbot.get_conversation_summary(session_id)
        
        if 'error' in summary:
            return Response(summary, status=status.HTTP_404_NOT_FOUND)
        
        complaint_data = summary.get('complaint_data', {})
        
        if not summary.get('ready_to_submit'):
            return Response({
                'error': 'Not enough information to create complaint',
                'complaint_data': complaint_data,
                'message': 'Please provide more details about your issue'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # If not confirmed, return preview
        if not confirm:
            return Response({
                'preview': True,
                'complaint_data': complaint_data,
                'message': 'Please review and confirm to create the complaint'
            })
        
        # Create the complaint
        title = complaint_data.get('title', 'Complaint from chatbot')
        description = complaint_data.get('description', '')
        category_name = complaint_data.get('category', 'Others')
        location = complaint_data.get('location', '')
        urgency = complaint_data.get('urgency', 'medium')
        
        # Get or create category
        category, _ = ComplaintCategory.objects.get_or_create(
            name=category_name,
            defaults={'description': f'{category_name} complaints'}
        )
        
        # Map category to department (simplified)
        department = None
        try:
            # Try to find appropriate department
            if category_name.lower() in ['infrastructure', 'roads']:
                department = Department.objects.filter(name__icontains='infrastructure').first()
            elif category_name.lower() in ['health', 'sanitation']:
                department = Department.objects.filter(name__icontains='health').first()
            
            if not department:
                department = Department.objects.first()
        except:
            pass
        
        # Create complaint
        complaint = Complaint.objects.create(
            user=request.user,
            title=title[:200],  # Max 200 chars
            description=description,
            category=category,
            department=department,
            urgency_level=urgency if urgency in ['low', 'medium', 'high', 'critical'] else 'medium',
            priority='high' if urgency in ['urgent', 'critical'] else 'medium',
            submitted_language=summary.get('language', 'en'),
            original_text=description,
            status='submitted'
        )
        
        # End the conversation
        gemini_chatbot.end_conversation(session_id)
        
        return Response({
            'success': True,
            'complaint_id': complaint.id,
            'message': 'Complaint created successfully',
            'complaint': {
                'id': complaint.id,
                'title': complaint.title,
                'status': complaint.status,
                'created_at': complaint.created_at
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to create complaint: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def conversation_summary(request, session_id):
    """Get conversation summary and extracted data"""
    
    try:
        summary = gemini_chatbot.get_conversation_summary(session_id)
        
        if 'error' in summary:
            return Response(summary, status=status.HTTP_404_NOT_FOUND)
        
        return Response(summary)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def start_conversation(request):
    """Start a new conversation with the chatbot"""
    
    language = request.data.get('language', 'en')
    session_id = str(uuid.uuid4())
    
    try:
        greeting = gemini_chatbot.start_conversation(session_id, language)
        
        return Response({
            'session_id': session_id,
            'greeting': greeting,
            'language': language
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def end_conversation(request, session_id):
    """End a conversation"""
    
    try:
        gemini_chatbot.end_conversation(session_id)
        
        return Response({
            'message': 'Conversation ended successfully'
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def gemini_health_check(request):
    """Check if Gemini service is available"""
    
    try:
        import os
        api_key = os.getenv('GEMINI_API_KEY')
        
        return Response({
            'status': 'healthy',
            'service': 'Gemini AI Chatbot',
            'api_key_configured': bool(api_key),
            'version': 'gemini-1.5-flash'
        })
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
