from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadedfile import InMemoryUploadedFile
import time
import io
import logging

from .models import (
    MLExperiment, ExperimentResult, ModelPerformanceMetric,
    DataDriftDetection, ModelRetrainingJob, FeatureImportance
)
from .serializers import (
    MLExperimentSerializer, ExperimentResultSerializer,
    ModelPerformanceMetricSerializer, DataDriftDetectionSerializer,
    ModelRetrainingJobSerializer, FeatureImportanceSerializer,
    OCRRequestSerializer, OCRResponseSerializer,
    ComplaintImageOCRSerializer, ComplaintImageOCRResponseSerializer
)
from .ocr_processor import (
    extract_text_from_image_bytes, 
    get_ocr_processor, 
    get_ocr_performance_stats
)

logger = logging.getLogger(__name__)

class MLExperimentListCreateView(generics.ListCreateAPIView):
    serializer_class = MLExperimentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MLExperiment.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class MLExperimentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MLExperimentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'experiment_id'
    
    def get_queryset(self):
        return MLExperiment.objects.filter(created_by=self.request.user)

class ExperimentResultsView(generics.ListAPIView):
    serializer_class = ExperimentResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        experiment_id = self.kwargs['experiment_id']
        return ExperimentResult.objects.filter(experiment__experiment_id=experiment_id)

class ModelPerformanceView(generics.ListAPIView):
    serializer_class = ModelPerformanceMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ModelPerformanceMetric.objects.all().order_by('-evaluation_date')

class ModelPerformanceDetailView(generics.RetrieveAPIView):
    serializer_class = ModelPerformanceMetricSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'model_id'

class DataDriftListView(generics.ListAPIView):
    serializer_class = DataDriftDetectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DataDriftDetection.objects.all().order_by('-detection_date')

class DataDriftDetailView(generics.ListAPIView):
    serializer_class = DataDriftDetectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        model_id = self.kwargs['model_id']
        return DataDriftDetection.objects.filter(model_id=model_id)

class ModelRetrainingView(generics.CreateAPIView):
    serializer_class = ModelRetrainingJobSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(triggered_by=self.request.user)

class RetrainingJobsView(generics.ListAPIView):
    serializer_class = ModelRetrainingJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ModelRetrainingJob.objects.all().order_by('-created_at')

class FeatureImportanceView(generics.ListAPIView):
    serializer_class = FeatureImportanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FeatureImportance.objects.all().order_by('-calculated_at')

class FeatureImportanceDetailView(generics.ListAPIView):
    serializer_class = FeatureImportanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        model_id = self.kwargs['model_id']
        return FeatureImportance.objects.filter(model_id=model_id).order_by('importance_rank')


class OCRImageProcessView(APIView):
    """
    API view for processing images with OCR to extract text.
    
    This endpoint accepts image uploads and returns extracted text using
    the TrOCR model for optical character recognition.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Process an uploaded image and extract text using OCR.
        
        Expected payload:
        - image: Image file (JPEG, PNG, BMP, TIFF, GIF)
        
        Returns:
        - extracted_text: Text found in the image
        - text_length: Number of characters extracted
        - status: Processing status
        - processing_time: Time taken for processing
        """
        start_time = time.time()
        
        try:
            # Validate the request data
            serializer = OCRRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid request data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the uploaded image
            image_file = serializer.validated_data['image']
            
            # Process the image with OCR
            try:
                # Convert uploaded file to bytes for processing
                image_bytes = io.BytesIO(image_file.read())
                result = extract_text_from_image_bytes(image_bytes)
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Prepare response data
                response_data = {
                    'extracted_text': result['extracted_text'],
                    'text_length': len(result['extracted_text']),
                    'status': 'success',
                    'processing_time': processing_time
                }
                
                # Validate response data
                response_serializer = OCRResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    logger.info(f"OCR processing completed successfully. Extracted {len(result['extracted_text'])} characters in {processing_time:.2f}s")
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {'error': 'Response validation failed', 'details': response_serializer.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                processing_time = time.time() - start_time
                logger.error(f"OCR processing failed: {str(e)}")
                
                error_response = {
                    'extracted_text': '',
                    'text_length': 0,
                    'status': 'error',
                    'error_message': str(e),
                    'processing_time': processing_time
                }
                
                return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"OCR API error: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ComplaintImageOCRView(APIView):
    """
    Advanced OCR view for complaint images with additional NLP processing.
    
    This endpoint processes complaint images, extracts text, and optionally
    performs named entity recognition and complaint classification.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Process a complaint image with OCR and optional NLP analysis.
        
        Expected payload:
        - image: Complaint image file
        - extract_entities: Boolean (optional, default True)
        - classify_complaint: Boolean (optional, default True)
        
        Returns:
        - extracted_text: Text extracted from image
        - entities: Named entities (if requested)
        - classification: Complaint classification (if requested)
        - sentiment: Sentiment analysis results
        """
        start_time = time.time()
        
        try:
            # Validate request data
            serializer = ComplaintImageOCRSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid request data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = serializer.validated_data['image']
            extract_entities = serializer.validated_data.get('extract_entities', True)
            classify_complaint = serializer.validated_data.get('classify_complaint', True)
            
            # Process image with OCR
            try:
                image_bytes = io.BytesIO(image_file.read())
                ocr_result = extract_text_from_image_bytes(image_bytes)
                extracted_text = ocr_result['extracted_text']
                
                # Prepare response data
                response_data = {
                    'extracted_text': extracted_text,
                    'text_length': len(extracted_text),
                    'status': 'success',
                    'processing_time': time.time() - start_time
                }
                
                # Optional NLP processing
                if extracted_text and len(extracted_text.strip()) > 0:
                    
                    # Named Entity Recognition (if requested)
                    if extract_entities:
                        try:
                            # This would integrate with your existing NLP pipeline
                            # For now, we'll provide a placeholder
                            response_data['entities'] = {
                                'persons': [],
                                'locations': [],
                                'organizations': [],
                                'dates': [],
                                'note': 'NLP entity extraction would be implemented here'
                            }
                        except Exception as e:
                            logger.warning(f"Entity extraction failed: {str(e)}")
                            response_data['entities'] = {'error': 'Entity extraction failed'}
                    
                    # Complaint Classification (if requested)
                    if classify_complaint:
                        try:
                            # This would integrate with your existing classification service
                            response_data['classification'] = {
                                'category': 'GENERAL',
                                'confidence': 0.0,
                                'department': 'General Administration',
                                'note': 'Complaint classification would be implemented here'
                            }
                        except Exception as e:
                            logger.warning(f"Complaint classification failed: {str(e)}")
                            response_data['classification'] = {'error': 'Classification failed'}
                    
                    # Basic sentiment analysis placeholder
                    response_data['sentiment'] = {
                        'polarity': 'neutral',
                        'confidence': 0.5,
                        'note': 'Sentiment analysis would be implemented here'
                    }
                
                # Validate and return response
                response_serializer = ComplaintImageOCRResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    logger.info(f"Complaint image OCR completed successfully in {response_data['processing_time']:.2f}s")
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {'error': 'Response validation failed', 'details': response_serializer.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                processing_time = time.time() - start_time
                logger.error(f"Complaint image OCR processing failed: {str(e)}")
                
                error_response = {
                    'extracted_text': '',
                    'text_length': 0,
                    'status': 'error',
                    'error_message': str(e),
                    'processing_time': processing_time
                }
                
                return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Complaint image OCR API error: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OCRHealthCheckView(APIView):
    """
    Health check endpoint for OCR services.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check if OCR services are available."""
        try:
            # Test if OCR processor is initialized
            processor = get_ocr_processor()
            if processor.pipeline is None:
                return Response(
                    {
                        'status': 'error',
                        'message': 'OCR pipeline not initialized',
                        'available': False
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            return Response(
                {
                    'status': 'healthy',
                    'message': 'OCR services are operational',
                    'available': True,
                    'model': 'microsoft/trocr-base-printed'
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"OCR health check failed: {str(e)}")
            return Response(
                {
                    'status': 'error',
                    'message': str(e),
                    'available': False
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class EnhancedOCRImageProcessView(APIView):
    """
    Enhanced OCR processing with advanced features, preprocessing, and performance metrics.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Process uploaded image with enhanced OCR capabilities."""
        try:
            start_time = time.time()
            
            # Validate request data
            serializer = OCRRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid request data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get uploaded image
            image_file = serializer.validated_data['image']
            preprocess = request.data.get('preprocess', 'true').lower() == 'true'
            include_regions = request.data.get('include_regions', 'false').lower() == 'true'
            
            if not isinstance(image_file, InMemoryUploadedFile):
                return Response(
                    {'error': 'Invalid image file'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Enhanced OCR processing image: {image_file.name}, size: {image_file.size}, preprocess: {preprocess}")
            
            try:
                # Create a BytesIO object from the uploaded file
                image_io = io.BytesIO(image_file.read())
                
                # Get advanced OCR processor
                ocr_processor = get_ocr_processor()
                
                # Load image
                from PIL import Image
                image = Image.open(image_io)
                
                # Process with advanced OCR
                result = ocr_processor.extract_text_advanced(
                    image, 
                    preprocess=preprocess,
                    confidence_threshold=0.3
                )
                
                # Add region analysis if requested
                if include_regions:
                    try:
                        # Region extraction temporarily disabled
                        # with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        #     image.save(temp_file.name, 'PNG')
                        #     region_result = extract_text_with_regions(temp_file.name)
                        #     result.update({
                        #         'text_regions': region_result.get('text_regions', []),
                        #         'total_lines': region_result.get('total_lines', 0)
                        #     })
                        #     os.unlink(temp_file.name)
                        result.update({
                            'text_regions': [],
                            'total_lines': 0
                        })
                    except Exception as e:
                        logger.warning(f"Region analysis failed: {str(e)}")
                        result['regions_error'] = str(e)
                
                # Prepare enhanced response
                response_data = {
                    'extracted_text': result['extracted_text'],
                    'text_length': result['character_count'],
                    'word_count': result['word_count'],
                    'confidence': result['confidence'],
                    'processing_time': result['processing_time'],
                    'preprocessing_applied': result['preprocessing_applied'],
                    'model_used': result['model_used'],
                    'device_used': result['device_used'],
                    'status': 'success'
                }
                
                # Add region data if available
                if 'text_regions' in result:
                    response_data['text_regions'] = result['text_regions']
                    response_data['total_lines'] = result['total_lines']
                
                logger.info(f"Enhanced OCR completed: {result['character_count']} chars, "
                           f"confidence: {result['confidence']:.2f}, time: {result['processing_time']:.2f}s")
                
                return Response(response_data, status=status.HTTP_200_OK)
                
            except Exception as e:
                processing_time = time.time() - start_time
                logger.error(f"Enhanced OCR processing failed: {str(e)}")
                
                return Response({
                    'extracted_text': '',
                    'text_length': 0,
                    'status': 'error',
                    'error_message': str(e),
                    'processing_time': processing_time
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Enhanced OCR API error: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OCRPerformanceStatsView(APIView):
    """
    Get OCR system performance statistics and health information.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get OCR performance statistics."""
        try:
            stats = get_ocr_performance_stats()
            # health = ocr_health_check()  # Function not implemented
            health = {'status': 'available', 'fallback_mode': True}
            
            response_data = {
                'performance_stats': stats,
                'health_status': health,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"OCR performance stats error: {str(e)}")
            return Response(
                {'error': 'Failed to get performance stats', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OCRBatchProcessView(APIView):
    """
    Process multiple images in batch for better performance.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Process multiple images in batch."""
        try:
            start_time = time.time()
            
            # Get uploaded images
            image_files = request.FILES.getlist('images')
            if not image_files:
                return Response(
                    {'error': 'No images provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(image_files) > 10:  # Limit batch size
                return Response(
                    {'error': 'Too many images. Maximum 10 images per batch.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Batch OCR processing {len(image_files)} images")
            
            # Get OCR processor
            ocr_processor = get_ocr_processor()
            
            # Process images
            results = []
            images = []
            
            # Load all images first
            for i, image_file in enumerate(image_files):
                try:
                    image_io = io.BytesIO(image_file.read())
                    from PIL import Image
                    image = Image.open(image_io)
                    images.append(image)
                except Exception as e:
                    results.append({
                        'image_index': i,
                        'filename': image_file.name,
                        'extracted_text': '',
                        'status': 'error',
                        'error_message': f"Failed to load image: {str(e)}"
                    })
                    images.append(None)
            
            # Process valid images in batch
            valid_images = [img for img in images if img is not None]
            if valid_images:
                batch_results = ocr_processor.batch_extract_text(valid_images)
                
                # Merge results
                valid_index = 0
                for i, image in enumerate(images):
                    if image is not None:
                        batch_result = batch_results[valid_index]
                        results.append({
                            'image_index': i,
                            'filename': image_files[i].name,
                            'extracted_text': batch_result['extracted_text'],
                            'confidence': batch_result.get('confidence', 0.0),
                            'character_count': batch_result.get('character_count', 0),
                            'word_count': batch_result.get('word_count', 0),
                            'processing_time': batch_result.get('processing_time', 0.0),
                            'status': 'success' if 'error' not in batch_result else 'error',
                            'error_message': batch_result.get('error', '')
                        })
                        valid_index += 1
            
            total_time = time.time() - start_time
            
            response_data = {
                'results': results,
                'total_images': len(image_files),
                'successful_extractions': len([r for r in results if r['status'] == 'success']),
                'total_processing_time': total_time,
                'status': 'completed'
            }
            
            logger.info(f"Batch OCR completed: {len(results)} images in {total_time:.2f}s")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Batch OCR error: {str(e)}")
            return Response(
                {'error': 'Batch processing failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MultimodalVideoAnalysisView(APIView):
    """
    API endpoint for multimodal video complaint analysis.
    Analyzes video complaints using audio, visual, and text analysis.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Analyze uploaded video complaint.
        
        Expected input:
        - video: Video file upload
        - groq_api_key: Optional Groq API key for AI response generation
        
        Returns:
        - Complete multimodal analysis with AI-generated response
        """
        try:
            # Get video file
            if 'video' not in request.FILES:
                return Response(
                    {'error': 'No video file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            video_file = request.FILES['video']
            
            # Save video temporarily
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            temp_video_path = os.path.join(temp_dir, f"complaint_{int(time.time())}_{video_file.name}")
            
            with open(temp_video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            
            # Get optional Groq API key
            groq_api_key = request.data.get('groq_api_key') or os.environ.get('GROQ_API_KEY')
            
            # Import and use multimodal analyzer
            from .multimodal_analyzer import get_multimodal_analyzer
            
            analyzer = get_multimodal_analyzer(groq_api_key)
            result = analyzer.analyze_video_complaint(temp_video_path)
            
            # Clean up temp file
            try:
                os.remove(temp_video_path)
            except:
                pass
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result.get('error', 'Analysis failed')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Multimodal video analysis error: {str(e)}")
            return Response(
                {'error': 'Video analysis failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AudioTranscriptionView(APIView):
    """
    API endpoint for audio transcription and analysis.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Transcribe and analyze audio file.
        
        Expected input:
        - audio: Audio file upload
        
        Returns:
        - Transcription, emotion, and urgency analysis
        """
        try:
            if 'audio' not in request.FILES:
                return Response(
                    {'error': 'No audio file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            audio_file = request.FILES['audio']
            
            # Save audio temporarily
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            temp_audio_path = os.path.join(temp_dir, f"audio_{int(time.time())}_{audio_file.name}")
            
            with open(temp_audio_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            # Analyze audio
            from .audio_analyzer import get_audio_analyzer
            
            analyzer = get_audio_analyzer()
            result = analyzer.analyze_audio(temp_audio_path)
            
            # Clean up temp file
            try:
                os.remove(temp_audio_path)
            except:
                pass
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result.get('error', 'Analysis failed')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Audio transcription error: {str(e)}")
            return Response(
                {'error': 'Audio analysis failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VisualObjectDetectionView(APIView):
    """
    API endpoint for visual object detection in images.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Detect objects in uploaded image.
        
        Expected input:
        - image: Image file upload
        
        Returns:
        - Detected objects and scene classification
        """
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            
            # Save image temporarily
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            temp_image_path = os.path.join(temp_dir, f"image_{int(time.time())}_{image_file.name}")
            
            with open(temp_image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            # Analyze image
            from .visual_analyzer import get_visual_analyzer
            
            analyzer = get_visual_analyzer()
            result = analyzer.analyze_image(temp_image_path)
            
            # Clean up temp file
            try:
                os.remove(temp_image_path)
            except:
                pass
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result.get('error', 'Analysis failed')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Visual object detection error: {str(e)}")
            return Response(
                {'error': 'Visual analysis failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
