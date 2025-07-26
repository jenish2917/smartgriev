from django.urls import path
from .views import (
    MLModelListCreateView,
    MLModelDetailView,
    PredictionListCreateView,
)

urlpatterns = [
    path('models/', MLModelListCreateView.as_view(), name='mlmodel-list-create'),
    path('models/<int:pk>/', MLModelDetailView.as_view(), name='mlmodel-detail'),
    path('predict/', PredictionListCreateView.as_view(), name='prediction-list-create'),
]
