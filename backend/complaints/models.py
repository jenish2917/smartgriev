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
    
    # Enhanced GPS location fields for incident location
    incident_latitude = models.FloatField(null=True, blank=True, help_text="Latitude where the incident occurred")
    incident_longitude = models.FloatField(null=True, blank=True, help_text="Longitude where the incident occurred")
    incident_address = models.TextField(null=True, blank=True, help_text="Full address of incident location")
    incident_landmark = models.CharField(max_length=200, null=True, blank=True, help_text="Nearby landmark")
    gps_accuracy = models.FloatField(null=True, blank=True, help_text="GPS accuracy in meters")
    location_method = models.CharField(max_length=50, default='gps', choices=[
        ('gps', 'GPS'),
        ('manual', 'Manual Entry'),
        ('address', 'Address Lookup')
    ])
    
    # Additional location context
    area_type = models.CharField(max_length=50, null=True, blank=True, choices=[
        ('residential', 'Residential Area'),
        ('commercial', 'Commercial Area'),
        ('industrial', 'Industrial Area'),
        ('public', 'Public Space'),
        ('road', 'Road/Highway'),
        ('park', 'Park/Garden'),
        ('other', 'Other')
    ])
    
    # Legacy fields (keeping for backward compatibility)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def get_incident_coordinates(self):
        """Get the primary incident coordinates"""
        # Use new GPS fields if available, otherwise fall back to legacy fields
        lat = self.incident_latitude if self.incident_latitude is not None else self.location_lat
        lon = self.incident_longitude if self.incident_longitude is not None else self.location_lon
        
        return {
            'latitude': lat,
            'longitude': lon,
            'accuracy': self.gps_accuracy,
            'method': self.location_method
        }
    
    def save(self, *args, **kwargs):
        """Override save to migrate legacy location data"""
        # If new GPS fields are empty but legacy fields exist, migrate the data
        if (self.incident_latitude is None and self.incident_longitude is None and 
            self.location_lat is not None and self.location_lon is not None):
            self.incident_latitude = self.location_lat
            self.incident_longitude = self.location_lon
            
        super().save(*args, **kwargs)

class IncidentLocationHistory(models.Model):
    """Track location updates and validations for complaints"""
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='location_history')
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    update_reason = models.CharField(max_length=100, choices=[
        ('initial', 'Initial Location'),
        ('correction', 'Location Correction'),
        ('verification', 'Field Verification'),
        ('auto_geocode', 'Automatic Geocoding')
    ])
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=50, null=True, blank=True, choices=[
        ('field_visit', 'Field Visit'),
        ('photo_verification', 'Photo Verification'),
        ('landmark_match', 'Landmark Matching'),
        ('address_verification', 'Address Verification')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Location for {self.complaint.title} - {self.update_reason}"

class GPSValidation(models.Model):
    """Validate GPS coordinates and detect anomalies"""
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='gps_validation')
    is_valid = models.BooleanField(default=True)
    validation_score = models.FloatField(default=1.0, help_text="Confidence score 0-1")
    
    # Validation checks
    accuracy_check = models.BooleanField(default=True)
    range_check = models.BooleanField(default=True)  # Within service area
    duplicate_check = models.BooleanField(default=True)  # Not duplicate location
    speed_check = models.BooleanField(default=True)  # Reasonable travel speed
    
    validation_notes = models.TextField(null=True, blank=True)
    validated_at = models.DateTimeField(auto_now_add=True)
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"GPS Validation for {self.complaint.title} - {'Valid' if self.is_valid else 'Invalid'}"

class AuditTrail(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='audit_trails')
    action = models.CharField(max_length=100)
    by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.complaint.title} - {self.action} by {self.by_user.username}"
