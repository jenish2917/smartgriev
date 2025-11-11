from rest_framework import serializers
from .models import Complaint, Department, ComplaintCategory, AuditTrail, IncidentLocationHistory, GPSValidation
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

class ComplaintCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintCategory
        fields = ('id', 'name', 'description', 'is_active')

class DepartmentSerializer(serializers.ModelSerializer):
    officer = UserMiniSerializer(read_only=True)
    officer_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.filter(is_officer=True),
        source='officer'
    )

    class Meta:
        model = Department
        fields = ('id', 'name', 'zone', 'officer', 'officer_id')

class ComplaintSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Department.objects.all(),
        source='department'
    )
    incident_coordinates = serializers.SerializerMethodField(read_only=True)
    
    # Field aliases for frontend compatibility
    citizen = serializers.IntegerField(source='user.id', read_only=True)
    assigned_official = serializers.IntegerField(source='department.officer.id', read_only=True, allow_null=True)
    urgency = serializers.CharField(source='urgency_level', required=False)
    latitude = serializers.FloatField(source='incident_latitude', required=False, allow_null=True)
    longitude = serializers.FloatField(source='incident_longitude', required=False, allow_null=True)
    address = serializers.CharField(source='incident_address', required=False, allow_blank=True, allow_null=True)
    landmark = serializers.CharField(source='incident_landmark', required=False, allow_blank=True, allow_null=True)
    audio_file_url = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    resolved_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = Complaint
        fields = ('id', 'user', 'citizen', 'assigned_official', 'complaint_number', 'title', 'description', 
                 'category', 'sentiment', 'department', 'department_id', 'status', 'priority',
                 'urgency', 'urgency_level',
                 # Multimodal input fields
                 'audio_file', 'audio_file_url', 'image_file', 'image', 'media',
                 # Multimodal analysis results
                 'audio_transcription', 'image_ocr_text', 'detected_objects',
                 # Location fields - original names
                 'incident_latitude', 'incident_longitude', 'incident_address', 
                 'incident_landmark', 'gps_accuracy', 'location_method', 'area_type',
                 'location_lat', 'location_lon', 'incident_coordinates',
                 # Location fields - frontend aliases
                 'latitude', 'longitude', 'address', 'landmark',
                 # AI processing results
                 'ai_confidence_score', 'ai_processed_text', 'department_classification',
                 'gemini_raw_response',
                 # Timestamps
                 'created_at', 'updated_at', 'resolved_at')
        read_only_fields = ('user', 'complaint_number', 'sentiment', 'created_at', 'updated_at', 
                           'audio_transcription', 'image_ocr_text', 
                           'detected_objects', 'ai_confidence_score', 'ai_processed_text',
                           'department_classification', 'gemini_raw_response', 'resolved_at',
                           'citizen', 'assigned_official', 'audio_file_url', 'image')
    
    def get_audio_file_url(self, obj):
        """Return audio file URL if available"""
        if obj.audio_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None
    
    def get_image(self, obj):
        """Return image URL - check both image_file and media fields"""
        image = obj.image_file or obj.media
        if image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.url)
            return image.url
        return None

    def get_incident_coordinates(self, obj):
        """Return formatted incident coordinates"""
        return obj.get_incident_coordinates()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        """Validate GPS coordinates"""
        incident_lat = data.get('incident_latitude')
        incident_lon = data.get('incident_longitude')
        
        if incident_lat is not None and incident_lon is not None:
            # Validate latitude range (-90 to 90)
            if not (-90 <= incident_lat <= 90):
                raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
            
            # Validate longitude range (-180 to 180)
            if not (-180 <= incident_lon <= 180):
                raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
            
            # Check GPS accuracy
            accuracy = data.get('gps_accuracy')
            if accuracy is not None and accuracy > 100:  # More than 100 meters
                raise serializers.ValidationError("GPS accuracy is too low. Please try again for better accuracy.")
        
        return data

class ComplaintStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ('status', 'priority')
        read_only_fields = ('priority',)

    def update(self, instance, validated_data):
        old_status = instance.status
        updated_instance = super().update(instance, validated_data)
        
        # Create audit trail
        if old_status != updated_instance.status:
            AuditTrail.objects.create(
                complaint=updated_instance,
                action=f'status_changed_from_{old_status}_to_{updated_instance.status}',
                by_user=self.context['request'].user
            )
        
        return updated_instance

class AuditTrailSerializer(serializers.ModelSerializer):
    by_user = UserMiniSerializer(read_only=True)
    complaint = ComplaintSerializer(read_only=True)
    
    class Meta:
        model = AuditTrail
        fields = ('id', 'complaint', 'action', 'by_user', 'timestamp')

class AuditTrailSerializer(serializers.ModelSerializer):
    by_user = UserMiniSerializer(read_only=True)
    complaint = serializers.SerializerMethodField()

    class Meta:
        model = AuditTrail
        fields = ('id', 'complaint', 'action', 'by_user', 'timestamp')

    def get_complaint(self, obj):
        return {
            'id': obj.complaint.id,
            'title': obj.complaint.title
        }

class IncidentLocationHistorySerializer(serializers.ModelSerializer):
    updated_by = UserMiniSerializer(read_only=True)
    complaint_title = serializers.CharField(source='complaint.title', read_only=True)
    
    class Meta:
        model = IncidentLocationHistory
        fields = ('id', 'complaint', 'complaint_title', 'latitude', 'longitude', 
                 'accuracy', 'address', 'updated_by', 'update_reason', 
                 'is_verified', 'verification_method', 'created_at')
        read_only_fields = ('updated_by', 'created_at')
    
    def create(self, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

class GPSValidationSerializer(serializers.ModelSerializer):
    validated_by = UserMiniSerializer(read_only=True)
    complaint_title = serializers.CharField(source='complaint.title', read_only=True)
    
    class Meta:
        model = GPSValidation
        fields = ('id', 'complaint', 'complaint_title', 'is_valid', 'validation_score',
                 'accuracy_check', 'range_check', 'duplicate_check', 'speed_check',
                 'validation_notes', 'validated_at', 'validated_by')
        read_only_fields = ('validated_by', 'validated_at')

class ComplaintLocationUpdateSerializer(serializers.ModelSerializer):
    """Specialized serializer for updating incident location"""
    
    class Meta:
        model = Complaint
        fields = ('incident_latitude', 'incident_longitude', 'incident_address', 
                 'incident_landmark', 'gps_accuracy', 'location_method', 'area_type')
    
    def validate(self, data):
        """Validate GPS coordinates for location updates"""
        incident_lat = data.get('incident_latitude')
        incident_lon = data.get('incident_longitude')
        
        if incident_lat is not None and incident_lon is not None:
            # Validate latitude range
            if not (-90 <= incident_lat <= 90):
                raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
            
            # Validate longitude range
            if not (-180 <= incident_lon <= 180):
                raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
        
        return data


class MultimodalComplaintSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for creating complaints with multimodal inputs
    (text, audio, image) - Video upload removed as per requirements
    """
    user = UserMiniSerializer(read_only=True)
    process_multimodal = serializers.BooleanField(write_only=True, default=True, required=False,
                                                   help_text="Process uploaded files with AI analysis")
    
    class Meta:
        model = Complaint
        fields = ('id', 'user', 'title', 'description',
                 # Multimodal inputs (video removed)
                 'audio_file', 'image_file',
                 # Optional text inputs
                 'category', 'priority', 'urgency_level',
                 # Location
                 'incident_latitude', 'incident_longitude', 'incident_address',
                 'incident_landmark', 'area_type', 'location_method',
                 # Processing flag
                 'process_multimodal',
                 # Read-only processed results (video removed)
                 'audio_transcription', 'image_ocr_text',
                 'detected_objects', 'ai_processed_text', 'department_classification',
                 'ai_confidence_score', 'sentiment', 'department',
                 # Timestamps
                 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at',
                           'audio_transcription', 'image_ocr_text',
                           'detected_objects', 'ai_processed_text', 'department_classification',
                           'ai_confidence_score', 'sentiment', 'department')
    
    def validate(self, data):
        """Validate that at least one input method is provided"""
        description = data.get('description', '').strip()
        audio_file = data.get('audio_file')
        image_file = data.get('image_file')
        
        # At least one input method must be provided (video removed)
        if not any([description, audio_file, image_file]):
            raise serializers.ValidationError(
                "Please provide at least one of: description text, audio file, or image file"
            )
        
        # Validate file sizes
        max_audio_size = 25 * 1024 * 1024   # 25MB
        max_image_size = 10 * 1024 * 1024   # 10MB
        
        if audio_file and audio_file.size > max_audio_size:
            raise serializers.ValidationError(f"Audio file too large. Maximum size is 25MB")
        
        if image_file and image_file.size > max_image_size:
            raise serializers.ValidationError(f"Image file too large. Maximum size is 10MB")
        
        return data
    
    def create(self, validated_data):
        # Remove process_multimodal flag from data
        process_multimodal = validated_data.pop('process_multimodal', True)
        
        # Set user if authenticated, otherwise set to None (anonymous complaint)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        else:
            # For anonymous complaints, user field should be nullable
            # Make sure to handle this in the model if needed
            validated_data['user'] = None
        
        # Create complaint
        complaint = super().create(validated_data)
        
        # FAST TRACK: Skip heavy AI processing for now - process in background later
        # This makes complaint submission instant instead of taking 30+ seconds
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Complaint created (ID: {complaint.id}). AI processing skipped for speed.")
        
        # You can process multimodal inputs later using a background task (Celery)
        # if process_multimodal:
        #     self._process_multimodal_inputs(complaint)
        
        return complaint
    
    def _process_multimodal_inputs(self, complaint):
        """Process uploaded files with AI analysis (video removed)"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Process image if uploaded
            if complaint.image_file:
                self._process_image(complaint)
            
            # Process audio if uploaded
            elif complaint.audio_file:
                self._process_audio(complaint)
            
            complaint.save()
            
        except Exception as e:
            logger.error(f"Multimodal processing failed: {str(e)}")
            # Don't fail the complaint creation, just log the error
    
    def _process_image(self, complaint):
        """Process image complaint with YOLO, OCR, and multiple AI models"""
        import logging
        import json
        logger = logging.getLogger(__name__)
        
        try:
            # Use advanced multi-model image processor
            from machine_learning.advanced_image_processor import get_image_processor
            
            logger.info(f"Processing image with advanced multi-model analysis: {complaint.image_file.path}")
            
            # Get the advanced image processor
            image_processor = get_image_processor()
            
            # Run comprehensive analysis with YOLO, OCR, CLIP, ResNet, etc.
            analysis_result = image_processor.analyze_image(complaint.image_file.path)
            
            if analysis_result.get('success'):
                logger.info(f"Advanced image analysis completed successfully. Models used: {analysis_result.get('models_used', [])}")
                
                # Extract OCR text from multiple OCR engines
                if 'ocr_extraction' in analysis_result:
                    ocr_data = analysis_result['ocr_extraction']
                    if ocr_data.get('text_found'):
                        complaint.image_ocr_text = ocr_data.get('extracted_text', '')
                        logger.info(f"OCR text extracted ({len(complaint.image_ocr_text)} chars) using: {ocr_data.get('methods_used', [])}")
                
                # Extract detected objects from YOLO
                detected_objects_list = []
                if 'yolo_detection' in analysis_result:
                    yolo_data = analysis_result['yolo_detection']
                    if yolo_data.get('success'):
                        yolo_objects = yolo_data.get('object_classes', [])
                        detected_objects_list.extend(yolo_objects)
                        logger.info(f"YOLO detected {len(yolo_objects)} object types: {yolo_objects}")
                
                # Add scene classification from CLIP
                if 'scene_analysis' in analysis_result:
                    scene_data = analysis_result['scene_analysis']
                    if scene_data.get('success'):
                        primary_scene = scene_data.get('primary_scene', '')
                        if primary_scene:
                            detected_objects_list.append(f"Scene: {primary_scene}")
                            logger.info(f"CLIP identified scene: {primary_scene} (confidence: {scene_data.get('primary_confidence', 0):.2f})")
                
                # Add ResNet classification
                if 'image_classification' in analysis_result:
                    resnet_data = analysis_result['image_classification']
                    if resnet_data.get('success'):
                        primary_class = resnet_data.get('primary_class', '')
                        if primary_class:
                            detected_objects_list.append(f"Type: {primary_class}")
                            logger.info(f"ResNet classification: {primary_class}")
                
                # Store all detected objects
                complaint.detected_objects = list(set(detected_objects_list))
                
                # Extract complaint-specific analysis
                if 'complaint_analysis' in analysis_result:
                    comp_data = analysis_result['complaint_analysis']
                    
                    # Auto-assign category
                    category = comp_data.get('category', 'general')
                    complaint.department_classification = {
                        'category': category,
                        'severity': comp_data.get('severity', 'low'),
                        'keywords': comp_data.get('keywords', []),
                        'damage_detected': comp_data.get('damage_detected', False),
                        'waste_detected': comp_data.get('waste_detected', False),
                        'infrastructure_issue': comp_data.get('infrastructure_issue', False)
                    }
                    logger.info(f"Complaint classified as: {category} (severity: {comp_data.get('severity')})")
                
                # Get analysis summary
                if 'summary' in analysis_result:
                    summary_data = analysis_result['summary']
                    
                    # Set AI confidence score
                    complaint.ai_confidence_score = summary_data.get('overall_confidence', 0.0)
                    
                    # Auto-set priority based on recommendation
                    recommended_priority = summary_data.get('recommended_priority', 'medium')
                    if not complaint.priority or complaint.priority == 'medium':
                        complaint.priority = recommended_priority
                    
                    # Generate AI processed text summary
                    summary_parts = []
                    if summary_data.get('detected_items'):
                        summary_parts.append(f"Detected: {', '.join(summary_data['detected_items'][:5])}")
                    if summary_data.get('extracted_text_summary'):
                        summary_parts.append(f"Text: {summary_data['extracted_text_summary']}")
                    if summary_data.get('analysis_notes'):
                        summary_parts.append(' | '.join(summary_data['analysis_notes']))
                    
                    complaint.ai_processed_text = ' | '.join(summary_parts)
                    
                    logger.info(f"Analysis summary generated. Confidence: {complaint.ai_confidence_score:.2f}, Priority: {recommended_priority}")
                
                # Image quality check
                if 'image_quality' in analysis_result:
                    quality = analysis_result['image_quality']
                    if not quality.get('is_acceptable', True):
                        logger.warning(f"Image quality is low (score: {quality.get('quality_score', 0):.1f})")
                
                logger.info("Multi-model image processing completed successfully")
            else:
                logger.error(f"Advanced image analysis failed: {analysis_result.get('error', 'Unknown error')}")
                # Fallback to basic processing
                self._process_image_fallback(complaint)
                
        except Exception as e:
            logger.error(f"Advanced image processing failed: {str(e)}")
            # Try fallback processing
            try:
                self._process_image_fallback(complaint)
            except Exception as fallback_error:
                logger.error(f"Fallback processing also failed: {str(fallback_error)}")
    
    def _process_image_fallback(self, complaint):
        """Fallback image processing using legacy methods"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            from machine_learning.ocr_processor import get_ocr_processor
            from machine_learning.visual_analyzer import get_visual_analyzer
            from PIL import Image
            
            logger.info("Using fallback image processing methods")
            
            # Extract text from image using OCR
            ocr_processor = get_ocr_processor()
            image = Image.open(complaint.image_file.path)
            ocr_result = ocr_processor.extract_text_advanced(image)
            complaint.image_ocr_text = ocr_result.get('extracted_text', '')
            
            # Detect objects using visual analyzer
            visual_analyzer = get_visual_analyzer()
            visual_result = visual_analyzer.analyze_image(complaint.image_file.path)
            if visual_result.get('success'):
                complaint.detected_objects = visual_result.get('detected_objects', [])
            
            logger.info("Fallback processing completed")
                
        except Exception as e:
            logger.warning(f"Fallback image processing failed: {str(e)}")
    
    def _process_audio(self, complaint):
        """Process audio complaint"""
        try:
            from machine_learning.audio_analyzer import get_audio_analyzer
            
            analyzer = get_audio_analyzer()
            result = analyzer.analyze_audio(complaint.audio_file.path)
            
            if result.get('success'):
                complaint.audio_transcription = result.get('transcription', '')
                complaint.ai_confidence_score = result.get('confidence', 0.0)
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Audio processing failed: {str(e)}")
    
    def _auto_assign_department(self, complaint, department_name):
        """Auto-assign department based on classification"""
        try:
            from .models import Department
            department = Department.objects.filter(name__icontains=department_name).first()
            if department:
                complaint.department = department
        except Exception:
            pass
