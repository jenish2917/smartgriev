from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import MLModel, ModelPrediction
from .serializers import MLModelSerializer, ModelPredictionSerializer
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import spacy
from celery import shared_task
import torch

# ML Models initialization
nlp = spacy.load('en_core_web_sm')
sentiment_analyzer = pipeline('sentiment-analysis')
text_classifier = pipeline('text-classification')

# Load complaint classifier
complaint_tokenizer = AutoTokenizer.from_pretrained('./saved_model')
complaint_model = AutoModelForSequenceClassification.from_pretrained('./saved_model')
complaint_classifier = pipeline('text-classification', model=complaint_model, tokenizer=complaint_tokenizer)

@shared_task
def process_prediction(prediction_id):
    """Background task to process predictions"""
    try:
        prediction = ModelPrediction.objects.get(id=prediction_id)
        model = prediction.model
        
        if model.model_type == 'sentiment':
            result = sentiment_analyzer(prediction.input_text)[0]
            prediction.prediction = result['label']
            prediction.confidence = result['score']
        
        elif model.model_type == 'classification':
            result = text_classifier(prediction.input_text)[0]
            prediction.prediction = result['label']
            prediction.confidence = result['score']
        
        elif model.model_type == 'ner':
            doc = nlp(prediction.input_text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            prediction.prediction = str(entities)
            prediction.confidence = 1.0
            
        elif model.model_type == 'complaint':
            result = complaint_classifier(prediction.input_text)[0]
            prediction.prediction = result['label']
            prediction.confidence = result['score']
        
        prediction.save()
        return True
    except Exception as e:
        print(f"Error processing prediction {prediction_id}: {str(e)}")
        return False

class MLModelListCreateView(generics.ListCreateAPIView):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    permission_classes = [permissions.IsAdminUser]

class MLModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    permission_classes = [permissions.IsAdminUser]

class PredictionListCreateView(generics.ListCreateAPIView):
    serializer_class = ModelPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ModelPrediction.objects.filter(model__is_active=True)

    def perform_create(self, serializer):
        prediction = serializer.save()
        # Process prediction asynchronously
        process_prediction.delay(prediction.id)
