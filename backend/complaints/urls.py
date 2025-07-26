from django.urls import path
from .views import (
    ComplaintListCreateView,
    ComplaintDetailView,
    DepartmentListCreateView,
    DepartmentDetailView,
    ComplaintStatusUpdateView,
    AuditTrailListView,
    DepartmentStatsView,
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
]
