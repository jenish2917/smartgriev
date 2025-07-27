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
)

urlpatterns = [
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
]
