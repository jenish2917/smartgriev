from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100)
    zone = models.CharField(max_length=100)
    officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='departments')
    
    def __str__(self):
        return f"{self.name} - {self.zone}"

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected')
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    media = models.FileField(upload_to='complaints/', null=True, blank=True)
    category = models.CharField(max_length=100)
    sentiment = models.FloatField(null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='complaints')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    location_lat = models.FloatField()
    location_lon = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.status}"

class AuditTrail(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='audit_trails')
    action = models.CharField(max_length=100)
    by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.complaint.title} - {self.action} by {self.by_user.username}"
