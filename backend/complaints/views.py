from rest_framework import generics, permissions, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, Count
from math import radians, sin, cos, sqrt, atan2
from .models import Complaint, Department, AuditTrail, IncidentLocationHistory, GPSValidation
from .serializers import (
    ComplaintSerializer,
    DepartmentSerializer,
    ComplaintStatusUpdateSerializer,
    AuditTrailSerializer,
    IncidentLocationHistorySerializer,
    GPSValidationSerializer,
    ComplaintLocationUpdateSerializer
)

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

    def get_queryset(self):
        queryset = Complaint.objects.all()
        if self.request.user.is_officer:
            queryset = queryset.filter(department__officer=self.request.user)
        else:
            queryset = queryset.filter(user=self.request.user)
            
        # Additional filters
        status = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
            
        return queryset

    def perform_create(self, serializer):
        # Set user and calculate sentiment
        complaint = serializer.save(user=self.request.user)
        
        # Create audit trail
        AuditTrail.objects.create(
            complaint=complaint,
            action='created',
            by_user=self.request.user
        )

        # Notify department officer
        if complaint.department and complaint.department.officer:
            pass  # Implement notification system later

class ComplaintDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_officer:
            return Complaint.objects.filter(department__officer=self.request.user)
        return Complaint.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        old_status = self.get_object().status
        complaint = serializer.save()
        
        # Create audit trail for status change
        if old_status != complaint.status:
            AuditTrail.objects.create(
                complaint=complaint,
                action=f'status_changed_from_{old_status}_to_{complaint.status}',
                by_user=self.request.user
            )
        
        # Notify user of status change
        if old_status != complaint.status:
            # Send notification to user (implement notification system)
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
        # Implement notification system

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
    permission_classes = [IsAuthenticated, IsOfficerOrReadOnly]

    def get_queryset(self):
        return Complaint.objects.filter(department__officer=self.request.user)

class AuditTrailListView(generics.ListAPIView):
    serializer_class = AuditTrailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_officer:
            return AuditTrail.objects.filter(
                Q(complaint__department__officer=self.request.user) |
                Q(by_user=self.request.user)
            )
        return AuditTrail.objects.filter(
            Q(complaint__user=self.request.user) |
            Q(by_user=self.request.user)
        )

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
        validation_results = _perform_gps_validation(complaint)
        
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

def _perform_gps_validation(complaint):
    """Perform GPS validation checks"""
    results = {
        'accuracy_check': True,
        'range_check': True,
        'duplicate_check': True,
        'speed_check': True,
        'score': 1.0,
        'is_valid': True,
        'notes': ''
    }
    
    notes = []
    
    # Check GPS accuracy
    if complaint.gps_accuracy and complaint.gps_accuracy > 50:
        results['accuracy_check'] = False
        notes.append(f"GPS accuracy too low: {complaint.gps_accuracy}m")
    
    # Check if coordinates are within service area (you can customize this)
    # Example: Check if within India bounds
    if complaint.incident_latitude and complaint.incident_longitude:
        if not (6.0 <= complaint.incident_latitude <= 37.6 and 68.7 <= complaint.incident_longitude <= 97.25):
            results['range_check'] = False
            notes.append("Location outside service area")
    
    # Check for duplicate locations (within 100m radius)
    from math import radians, sin, cos, sqrt, atan2
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    if complaint.incident_latitude and complaint.incident_longitude:
        nearby_complaints = Complaint.objects.filter(
            incident_latitude__isnull=False,
            incident_longitude__isnull=False
        ).exclude(id=complaint.id)
        
        for nearby in nearby_complaints:
            distance = calculate_distance(
                complaint.incident_latitude, complaint.incident_longitude,
                nearby.incident_latitude, nearby.incident_longitude
            )
            if distance < 100:  # Within 100 meters
                results['duplicate_check'] = False
                notes.append(f"Similar location within 100m (Complaint #{nearby.id})")
                break
    
    # Calculate overall score
    checks = [results['accuracy_check'], results['range_check'], results['duplicate_check'], results['speed_check']]
    results['score'] = sum(checks) / len(checks)
    results['is_valid'] = results['score'] >= 0.75
    results['notes'] = '; '.join(notes) if notes else 'All validation checks passed'
    
    return results

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
