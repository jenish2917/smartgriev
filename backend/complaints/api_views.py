"""
Comprehensive API Views for SmartGriev Multi-Modal Complaint Processing System
Integrates AI processing, department classification, and authentication
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.http import JsonResponse
import tempfile
import os

from .models import Complaint, ComplaintStatus, ComplaintCategory
from .ai_processor import AdvancedAIProcessor
from .department_classifier import GovernmentDepartmentClassifier
from authentication.auth_service import AdvancedAuthService
from authentication.models import User, OTPVerification

logger = logging.getLogger(__name__)

# Initialize services
ai_processor = AdvancedAIProcessor()
dept_classifier = GovernmentDepartmentClassifier()
auth_service = AdvancedAuthService()


class MultiModalComplaintProcessingView(APIView):
    """
    Advanced multi-modal complaint processing endpoint
    Supports text, audio, and image inputs with AI enhancement
    """
    permission_classes = [permissions.AllowAny]  # Allow anonymous complaints
    
    async def post(self, request, *args, **kwargs):
        """Process multi-modal complaint with AI enhancement"""
        try:
            # Extract input data
            complaint_text = request.data.get('text', '')
            audio_file = request.FILES.get('audio')
            image_file = request.FILES.get('image')
            location = request.data.get('location')
            user_id = request.data.get('user_id')  # Optional for registered users
            
            # Validate input - at least one input type required
            if not any([complaint_text, audio_file, image_file]):
                return Response({
                    'error': 'At least one input type (text, audio, or image) is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            processing_results = {
                'original_text': complaint_text,
                'audio_processed': False,
                'image_processed': False,
                'ai_enhanced': False,
                'department_classified': False
            }
            
            # Process audio to text if provided
            if audio_file:
                logger.info("Processing audio file...")
                audio_text = await self._process_audio_file(audio_file)
                if audio_text:
                    complaint_text += f" {audio_text}"
                    processing_results['audio_processed'] = True
                    processing_results['audio_text'] = audio_text
            
            # Process image if provided
            if image_file:
                logger.info("Processing image file...")
                image_analysis = await self._process_image_file(image_file)
                if image_analysis:
                    complaint_text += f" {image_analysis}"
                    processing_results['image_processed'] = True
                    processing_results['image_analysis'] = image_analysis
            
            # Enhance text with AI if we have any content
            if complaint_text.strip():
                logger.info("Enhancing complaint with AI...")
                enhanced_text = await ai_processor.enhance_complaint_text(
                    complaint_text, 
                    location=location
                )
                if enhanced_text:
                    complaint_text = enhanced_text
                    processing_results['ai_enhanced'] = True
            
            # Classify department
            logger.info("Classifying government department...")
            classification_result = await dept_classifier.classify_complaint(
                complaint_text,
                location=location
            )
            
            if classification_result['success']:
                processing_results['department_classified'] = True
                processing_results['classification'] = classification_result
            
            # Store complaint in database
            complaint_data = await self._store_complaint(
                text=complaint_text,
                classification=classification_result if classification_result['success'] else None,
                user_id=user_id,
                location=location,
                audio_file=audio_file,
                image_file=image_file
            )
            
            # Prepare response
            response_data = {
                'success': True,
                'complaint_id': complaint_data['complaint_id'],
                'processed_text': complaint_text,
                'department': classification_result.get('department', 'General'),
                'urgency_level': classification_result.get('urgency_level', 'medium'),
                'estimated_resolution_days': classification_result.get('estimated_resolution_days', 7),
                'processing_details': processing_results,
                'message': 'Complaint processed successfully'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Multi-modal processing failed: {e}")
            return Response({
                'error': 'Failed to process complaint',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def _process_audio_file(self, audio_file) -> Optional[str]:
        """Process audio file to extract text"""
        try:
            # Save audio file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Process with AI
            audio_text = await ai_processor.process_audio_to_text(temp_path)
            
            # Cleanup
            os.unlink(temp_path)
            
            return audio_text
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return None
    
    async def _process_image_file(self, image_file) -> Optional[str]:
        """Process image file to extract context and text"""
        try:
            # Save image file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Process with AI
            image_analysis = await ai_processor.process_image_with_context(temp_path)
            
            # Cleanup
            os.unlink(temp_path)
            
            return image_analysis
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return None
    
    async def _store_complaint(self, text: str, classification: Dict = None, 
                              user_id: str = None, location: str = None,
                              audio_file=None, image_file=None) -> Dict[str, Any]:
        """Store processed complaint in database"""
        try:
            # Get user if provided
            user = None
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    pass
            
            # Get or create complaint category
            category_name = classification.get('department', 'General') if classification else 'General'
            category, _ = ComplaintCategory.objects.get_or_create(
                name=category_name,
                defaults={'description': f'{category_name} related complaints'}
            )
            
            # Create complaint
            complaint = Complaint.objects.create(
                user=user,
                title=text[:100] + '...' if len(text) > 100 else text,
                description=text,
                category=category,
                location=location or '',
                urgency_level=classification.get('urgency_level', 'medium') if classification else 'medium',
                ai_confidence_score=classification.get('confidence', 0.0) if classification else 0.0,
                department_classification=json.dumps(classification) if classification else '{}',
                gemini_raw_response=classification if classification else {},  # Store raw Gemini response
            )
            
            # Store files if provided
            if audio_file:
                audio_path = default_storage.save(
                    f'complaints/audio/{complaint.id}_{audio_file.name}',
                    ContentFile(audio_file.read())
                )
                complaint.audio_file = audio_path
            
            if image_file:
                image_path = default_storage.save(
                    f'complaints/images/{complaint.id}_{image_file.name}',
                    ContentFile(image_file.read())
                )
                complaint.image_file = image_path
            
            complaint.save()
            
            # Create initial status
            ComplaintStatus.objects.create(
                complaint=complaint,
                status='submitted',
                notes='Complaint submitted and processed with AI',
                updated_by=user
            )
            
            return {
                'complaint_id': complaint.id,
                'category': category.name,
                'created_at': complaint.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to store complaint: {e}")
            raise


class AuthenticationAPIView(APIView):
    """
    Advanced authentication endpoints with OTP support
    """
    permission_classes = [permissions.AllowAny]
    
    async def post(self, request, *args, **kwargs):
        """Handle authentication requests"""
        action = request.data.get('action')
        
        if action == 'register':
            return await self._handle_registration(request)
        elif action == 'login':
            return await self._handle_login(request)
        elif action == 'verify_otp':
            return await self._handle_otp_verification(request)
        elif action == 'send_otp':
            return await self._handle_send_otp(request)
        else:
            return Response({
                'error': 'Invalid action. Supported: register, login, verify_otp, send_otp'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    async def _handle_registration(self, request):
        """Handle user registration with OTP"""
        try:
            phone_number = request.data.get('phone_number')
            email = request.data.get('email')
            password = request.data.get('password')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            
            success, message, user = await auth_service.register_user(
                phone_number=phone_number,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            if success:
                return Response({
                    'success': True,
                    'message': message,
                    'user_id': user.id,
                    'requires_verification': True
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': message
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return Response({
                'error': 'Registration failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def _handle_login(self, request):
        """Handle user login"""
        try:
            identifier = request.data.get('identifier')  # phone/email/username
            password = request.data.get('password')
            
            if not identifier or not password:
                return Response({
                    'error': 'Identifier and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success, message, user = await auth_service.authenticate_user(
                identifier=identifier,
                password=password,
                request_ip=request.META.get('REMOTE_ADDR')
            )
            
            if success:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'success': True,
                    'message': message,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    },
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'phone': user.mobile,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': message
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return Response({
                'error': 'Login failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def _handle_otp_verification(self, request):
        """Handle OTP verification"""
        try:
            user_id = request.data.get('user_id')
            otp_code = request.data.get('otp_code')
            otp_type = request.data.get('otp_type', 'registration')
            
            if not all([user_id, otp_code]):
                return Response({
                    'error': 'User ID and OTP code are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success, message = await auth_service.verify_otp(
                user_id=user_id,
                otp_code=otp_code,
                otp_type=otp_type
            )
            
            return Response({
                'success': success,
                'message': message
            }, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"OTP verification failed: {e}")
            return Response({
                'error': 'OTP verification failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def _handle_send_otp(self, request):
        """Handle sending OTP"""
        try:
            identifier = request.data.get('identifier')  # phone or email
            otp_type = request.data.get('otp_type', 'login')
            
            if not identifier:
                return Response({
                    'error': 'Phone number or email is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find user
            user = None
            if identifier.isdigit():
                user = User.objects.filter(mobile=identifier).first()
            elif '@' in identifier:
                user = User.objects.filter(email=identifier).first()
            
            if not user:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Send OTP
            if identifier.isdigit():
                await auth_service.send_phone_otp(user, identifier, otp_type)
            else:
                await auth_service.send_email_otp(user, identifier, otp_type)
            
            return Response({
                'success': True,
                'message': f'OTP sent to {identifier}'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Send OTP failed: {e}")
            return Response({
                'error': 'Failed to send OTP'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ComplaintStatusView(APIView):
    """
    Complaint status tracking and updates
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, complaint_id=None):
        """Get complaint status and updates"""
        try:
            if not complaint_id:
                return Response({
                    'error': 'Complaint ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            complaint = Complaint.objects.get(id=complaint_id)
            statuses = ComplaintStatus.objects.filter(complaint=complaint).order_by('-created_at')
            
            return Response({
                'complaint': {
                    'id': complaint.id,
                    'title': complaint.title,
                    'description': complaint.description,
                    'category': complaint.category.name,
                    'location': complaint.location,
                    'urgency_level': complaint.urgency_level,
                    'created_at': complaint.created_at.isoformat(),
                    'updated_at': complaint.updated_at.isoformat()
                },
                'statuses': [
                    {
                        'status': status.status,
                        'notes': status.notes,
                        'created_at': status.created_at.isoformat(),
                        'updated_by': status.updated_by.username if status.updated_by else 'System'
                    }
                    for status in statuses
                ]
            }, status=status.HTTP_200_OK)
            
        except Complaint.DoesNotExist:
            return Response({
                'error': 'Complaint not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to get complaint status: {e}")
            return Response({
                'error': 'Failed to retrieve complaint status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartmentListView(APIView):
    """
    Government departments and their information
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get list of available government departments"""
        try:
            departments = dept_classifier.get_all_departments()
            
            return Response({
                'departments': departments,
                'total_count': len(departments)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get departments: {e}")
            return Response({
                'error': 'Failed to retrieve departments'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Legacy function-based views for backward compatibility
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def process_complaint_simple(request):
    """Simple complaint processing endpoint for basic text complaints"""
    try:
        text = request.data.get('text', '')
        location = request.data.get('location', '')
        
        if not text:
            return Response({
                'error': 'Complaint text is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Basic processing without multi-modal features
        classification_result = asyncio.run(
            dept_classifier.classify_complaint(text, location=location)
        )
        
        return Response({
            'success': True,
            'classification': classification_result,
            'message': 'Basic complaint processed successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Simple complaint processing failed: {e}")
        return Response({
            'error': 'Failed to process complaint'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint for the complaint processing system"""
    try:
        # Test AI processor
        ai_status = "available"
        try:
            asyncio.run(ai_processor.enhance_complaint_text("test"))
        except:
            ai_status = "unavailable"
        
        # Test department classifier
        dept_status = "available"
        try:
            asyncio.run(dept_classifier.classify_complaint("test complaint"))
        except:
            dept_status = "unavailable"
        
        return Response({
            'status': 'healthy',
            'services': {
                'ai_processor': ai_status,
                'department_classifier': dept_status,
                'database': 'available'
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)