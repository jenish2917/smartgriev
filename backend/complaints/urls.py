from django.urls import path
from .views import (
    ComplaintListCreateView,
    ComplaintDetailView,
    DepartmentListCreateView,
    DepartmentDetailView,
    ComplaintStatusUpdateView,
    AuditTrailListView,
    DepartmentStatsView,
    IncidentLocationHistoryView,
    ComplaintLocationUpdateView,
    GPSValidationView,
    validate_gps_location,
    nearby_complaints,
    classify_complaint_text,
)
from .api_views import (
    MultiModalComplaintProcessingView,
    AuthenticationAPIView, 
    ComplaintStatusView,
    DepartmentListView,
    process_complaint_simple,
    health_check
)

urlpatterns = [
    # Advanced Multi-Modal API endpoints
    path('api/process/', MultiModalComplaintProcessingView.as_view(), name='api-process-multimodal'),
    path('api/auth/', AuthenticationAPIView.as_view(), name='api-authentication'),
    path('api/status/<int:complaint_id>/', ComplaintStatusView.as_view(), name='api-complaint-status'),
    path('api/departments/', DepartmentListView.as_view(), name='api-departments'),
    path('api/simple/', process_complaint_simple, name='api-process-simple'),
    path('api/health/', health_check, name='api-health-check'),
    
    # Original complaint management endpoints
    path('', ComplaintListCreateView.as_view(), name='complaint-list-create'),
    path('<int:pk>/', ComplaintDetailView.as_view(), name='complaint-detail'),
    path('<int:pk>/status/', ComplaintStatusUpdateView.as_view(), name='complaint-status-update'),
    path('<int:complaint_id>/audit-trail/', AuditTrailListView.as_view(), name='complaint-audit-trail'),
    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('departments/<int:pk>/stats/', DepartmentStatsView.as_view(), name='department-stats'),
    path('audit-trail/', AuditTrailListView.as_view(), name='audit-trail-list'),
    
    # GPS Location endpoints
    path('<int:pk>/location/', ComplaintLocationUpdateView.as_view(), name='complaint-location-update'),
    path('<int:complaint_id>/location-history/', IncidentLocationHistoryView.as_view(), name='incident-location-history'),
    path('<int:pk>/gps-validation/', GPSValidationView.as_view(), name='gps-validation'),
    path('<int:complaint_id>/validate-gps/', validate_gps_location, name='validate-gps-location'),
    path('nearby/', nearby_complaints, name='nearby-complaints'),
    path('location-history/', IncidentLocationHistoryView.as_view(), name='all-location-history'),
    
    # AI Classification
    path('classify/', classify_complaint_text, name='classify-complaint'),
]
