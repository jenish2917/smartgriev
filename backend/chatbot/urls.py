from django.urls import path
from .views import (
    ChatMessageView,
    ChatHistoryView,
)

urlpatterns = [
    path('message/', ChatMessageView.as_view(), name='chat-message'),
    path('history/', ChatHistoryView.as_view(), name='chat-history'),
]
