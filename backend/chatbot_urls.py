"""
Minimal URL configuration for chatbot-only server
"""
from django.urls import path, include

urlpatterns = [
    path('api/chatbot/', include('chatbot.urls')),
]
