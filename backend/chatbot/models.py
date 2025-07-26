from django.db import models
from django.conf import settings

class ChatLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_logs')
    message = models.TextField()
    reply = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    intent = models.CharField(max_length=100, null=True)
    confidence = models.FloatField(null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
