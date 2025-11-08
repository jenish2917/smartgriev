from django.urls import path
# Only import simple views (no spaCy dependency)
from .simple_views import (
    simple_chat,
    chat_health,
)

# Import Gemini views
from .gemini_views import (
    gemini_chat,
    create_complaint_from_chat,
    conversation_summary,
    start_conversation,
    end_conversation,
    gemini_health_check,
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
    
    # Gemini AI chatbot endpoints
    path('gemini/chat/', gemini_chat, name='gemini-chat'),
    path('gemini/start/', start_conversation, name='gemini-start'),
    path('gemini/summary/<str:session_id>/', conversation_summary, name='gemini-summary'),
    path('gemini/end/<str:session_id>/', end_conversation, name='gemini-end'),
    path('gemini/create-complaint/', create_complaint_from_chat, name='gemini-create-complaint'),
    path('gemini/health/', gemini_health_check, name='gemini-health'),
    
    # CivicAI Voice Assistant endpoints
    path('voice/submit/', voice_complaint_submit, name='voice-complaint-submit'),
    path('voice/chat/', voice_chat, name='voice-chat'),
    path('voice/languages/', voice_languages, name='voice-languages'),
    path('voice/health/', voice_health, name='voice-health'),
]

