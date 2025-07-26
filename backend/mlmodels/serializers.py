from rest_framework import serializers
from .models import MLModel, ModelPrediction

class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = ('id', 'name', 'model_type', 'model_file', 'version', 'accuracy', 'created_at', 'is_active')
        read_only_fields = ('created_at',)

class ModelPredictionSerializer(serializers.ModelSerializer):
    model = MLModelSerializer(read_only=True)
    model_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=MLModel.objects.filter(is_active=True),
        source='model'
    )

    class Meta:
        model = ModelPrediction
        fields = ('id', 'model', 'model_id', 'input_text', 'prediction', 'confidence', 'timestamp')
        read_only_fields = ('prediction', 'confidence', 'timestamp')
