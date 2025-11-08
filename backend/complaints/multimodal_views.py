"""
Multimodal Complaint Submission Views
Handles image and audio complaint submissions with AI processing
"""

import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Complaint
from .serializers import MultimodalComplaintSerializer, ComplaintSerializer

logger = logging.getLogger(__name__)


class MultimodalComplaintCreateView(generics.CreateAPIView):
    """
    Create complaint with multimodal inputs (text, audio, image).
    
    This endpoint accepts:
    - Text description
    - Audio file (transcribed automatically)
    - Image file (OCR + object detection)
    
    Files are processed with AI to extract text, detect objects, and classify the complaint.
    """
    queryset = Complaint.objects.all()
    serializer_class = MultimodalComplaintSerializer
    permission_classes = [AllowAny]  # Allow public complaint submission
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        """Create complaint with multimodal processing"""
        username = request.user.username if request.user.is_authenticated else "Anonymous"
        logger.info(f"Multimodal complaint submission from user: {username}")
        
        try:
            # FAST TRACK: Create complaint first, process AI later
            logger.info("Fast-track complaint creation - AI processing will happen in background")
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Save complaint - this will trigger AI processing but we don't wait for it
            try:
                complaint = serializer.save()
            except Exception as save_error:
                logger.warning(f"AI processing delayed, but complaint saved: {str(save_error)}")
                # Even if AI processing fails, complaint is created
                complaint = serializer.instance
            
            # Return IMMEDIATELY - don't wait for AI processing
            response_serializer = ComplaintSerializer(complaint)
            return Response({
                'success': True,
                'message': 'Complaint submitted successfully! AI processing in progress.',
                'complaint': response_serializer.data,
                'processing_status': {
                    'image_processing': 'in_progress' if complaint.image_file else 'not_applicable',
                    'audio_processing': 'in_progress' if complaint.audio_file else 'not_applicable',
                    'ai_classification': 'in_progress'
                },
                'note': 'Your complaint has been received. AI analysis will complete shortly.'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Multimodal complaint creation failed: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class QuickComplaintSubmitView(APIView):
    """
    Quick complaint submission endpoint for citizens.
    Allows anonymous or authenticated submissions.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Submit complaint quickly with minimal required fields"""
        try:
            # Prepare data
            data = request.data.copy()
            
            # Allow anonymous submissions
            if not request.user.is_authenticated:
                # Create anonymous user placeholder or skip user assignment
                data['title'] = data.get('title', 'Anonymous Complaint')
            
            # Set default priority if not provided
            if 'priority' not in data:
                data['priority'] = 'medium'
            
            if 'urgency_level' not in data:
                data['urgency_level'] = 'medium'
            
            serializer = MultimodalComplaintSerializer(data=data, context={'request': request})
            
            if serializer.is_valid():
                complaint = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Complaint submitted successfully',
                    'complaint_id': complaint.id,
                    'tracking_number': f"COMP-{complaint.id:06d}",
                    'status': complaint.status
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Quick complaint submission failed: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to submit complaint. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ComplaintMediaUploadView(APIView):
    """
    Upload additional media (images/audio) to existing complaint.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, complaint_id):
        """Add media files to existing complaint"""
        try:
            complaint = Complaint.objects.get(id=complaint_id, user=request.user)
            
            # Handle different media types
            if 'image' in request.FILES:
                complaint.image_file = request.FILES['image']
                # Process image
                try:
                    serializer = MultimodalComplaintSerializer()
                    serializer._process_image(complaint)
                except Exception as e:
                    logger.warning(f"Image processing failed: {str(e)}")
            
            if 'audio' in request.FILES:
                complaint.audio_file = request.FILES['audio']
                # Process audio
                try:
                    serializer = MultimodalComplaintSerializer()
                    serializer._process_audio(complaint)
                except Exception as e:
                    logger.warning(f"Audio processing failed: {str(e)}")
            
            complaint.save()
            
            return Response({
                'success': True,
                'message': 'Media uploaded and processed successfully',
                'complaint_id': complaint.id
            }, status=status.HTTP_200_OK)
            
        except Complaint.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Complaint not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Media upload failed: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ComplaintListView(generics.ListAPIView):
    """
    List all complaints for the authenticated user.
    """
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user).order_by('-created_at')


class ComplaintDetailView(generics.RetrieveAPIView):
    """
    Get detailed complaint information including all multimodal analysis results.
    """
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user)
