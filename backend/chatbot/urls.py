from django.urls import path
# Only import simple views (no spaCy dependency)
from .simple_views import (
    simple_chat,
    chat_health,
)
# Import voice assistant views
from .voice_views import (
    voice_complaint_submit,
    voice_chat,
    voice_languages,
    voice_health,
)

urlpatterns = [
    # Simple ChatGPT-like chat (Google AI powered)
    path('chat/', simple_chat, name='simple-chat'),
    path('health/', chat_health, name='chat-health'),
    
    # CivicAI Voice Assistant endpoints
    path('voice/submit/', voice_complaint_submit, name='voice-complaint-submit'),
    path('voice/chat/', voice_chat, name='voice-chat'),
    path('voice/languages/', voice_languages, name='voice-languages'),
    path('voice/health/', voice_health, name='voice-health'),
]

