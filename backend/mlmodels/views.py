from rest_framework import generics, permissions
from .models import MLModel, ModelPrediction
from .serializers import MLModelSerializer, ModelPredictionSerializer
from .tasks import process_prediction

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
        process_prediction.delay(prediction.id)