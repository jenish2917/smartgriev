from math import radians, sin, cos, sqrt, atan2
from django.conf import settings
from .models import Complaint

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def perform_gps_validation(complaint):
    """Perform GPS validation checks"""
    results = {
        'accuracy_check': True,
        'range_check': True,
        'duplicate_check': True,
        'speed_check': True,
        'score': 1.0,
        'is_valid': True,
        'notes': ''
    }
    
    notes = []
    
    # Check GPS accuracy
    if complaint.gps_accuracy and complaint.gps_accuracy > settings.GPS_ACCURACY_THRESHOLD:
        results['accuracy_check'] = False
        notes.append(f"GPS accuracy too low: {complaint.gps_accuracy}m")
    
    # Check if coordinates are within service area
    if complaint.incident_latitude and complaint.incident_longitude:
        if not (settings.MIN_LAT <= complaint.incident_latitude <= settings.MAX_LAT and \
                settings.MIN_LON <= complaint.incident_longitude <= settings.MAX_LON):
            results['range_check'] = False
            notes.append("Location outside service area")
    
    # Check for duplicate locations
    if complaint.incident_latitude and complaint.incident_longitude:
        nearby_complaints = Complaint.objects.filter(
            incident_latitude__isnull=False,
            incident_longitude__isnull=False
        ).exclude(id=complaint.id)
        
        for nearby in nearby_complaints:
            distance = calculate_distance(
                complaint.incident_latitude, complaint.incident_longitude,
                nearby.incident_latitude, nearby.incident_longitude
            )
            if distance < 100:  # Within 100 meters
                results['duplicate_check'] = False
                notes.append(f"Similar location within 100m (Complaint #{nearby.id})")
                break
    
    # Calculate overall score
    checks = [results['accuracy_check'], results['range_check'], results['duplicate_check'], results['speed_check']]
    results['score'] = sum(checks) / len(checks)
    results['is_valid'] = results['score'] >= 0.75
    results['notes'] = '; '.join(notes) if notes else 'All validation checks passed'
    
    return results
