from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from authentication.models import User
from complaints.models import Complaint, Department
from .models import UserActivity, ComplaintStats, DepartmentMetrics, SystemMetrics
from .serializers import (
    UserActivitySerializer, ComplaintStatsSerializer,
    DepartmentMetricsSerializer, SystemMetricsSerializer,
    DashboardStatsSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get comprehensive dashboard statistics"""
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # User statistics
    total_users = User.objects.count()
    active_users_today = UserActivity.objects.filter(
        created_at__date=today
    ).values('user').distinct().count()
    new_users_this_week = User.objects.filter(
        date_joined__gte=week_ago
    ).count()
    
    # Complaint statistics
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(
        status__in=['submitted', 'pending', 'in_progress']
    ).count()
    resolved_complaints = Complaint.objects.filter(
        status='resolved'
    ).count()
    resolved_this_week = Complaint.objects.filter(
        status='resolved',
        updated_at__gte=week_ago
    ).count()
    
    # Performance metrics
    resolved_with_time = Complaint.objects.filter(
        status='resolved',
        updated_at__isnull=False
    )
    
    avg_resolution_time = 0
    if resolved_with_time.exists():
        total_hours = sum([
            (c.updated_at - c.created_at).total_seconds() / 3600
            for c in resolved_with_time
        ])
        avg_resolution_time = total_hours / resolved_with_time.count()
    
    resolution_rate = 0
    if total_complaints > 0:
        resolution_rate = (resolved_complaints / total_complaints) * 100
    
    # Complaints trend (last 7 days)
    complaints_trend = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = Complaint.objects.filter(created_at__date=date).count()
        complaints_trend.append({
            'date': date.isoformat(),
            'count': count
        })
    complaints_trend.reverse()
    
    # Department performance
    department_performance = []
    departments = Department.objects.all()
    for dept in departments:
        dept_complaints = Complaint.objects.filter(department=dept)
        dept_resolved = dept_complaints.filter(status='resolved').count()
        dept_total = dept_complaints.count()
        
        dept_rate = 0
        if dept_total > 0:
            dept_rate = (dept_resolved / dept_total) * 100
        
        department_performance.append({
            'name': dept.name,
            'total': dept_total,
            'resolved': dept_resolved,
            'rate': round(dept_rate, 2)
        })
    
    data = {
        'total_users': total_users,
        'active_users_today': active_users_today,
        'new_users_this_week': new_users_this_week,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'resolved_this_week': resolved_this_week,
        'avg_resolution_time_hours': round(avg_resolution_time, 2),
        'resolution_rate': round(resolution_rate, 2),
        'complaints_trend': complaints_trend,
        'department_performance': department_performance
    }
    
    serializer = DashboardStatsSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def complaint_trends(request):
    """Get complaint trends over time"""
    
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    trends = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_stats = Complaint.objects.filter(
            created_at__date=current_date
        ).aggregate(
            total=Count('id'),
            resolved=Count('id', filter=Q(status='resolved')),
            pending=Count('id', filter=Q(status__in=['submitted', 'pending'])),
            in_progress=Count('id', filter=Q(status='in_progress'))
        )
        
        trends.append({
            'date': current_date.isoformat(),
            'total': daily_stats['total'] or 0,
            'resolved': daily_stats['resolved'] or 0,
            'pending': daily_stats['pending'] or 0,
            'in_progress': daily_stats['in_progress'] or 0
        })
        
        current_date += timedelta(days=1)
    
    return Response({
        'period': f'{days} days',
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'trends': trends
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_analytics(request):
    """Get department-wise analytics"""
    
    departments = Department.objects.all()
    analytics = []
    
    for dept in departments:
        complaints = Complaint.objects.filter(department=dept)
        
        stats = complaints.aggregate(
            total=Count('id'),
            resolved=Count('id', filter=Q(status='resolved')),
            pending=Count('id', filter=Q(status__in=['submitted', 'pending'])),
            rejected=Count('id', filter=Q(status='rejected')),
            high_priority=Count('id', filter=Q(priority='high')),
            urgent=Count('id', filter=Q(urgency_level='critical'))
        )
        
        # Calculate resolution rate
        resolution_rate = 0
        if stats['total'] > 0:
            resolution_rate = (stats['resolved'] / stats['total']) * 100
        
        analytics.append({
            'id': dept.id,
            'name': dept.name,
            'zone': dept.zone,
            'total_complaints': stats['total'] or 0,
            'resolved': stats['resolved'] or 0,
            'pending': stats['pending'] or 0,
            'rejected': stats['rejected'] or 0,
            'high_priority': stats['high_priority'] or 0,
            'urgent': stats['urgent'] or 0,
            'resolution_rate': round(resolution_rate, 2)
        })
    
    return Response({
        'total_departments': len(departments),
        'analytics': analytics
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity_log(request):
    """Get user activity log"""
    
    user_id = request.query_params.get('user_id')
    activity_type = request.query_params.get('type')
    days = int(request.query_params.get('days', 7))
    
    queryset = UserActivity.objects.all()
    
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    
    if activity_type:
        queryset = queryset.filter(activity_type=activity_type)
    
    if days:
        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(created_at__gte=start_date)
    
    queryset = queryset[:100]  # Limit to 100 records
    
    serializer = UserActivitySerializer(queryset, many=True)
    
    return Response({
        'count': queryset.count(),
        'activities': serializer.data
    })


class ComplaintStatsListView(generics.ListAPIView):
    """List complaint statistics"""
    serializer_class = ComplaintStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        return ComplaintStats.objects.filter(date__gte=start_date)


class DepartmentMetricsListView(generics.ListAPIView):
    """List department metrics"""
    serializer_class = DepartmentMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        department_id = self.request.query_params.get('department_id')
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        queryset = DepartmentMetrics.objects.filter(date__gte=start_date)
        
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        return queryset


@api_view(['POST'])
@permission_classes([IsAdminUser])
def log_user_activity(request):
    """Log user activity (internal use)"""
    
    user_id = request.data.get('user_id')
    activity_type = request.data.get('activity_type')
    description = request.data.get('description', '')
    metadata = request.data.get('metadata', {})
    
    if not all([user_id, activity_type]):
        return Response({
            'error': 'user_id and activity_type are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    activity = UserActivity.objects.create(
        user_id=user_id,
        activity_type=activity_type,
        description=description,
        metadata=metadata,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    serializer = UserActivitySerializer(activity)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)
