from django.urls import path, include
from . import views

urlpatterns = [
    # Experiment management
    path('experiments/', views.MLExperimentListCreateView.as_view(), name='ml-experiments'),
    path('experiments/<uuid:experiment_id>/', views.MLExperimentDetailView.as_view(), name='ml-experiment-detail'),
    path('experiments/<uuid:experiment_id>/results/', views.ExperimentResultsView.as_view(), name='experiment-results'),
    
    # Model performance
    path('performance/', views.ModelPerformanceView.as_view(), name='model-performance'),
    path('performance/<int:model_id>/', views.ModelPerformanceDetailView.as_view(), name='model-performance-detail'),
    
    # Data drift detection
    path('drift/', views.DataDriftListView.as_view(), name='data-drift'),
    path('drift/<int:model_id>/', views.DataDriftDetailView.as_view(), name='data-drift-detail'),
    
    # Model retraining
    path('retrain/', views.ModelRetrainingView.as_view(), name='model-retrain'),
    path('retrain/jobs/', views.RetrainingJobsView.as_view(), name='retraining-jobs'),
    
    # Feature importance
    path('features/', views.FeatureImportanceView.as_view(), name='feature-importance'),
    path('features/<int:model_id>/', views.FeatureImportanceDetailView.as_view(), name='feature-importance-detail'),
]
