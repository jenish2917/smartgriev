from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import (
    GeospatialCluster, HeatmapData, GeoAnalytics,
    RouteOptimization, LocationIntelligence
)
from .serializers import (
    GeospatialClusterSerializer, HeatmapDataSerializer,
    GeoAnalyticsSerializer, RouteOptimizationSerializer,
    LocationIntelligenceSerializer
)

class GeospatialClusterView(generics.ListCreateAPIView):
    serializer_class = GeospatialClusterSerializer
    permission_classes = [IsAuthenticated]
    queryset = GeospatialCluster.objects.all()

class GeospatialClusterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GeospatialClusterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'cluster_id'
    queryset = GeospatialCluster.objects.all()

class HeatmapDataView(generics.ListCreateAPIView):
    serializer_class = HeatmapDataSerializer
    permission_classes = [IsAuthenticated]
    queryset = HeatmapData.objects.all()

class HeatmapDetailView(generics.RetrieveAPIView):
    serializer_class = HeatmapDataSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        region_type = self.kwargs['region_type']
        region_id = self.kwargs['region_id']
        return HeatmapData.objects.filter(
            region_type=region_type, 
            region_id=region_id
        ).first()

class GeoAnalyticsView(generics.ListCreateAPIView):
    serializer_class = GeoAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    queryset = GeoAnalytics.objects.all()

class GeoAnalyticsDetailView(generics.ListAPIView):
    serializer_class = GeoAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        analysis_type = self.kwargs['analysis_type']
        return GeoAnalytics.objects.filter(analysis_type=analysis_type)

class RouteOptimizationView(generics.ListCreateAPIView):
    serializer_class = RouteOptimizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_officer:
            return RouteOptimization.objects.filter(officer=self.request.user)
        return RouteOptimization.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(officer=self.request.user)

class RouteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RouteOptimizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_officer:
            return RouteOptimization.objects.filter(officer=self.request.user)
        return RouteOptimization.objects.all()

class LocationIntelligenceView(generics.ListCreateAPIView):
    serializer_class = LocationIntelligenceSerializer
    permission_classes = [IsAuthenticated]
    queryset = LocationIntelligence.objects.all()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def risk_analysis(request):
    """Analyze risk for a specific location"""
    lat = request.data.get('lat')
    lon = request.data.get('lon')
    
    if not lat or not lon:
        return Response({'error': 'Latitude and longitude required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Mock risk analysis - replace with actual algorithm
    risk_score = 0.3  # Placeholder
    
    return Response({
        'risk_score': risk_score,
        'risk_level': 'medium',
        'recommendations': [
            'Increase patrol frequency',
            'Install additional lighting'
        ]
    })

class RiskAnalysisView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return risk_analysis(request)
