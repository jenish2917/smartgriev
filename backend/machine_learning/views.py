from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import (
    MLExperiment, ExperimentResult, ModelPerformanceMetric,
    DataDriftDetection, ModelRetrainingJob, FeatureImportance
)
from .serializers import (
    MLExperimentSerializer, ExperimentResultSerializer,
    ModelPerformanceMetricSerializer, DataDriftDetectionSerializer,
    ModelRetrainingJobSerializer, FeatureImportanceSerializer
)

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
