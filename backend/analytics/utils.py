from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from complaints.models import Complaint, Department
from chatbot.models import ChatLog, ChatFeedback

def get_resolution_rate(complaints):
    total_complaints = complaints.count()
    resolved_complaints = complaints.filter(status='resolved').count()
    return (resolved_complaints / max(total_complaints, 1)) * 100

def get_avg_resolution_time(complaints):
    resolved_with_time = complaints.filter(
        status='resolved',
        updated_at__isnull=False
    ).annotate(
        resolution_time=F('updated_at') - F('created_at')
    )
    
    if resolved_with_time.exists():
        avg_seconds = resolved_with_time.aggregate(
            avg_time=Avg('resolution_time')
        )['avg_time'].total_seconds()
        return avg_seconds / 3600  # Convert to hours
    return 0

def get_satisfaction_score(user):
    return ChatFeedback.objects.filter(user=user).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

def get_sentiment_distribution(complaints):
    return complaints.exclude(sentiment__isnull=True).aggregate(
        positive=Count('id', filter=Q(sentiment__gt=0.1)),
        neutral=Count('id', filter=Q(sentiment__gte=-0.1, sentiment__lte=0.1)),
        negative=Count('id', filter=Q(sentiment__lt=-0.1))
    )

def get_department_performance(user):
    if user.is_superuser or user.is_staff:
        return list(Department.objects.annotate(
            total_complaints=Count('complaints'),
            resolved_complaints=Count('complaints', filter=Q(complaints__status='resolved')),
            avg_resolution_time=Avg('complaints__updated_at') - Avg('complaints__created_at')
        ).values('name', 'total_complaints', 'resolved_complaints', 'avg_resolution_time'))
    return []

def get_daily_trends(complaints):
    return list(complaints.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        resolved=Count('id', filter=Q(status='resolved'))
    ).order_by('date'))

def get_chatbot_stats(user):
    if ChatLog.objects.filter(user=user).exists():
        stats = ChatLog.objects.filter(user=user).aggregate(
            total_interactions=Count('id'),
            escalated_count=Count('id', filter=Q(escalated_to_human=True)),
            avg_confidence=Avg('confidence')
        )
        stats['effectiveness_rate'] = (1 - (stats['escalated_count'] / max(stats['total_interactions'], 1))) * 100
        return stats
    return {}
