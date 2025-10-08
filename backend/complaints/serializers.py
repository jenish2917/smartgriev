from rest_framework import serializers
from .models import Complaint, Department, AuditTrail, IncidentLocationHistory, GPSValidation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

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

    class Meta:
        model = Complaint
        fields = ('id', 'user', 'title', 'description', 'media', 'category',
                 'sentiment', 'department', 'department_id', 'status', 'priority',
                 # Multimodal input fields
                 'audio_file', 'image_file', 'video_file',
                 # Multimodal analysis results
                 'video_analysis', 'audio_transcription', 'image_ocr_text', 'detected_objects',
                 # Location fields
                 'incident_latitude', 'incident_longitude', 'incident_address', 
                 'incident_landmark', 'gps_accuracy', 'location_method', 'area_type',
                 'location_lat', 'location_lon', 'incident_coordinates',
                 # AI processing results
                 'ai_confidence_score', 'ai_processed_text', 'department_classification',
                 # Timestamps
                 'created_at', 'updated_at')
        read_only_fields = ('user', 'sentiment', 'created_at', 'updated_at', 
                           'video_analysis', 'audio_transcription', 'image_ocr_text', 
                           'detected_objects', 'ai_confidence_score', 'ai_processed_text',
                           'department_classification')

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
    (text, audio, image, video)
    """
    user = UserMiniSerializer(read_only=True)
    process_multimodal = serializers.BooleanField(write_only=True, default=True, required=False,
                                                   help_text="Process uploaded files with AI analysis")
    
    class Meta:
        model = Complaint
        fields = ('id', 'user', 'title', 'description',
                 # Multimodal inputs
                 'audio_file', 'image_file', 'video_file',
                 # Optional text inputs
                 'category', 'priority', 'urgency_level',
                 # Location
                 'incident_latitude', 'incident_longitude', 'incident_address',
                 'incident_landmark', 'area_type', 'location_method',
                 # Processing flag
                 'process_multimodal',
                 # Read-only processed results
                 'audio_transcription', 'image_ocr_text', 'video_analysis',
                 'detected_objects', 'ai_processed_text', 'department_classification',
                 'ai_confidence_score', 'sentiment', 'department',
                 # Timestamps
                 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at',
                           'audio_transcription', 'image_ocr_text', 'video_analysis',
                           'detected_objects', 'ai_processed_text', 'department_classification',
                           'ai_confidence_score', 'sentiment', 'department')
    
    def validate(self, data):
        """Validate that at least one input method is provided"""
        description = data.get('description', '').strip()
        audio_file = data.get('audio_file')
        image_file = data.get('image_file')
        video_file = data.get('video_file')
        
        # At least one input method must be provided
        if not any([description, audio_file, image_file, video_file]):
            raise serializers.ValidationError(
                "Please provide at least one of: description text, audio file, image file, or video file"
            )
        
        # Validate file sizes
        max_video_size = 100 * 1024 * 1024  # 100MB
        max_audio_size = 25 * 1024 * 1024   # 25MB
        max_image_size = 10 * 1024 * 1024   # 10MB
        
        if video_file and video_file.size > max_video_size:
            raise serializers.ValidationError(f"Video file too large. Maximum size is 100MB")
        
        if audio_file and audio_file.size > max_audio_size:
            raise serializers.ValidationError(f"Audio file too large. Maximum size is 25MB")
        
        if image_file and image_file.size > max_image_size:
            raise serializers.ValidationError(f"Image file too large. Maximum size is 10MB")
        
        return data
    
    def create(self, validated_data):
        # Remove process_multimodal flag from data
        process_multimodal = validated_data.pop('process_multimodal', True)
        
        # Set user
        validated_data['user'] = self.context['request'].user
        
        # Create complaint
        complaint = super().create(validated_data)
        
        # Process multimodal inputs if requested
        if process_multimodal:
            self._process_multimodal_inputs(complaint)
        
        return complaint
    
    def _process_multimodal_inputs(self, complaint):
        """Process uploaded files with AI analysis"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Process video if uploaded
            if complaint.video_file:
                self._process_video(complaint)
            
            # Process image if uploaded
            elif complaint.image_file:
                self._process_image(complaint)
            
            # Process audio if uploaded
            elif complaint.audio_file:
                self._process_audio(complaint)
            
            complaint.save()
            
        except Exception as e:
            logger.error(f"Multimodal processing failed: {str(e)}")
            # Don't fail the complaint creation, just log the error
    
    def _process_video(self, complaint):
        """Process video complaint"""
        try:
            from machine_learning.multimodal_analyzer import get_multimodal_analyzer
            import os
            
            analyzer = get_multimodal_analyzer(os.environ.get('GROQ_API_KEY'))
            result = analyzer.analyze_video_complaint(complaint.video_file.path)
            
            if result.get('success'):
                complaint.video_analysis = result
                complaint.audio_transcription = result.get('transcription', '')
                complaint.detected_objects = result.get('detected_objects', [])
                complaint.ai_processed_text = result.get('ai_response', '')
                complaint.ai_confidence_score = result.get('confidence', 0.0)
                
                # Auto-classify department if detected
                if result.get('suggested_department'):
                    self._auto_assign_department(complaint, result['suggested_department'])
                    
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Video processing failed: {str(e)}")
    
    def _process_image(self, complaint):
        """Process image complaint with OCR"""
        try:
            from machine_learning.ocr_processor import get_ocr_processor
            from machine_learning.visual_analyzer import get_visual_analyzer
            from PIL import Image
            
            # Extract text from image
            ocr_processor = get_ocr_processor()
            image = Image.open(complaint.image_file.path)
            ocr_result = ocr_processor.extract_text_advanced(image)
            complaint.image_ocr_text = ocr_result.get('extracted_text', '')
            
            # Detect objects
            visual_analyzer = get_visual_analyzer()
            visual_result = visual_analyzer.analyze_image(complaint.image_file.path)
            if visual_result.get('success'):
                complaint.detected_objects = visual_result.get('detected_objects', [])
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Image processing failed: {str(e)}")
    
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
