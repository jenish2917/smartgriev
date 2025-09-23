from rest_framework import generics, permissions, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from math import cos, radians
from backend.complaints.models import Complaint, Department, AuditTrail, IncidentLocationHistory, GPSValidation
from backend.complaints.serializers import (
    ComplaintSerializer,
    DepartmentSerializer,
    ComplaintStatusUpdateSerializer,
    AuditTrailSerializer,
    IncidentLocationHistorySerializer,
    GPSValidationSerializer,
    ComplaintLocationUpdateSerializer
)
from backend.complaints.services import ComplaintService
from backend.complaints.utils import perform_gps_validation

class IsOfficerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_officer

class ComplaintListCreateView(generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'sentiment']
    filterset_fields = ['status', 'priority', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.complaint_service = ComplaintService()

    def get_queryset(self):
        queryset = self.complaint_service.get_queryset()
        
        if self.request.user.is_officer:
            queryset = queryset.filter(department__officer=self.request.user)
        else:
            queryset = queryset.filter(user=self.request.user)
            
        # Additional filters
        status = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        search = self.request.query_params.get('search', None)
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if search:
            queryset = self.complaint_service.search(search, **{
                'user': self.request.user if not self.request.user.is_officer else None
            })
            
        return queryset

    def perform_create(self, serializer):
        # Use service to create complaint with enhanced location tracking
        complaint_data = serializer.validated_data
        complaint = self.complaint_service.create_complaint_with_location(
            complaint_data, 
            created_by=self.request.user
        )
        
        # Set the instance for the serializer response
        serializer.instance = complaint

        # Notify department officer
        if complaint.department and complaint.department.officer:
            try:
                # send_notification(
                #     complaint.department.officer, 
                #     f'New complaint assigned to your department: {complaint.title}'
                # )
                pass  # Notification service will be implemented later
            except Exception:
                # Log error but don't fail the request
                pass

class ComplaintDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.complaint_service = ComplaintService()

    def get_queryset(self):
        if self.request.user.is_officer:
            return self.complaint_service.get_queryset(department__officer=self.request.user)
        return self.complaint_service.get_queryset(user=self.request.user)

    def perform_update(self, serializer):
        complaint_id = self.get_object().id
        old_status = self.get_object().status
        
        # Use service to update complaint
        updated_data = serializer.validated_data
        complaint = self.complaint_service.update(
            complaint_id, 
            updated_data, 
            updated_by=self.request.user
        )
        
        # Set the instance for the serializer response
        serializer.instance = complaint
        
        # Notify user of status change
        if complaint and old_status != complaint.status:
            try:
                # send_notification(
                #     complaint.user, 
                #     f'Your complaint status has been updated to: {complaint.status}'
                # )
                pass  # Notification service will be implemented later
            except Exception:
                pass

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsOfficerOrReadOnly]

class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsOfficerOrReadOnly]

class ComplaintStatusUpdateView(generics.UpdateAPIView):
    serializer_class = ComplaintStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsOfficerOrReadOnly]

    def get_queryset(self):
        return Complaint.objects.filter(department__officer=self.request.user)

    def perform_update(self, serializer):
        complaint = serializer.save()
        
        # Create audit trail
        AuditTrail.objects.create(
            complaint=complaint,
            action=f'status_updated_to_{complaint.status}',
            by_user=self.request.user
        )
        
        # Notify user of status update
        # send_notification(complaint.user, f'Your complaint status has been updated to: {complaint.status}')
        pass  # Notification service will be implemented later

class AuditTrailListView(generics.ListAPIView):
    serializer_class = AuditTrailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        complaint_id = self.kwargs.get('complaint_id')
        if self.request.user.is_officer:
            return AuditTrail.objects.filter(
                complaint_id=complaint_id,
                complaint__department__officer=self.request.user
            ).order_by('-timestamp')
        return AuditTrail.objects.filter(
            complaint_id=complaint_id,
            complaint__user=self.request.user
        ).order_by('-timestamp')

class DepartmentStatsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOfficerOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        from django.db.models import Count
        from rest_framework.response import Response
        
        department_id = kwargs.get('pk')
        stats = Complaint.objects.filter(department_id=department_id).aggregate(
            total_complaints=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            resolved=Count('id', filter=Q(status='resolved')),
            rejected=Count('id', filter=Q(status='rejected')),
            high_priority=Count('id', filter=Q(priority='high')),
            urgent_priority=Count('id', filter=Q(priority='urgent'))
        )
        return Response(stats)

# GPS Location Views
class IncidentLocationHistoryView(generics.ListCreateAPIView):
    serializer_class = IncidentLocationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        complaint_id = self.kwargs.get('complaint_id')
        if complaint_id:
            return IncidentLocationHistory.objects.filter(complaint_id=complaint_id)
        
        if self.request.user.is_officer:
            return IncidentLocationHistory.objects.filter(
                complaint__department__officer=self.request.user
            )
        return IncidentLocationHistory.objects.filter(
            complaint__user=self.request.user
        )

class ComplaintLocationUpdateView(generics.UpdateAPIView):
    serializer_class = ComplaintLocationUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_officer:
            return Complaint.objects.filter(department__officer=self.request.user)
        return Complaint.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
        # Create location history entry
        IncidentLocationHistory.objects.create(
            complaint=instance,
            latitude=instance.incident_latitude,
            longitude=instance.incident_longitude,
            accuracy=instance.gps_accuracy,
            address=instance.incident_address,
            updated_by=self.request.user,
            update_reason='correction' if IncidentLocationHistory.objects.filter(complaint=instance).exists() else 'initial'
        )

class GPSValidationView(generics.RetrieveUpdateAPIView):
    serializer_class = GPSValidationSerializer
    permission_classes = [IsAuthenticated, IsOfficerOrReadOnly]
    
    def get_queryset(self):
        return GPSValidation.objects.filter(complaint__department__officer=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_gps_location(request, complaint_id):
    """Validate GPS coordinates for a complaint"""
    try:
        complaint = Complaint.objects.get(id=complaint_id)
        
        # Check permissions
        if not request.user.is_officer and complaint.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create GPS validation
        gps_validation, created = GPSValidation.objects.get_or_create(
            complaint=complaint,
            defaults={'validated_by': request.user}
        )
        
        # Perform validation checks
        validation_results = perform_gps_validation(complaint)
        
        # Update validation record
        gps_validation.accuracy_check = validation_results['accuracy_check']
        gps_validation.range_check = validation_results['range_check']
        gps_validation.duplicate_check = validation_results['duplicate_check']
        gps_validation.speed_check = validation_results['speed_check']
        gps_validation.validation_score = validation_results['score']
        gps_validation.is_valid = validation_results['is_valid']
        gps_validation.validation_notes = validation_results['notes']
        gps_validation.validated_by = request.user
        gps_validation.save()
        
        serializer = GPSValidationSerializer(gps_validation)
        return Response(serializer.data)
        
    except Complaint.DoesNotExist:
        return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nearby_complaints(request):
    """Find complaints near a given location"""
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    radius = float(request.GET.get('radius', 1000))  # Default 1km
    
    if not lat or not lon:
        return Response({'error': 'Latitude and longitude required'}, status=status.HTTP_400_BAD_REQUEST)
    
    lat, lon = float(lat), float(lon)
    
    # Simple bounding box search (for better performance, consider using PostGIS)
    lat_range = radius / 111000  # Rough conversion: 1 degree ≈ 111km
    lon_range = radius / (111000 * cos(radians(lat)))
    
    nearby = Complaint.objects.filter(
        incident_latitude__range=[lat - lat_range, lat + lat_range],
        incident_longitude__range=[lon - lon_range, lon + lon_range],
        incident_latitude__isnull=False,
        incident_longitude__isnull=False
    )
    
    # Filter by user permissions
    if not request.user.is_officer:
        nearby = nearby.filter(user=request.user)
    else:
        nearby = nearby.filter(department__officer=request.user)
    
    serializer = ComplaintSerializer(nearby, many=True)
    return Response({
        'count': nearby.count(),
        'complaints': serializer.data
    })