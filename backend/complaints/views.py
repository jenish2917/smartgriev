from rest_framework import generics, permissions, filters
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Complaint, Department, AuditTrail
from .serializers import (
    ComplaintSerializer,
    DepartmentSerializer,
    ComplaintStatusUpdateSerializer,
    AuditTrailSerializer
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
