from django.db import models

class MLModel(models.Model):
    class ModelType(models.TextChoices):
        COMPLAINT = 'COMPLAINT', 'Complaint Classifier'
        SENTIMENT = 'SENTIMENT', 'Sentiment Analyzer'
        NER = 'NER', 'Named Entity Recognition'
        LANG = 'LANG', 'Language Detector'
        TRANS = 'TRANS', 'Translator'

    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    model_type = models.CharField(max_length=20, choices=ModelType.choices)
    version = models.CharField(max_length=20)
    model_path = models.FilePathField(path='models/', default='models/default')
    config_path = models.FilePathField(path='models/', null=True, blank=True)
    vocab_path = models.FilePathField(path='models/', null=True, blank=True)
    accuracy = models.FloatField(default=0.0)
    supported_languages = models.JSONField(default=list, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

    class Meta:
        unique_together = ('name', 'version')

class ModelPrediction(models.Model):
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='predictions')
    input_text = models.TextField()
    confidence = models.FloatField()
    processing_time = models.FloatField(help_text="Processing time in seconds", null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model.name} - {self.timestamp}"

class Prediction(models.Model):
    model_prediction = models.OneToOneField(ModelPrediction, on_delete=models.CASCADE, related_name='prediction')
    # Add fields for your prediction, e.g.:
    # label = models.CharField(max_length=100)
    # score = models.FloatField()

class PredictionMetadata(models.Model):
    model_prediction = models.OneToOneField(ModelPrediction, on_delete=models.CASCADE, related_name='metadata')
    # Add fields for your metadata, e.g.:
    # request_id = models.UUIDField()
    # user_id = models.IntegerField()