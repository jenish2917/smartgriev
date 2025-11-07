from django.urls import path
# Only import simple views (no spaCy dependency)
from .simple_views import (
    simple_chat,
    chat_health,
)

urlpatterns = [
    # Simple ChatGPT-like chat (Google AI powered)
    path('chat/', simple_chat, name='simple-chat'),
    path('health/', chat_health, name='chat-health'),
]
