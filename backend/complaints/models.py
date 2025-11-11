from django.db import models
from django.conf import settings
from collections import namedtuple

class ComplaintCategory(models.Model):
    """Categories for complaints"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Complaint Categories"
    
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    zone = models.CharField(max_length=100)
    officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='departments')
    
    def __str__(self):
        return f"{self.name} - {self.zone}"

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed')
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical')
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('bn', 'Bengali'),
        ('te', 'Telugu'),
        ('mr', 'Marathi'),
        ('ta', 'Tamil'),
        ('gu', 'Gujarati'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
        ('pa', 'Punjabi'),
        ('ur', 'Urdu'),        # RTL support
        ('or', 'Odia'),
        ('as', 'Assamese'),
    ]
    
    # Unique complaint number (format: BC-{YEAR}-{CITY}-{DEPT}-{SEQ})
    complaint_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text='Unique complaint identifier: BC-YEAR-CITY-DEPT-SEQUENCE'
    )
    
    # Basic complaint fields
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ComplaintCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='complaints', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='medium')
    
    # Multi-lingual support
    submitted_language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text='Language in which the complaint was originally submitted'
    )
    original_text = models.TextField(
        blank=True,
        help_text='Original complaint text before translation (if submitted in non-English)'
    )
    translated_text = models.TextField(
        blank=True,
        help_text='English translation of the complaint for AI processing'
    )
    auto_translated = models.BooleanField(
        default=False,
        help_text='Whether the complaint was automatically translated'
    )
    
    # Multi-modal input support
    audio_file = models.FileField(upload_to='complaints/audio/', null=True, blank=True, help_text="Audio complaint file")
    image_file = models.ImageField(upload_to='complaints/images/', null=True, blank=True, help_text="Image complaint file")
    media = models.ImageField(upload_to='complaints/', null=True, blank=True)  # Legacy field
    
    # Multimodal analysis results
    audio_transcription = models.TextField(blank=True, help_text="Transcribed text from audio files")
    audio_language_detected = models.CharField(
        max_length=10,
        blank=True,
        help_text='Language detected in audio transcription'
    )
    image_ocr_text = models.TextField(blank=True, help_text="Text extracted from images via OCR")
    detected_objects = models.JSONField(default=list, blank=True, help_text="Objects detected in images")
    
    # AI processing results
    ai_confidence_score = models.FloatField(default=0.0, help_text="AI processing confidence score")
    sentiment = models.FloatField(null=True, help_text="Sentiment analysis score")
    department_classification = models.JSONField(default=dict, blank=True, help_text="AI department classification results")
    ai_processed_text = models.TextField(blank=True, help_text="AI enhanced/processed complaint text")
    
    # Gemini AI raw response (JSONB for advanced analytics)
    gemini_raw_response = models.JSONField(
        default=dict,
        blank=True,
        help_text='Raw Gemini API response including department classification, confidence scores, and metadata'
    )
    
    # Location fields
    location = models.CharField(max_length=500, blank=True, help_text="Location description or address")
    incident_latitude = models.FloatField(null=True, blank=True, help_text="Latitude where the incident occurred")
    incident_longitude = models.FloatField(null=True, blank=True, help_text="Longitude where the incident occurred")
    incident_address = models.TextField(null=True, blank=True, help_text="Full address of incident location")
    incident_landmark = models.CharField(max_length=200, null=True, blank=True, help_text="Nearby landmark")
    gps_accuracy = models.FloatField(null=True, blank=True, help_text="GPS accuracy in meters")
    location_method = models.CharField(max_length=50, default='gps', choices=[
        ('gps', 'GPS'),
        ('manual', 'Manual Entry'),
        ('address', 'Address Lookup'),
        ('plus_code', 'Plus Code')
    ])
    
    # MapMyIndia & Plus Code fields
    plus_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='Open Location Code (Plus Code) for precise location (e.g., 7JWWJ6J9+2V)'
    )
    ward_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Assigned ward/zone identifier'
    )
    ward_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='Ward/zone name for the complaint location'
    )
    
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
    
    # Escalation tracking
    escalated_at = models.DateTimeField(null=True, blank=True, help_text="When the complaint was last escalated")
    escalation_count = models.IntegerField(default=0, help_text="Number of times this complaint has been escalated")
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes and escalation history")
    internal_notes = models.TextField(blank=True, help_text="Internal notes for tracking")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When the complaint was resolved")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['complaint_number']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['department', 'status']),
        ]
    
    def __str__(self):
        return f"{self.complaint_number or self.title} - {self.status}"
    
    def save(self, *args, **kwargs):
        """Override save to generate complaint number and update resolved_at"""
        # Generate complaint number if not exists
        if not self.complaint_number:
            self.complaint_number = self.generate_complaint_number()
        
        # Update resolved_at timestamp when status changes to resolved
        if self.pk:  # Only for existing complaints
            try:
                old_complaint = Complaint.objects.get(pk=self.pk)
                if old_complaint.status != 'resolved' and self.status == 'resolved':
                    from django.utils import timezone
                    self.resolved_at = timezone.now()
            except Complaint.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def generate_complaint_number(self):
        """
        Generate unique complaint number: BC-{YEAR}-{CITY}-{DEPT}-{SEQ}
        Example: BC-2025-MUM-WAT-00123
        """
        from datetime import datetime
        
        year = datetime.now().year
        
        # Get city code (default to 'GEN' for general if no user location)
        city_code = 'GEN'
        if self.user and hasattr(self.user, 'city'):
            city_code = self.user.city[:3].upper()
        elif self.incident_address:
            # Extract city from address (simplified)
            city_code = self.incident_address.split(',')[0][:3].upper()
        
        # Get department code
        dept_code = 'OTH'  # Default
        if self.department:
            dept_code = self.department.name[:3].upper()
        elif self.category:
            dept_code = self.category.name[:3].upper()
        
        # Get sequence number for this year/city/dept combination
        from django.db.models import Max
        last_complaint = Complaint.objects.filter(
            complaint_number__startswith=f'BC-{year}-{city_code}-{dept_code}'
        ).aggregate(Max('complaint_number'))
        
        last_number = last_complaint['complaint_number__max']
        if last_number:
            # Extract sequence number and increment
            try:
                last_seq = int(last_number.split('-')[-1])
                seq = last_seq + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        
        return f'BC-{year}-{city_code}-{dept_code}-{seq:05d}'
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def get_incident_coordinates(self):
        """Get the primary incident coordinates"""
        Coordinates = namedtuple('Coordinates', ['latitude', 'longitude', 'accuracy', 'method'])
        # Use new GPS fields if available, otherwise fall back to legacy fields
        lat = self.incident_latitude if self.incident_latitude is not None else self.location_lat
        lon = self.incident_longitude if self.incident_longitude is not None else self.location_lon
        
        return Coordinates(
            latitude=lat,
            longitude=lon,
            accuracy=self.gps_accuracy,
            method=self.location_method
        )

class ComplaintStatus(models.Model):
    """Track status changes for complaints"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('pending_review', 'Pending Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected')
    ]
    
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.complaint.title} - {self.status}"

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