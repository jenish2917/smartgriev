from rest_framework import serializers
from .models import (
    MLExperiment, ExperimentResult, ModelPerformanceMetric,
    DataDriftDetection, ModelRetrainingJob, FeatureImportance,
    PredictionExplanation
)

class MLExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLExperiment
        fields = '__all__'
        read_only_fields = ('created_by', 'statistical_significance', 'p_value', 'effect_size', 'winner')

class ExperimentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentResult
        fields = '__all__'

class ModelPerformanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelPerformanceMetric
        fields = '__all__'

class DataDriftDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDriftDetection
        fields = '__all__'

class ModelRetrainingJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelRetrainingJob
        fields = '__all__'
        read_only_fields = ('triggered_by', 'job_id', 'started_at', 'completed_at')

class FeatureImportanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureImportance
        fields = '__all__'

class PredictionExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionExplanation
        fields = '__all__'


class OCRRequestSerializer(serializers.Serializer):
    """Serializer for OCR image upload requests."""
    image = serializers.ImageField(required=True, help_text="Image file to extract text from")
    
    def validate_image(self, value):
        """Validate the uploaded image."""
        # Check file size (limit to 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image file too large. Maximum size is 10MB.")
        
        # Check file format
        allowed_formats = ['JPEG', 'PNG', 'BMP', 'TIFF', 'GIF']
        if hasattr(value, 'image') and value.image.format not in allowed_formats:
            raise serializers.ValidationError(f"Unsupported image format. Allowed formats: {', '.join(allowed_formats)}")
        
        return value


class OCRResponseSerializer(serializers.Serializer):
    """Serializer for OCR response data."""
    extracted_text = serializers.CharField(help_text="Text extracted from the image")
    text_length = serializers.IntegerField(help_text="Length of extracted text in characters")
    status = serializers.CharField(help_text="Processing status (success/error)")
    error_message = serializers.CharField(required=False, help_text="Error message if processing failed")
    processing_time = serializers.FloatField(required=False, help_text="Processing time in seconds")


class ComplaintImageOCRSerializer(serializers.Serializer):
    """Serializer for complaint image OCR with additional processing."""
    image = serializers.ImageField(required=True, help_text="Complaint image to process")
    extract_entities = serializers.BooleanField(default=True, help_text="Whether to extract named entities from text")
    classify_complaint = serializers.BooleanField(default=True, help_text="Whether to classify the complaint")
    
    def validate_image(self, value):
        """Validate the uploaded complaint image."""
        # Check file size (limit to 15MB for complaint images)
        if value.size > 15 * 1024 * 1024:
            raise serializers.ValidationError("Image file too large. Maximum size is 15MB.")
        
        return value


class ComplaintImageOCRResponseSerializer(serializers.Serializer):
    """Serializer for complaint image OCR response with NLP analysis."""
    extracted_text = serializers.CharField(help_text="Text extracted from the image")
    text_length = serializers.IntegerField(help_text="Length of extracted text")
    entities = serializers.JSONField(required=False, help_text="Named entities found in the text")
    classification = serializers.JSONField(required=False, help_text="Complaint classification results")
    sentiment = serializers.JSONField(required=False, help_text="Sentiment analysis results")
    status = serializers.CharField(help_text="Processing status")
    error_message = serializers.CharField(required=False, help_text="Error message if any")
    processing_time = serializers.FloatField(help_text="Total processing time in seconds")
