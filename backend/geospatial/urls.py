from django.urls import path
from . import views

urlpatterns = [
    # Geospatial clusters
    path('clusters/', views.GeospatialClusterView.as_view(), name='geospatial-clusters'),
    path('clusters/<str:cluster_id>/', views.GeospatialClusterDetailView.as_view(), name='cluster-detail'),
    
    # Heatmap data
    path('heatmap/', views.HeatmapDataView.as_view(), name='heatmap-data'),
    path('heatmap/<str:region_type>/<str:region_id>/', views.HeatmapDetailView.as_view(), name='heatmap-detail'),
    
    # Analytics
    path('analytics/', views.GeoAnalyticsView.as_view(), name='geo-analytics'),
    path('analytics/<str:analysis_type>/', views.GeoAnalyticsDetailView.as_view(), name='geo-analytics-detail'),
    
    # Route optimization
    path('routes/', views.RouteOptimizationView.as_view(), name='route-optimization'),
    path('routes/<int:route_id>/', views.RouteDetailView.as_view(), name='route-detail'),
    
    # Location intelligence
    path('intelligence/', views.LocationIntelligenceView.as_view(), name='location-intelligence'),
    path('intelligence/risk/', views.RiskAnalysisView.as_view(), name='risk-analysis'),
]
