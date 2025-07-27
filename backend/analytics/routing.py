# WebSocket routing for real-time features
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]
