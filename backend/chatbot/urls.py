from django.urls import path
from .views import (
    ChatMessageView,
    ChatHistoryView,
    ChatFeedbackView,
    ChatSessionView,
    ChatNotificationView,
    chat_stats,
)

urlpatterns = [
    # Core chat functionality
    path('message/', ChatMessageView.as_view(), name='chat-message'),
    path('history/', ChatHistoryView.as_view(), name='chat-history'),
    
    # Session management
    path('session/', ChatSessionView.as_view(), name='chat-session-create'),
    path('session/<uuid:session_id>/', ChatSessionView.as_view(), name='chat-session-detail'),
    
    # Feedback system
    path('feedback/', ChatFeedbackView.as_view(), name='chat-feedback'),
    
    # Notifications
    path('notifications/', ChatNotificationView.as_view(), name='chat-notifications'),
    
    # Analytics and stats
    path('stats/', chat_stats, name='chat-stats'),
]
