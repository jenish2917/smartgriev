"""
Gemini-powered chatbot views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import uuid
import logging
from .gemini_service import gemini_chatbot
from .models import ChatSession, ChatLog
from complaints.models import Complaint, ComplaintCategory, Department

logger = logging.getLogger(__name__)


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
                logger.error(f"Error saving chat log: {e}")
        
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
    Automatically formats, classifies, and assigns to correct department
    
    POST data:
    - session_id: Chat session ID
    - confirm: Set to true to confirm and create complaint
    """
    
    session_id = request.data.get('session_id')
    confirm = request.data.get('confirm', True)  # Auto-confirm by default
    
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
        
        # Extract and format complaint data
        title = complaint_data.get('title', 'Complaint from AI Chat')
        description = complaint_data.get('description', '')
        category_name = complaint_data.get('category', 'General')
        location = complaint_data.get('location', '')
        urgency = complaint_data.get('urgency', 'medium').lower()
        
        # Smart department classification based on keywords
        department = classify_department_from_complaint(title, description, category_name)
        
        # Get or create category
        category, _ = ComplaintCategory.objects.get_or_create(
            name=category_name,
            defaults={'description': f'{category_name} related complaints'}
        )
        
        # Map urgency to priority
        priority_mapping = {
            'low': 'low',
            'medium': 'medium',
            'high': 'high',
            'urgent': 'urgent',
            'critical': 'urgent'
        }
        priority = priority_mapping.get(urgency, 'medium')
        
        # Create complaint with proper formatting
        complaint = Complaint.objects.create(
            user=request.user,
            title=title[:200],  # Max 200 chars
            description=description,
            location=location,
            category=category,
            department=department,
            priority=priority,
            submitted_language=summary.get('language', 'en'),
            original_text=description,
            status='submitted',
            # Additional metadata
            sentiment=complaint_data.get('sentiment', 'neutral')
        )
        
        logger.info(f"Complaint created from chat: ID={complaint.id}, Department={department.name if department else 'None'}")
        
        # End the conversation
        gemini_chatbot.end_conversation(session_id)
        
        return Response({
            'success': True,
            'complaint_id': complaint.id,
            'message': f'Complaint submitted successfully and assigned to {department.name if department else "General Administration"}',
            'complaint': {
                'id': complaint.id,
                'title': complaint.title,
                'status': complaint.status,
                'department': department.name if department else None,
                'priority': complaint.priority,
                'created_at': complaint.created_at
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Failed to create complaint from chat: {str(e)}")
        return Response({
            'error': f'Failed to create complaint: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def classify_department_from_complaint(title: str, description: str, category: str) -> Department:
    """
    Classify complaint to appropriate civic department using keyword matching
    """
    text = f"{title} {description} {category}".lower()
    
    # Department classification rules with priority
    department_keywords = {
        'Road & Transportation': ['road', 'pothole', 'street', 'highway', 'traffic', 'signal', 'crossing', 'pavement'],
        'Water Supply & Sewerage': ['water', 'supply', 'sewage', 'drainage', 'leak', 'pipe', 'tap', 'plumbing'],
        'Sanitation & Cleanliness': ['garbage', 'waste', 'trash', 'sanitation', 'clean', 'dirty', 'smell', 'sweeping'],
        'Electricity Board': ['electricity', 'power', 'light', 'streetlight', 'outage', 'transformer', 'wire', 'pole'],
        'Health & Medical Services': ['health', 'hospital', 'medical', 'clinic', 'doctor', 'disease', 'hygiene'],
        'Fire & Emergency Services': ['fire', 'emergency', 'accident', 'disaster', 'rescue'],
        'Police & Law Enforcement': ['police', 'crime', 'theft', 'safety', 'law', 'violation', 'illegal'],
        'Traffic Police': ['traffic', 'parking', 'vehicle', 'challan', 'towing'],
        'Environment & Pollution Control': ['pollution', 'noise', 'air quality', 'environment', 'tree', 'green'],
        'Parks & Gardens': ['park', 'garden', 'playground', 'trees', 'plants'],
        'Municipal Corporation': ['tax', 'property', 'building', 'permit', 'license', 'civic'],
        'Food Safety & Standards': ['food', 'restaurant', 'hygiene', 'quality', 'adulteration'],
        'Animal Control & Welfare': ['animal', 'stray', 'dog', 'cat', 'pet', 'veterinary'],
        'Public Transport (BRTS/Bus)': ['bus', 'transport', 'brts', 'route', 'stop'],
    }
    
    # Find best matching department
    max_matches = 0
    best_department = None
    
    for dept_name, keywords in department_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in text)
        if matches > max_matches:
            max_matches = matches
            try:
                best_department = Department.objects.filter(name__icontains=dept_name).first()
            except:
                pass
    
    # If no match found, assign to General Administration
    if not best_department or max_matches == 0:
        try:
            best_department = Department.objects.filter(name__icontains='General Administration').first()
            if not best_department:
                best_department = Department.objects.first()
        except:
            pass
    
    return best_department


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
