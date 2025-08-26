from django.contrib.gis.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class GeospatialCluster(models.Model):
    CLUSTER_TYPE = [
        ('hotspot', 'Complaint Hotspot'),
        ('pattern', 'Pattern Cluster'),
        ('temporal', 'Temporal Cluster'),
        ('category', 'Category Cluster')
    ]
    
    cluster_id = models.CharField(max_length=100, unique=True)
    cluster_type = models.CharField(max_length=20, choices=CLUSTER_TYPE)
    center = models.PointField()
    radius_meters = models.FloatField()
    complaint_count = models.IntegerField()
    severity_score = models.FloatField()
    first_complaint_date = models.DateTimeField()
    last_complaint_date = models.DateTimeField()
    time_span_days = models.IntegerField()
    is_active = models.BooleanField(default=True)
    priority_level = models.CharField(max_length=20, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CategoryDistribution(models.Model):
    cluster = models.ForeignKey(GeospatialCluster, on_delete=models.CASCADE, related_name='category_distribution')
    category = models.CharField(max_length=100)
    count = models.IntegerField()

class RecommendedAction(models.Model):
    cluster = models.ForeignKey(GeospatialCluster, on_delete=models.CASCADE, related_name='recommended_actions')
    action = models.TextField()

class HeatmapData(models.Model):
    region_type = models.CharField(max_length=50)
    region_id = models.CharField(max_length=100)
    bounds = models.PolygonField()
    center = models.PointField()
    complaint_density = models.FloatField()
    resolution_rate = models.FloatField()
    avg_response_time = models.FloatField()
    satisfaction_score = models.FloatField()
    time_period = models.CharField(max_length=20)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    total_complaints = models.IntegerField()
    resolved_complaints = models.IntegerField()
    pending_complaints = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

class GeoAnalytics(models.Model):
    analysis_type = models.CharField(max_length=50)
    analysis_date = models.DateTimeField(auto_now_add=True)
    data_version = models.CharField(max_length=50)
    algorithm_version = models.CharField(max_length=50)

class GeoAnalyticsResult(models.Model):
    analysis = models.ForeignKey(GeoAnalytics, on_delete=models.CASCADE, related_name='results')
    # Add fields for your results, e.g.:
    # key = models.CharField(max_length=100)
    # value = models.TextField()

class GeoAnalyticsParameter(models.Model):
    analysis = models.ForeignKey(GeoAnalytics, on_delete=models.CASCADE, related_name='parameters')
    # Add fields for your parameters, e.g.:
    # name = models.CharField(max_length=100)
    # value = models.CharField(max_length=100)

class RouteOptimization(models.Model):
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimized_routes')
    route_date = models.DateField()
    total_distance_km = models.FloatField()
    estimated_time_hours = models.FloatField()
    fuel_cost_estimate = models.FloatField(null=True)
    is_completed = models.BooleanField(default=False)
    actual_distance_km = models.FloatField(null=True)
    actual_time_hours = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)

class ComplaintVisit(models.Model):
    route = models.ForeignKey(RouteOptimization, on_delete=models.CASCADE, related_name='complaint_visits')
    complaint = models.ForeignKey('complaints.Complaint', on_delete=models.CASCADE)
    order = models.IntegerField()

class RouteCoordinate(models.Model):
    route = models.ForeignKey(RouteOptimization, on_delete=models.CASCADE, related_name='route_coordinates')
    point = models.PointField()
    order = models.IntegerField()

class LocationIntelligence(models.Model):
    location = models.PointField()
    risk_score = models.FloatField()
    confidence_score = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

class PredictedComplaintType(models.Model):
    location_intelligence = models.ForeignKey(LocationIntelligence, on_delete=models.CASCADE, related_name='predicted_complaint_types')
    complaint_type = models.CharField(max_length=100)

class SeasonalPattern(models.Model):
    location_intelligence = models.ForeignKey(LocationIntelligence, on_delete=models.CASCADE, related_name='seasonal_patterns')
    # Add fields for your seasonal patterns, e.g.:
    # month = models.IntegerField()
    # complaint_type = models.CharField(max_length=100)
    # count = models.IntegerField()

class DemographicFactor(models.Model):
    location_intelligence = models.ForeignKey(LocationIntelligence, on_delete=models.CASCADE, related_name='demographic_factors')
    # Add fields for your demographic factors, e.g.:
    # factor = models.CharField(max_length=100)
    # value = models.CharField(max_length=100)

class PreventiveMeasure(models.Model):
    location_intelligence = models.ForeignKey(LocationIntelligence, on_delete=models.CASCADE, related_name='preventive_measures')
    measure = models.TextField()

class ResourceAllocation(models.Model):
    location_intelligence = models.ForeignKey(LocationIntelligence, on_delete=models.CASCADE, related_name='resource_allocation')
    # Add fields for your resource allocation, e.g.:
    # resource = models.CharField(max_length=100)
    # amount = models.FloatField()

class DataSource(models.Model):
    location_intelligence = models.ForeignKey(LocationIntelligence, on_delete=models.CASCADE, related_name='data_sources')
    source = models.CharField(max_length=100)