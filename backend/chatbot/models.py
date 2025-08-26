from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class ChatSession(models.Model):
    """Represents a chat session for maintaining context"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.UUIDField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    context = models.JSONField(default=dict, blank=True)  # Store conversation context
    
    def __str__(self):
        return f"{self.user.username} - Session {self.session_id}"

class ChatLog(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('mr', 'Marathi'),
        ('gu', 'Gujarati'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
        ('bn', 'Bengali'),
        ('pa', 'Punjabi'),
    ]
    
    REPLY_TYPE_CHOICES = [
        ('text', 'Text Reply'),
        ('quick_reply', 'Quick Reply Buttons'),
        ('rich_media', 'Rich Media'),
        ('escalation', 'Human Escalation'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_logs')
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    message = models.TextField()
    reply = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    intent = models.CharField(max_length=100, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    
    # Language support
    input_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    reply_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    
    # Reply type
    reply_type = models.CharField(max_length=20, choices=REPLY_TYPE_CHOICES, default='text')
    
    # Sentiment analysis
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    
    # Escalation tracking
    escalated_to_human = models.BooleanField(default=False)
    escalation_reason = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"

class ReplyMetadata(models.Model):
    chat_log = models.OneToOneField(ChatLog, on_delete=models.CASCADE, related_name='reply_metadata')
    # Add fields for your metadata, e.g.:
    # image_url = models.URLField(null=True, blank=True)
    # video_url = models.URLField(null=True, blank=True)
    # document_url = models.URLField(null=True, blank=True)

class QuickReplyTemplate(models.Model):
    """Predefined quick reply templates"""
    name = models.CharField(max_length=100)
    intent = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Quick Reply: {self.name}"

class QuickReplyButton(models.Model):
    template = models.ForeignKey(QuickReplyTemplate, on_delete=models.CASCADE, related_name='buttons')
    text = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    # Add other button properties as needed

class ChatFeedback(models.Model):
    """User feedback on chat interactions"""
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    chat_log = models.OneToOneField(ChatLog, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_helpful = models.BooleanField()
    comments = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.chat_log} - Rating: {self.rating}"

class ChatNotification(models.Model):
    """Proactive notifications to users"""
    NOTIFICATION_TYPES = [
        ('status_update', 'Status Update'),
        ('reminder', 'Reminder'),
        ('info', 'Information'),
        ('alert', 'Alert'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

class NotificationMetadata(models.Model):
    chat_notification = models.OneToOneField(ChatNotification, on_delete=models.CASCADE, related_name='metadata')
    # Add fields for your metadata, e.g.:
    # complaint_id = models.IntegerField(null=True, blank=True)
    # url = models.URLField(null=True, blank=True)