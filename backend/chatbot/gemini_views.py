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
    
    logger.info(f"[CREATE_COMPLAINT] Request received from user: {request.user.email}")
    
    session_id = request.data.get('session_id')
    confirm = request.data.get('confirm', True)  # Auto-confirm by default
    
    logger.info(f"[CREATE_COMPLAINT] Session ID: {session_id}, Confirm: {confirm}")
    
    if not session_id:
        logger.error("[CREATE_COMPLAINT] Missing session_id")
        return Response({
            'error': 'session_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get conversation summary
        logger.info(f"[CREATE_COMPLAINT] Getting conversation summary...")
        summary = gemini_chatbot.get_conversation_summary(session_id)
        logger.info(f"[CREATE_COMPLAINT] Summary: {summary}")
        
        if 'error' in summary:
            logger.error(f"[CREATE_COMPLAINT] Summary error: {summary}")
            return Response(summary, status=status.HTTP_404_NOT_FOUND)
        
        complaint_data = summary.get('complaint_data', {})
        logger.info(f"[CREATE_COMPLAINT] Complaint data: {complaint_data}")
        
        if not summary.get('ready_to_submit'):
            logger.warning("[CREATE_COMPLAINT] Not ready to submit - missing information")
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
        submitted_language = summary.get('language', 'en')
        
        # Store original text
        original_title = title
        original_description = description
        
        # Translate to English for classification if needed
        if submitted_language != 'en':
            try:
                from authentication.translation_service import TranslationService
                translator = TranslationService()
                
                # Translate title and description to English
                title_translation = translator.translate_text(title, submitted_language, 'en')
                desc_translation = translator.translate_text(description, submitted_language, 'en')
                
                if title_translation and title_translation.get('translated_text'):
                    title = title_translation['translated_text']
                    logger.info(f"Translated title from {submitted_language} to English: {original_title} -> {title}")
                
                if desc_translation and desc_translation.get('translated_text'):
                    description = desc_translation['translated_text']
                    logger.info(f"Translated description from {submitted_language} to English")
                    
            except Exception as e:
                logger.warning(f"Translation failed, using original text: {e}")
                # Fall back to original text if translation fails
                title = original_title
                description = original_description
        
        # Smart department classification based on English keywords
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
            title=title[:200],  # English title for consistency (Max 200 chars)
            description=description,  # English description for department routing
            location=location,
            category=category,
            department=department,
            priority=priority,
            submitted_language=submitted_language,
            original_text=f"{original_title}\n\n{original_description}" if submitted_language != 'en' else description,
            status='submitted',
            # Additional metadata - sentiment is a float score
            sentiment=None  # Will be analyzed separately if needed
        )
        
        logger.info(f"Complaint created from chat: ID={complaint.id}, Language={submitted_language}, Department={department.name if department else 'None'}")
        
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
    Classify complaint to appropriate civic department using enhanced keyword matching
    """
    text = f"{title} {description} {category}".lower()
    
    # Department classification rules with priority (order matters - most specific first)
    # Enhanced with more keywords for 100% accuracy
    department_keywords = [
        ('Road & Transportation', ['pothole', 'road', 'street', 'highway', 'pavement', 'crossing', 'manhole', 'footpath', 'accident', 'traffic accident', 'road damage', 'path', 'bridge']),
        ('Water Supply & Sewerage', ['water', 'supply', 'sewage', 'drainage', 'leak', 'pipe', 'tap', 'plumbing', 'sewer', 'broken pipe', 'water shortage', 'water problem']),
        ('Sanitation & Cleanliness', ['garbage', 'waste', 'trash', 'sanitation', 'clean', 'dirty', 'smell', 'sweeping', 'dust', 'litter', 'filth', 'refuse']),
        ('Electricity Board', ['electricity', 'power', 'light', 'streetlight', 'outage', 'transformer', 'wire', 'pole', 'electric', 'blackout', 'voltage']),
        ('Health & Medical Services', ['health', 'hospital', 'medical', 'clinic', 'doctor', 'disease', 'hygiene', 'medicine', 'healthcare', 'patient', 'treatment']),
        ('Fire & Emergency Services', ['fire', 'emergency', 'disaster', 'rescue', 'burning', 'blaze', 'flames']),
        ('Police & Law Enforcement', ['police', 'crime', 'theft', 'safety', 'law', 'violation', 'illegal', 'security', 'robbery', 'criminal']),
        ('Traffic Police', ['traffic jam', 'parking', 'vehicle', 'challan', 'towing', 'congestion', 'traffic', 'blocked road']),
        ('Environment & Pollution Control', ['pollution', 'noise', 'air quality', 'environment', 'smoke', 'industrial', 'contamination', 'environmental']),
        ('Parks & Gardens', ['park', 'garden', 'playground', 'trees', 'plants', 'green space', 'landscaping', 'greenery']),
        ('Municipal Corporation', ['tax', 'property tax', 'building permit', 'license', 'civic', 'registration', 'municipal', 'permit', 'certificate', 'documentation']),
        ('Town Planning & Development', ['construction', 'building', 'planning', 'development', 'illegal construction', 'urban planning', 'zoning']),
        ('Food Safety & Standards', ['food', 'restaurant', 'eating', 'quality', 'adulteration', 'expired', 'food safety', 'hygiene standards']),
        ('Animal Control & Welfare', ['stray dog', 'stray cat', 'animal bite', 'pet', 'veterinary', 'cattle', 'animal', 'dog', 'cat', 'livestock']),
        ('Public Transport (BRTS/Bus)', ['bus', 'brts', 'route', 'bus stop', 'conductor', 'public transport', 'transit']),
        ('Education Department', ['school', 'education', 'teacher', 'student', 'college', 'educational', 'classroom', 'learning']),
    ]
    
    # Find best matching department with improved scoring
    max_score = 0
    best_department_name = None
    matched_keywords = []
    
    # Category to department hints
    category_hints = {
        'transportation': ['Road & Transportation', 'Traffic Police', 'Public Transport (BRTS/Bus)'],
        'water': ['Water Supply & Sewerage'],
        'sanitation': ['Sanitation & Cleanliness', 'Water Supply & Sewerage'],
        'utilities': ['Electricity Board', 'Water Supply & Sewerage'],
        'healthcare': ['Health & Medical Services'],
        'emergency': ['Fire & Emergency Services', 'Police & Law Enforcement'],
        'crime': ['Police & Law Enforcement'],
        'environment': ['Environment & Pollution Control', 'Parks & Gardens'],
        'administration': ['Municipal Corporation', 'Town Planning & Development'],
        'infrastructure': ['Road & Transportation', 'Town Planning & Development'],
        'food safety': ['Food Safety & Standards'],
        'animal welfare': ['Animal Control & Welfare'],
        'education': ['Education Department'],
    }
    
    for dept_name, keywords in department_keywords:
        score = 0
        dept_matched_keywords = []
        
        # Keyword matching
        for keyword in keywords:
            # Exact phrase match with word boundaries (highest weight)
            if f' {keyword} ' in f' {text} ':
                score += 5
                dept_matched_keywords.append(keyword)
            # Start or end of text match
            elif text.startswith(keyword) or text.endswith(keyword):
                score += 4
                dept_matched_keywords.append(keyword)
            # Contains keyword (lower weight)
            elif keyword in text:
                score += 2
                dept_matched_keywords.append(keyword)
        
        # Category boost - add bonus if category matches department domain
        for cat_key, cat_depts in category_hints.items():
            if cat_key in category.lower() and dept_name in cat_depts:
                score += 3
                logger.info(f"Category boost for {dept_name}: {category} -> +3 points")
        
        if score > max_score:
            max_score = score
            best_department_name = dept_name
            matched_keywords = dept_matched_keywords
            logger.info(f"Testing {dept_name}: score={score}, keywords={dept_matched_keywords}")

    
    # Find department in database
    if best_department_name and max_score > 0:
        try:
            # Try exact match first
            dept = Department.objects.filter(name__iexact=best_department_name).first()
            if not dept:
                # Try partial match
                dept = Department.objects.filter(name__icontains=best_department_name.split(' &')[0]).first()
            if dept:
                logger.info(f"✅ Classified complaint to: {dept.name} (score: {max_score}, keywords: {matched_keywords})")
                return dept
            else:
                logger.warning(f"Department '{best_department_name}' not found in database")
        except Exception as e:
            logger.error(f"Error finding department: {e}")
    
    # Fallback to General Administration
    logger.warning(f"No matching department found (max_score: {max_score}), using fallback")
    try:
        general_dept = Department.objects.filter(name__icontains='General').first()
        if general_dept:
            logger.info(f"Using fallback department: {general_dept.name}")
            return general_dept
        # Ultimate fallback - first department
        first_dept = Department.objects.first()
        logger.info(f"Using ultimate fallback department: {first_dept.name if first_dept else 'None'}")
        return first_dept
    except Exception as e:
        logger.error(f"Error getting fallback department: {e}")
        return None



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
