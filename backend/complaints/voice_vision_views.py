"""
Voice & Vision AI API Views for SmartGriev
Handles voice and vision-based complaint analysis using Gemini 1.5 Pro
"""

import os
import logging
import tempfile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from complaints.services import get_vision_service, get_audio_service

logger = logging.getLogger(__name__)


class ImageAnalysisView(APIView):
    """
    API endpoint for analyzing images of civic complaints
    Uses Gemini 1.5 Pro Vision for image analysis
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Analyze uploaded image for complaint
        
        Expected input:
        - image: Image file upload (required)
        - context: Optional context text
        
        Returns:
        - Image analysis with detected issues, severity, department suggestion
        """
        try:
            # Validate image file
            if 'image' not in request.FILES:
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            context = request.data.get('context', None)
            
            # Save image temporarily
            temp_path = tempfile.mktemp(suffix=os.path.splitext(image_file.name)[1])
            with open(temp_path, 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
            
            try:
                # Analyze image
                vision_service = get_vision_service()
                result = vision_service.analyze_image(temp_path, context)
                
                return Response(result, status=status.HTTP_200_OK)
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return Response(
                {'error': 'Image analysis failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MultiImageAnalysisView(APIView):
    """
    API endpoint for analyzing multiple images together
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Analyze multiple uploaded images for complaint
        
        Expected input:
        - images: Multiple image files (max 5)
        - context: Optional context text
        
        Returns:
        - Aggregated image analysis
        """
        try:
            # Get uploaded images
            images = request.FILES.getlist('images')
            if not images:
                return Response(
                    {'error': 'No images provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(images) > 5:
                return Response(
                    {'error': 'Maximum 5 images allowed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            context = request.data.get('context', None)
            
            # Save images temporarily
            temp_paths = []
            for img in images:
                temp_path = tempfile.mktemp(suffix=os.path.splitext(img.name)[1])
                with open(temp_path, 'wb') as f:
                    for chunk in img.chunks():
                        f.write(chunk)
                temp_paths.append(temp_path)
            
            try:
                # Analyze images
                vision_service = get_vision_service()
                result = vision_service.analyze_multiple_images(temp_paths, context)
                
                return Response(result, status=status.HTTP_200_OK)
            
            finally:
                # Clean up temp files
                for temp_path in temp_paths:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        except Exception as e:
            logger.error(f"Multi-image analysis error: {str(e)}")
            return Response(
                {'error': 'Image analysis failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoAnalysisView(APIView):
    """
    API endpoint for analyzing videos of civic complaints
    Uses Gemini 1.5 Pro Vision for video analysis
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Analyze uploaded video for complaint
        
        Expected input:
        - video: Video file upload (required)
        - context: Optional context text
        
        Returns:
        - Video analysis with detected issues, timeline observations
        """
        try:
            # Validate video file
            if 'video' not in request.FILES:
                return Response(
                    {'error': 'No video file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            video_file = request.FILES['video']
            context = request.data.get('context', None)
            
            # Save video temporarily
            temp_path = tempfile.mktemp(suffix=os.path.splitext(video_file.name)[1])
            with open(temp_path, 'wb') as f:
                for chunk in video_file.chunks():
                    f.write(chunk)
            
            try:
                # Analyze video
                vision_service = get_vision_service()
                result = vision_service.analyze_video(temp_path, context)
                
                return Response(result, status=status.HTTP_200_OK)
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        except Exception as e:
            logger.error(f"Video analysis error: {str(e)}")
            return Response(
                {'error': 'Video analysis failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AudioTranscriptionView(APIView):
    """
    API endpoint for transcribing audio complaints
    Uses Gemini 1.5 Pro for speech-to-text in 12 Indian languages
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Transcribe uploaded audio file
        
        Expected input:
        - audio: Audio file upload (required)
        - language: Optional language code (auto-detected if not provided)
        - context: Optional context text
        
        Returns:
        - Transcription with language detection, emotion, urgency
        """
        try:
            # Validate audio file
            if 'audio' not in request.FILES:
                return Response(
                    {'error': 'No audio file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            audio_file = request.FILES['audio']
            language = request.data.get('language', None)
            context = request.data.get('context', None)
            
            # Save audio temporarily
            temp_path = tempfile.mktemp(suffix=os.path.splitext(audio_file.name)[1])
            with open(temp_path, 'wb') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            
            try:
                # Transcribe audio
                audio_service = get_audio_service()
                result = audio_service.transcribe_audio(temp_path, language, context)
                
                return Response(result, status=status.HTTP_200_OK)
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        except Exception as e:
            logger.error(f"Audio transcription error: {str(e)}")
            return Response(
                {'error': 'Audio transcription failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VoiceComplaintAnalysisView(APIView):
    """
    API endpoint for comprehensive voice complaint analysis
    Includes transcription + sentiment + department classification
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Analyze voice complaint comprehensively
        
        Expected input:
        - audio: Audio file upload (required)
        - language: Optional language code
        
        Returns:
        - Complete analysis with transcription, sentiment, classification, department
        """
        try:
            # Validate audio file
            if 'audio' not in request.FILES:
                return Response(
                    {'error': 'No audio file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            audio_file = request.FILES['audio']
            language = request.data.get('language', None)
            
            # Save audio temporarily
            temp_path = tempfile.mktemp(suffix=os.path.splitext(audio_file.name)[1])
            with open(temp_path, 'wb') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            
            try:
                # Analyze voice complaint
                audio_service = get_audio_service()
                result = audio_service.analyze_voice_complaint(temp_path, language)
                
                return Response(result, status=status.HTTP_200_OK)
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        except Exception as e:
            logger.error(f"Voice complaint analysis error: {str(e)}")
            return Response(
                {'error': 'Voice complaint analysis failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MultimodalAnalysisView(APIView):
    """
    API endpoint for combined voice + vision analysis
    Supports text + image + audio + video combined
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Analyze multimodal complaint inputs
        
        Expected input:
        - text: Optional text description
        - image: Optional image file
        - audio: Optional audio file
        - video: Optional video file
        - language: Optional language code
        
        Returns:
        - Combined analysis from all modalities
        """
        try:
            # Collect all inputs
            text = request.data.get('text', '')
            image = request.FILES.get('image', None)
            audio = request.FILES.get('audio', None)
            video = request.FILES.get('video', None)
            language = request.data.get('language', 'en')
            
            # Must have at least one input
            if not any([text, image, audio, video]):
                return Response(
                    {'error': 'At least one input modality required (text, image, audio, or video)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = {
                'success': True,
                'modalities_processed': [],
                'combined_analysis': {}
            }
            
            # Process image if provided
            if image:
                temp_img_path = tempfile.mktemp(suffix=os.path.splitext(image.name)[1])
                with open(temp_img_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                
                try:
                    vision_service = get_vision_service()
                    img_result = vision_service.analyze_image(temp_img_path, text)
                    result['image_analysis'] = img_result
                    result['modalities_processed'].append('image')
                finally:
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
            
            # Process audio if provided
            if audio:
                temp_audio_path = tempfile.mktemp(suffix=os.path.splitext(audio.name)[1])
                with open(temp_audio_path, 'wb') as f:
                    for chunk in audio.chunks():
                        f.write(chunk)
                
                try:
                    audio_service = get_audio_service()
                    audio_result = audio_service.analyze_voice_complaint(temp_audio_path, language)
                    result['audio_analysis'] = audio_result
                    result['modalities_processed'].append('audio')
                finally:
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
            
            # Process video if provided
            if video:
                temp_video_path = tempfile.mktemp(suffix=os.path.splitext(video.name)[1])
                with open(temp_video_path, 'wb') as f:
                    for chunk in video.chunks():
                        f.write(chunk)
                
                try:
                    vision_service = get_vision_service()
                    video_result = vision_service.analyze_video(temp_video_path, text)
                    result['video_analysis'] = video_result
                    result['modalities_processed'].append('video')
                finally:
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)
            
            # Combine analyses
            result['combined_analysis'] = self._combine_multimodal_analyses(result)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Multimodal analysis error: {str(e)}")
            return Response(
                {'error': 'Multimodal analysis failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _combine_multimodal_analyses(self, result: dict) -> dict:
        """Combine analyses from different modalities into unified result"""
        combined = {
            'issue_type': 'Unknown',
            'description': '',
            'severity': 'Medium',
            'urgency': 'medium',
            'suggested_department': 'Other',
            'confidence': 0.0
        }
        
        # Priority: audio > video > image (audio has most context)
        if 'audio_analysis' in result and result['audio_analysis'].get('success'):
            audio = result['audio_analysis']
            combined['issue_type'] = audio.get('issue_type', 'Unknown')
            combined['description'] = audio.get('description', '')
            combined['urgency'] = audio.get('urgency', 'medium')
            combined['suggested_department'] = audio.get('suggested_department', 'Other')
            combined['transcription'] = audio.get('transcription', '')
        
        if 'video_analysis' in result and result['video_analysis'].get('success'):
            video = result['video_analysis']
            if not combined['issue_type'] or combined['issue_type'] == 'Unknown':
                combined['issue_type'] = video.get('issue_type', 'Unknown')
            if not combined['description']:
                combined['description'] = video.get('description', '')
            combined['severity'] = video.get('severity', 'Medium')
            combined['visual_evidence'] = video.get('detected_objects', [])
        
        if 'image_analysis' in result and result['image_analysis'].get('success'):
            image = result['image_analysis']
            if not combined['issue_type'] or combined['issue_type'] == 'Unknown':
                combined['issue_type'] = image.get('issue_type', 'Unknown')
            if not combined['description']:
                combined['description'] = image.get('description', '')
            if 'visual_evidence' not in combined:
                combined['visual_evidence'] = image.get('detected_objects', [])
        
        return combined
