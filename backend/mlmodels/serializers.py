from rest_framework import serializers
from .models import MLModel, ModelPrediction

class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = ('id', 'name', 'model_type', 'version', 'accuracy', 'created_at', 'is_active')
        read_only_fields = ('created_at',)

class ModelPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelPrediction
        fields = ('id', 'model', 'input_text', 'prediction', 'confidence', 'timestamp')
        read_only_fields = ('prediction', 'confidence', 'timestamp')