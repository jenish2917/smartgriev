from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import (
    GeospatialCluster, HeatmapData, GeoAnalytics,
    RouteOptimization, LocationIntelligence, CategoryDistribution,
    RecommendedAction, ComplaintVisit, RouteCoordinate
)

class CategoryDistributionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = CategoryDistribution
        fields = ('category', 'count')

class RecommendedActionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = RecommendedAction
        fields = ('action',)

class GeospatialClusterSerializer(GeoFeatureModelSerializer):
    category_distribution = CategoryDistributionSerializer(many=True, read_only=True)
    recommended_actions = RecommendedActionSerializer(many=True, read_only=True)

    class Meta:
        model = GeospatialCluster
        geo_field = "center"
        fields = ('id', 'cluster_id', 'cluster_type', 'center', 'radius_meters', 'complaint_count', 'severity_score', 'first_complaint_date', 'last_complaint_date', 'time_span_days', 'is_active', 'priority_level', 'category_distribution', 'recommended_actions', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class HeatmapDataSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = HeatmapData
        geo_field = "bounds"
        fields = ('id', 'region_type', 'region_id', 'bounds', 'center', 'complaint_density', 'resolution_rate', 'avg_response_time', 'satisfaction_score', 'time_period', 'period_start', 'period_end', 'total_complaints', 'resolved_complaints', 'pending_complaints', 'updated_at')
        read_only_fields = ('id', 'updated_at')

class GeoAnalyticsSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = GeoAnalytics
        fields = ('id', 'analysis_type', 'analysis_date', 'data_version', 'algorithm_version')
        read_only_fields = ('id', 'analysis_date')

class ComplaintVisitSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = ComplaintVisit
        fields = ('complaint', 'order')

class RouteCoordinateSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = RouteCoordinate
        geo_field = "point"
        fields = ('point', 'order')

class RouteOptimizationSerializer(GeoFeatureModelSerializer):
    complaint_visits = ComplaintVisitSerializer(many=True)
    route_coordinates = RouteCoordinateSerializer(many=True)

    class Meta:
        model = RouteOptimization
        fields = ('id', 'officer', 'route_date', 'total_distance_km', 'estimated_time_hours', 'fuel_cost_estimate', 'is_completed', 'actual_distance_km', 'actual_time_hours', 'created_at', 'completed_at', 'complaint_visits', 'route_coordinates')
        read_only_fields = ('id', 'created_at', 'completed_at')

class LocationIntelligenceSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = LocationIntelligence
        geo_field = "location"
        fields = ('id', 'location', 'risk_score', 'confidence_score', 'last_updated')
        read_only_fields = ('id', 'last_updated')