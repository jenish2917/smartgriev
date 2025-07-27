# Advanced ML Pipeline with A/B Testing
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class MLExperiment(models.Model):
    """A/B testing for ML models"""
    EXPERIMENT_STATUS = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('archived', 'Archived')
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    experiment_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Model configurations
    control_model = models.ForeignKey('mlmodels.MLModel', on_delete=models.CASCADE, related_name='control_experiments')
    treatment_model = models.ForeignKey('mlmodels.MLModel', on_delete=models.CASCADE, related_name='treatment_experiments')
    
    # Traffic allocation (percentage)
    traffic_allocation = models.FloatField(default=50.0, help_text="Percentage of traffic to treatment model")
    
    # Experiment configuration
    target_metric = models.CharField(max_length=100)  # accuracy, response_time, user_satisfaction
    minimum_sample_size = models.IntegerField(default=100)
    confidence_level = models.FloatField(default=95.0)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=EXPERIMENT_STATUS, default='draft')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Results
    statistical_significance = models.BooleanField(default=False)
    p_value = models.FloatField(null=True)
    effect_size = models.FloatField(null=True)
    winner = models.CharField(max_length=20, choices=[('control', 'Control'), ('treatment', 'Treatment')], null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

class ExperimentResult(models.Model):
    """Individual experiment results"""
    experiment = models.ForeignKey(MLExperiment, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Which variant was shown
    variant = models.CharField(max_length=20, choices=[('control', 'Control'), ('treatment', 'Treatment')])
    
    # Input and output
    input_text = models.TextField()
    prediction = models.JSONField()
    confidence_score = models.FloatField()
    
    # Performance metrics
    response_time = models.FloatField()  # milliseconds
    accuracy = models.FloatField(null=True)  # if ground truth available
    user_feedback = models.IntegerField(null=True)  # 1-5 rating
    
    # Context
    session_id = models.UUIDField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

class ModelPerformanceMetric(models.Model):
    """Track model performance over time"""
    model = models.ForeignKey('mlmodels.MLModel', on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Metric details
    metric_name = models.CharField(max_length=100)  # accuracy, precision, recall, f1_score, etc.
    metric_value = models.FloatField()
    
    # Data info
    sample_size = models.IntegerField()
    evaluation_date = models.DateTimeField(auto_now_add=True)
    
    # Version tracking
    model_version = models.CharField(max_length=50)
    data_version = models.CharField(max_length=50, null=True)
    
    # Context
    evaluation_context = models.JSONField(default=dict)  # test set info, methodology, etc.

class DataDriftDetection(models.Model):
    """Monitor for data drift in ML models"""
    model = models.ForeignKey('mlmodels.MLModel', on_delete=models.CASCADE, related_name='drift_detections')
    
    # Drift metrics
    drift_score = models.FloatField()
    drift_threshold = models.FloatField(default=0.1)
    is_drift_detected = models.BooleanField(default=False)
    
    # Drift details
    drift_type = models.CharField(max_length=50)  # covariate, prior, concept
    affected_features = models.JSONField(default=list)
    
    # Reference and current data
    reference_period_start = models.DateTimeField()
    reference_period_end = models.DateTimeField()
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    
    detection_date = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

class ModelRetrainingJob(models.Model):
    """Track model retraining jobs"""
    JOB_STATUS = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    
    model = models.ForeignKey('mlmodels.MLModel', on_delete=models.CASCADE, related_name='retraining_jobs')
    job_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Job configuration
    training_data_source = models.CharField(max_length=200)
    training_config = models.JSONField(default=dict)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='queued')
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    
    # Results
    new_model_accuracy = models.FloatField(null=True)
    performance_improvement = models.FloatField(null=True)
    
    # Logs and errors
    logs = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class FeatureImportance(models.Model):
    """Track feature importance for model interpretability"""
    model = models.ForeignKey('mlmodels.MLModel', on_delete=models.CASCADE, related_name='feature_importance')
    
    feature_name = models.CharField(max_length=200)
    importance_score = models.FloatField()
    importance_rank = models.IntegerField()
    
    # Method used for importance calculation
    method = models.CharField(max_length=50)  # permutation, shap, lime, etc.
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=50)

class PredictionExplanation(models.Model):
    """Store explanations for individual predictions"""
    prediction = models.ForeignKey('mlmodels.ModelPrediction', on_delete=models.CASCADE, related_name='explanations')
    
    # Explanation method and results
    explanation_method = models.CharField(max_length=50)  # SHAP, LIME, attention, etc.
    explanation_data = models.JSONField()  # Feature contributions, attention weights, etc.
    
    # Confidence in explanation
    explanation_confidence = models.FloatField(null=True)
    
    generated_at = models.DateTimeField(auto_now_add=True)
