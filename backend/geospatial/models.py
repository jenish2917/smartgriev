# Geospatial Analytics for Complaint Clustering and Hotspot Detection
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

class GeospatialCluster(models.Model):
    """Geographic clusters of complaints"""
    CLUSTER_TYPE = [
        ('hotspot', 'Complaint Hotspot'),
        ('pattern', 'Pattern Cluster'),
        ('temporal', 'Temporal Cluster'),
        ('category', 'Category Cluster')
    ]
    
    cluster_id = models.CharField(max_length=100, unique=True)
    cluster_type = models.CharField(max_length=20, choices=CLUSTER_TYPE)
    
    # Geographic bounds
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    radius_meters = models.FloatField()
    
    # Cluster statistics
    complaint_count = models.IntegerField()
    severity_score = models.FloatField()  # Calculated based on complaints
    category_distribution = models.JSONField(default=dict)
    
    # Time-based info
    first_complaint_date = models.DateTimeField()
    last_complaint_date = models.DateTimeField()
    time_span_days = models.IntegerField()
    
    # Analysis results
    is_active = models.BooleanField(default=True)
    priority_level = models.CharField(max_length=20, default='medium')
    recommended_actions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class HeatmapData(models.Model):
    """Precomputed heatmap data for visualization"""
    region_type = models.CharField(max_length=50)  # city, district, zone
    region_id = models.CharField(max_length=100)
    
    # Geographic info
    bounds = models.JSONField()  # Polygon bounds for the region
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    
    # Metrics
    complaint_density = models.FloatField()  # Complaints per square km
    resolution_rate = models.FloatField()
    avg_response_time = models.FloatField()  # Hours
    satisfaction_score = models.FloatField()
    
    # Time period
    time_period = models.CharField(max_length=20)  # daily, weekly, monthly
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Additional data
    total_complaints = models.IntegerField()
    resolved_complaints = models.IntegerField()
    pending_complaints = models.IntegerField()
    
    updated_at = models.DateTimeField(auto_now=True)

class GeoAnalytics(models.Model):
    """Geographic analytics results"""
    analysis_type = models.CharField(max_length=50)
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    # Results data
    results = models.JSONField()
    
    # Parameters used
    parameters = models.JSONField(default=dict)
    
    # Metadata
    data_version = models.CharField(max_length=50)
    algorithm_version = models.CharField(max_length=50)

class RouteOptimization(models.Model):
    """Optimized routes for field officers"""
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimized_routes')
    
    # Route details
    route_date = models.DateField()
    complaint_ids = models.JSONField(default=list)  # Order of visits
    route_coordinates = models.JSONField(default=list)  # Lat/lon pairs
    
    # Optimization results
    total_distance_km = models.FloatField()
    estimated_time_hours = models.FloatField()
    fuel_cost_estimate = models.FloatField(null=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    actual_distance_km = models.FloatField(null=True)
    actual_time_hours = models.FloatField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)

class LocationIntelligence(models.Model):
    """AI-powered location insights"""
    location_lat = models.FloatField()
    location_lon = models.FloatField()
    
    # Insights
    risk_score = models.FloatField()  # 0-1 scale
    predicted_complaint_types = models.JSONField(default=list)
    seasonal_patterns = models.JSONField(default=dict)
    demographic_factors = models.JSONField(default=dict)
    
    # Recommendations
    preventive_measures = models.JSONField(default=list)
    resource_allocation = models.JSONField(default=dict)
    
    # Analysis metadata
    confidence_score = models.FloatField()
    data_sources = models.JSONField(default=list)
    last_updated = models.DateTimeField(auto_now=True)

# Note: For full GIS functionality, you would typically use PostGIS
# Note: For production with PostGIS, consider using django.contrib.gis models
# with PointField and PolygonField for better geospatial queries
