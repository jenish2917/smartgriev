from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
import csv
from django.http import HttpResponse

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
from chatbot.models import ChatLog, ChatFeedback
from .utils import get_satisfaction_score, get_department_performance, get_chatbot_stats, get_daily_trends, get_sentiment_distribution, get_resolution_rate, get_avg_resolution_time

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
            
        if self.request.user.is_officer:
            user_departments = Department.objects.filter(officer=self.request.user)
            queryset = queryset.filter(department__in=user_departments)
            
        return queryset.order_by('-timestamp')[:100]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    cache_key = f"dashboard_stats_{request.user.id}_{request.user.is_officer}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    user = request.user
    complaints = Complaint.objects.filter(user=user) if not user.is_officer else Complaint.objects.filter(department__officer=user)
    
    data = {
        'total_complaints': complaints.count(),
        'pending_complaints': complaints.filter(status='pending').count(),
        'resolved_complaints': complaints.filter(status='resolved').count(),
        'resolution_rate': get_resolution_rate(complaints),
        'avg_resolution_time': get_avg_resolution_time(complaints),
        'satisfaction_score': get_satisfaction_score(user),
        'sentiment_distribution': get_sentiment_distribution(complaints),
        'department_performance': get_department_performance(user),
        'recent_activity': list(complaints.order_by('-created_at')[:10].values('id', 'title', 'status', 'priority', 'created_at')) if user.is_officer or user.is_superuser else [],
        'geographic_hotspots': list(complaints.values('location_lat', 'location_lon').annotate(complaint_count=Count('id')).filter(complaint_count__gt=1).order_by('-complaint_count')[:20]),
        'daily_trends': get_daily_trends(complaints),
        'chatbot_stats': get_chatbot_stats(user)
    }
    
    cache.set(cache_key, data, getattr(settings, 'DASHBOARD_CACHE_TIMEOUT', 900))
    
    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def real_time_updates(request):
    last_update = request.query_params.get('last_update')
    
    if last_update:
        last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
    else:
        last_update = timezone.now() - timedelta(hours=1)
    
    recent_complaints = Complaint.objects.filter(created_at__gt=last_update).count()
    recent_updates = Complaint.objects.filter(updated_at__gt=last_update).exclude(created_at__gt=last_update).count()
    alerts = AlertInstance.objects.filter(triggered_at__gt=last_update, is_resolved=False).count()
    
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
    format_type = request.query_params.get('format', 'json')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    queryset = UserActivity.objects.all()
    if date_from:
        queryset = queryset.filter(timestamp__gte=date_from)
    if date_to:
        queryset = queryset.filter(timestamp__lte=date_to)
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['user', 'activity_type', 'endpoint', 'ip_address', 'timestamp'])
        for activity in queryset:
            writer.writerow([activity.user.username, activity.activity_type, activity.endpoint, activity.ip_address, activity.timestamp])
        return response
    else:
        data = list(queryset.values('user__username', 'activity_type', 'endpoint', 'ip_address', 'timestamp'))
        return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def system_health(request):
    try:
        Complaint.objects.count()
        db_status = 'healthy'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    try:
        cache.set('health_check', 'ok', 10)
        cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'error'
    except Exception as e:
        cache_status = f'error: {str(e)}'
    
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