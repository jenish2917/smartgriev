from typing import Dict, Any, List, Optional
from django.db.models import QuerySet, Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from .base import BaseModelService, SearchableService, AuditableService
from ..models import Complaint, Department, AuditTrail, GPSValidation

User = get_user_model()


class ComplaintService(SearchableService, AuditableService):
    """
    Service class for handling complaint-related business logic.
    
    This service encapsulates all business operations for complaints,
    providing a clean interface for views and maintaining data integrity.
    """
    
    model = Complaint
    search_fields = ['title', 'description', 'category', 'incident_address']
    
    def get_queryset(self, **filters) -> QuerySet:
        """Get complaints queryset with optimized joins"""
        return super().get_queryset(**filters).select_related(
            'user', 'department'
        ).prefetch_related(
            'audit_trails', 'location_history'
        )
    
    def get_complaints_by_department(self, department_id: int, **filters) -> QuerySet:
        """Get complaints for specific department"""
        return self.get_queryset(department_id=department_id, **filters)
    
    def get_complaints_by_user(self, user_id: int, **filters) -> QuerySet:
        """Get complaints by specific user"""
        return self.get_queryset(user_id=user_id, **filters)
    
    def get_complaints_by_status(self, status: str, **filters) -> QuerySet:
        """Get complaints by status"""
        return self.get_queryset(status=status, **filters)
    
    def get_complaints_by_priority(self, priority: str, **filters) -> QuerySet:
        """Get complaints by priority"""
        return self.get_queryset(priority=priority, **filters)
    
    def get_complaints_in_area(self, center_lat: float, center_lon: float, 
                              radius_km: float = 5.0, **filters) -> QuerySet:
        """
        Get complaints within a geographical area.
        Uses Haversine formula approximation for distance calculation.
        """
        # Convert radius from km to degrees (approximate)
        # 1 degree ≈ 111 km at equator
        radius_deg = radius_km / 111.0
        
        lat_min = center_lat - radius_deg
        lat_max = center_lat + radius_deg
        lon_min = center_lon - radius_deg
        lon_max = center_lon + radius_deg
        
        return self.get_queryset(**filters).filter(
            Q(incident_latitude__gte=lat_min, incident_latitude__lte=lat_max,
              incident_longitude__gte=lon_min, incident_longitude__lte=lon_max) |
            Q(location_lat__gte=lat_min, location_lat__lte=lat_max,
              location_lon__gte=lon_min, location_lon__lte=lon_max)
        )
    
    def validate_before_save(self, instance: Complaint) -> None:
        """Custom validation for complaints"""
        super().validate_before_save(instance)
        
        # Validate GPS coordinates if provided
        if instance.incident_latitude and instance.incident_longitude:
            self._validate_gps_coordinates(instance.incident_latitude, instance.incident_longitude)
        
        # Validate department exists and is active
        if instance.department_id:
            if not Department.objects.filter(id=instance.department_id).exists():
                raise ValidationError("Invalid department selected")
        
        # Validate priority and status combinations
        if instance.status == 'resolved' and instance.priority == 'urgent':
            # Log this as it might need review
            pass
    
    def _validate_gps_coordinates(self, lat: float, lon: float) -> None:
        """Validate GPS coordinates are within reasonable bounds"""
        if not (-90 <= lat <= 90):
            raise ValidationError("Latitude must be between -90 and 90 degrees")
        if not (-180 <= lon <= 180):
            raise ValidationError("Longitude must be between -180 and 180 degrees")
    
    def create_complaint_with_location(self, data: Dict[str, Any], 
                                     created_by: User = None) -> Complaint:
        """Create complaint with enhanced location tracking"""
        with transaction.atomic():
            # Extract location data
            location_data = self._extract_location_data(data)
            
            # Create complaint
            complaint = self.create(data, created_by=created_by)
            
            # Create GPS validation entry if coordinates provided
            if location_data.get('incident_latitude') and location_data.get('incident_longitude'):
                self._create_gps_validation(complaint, location_data)
            
            # Create initial location history entry
            self._create_location_history(complaint, location_data, created_by, 'initial')
            
            return complaint
    
    def update_complaint_status(self, complaint_id: int, status: str, 
                               updated_by: User, notes: str = None) -> Optional[Complaint]:
        """Update complaint status with audit trail"""
        complaint = self.get_by_id(complaint_id)
        if not complaint:
            return None
        
        old_status = complaint.status
        complaint = self.update(complaint_id, {'status': status}, updated_by=updated_by)
        
        # Create detailed audit entry for status change
        if complaint and old_status != status:
            action = f"Status changed from {old_status} to {status}"
            if notes:
                action += f" - Notes: {notes}"
            self.create_audit_entry(complaint, action, updated_by)
        
        return complaint
    
    def assign_to_department(self, complaint_id: int, department_id: int, 
                           assigned_by: User) -> Optional[Complaint]:
        """Assign complaint to department"""
        complaint = self.get_by_id(complaint_id)
        if not complaint:
            return None
        
        old_dept = complaint.department
        complaint = self.update(complaint_id, {'department_id': department_id}, 
                              updated_by=assigned_by)
        
        if complaint and old_dept.id != department_id:
            new_dept = Department.objects.get(id=department_id)
            action = f"Assigned from {old_dept.name} to {new_dept.name}"
            self.create_audit_entry(complaint, action, assigned_by)
        
        return complaint
    
    def update_location(self, complaint_id: int, location_data: Dict[str, Any],
                       updated_by: User, update_reason: str = 'correction') -> Optional[Complaint]:
        """Update complaint location with tracking"""
        complaint = self.get_by_id(complaint_id)
        if not complaint:
            return None
        
        with transaction.atomic():
            # Update complaint with new location
            complaint = self.update(complaint_id, location_data, updated_by=updated_by)
            
            # Create location history entry
            self._create_location_history(complaint, location_data, updated_by, update_reason)
            
            # Update GPS validation if coordinates changed
            if location_data.get('incident_latitude') and location_data.get('incident_longitude'):
                self._update_gps_validation(complaint, location_data)
            
            return complaint
    
    def get_complaint_statistics(self, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Get complaint statistics"""
        queryset = self.get_queryset()
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        from django.db.models import Count
        
        stats = {
            'total': queryset.count(),
            'by_status': dict(queryset.values('status').annotate(count=Count('status')).values_list('status', 'count')),
            'by_priority': dict(queryset.values('priority').annotate(count=Count('priority')).values_list('priority', 'count')),
            'by_department': dict(queryset.values('department__name').annotate(count=Count('department')).values_list('department__name', 'count'))
        }
        
        return stats
    
    def create_audit_entry(self, instance: Complaint, action: str, user: User) -> None:
        """Create audit trail entry for complaint"""
        AuditTrail.objects.create(
            complaint=instance,
            action=action,
            by_user=user
        )
    
    def _extract_location_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract location-specific data from request data"""
        location_fields = [
            'incident_latitude', 'incident_longitude', 'incident_address',
            'incident_landmark', 'gps_accuracy', 'location_method', 'area_type'
        ]
        return {key: data.get(key) for key in location_fields if key in data}
    
    def _create_gps_validation(self, complaint: Complaint, location_data: Dict[str, Any]) -> None:
        """Create GPS validation entry"""
        lat = location_data.get('incident_latitude')
        lon = location_data.get('incident_longitude')
        accuracy = location_data.get('gps_accuracy', 0)
        
        # Basic validation rules
        accuracy_check = accuracy is None or accuracy < 100  # Good accuracy
        range_check = self._is_coordinates_in_service_area(lat, lon)
        
        validation_score = 1.0
        if not accuracy_check:
            validation_score -= 0.3
        if not range_check:
            validation_score -= 0.5
        
        GPSValidation.objects.create(
            complaint=complaint,
            is_valid=validation_score >= 0.5,
            validation_score=validation_score,
            accuracy_check=accuracy_check,
            range_check=range_check,
            duplicate_check=True,  # TODO: Implement duplicate detection
            speed_check=True       # TODO: Implement speed validation
        )
    
    def _update_gps_validation(self, complaint: Complaint, location_data: Dict[str, Any]) -> None:
        """Update GPS validation for complaint"""
        # Delete old validation and create new one
        GPSValidation.objects.filter(complaint=complaint).delete()
        self._create_gps_validation(complaint, location_data)
    
    def _create_location_history(self, complaint: Complaint, location_data: Dict[str, Any],
                                user: User, reason: str) -> None:
        """Create location history entry"""
        from ..models import IncidentLocationHistory
        
        lat = location_data.get('incident_latitude')
        lon = location_data.get('incident_longitude')
        
        if lat and lon:
            IncidentLocationHistory.objects.create(
                complaint=complaint,
                latitude=lat,
                longitude=lon,
                accuracy=location_data.get('gps_accuracy'),
                address=location_data.get('incident_address'),
                updated_by=user,
                update_reason=reason
            )
    
    def _is_coordinates_in_service_area(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within service area"""
        # TODO: Implement actual service area validation
        # For now, just check basic bounds (example for a city)
        # This should be configurable based on actual service area
        return True  # Placeholder implementation


class DepartmentService(BaseModelService):
    """Service for department management"""
    
    model = Department
    
    def get_departments_by_zone(self, zone: str) -> QuerySet:
        """Get departments by zone"""
        return self.get_queryset(zone=zone)
    
    def get_departments_with_officer(self) -> QuerySet:
        """Get departments that have assigned officers"""
        return self.get_queryset(officer__isnull=False)
    
    def assign_officer(self, department_id: int, officer_id: int) -> Optional[Department]:
        """Assign officer to department"""
        return self.update(department_id, {'officer_id': officer_id})