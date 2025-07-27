from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .models import (
    NotificationTemplate, NotificationRule, NotificationDeliveryLog,
    NotificationPreference, NotificationQueue, NotificationAnalytics,
    PushNotificationDevice
)
from .serializers import (
    NotificationTemplateSerializer, NotificationRuleSerializer,
    NotificationDeliveryLogSerializer, NotificationPreferenceSerializer,
    NotificationQueueSerializer, NotificationAnalyticsSerializer,
    PushNotificationDeviceSerializer
)

User = get_user_model()

class NotificationTemplateView(generics.ListCreateAPIView):
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    queryset = NotificationTemplate.objects.all()

class NotificationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    queryset = NotificationTemplate.objects.all()

class NotificationRuleView(generics.ListCreateAPIView):
    serializer_class = NotificationRuleSerializer
    permission_classes = [IsAuthenticated]
    queryset = NotificationRule.objects.all()

class NotificationRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationRuleSerializer
    permission_classes = [IsAuthenticated]
    queryset = NotificationRule.objects.all()

class NotificationLogView(generics.ListAPIView):
    serializer_class = NotificationDeliveryLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = NotificationDeliveryLog.objects.all()
        user_id = self.request.query_params.get('user_id')
        status_filter = self.request.query_params.get('status')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status_filter:
            queryset = queryset.filter(delivery_status=status_filter)
            
        return queryset.order_by('-sent_at')

class NotificationPreferenceView(generics.ListCreateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationPreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

class NotificationQueueView(generics.ListAPIView):
    serializer_class = NotificationQueueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationQueue.objects.filter(
            status='pending'
        ).order_by('priority', 'scheduled_time')

class DeviceTrackingView(generics.ListAPIView):
    serializer_class = PushNotificationDeviceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PushNotificationDevice.objects.all()
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset.order_by('-created_at')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):
    """Send a notification through selected channels"""
    user_id = request.data.get('user_id')
    template_id = request.data.get('template_id')
    channels = request.data.get('channels', ['email'])
    context_data = request.data.get('context', {})
    
    if not user_id or not template_id:
        return Response(
            {'error': 'user_id and template_id are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
        template = NotificationTemplate.objects.get(id=template_id)
    except (User.DoesNotExist, NotificationTemplate.DoesNotExist):
        return Response(
            {'error': 'User or template not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Queue notifications for each channel
    notifications_created = []
    for channel in channels:
        queue_item = NotificationQueue.objects.create(
            user=user,
            template=template,
            channel=channel,
            context_data=context_data,
            priority='medium'
        )
        notifications_created.append(queue_item.queue_id)
    
    return Response({
        'message': 'Notifications queued successfully',
        'queue_ids': notifications_created
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """Get notification delivery statistics"""
    total_sent = NotificationDeliveryLog.objects.count()
    delivered = NotificationDeliveryLog.objects.filter(delivery_status='delivered').count()
    failed = NotificationDeliveryLog.objects.filter(delivery_status='failed').count()
    pending = NotificationQueue.objects.filter(status='pending').count()
    
    delivery_rate = (delivered / total_sent * 100) if total_sent > 0 else 0
    
    return Response({
        'total_sent': total_sent,
        'delivered': delivered,
        'failed': failed,
        'pending': pending,
        'delivery_rate': round(delivery_rate, 2)
    })

class NotificationStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return notification_stats(request)
