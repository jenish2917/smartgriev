# WebSocket Support for Real-time Updates
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from datetime import datetime

User = get_user_model()

class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time dashboard updates"""
    
    async def connect(self):
        # Check authentication
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Join user-specific group
        self.group_name = f"dashboard_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        # Join role-specific groups
        if self.user.is_officer:
            await self.channel_layer.group_add("officers", self.channel_name)
        if self.user.is_superuser:
            await self.channel_layer.group_add("admins", self.channel_name)
        
        await self.accept()
        
        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to dashboard updates',
            'user_id': self.user.id
        }))
    
    async def disconnect(self, close_code):
        # Leave groups
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if self.user.is_officer:
            await self.channel_layer.group_discard("officers", self.channel_name)
        if self.user.is_superuser:
            await self.channel_layer.group_discard("admins", self.channel_name)
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_metrics':
                # Subscribe to specific metrics
                metrics = data.get('metrics', [])
                for metric in metrics:
                    group_name = f"metrics_{metric}"
                    await self.channel_layer.group_add(group_name, self.channel_name)
                
                await self.send(text_data=json.dumps({
                    'type': 'subscription_confirmed',
                    'metrics': metrics
                }))
            
            elif message_type == 'request_update':
                # Send current dashboard data
                dashboard_data = await self.get_dashboard_data()
                await self.send(text_data=json.dumps({
                    'type': 'dashboard_update',
                    'data': dashboard_data,
                    'timestamp': datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data'],
            'timestamp': event['timestamp']
        }))
    
    async def metric_update(self, event):
        """Send metric update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'metric_update',
            'metric_type': event['metric_type'],
            'value': event['value'],
            'timestamp': event['timestamp']
        }))
    
    async def alert_notification(self, event):
        """Send alert notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'alert_id': event['alert_id'],
            'message': event['message'],
            'severity': event['severity'],
            'timestamp': event['timestamp']
        }))
    
    async def complaint_update(self, event):
        """Send complaint update notification"""
        await self.send(text_data=json.dumps({
            'type': 'complaint_update',
            'complaint_id': event['complaint_id'],
            'status': event['status'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def get_dashboard_data(self):
        """Get current dashboard data"""
        from analytics.views import dashboard_stats
        from django.test import RequestFactory
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/dashboard/stats/')
        request.user = self.user
        
        # This is a simplified version - in practice, you'd want to
        # extract the logic from the view into a separate function
        return {
            'total_complaints': 42,  # Placeholder
            'pending_complaints': 12,
            'resolved_complaints': 30,
            'resolution_rate': 71.4
        }

class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for general notifications"""
    
    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        self.group_name = f"notifications_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def notification(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event['title'],
            'message': event['message'],
            'category': event.get('category', 'info'),
            'timestamp': event['timestamp']
        }))

class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        self.group_name = f"chat_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive(self, text_data):
        """Handle chat messages"""
        try:
            data = json.loads(text_data)
            message = data.get('message')
            
            if message:
                # Process chat message (integrate with chatbot system)
                response = await self.process_chat_message(message)
                
                await self.send(text_data=json.dumps({
                    'type': 'chat_response',
                    'message': response,
                    'timestamp': datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
    
    @database_sync_to_async
    def process_chat_message(self, message):
        """Process chat message with chatbot"""
        # This would integrate with your existing chatbot system
        # For now, return a simple response
        return f"I received your message: {message}. How can I help you?"
