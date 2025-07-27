from rest_framework import serializers
from .models import (
    GeospatialCluster, HeatmapData, GeoAnalytics,
    RouteOptimization, LocationIntelligence
)

class GeospatialClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeospatialCluster
        fields = '__all__'
        read_only_fields = ('cluster_id', 'created_at', 'updated_at')

class HeatmapDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeatmapData
        fields = '__all__'
        read_only_fields = ('heatmap_id', 'created_at', 'updated_at')

class GeoAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoAnalytics
        fields = '__all__'
        read_only_fields = ('analytics_id', 'created_at')

class RouteOptimizationSerializer(serializers.ModelSerializer):
    officer_name = serializers.CharField(source='officer.username', read_only=True)
    
    class Meta:
        model = RouteOptimization
        fields = '__all__'
        read_only_fields = ('route_id', 'officer', 'created_at', 'updated_at')
    
    def validate_waypoints(self, value):
        """Validate waypoints format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Waypoints must be a list")
        
        for waypoint in value:
            if not isinstance(waypoint, dict) or 'lat' not in waypoint or 'lon' not in waypoint:
                raise serializers.ValidationError(
                    "Each waypoint must contain 'lat' and 'lon' keys"
                )
        
        return value

class LocationIntelligenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationIntelligence
        fields = '__all__'
        read_only_fields = ('intelligence_id', 'created_at')
    
    def validate_coordinates(self, value):
        """Validate coordinates format"""
        if not isinstance(value, dict) or 'lat' not in value or 'lon' not in value:
            raise serializers.ValidationError(
                "Coordinates must contain 'lat' and 'lon' keys"
            )
        
        lat = value.get('lat')
        lon = value.get('lon')
        
        if not (-90 <= lat <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        
        if not (-180 <= lon <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        
        return value
