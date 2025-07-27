from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
import json
from django.core.cache import cache

from .models import (
    AnalyticsDashboard, RealTimeMetrics, UserActivity, 
    PerformanceMetrics, AlertRule, AlertInstance
)
from .serializers import (
    AnalyticsDashboardSerializer, RealTimeMetricsSerializer,
    UserActivitySerializer, PerformanceMetricsSerializer,
    AlertRuleSerializer, AlertInstanceSerializer, DashboardStatsSerializer
)
from complaints.models import Complaint, Department
from chatbot.models import ChatLog

User = get_user_model()

class AnalyticsDashboardView(generics.ListCreateAPIView):
    serializer_class = AnalyticsDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalyticsDashboard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RealTimeMetricsView(generics.ListAPIView):
    serializer_class = RealTimeMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        time_period = self.request.query_params.get('period', 'daily')
        metric_type = self.request.query_params.get('type')
        
        queryset = RealTimeMetrics.objects.filter(time_period=time_period)
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
            
        # Filter by department for officers
        if self.request.user.is_officer:
            user_departments = Department.objects.filter(officer=self.request.user)
            queryset = queryset.filter(department__in=user_departments)
            
        return queryset.order_by('-timestamp')[:100]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get comprehensive dashboard statistics"""
    cache_key = f"dashboard_stats_{request.user.id}_{request.user.is_officer}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    user = request.user
    now = timezone.now()
    
    # Base complaint queryset
    if user.is_officer:
        complaints = Complaint.objects.filter(department__officer=user)
    else:
        complaints = Complaint.objects.filter(user=user)
    
    # Basic stats
    total_complaints = complaints.count()
    pending_complaints = complaints.filter(status='pending').count()
    resolved_complaints = complaints.filter(status='resolved').count()
    
    # Resolution rate
    resolution_rate = (resolved_complaints / max(total_complaints, 1)) * 100
    
    # Average resolution time
    resolved_with_time = complaints.filter(
        status='resolved',
        updated_at__isnull=False
    ).annotate(
        resolution_time=F('updated_at') - F('created_at')
    )
    
    avg_resolution_time = 0
    if resolved_with_time.exists():
        avg_seconds = resolved_with_time.aggregate(
            avg_time=Avg('resolution_time')
        )['avg_time'].total_seconds()
        avg_resolution_time = avg_seconds / 3600  # Convert to hours
    
    # Satisfaction score (mock - implement based on feedback system)
    satisfaction_score = 4.2
    
    # Sentiment distribution
    sentiment_data = complaints.exclude(sentiment__isnull=True).aggregate(
        positive=Count('id', filter=Q(sentiment__gt=0.1)),
        neutral=Count('id', filter=Q(sentiment__gte=-0.1, sentiment__lte=0.1)),
        negative=Count('id', filter=Q(sentiment__lt=-0.1))
    )
    
    # Department performance (for admin users)
    department_performance = []
    if user.is_superuser or user.is_staff:
        dept_stats = Department.objects.annotate(
            total_complaints=Count('complaints'),
            resolved_complaints=Count('complaints', filter=Q(complaints__status='resolved')),
            avg_resolution_time=Avg('complaints__updated_at') - Avg('complaints__created_at')
        ).values(
            'name', 'total_complaints', 'resolved_complaints', 'avg_resolution_time'
        )
        department_performance = list(dept_stats)
    
    # Recent activity
    recent_activity = []
    if user.is_officer or user.is_superuser:
        recent_complaints = complaints.order_by('-created_at')[:10].values(
            'id', 'title', 'status', 'priority', 'created_at'
        )
        recent_activity = list(recent_complaints)
    
    # Geographic hotspots
    geographic_hotspots = complaints.values(
        'location_lat', 'location_lon'
    ).annotate(
        complaint_count=Count('id')
    ).filter(complaint_count__gt=1).order_by('-complaint_count')[:20]
    
    # Time series data for trends
    daily_stats = complaints.filter(
        created_at__gte=now - timedelta(days=30)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        resolved=Count('id', filter=Q(status='resolved'))
    ).order_by('date')
    
    # Chatbot effectiveness
    chatbot_stats = {}
    if ChatLog.objects.filter(user=user).exists():
        chatbot_stats = ChatLog.objects.filter(user=user).aggregate(
            total_interactions=Count('id'),
            escalated_count=Count('id', filter=Q(escalated_to_human=True)),
            avg_confidence=Avg('confidence')
        )
        chatbot_stats['effectiveness_rate'] = (
            1 - (chatbot_stats['escalated_count'] / max(chatbot_stats['total_interactions'], 1))
        ) * 100
    
    data = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'resolution_rate': resolution_rate,
        'avg_resolution_time': avg_resolution_time,
        'satisfaction_score': satisfaction_score,
        'sentiment_distribution': sentiment_data,
        'department_performance': department_performance,
        'recent_activity': recent_activity,
        'geographic_hotspots': list(geographic_hotspots),
        'daily_trends': list(daily_stats),
        'chatbot_stats': chatbot_stats
    }
    
    # Cache for 15 minutes
    cache.set(cache_key, data, 900)
    
    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def real_time_updates(request):
    """Get real-time updates for dashboard"""
    last_update = request.query_params.get('last_update')
    
    if last_update:
        last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
    else:
        last_update = timezone.now() - timedelta(hours=1)
    
    # Get recent complaints
    recent_complaints = Complaint.objects.filter(
        created_at__gt=last_update
    ).count()
    
    # Get recent status updates
    recent_updates = Complaint.objects.filter(
        updated_at__gt=last_update
    ).exclude(created_at__gt=last_update).count()
    
    # Get alerts
    alerts = AlertInstance.objects.filter(
        triggered_at__gt=last_update,
        is_resolved=False
    ).count()
    
    return Response({
        'new_complaints': recent_complaints,
        'status_updates': recent_updates,
        'new_alerts': alerts,
        'timestamp': timezone.now().isoformat()
    })

class UserActivityView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        days = int(self.request.query_params.get('days', 7))
        return UserActivity.objects.filter(
            user=self.request.user,
            timestamp__gte=timezone.now() - timedelta(days=days)
        ).order_by('-timestamp')

class PerformanceMetricsView(generics.ListAPIView):
    serializer_class = PerformanceMetricsSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        hours = int(self.request.query_params.get('hours', 24))
        return PerformanceMetrics.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=hours)
        ).order_by('-timestamp')

class AlertRuleView(generics.ListCreateAPIView):
    serializer_class = AlertRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return AlertRule.objects.all()
        return AlertRule.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AlertInstanceView(generics.ListAPIView):
    serializer_class = AlertInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return AlertInstance.objects.all()
        return AlertInstance.objects.filter(rule__created_by=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_alert_resolved(request, alert_id):
    """Mark an alert as resolved"""
    try:
        alert = AlertInstance.objects.get(id=alert_id)
        if not request.user.is_superuser and alert.rule.created_by != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        
        return Response({'message': 'Alert marked as resolved'})
    except AlertInstance.DoesNotExist:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_analytics_data(request):
    """Export analytics data as CSV/JSON"""
    format_type = request.query_params.get('format', 'json')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    # Implementation for data export
    # This would include CSV generation, data filtering, etc.
    return Response({'message': 'Export functionality to be implemented'})

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def system_health(request):
    """Get system health metrics"""
    
    # Database connectivity
    try:
        Complaint.objects.count()
        db_status = 'healthy'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    # Cache connectivity
    try:
        cache.set('health_check', 'ok', 10)
        cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'error'
    except Exception as e:
        cache_status = f'error: {str(e)}'
    
    # Recent error rate
    recent_errors = UserActivity.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=1),
        response_code__gte=400
    ).count()
    
    total_requests = UserActivity.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).count()
    
    error_rate = (recent_errors / max(total_requests, 1)) * 100
    
    return Response({
        'database': db_status,
        'cache': cache_status,
        'error_rate': error_rate,
        'recent_requests': total_requests,
        'timestamp': timezone.now().isoformat()
    })
