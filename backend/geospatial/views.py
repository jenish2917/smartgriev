from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import (
    GeospatialCluster, HeatmapData, GeoAnalytics,
    RouteOptimization, LocationIntelligence
)
from .serializers import (
    GeospatialClusterSerializer, HeatmapDataSerializer,
    GeoAnalyticsSerializer, RouteOptimizationSerializer,
    LocationIntelligenceSerializer
)
from .utils import calculate_risk_score

class GeospatialClusterView(generics.ListCreateAPIView):
    serializer_class = GeospatialClusterSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = GeospatialCluster.objects.all()

class GeospatialClusterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GeospatialClusterSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'cluster_id'
    queryset = GeospatialCluster.objects.all()

class HeatmapDataView(generics.ListCreateAPIView):
    serializer_class = HeatmapDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = HeatmapData.objects.all()

class HeatmapDetailView(generics.RetrieveAPIView):
    serializer_class = HeatmapDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        region_type = self.kwargs['region_type']
        region_id = self.kwargs['region_id']
        return get_object_or_404(HeatmapData, region_type=region_type, region_id=region_id)

class GeoAnalyticsView(generics.ListCreateAPIView):
    serializer_class = GeoAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = GeoAnalytics.objects.all()

class GeoAnalyticsDetailView(generics.RetrieveAPIView):
    serializer_class = GeoAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        analysis_type = self.kwargs['analysis_type']
        return get_object_or_404(GeoAnalytics, analysis_type=analysis_type)

class RouteOptimizationView(generics.ListCreateAPIView):
    serializer_class = RouteOptimizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_officer:
            return RouteOptimization.objects.filter(officer=self.request.user)
        return RouteOptimization.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(officer=self.request.user)

class RouteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RouteOptimizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_officer:
            return RouteOptimization.objects.filter(officer=self.request.user)
        return RouteOptimization.objects.all()

class LocationIntelligenceView(generics.ListCreateAPIView):
    serializer_class = LocationIntelligenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = LocationIntelligence.objects.all()

class RiskAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        lat = request.data.get('lat')
        lon = request.data.get('lon')
        
        if not lat or not lon:
            return Response({'error': 'Latitude and longitude required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        risk_score, recommendations = calculate_risk_score(lat, lon)
        
        return Response({
            'risk_score': risk_score,
            'recommendations': recommendations
        })