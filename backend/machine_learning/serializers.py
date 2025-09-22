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
