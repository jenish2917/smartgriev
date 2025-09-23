"""
Complaint Service Module

This module provides a comprehensive service layer for handling complaint operations
following SOLID principles and clean architecture patterns.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from django.db.models import QuerySet, Q, Count, Avg
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .base import BaseModelService, SearchableService, AuditableService
from ..models import Complaint, Department, AuditTrail, GPSValidation

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


class ComplaintStatus(Enum):
    """Enumeration for complaint statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class ComplaintPriority(Enum):
    """Enumeration for complaint priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplaintFilterCriteria:
    """Data class for complaint filtering criteria"""
    user_id: Optional[int] = None
    department_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    location_radius: Optional[float] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None


@dataclass
class ComplaintAnalytics:
    """Data class for complaint analytics"""
    total_complaints: int
    resolved_complaints: int
    pending_complaints: int
    average_resolution_time: float
    resolution_rate: float
    complaints_by_category: Dict[str, int]
    complaints_by_priority: Dict[str, int]


class ComplaintValidatorInterface(ABC):
    """Interface for complaint validation strategies"""
    
    @abstractmethod
    def validate(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate complaint data and return list of errors"""
        pass


class LocationValidator(ComplaintValidatorInterface):
    """Validator for complaint location data"""
    
    def validate(self, complaint_data: Dict[str, Any]) -> List[str]:
        errors = []
        
        latitude = complaint_data.get('latitude')
        longitude = complaint_data.get('longitude')
        
        if latitude is None or longitude is None:
            errors.append("Both latitude and longitude are required")
            return errors
        
        if not (-90 <= latitude <= 90):
            errors.append("Latitude must be between -90 and 90 degrees")
        
        if not (-180 <= longitude <= 180):
            errors.append("Longitude must be between -180 and 180 degrees")
        
        # GPS accuracy validation
        gps_accuracy = complaint_data.get('gps_accuracy', 0)
        if gps_accuracy > 100:  # 100 meters threshold
            errors.append("GPS accuracy is too low for reliable location")
        
        return errors


class CategoryValidator(ComplaintValidatorInterface):
    """Validator for complaint category data"""
    
    VALID_CATEGORIES = [
        'infrastructure', 'environment', 'transportation', 
        'health', 'education', 'public_services', 'other'
    ]
    
    def validate(self, complaint_data: Dict[str, Any]) -> List[str]:
        errors = []
        
        category = complaint_data.get('category')
        if not category:
            errors.append("Category is required")
        elif category not in self.VALID_CATEGORIES:
            errors.append(f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}")
        
        return errors


class ComplaintNotificationInterface(ABC):
    """Interface for complaint notification strategies"""
    
    @abstractmethod
    def notify_created(self, complaint: Complaint) -> None:
        """Send notification when complaint is created"""
        pass
    
    @abstractmethod
    def notify_status_changed(self, complaint: Complaint, old_status: str) -> None:
        """Send notification when complaint status changes"""
        pass


class EmailNotificationStrategy(ComplaintNotificationInterface):
    """Email notification implementation"""
    
    def notify_created(self, complaint: Complaint) -> None:
        # Implementation for email notification on creation
        pass
    
    def notify_status_changed(self, complaint: Complaint, old_status: str) -> None:
        # Implementation for email notification on status change
        pass


class ComplaintService(SearchableService, AuditableService):
    """
    Enhanced complaint service with SOLID principles and clean architecture.
    
    This service provides comprehensive complaint management functionality
    while maintaining separation of concerns and extensibility.
    """
    
    model = Complaint
    search_fields = ['title', 'description', 'category', 'incident_address']
    
    def __init__(self):
        super().__init__()
        self._validators: List[ComplaintValidatorInterface] = [
            LocationValidator(),
            CategoryValidator()
        ]
        self._notification_strategy: ComplaintNotificationInterface = EmailNotificationStrategy()
    
    def add_validator(self, validator: ComplaintValidatorInterface) -> None:
        """Add custom validator to the service"""
        self._validators.append(validator)
    
    def set_notification_strategy(self, strategy: ComplaintNotificationInterface) -> None:
        """Set notification strategy"""
        self._notification_strategy = strategy
    
    def get_queryset(self, **filters) -> QuerySet:
        """Get optimized complaints queryset"""
        return super().get_queryset(**filters).select_related(
            'user', 'department'
        ).prefetch_related(
            'audit_trails'
        )
    
    def get_filtered_complaints(self, criteria: ComplaintFilterCriteria) -> QuerySet:
        """Get complaints based on filter criteria"""
        queryset = self.get_queryset()
        
        if criteria.user_id:
            queryset = queryset.filter(user_id=criteria.user_id)
        
        if criteria.department_id:
            queryset = queryset.filter(department_id=criteria.department_id)
        
        if criteria.status:
            queryset = queryset.filter(status=criteria.status)
        
        if criteria.priority:
            queryset = queryset.filter(priority=criteria.priority)
        
        if criteria.category:
            queryset = queryset.filter(category=criteria.category)
        
        if criteria.date_from:
            queryset = queryset.filter(created_at__gte=criteria.date_from)
        
        if criteria.date_to:
            queryset = queryset.filter(created_at__lte=criteria.date_to)
        
        if (criteria.center_latitude and criteria.center_longitude and 
            criteria.location_radius):
            queryset = self._filter_by_location(
                queryset, 
                criteria.center_latitude, 
                criteria.center_longitude, 
                criteria.location_radius
            )
        
        return queryset
    
    def create_complaint(self, complaint_data: Dict[str, Any], user: AbstractUser) -> Complaint:
        """Create new complaint with comprehensive validation"""
        # Validate complaint data
        validation_errors = self._validate_complaint_data(complaint_data)
        if validation_errors:
            raise ValidationError(validation_errors)
        
        # Auto-assign department based on category and location
        department = self._auto_assign_department(
            complaint_data.get('category'),
            complaint_data.get('latitude'),
            complaint_data.get('longitude')
        )
        
        # Set default values
        complaint_data.update({
            'user': user,
            'department': department,
            'status': ComplaintStatus.PENDING.value,
            'priority': self._calculate_priority(complaint_data),
            'created_at': timezone.now()
        })
        
        with transaction.atomic():
            complaint = self.create(complaint_data, created_by=user)
            
            # Create GPS validation record
            self._create_gps_validation(complaint, complaint_data)
            
            # Send notification
            self._notification_strategy.notify_created(complaint)
            
            return complaint
    
    def update_complaint_status(self, complaint_id: int, new_status: str, 
                               updated_by: AbstractUser, notes: str = None) -> Optional[Complaint]:
        """Update complaint status with validation and notifications"""
        complaint = self.get_by_id(complaint_id)
        if not complaint:
            return None
        
        if new_status not in [status.value for status in ComplaintStatus]:
            raise ValidationError(f"Invalid status: {new_status}")
        
        old_status = complaint.status
        update_data = {
            'status': new_status,
            'updated_at': timezone.now()
        }
        
        if notes:
            update_data['notes'] = notes
        
        if new_status == ComplaintStatus.RESOLVED.value:
            update_data['resolved_at'] = timezone.now()
        
        with transaction.atomic():
            updated_complaint = self.update(complaint_id, update_data, updated_by=updated_by)
            
            if updated_complaint:
                self._notification_strategy.notify_status_changed(updated_complaint, old_status)
            
            return updated_complaint
    
    def get_complaint_analytics(self, criteria: ComplaintFilterCriteria = None) -> ComplaintAnalytics:
        """Get comprehensive complaint analytics"""
        if criteria:
            queryset = self.get_filtered_complaints(criteria)
        else:
            queryset = self.get_queryset()
        
        total_complaints = queryset.count()
        resolved_complaints = queryset.filter(status=ComplaintStatus.RESOLVED.value).count()
        pending_complaints = queryset.filter(status=ComplaintStatus.PENDING.value).count()
        
        # Calculate average resolution time
        resolved_queryset = queryset.filter(
            status=ComplaintStatus.RESOLVED.value,
            resolved_at__isnull=False
        )
        
        avg_resolution_time = 0.0
        if resolved_queryset.exists():
            # Calculate in hours
            for complaint in resolved_queryset:
                resolution_time = (complaint.resolved_at - complaint.created_at).total_seconds() / 3600
                avg_resolution_time += resolution_time
            avg_resolution_time /= resolved_queryset.count()
        
        resolution_rate = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0.0
        
        # Complaints by category
        complaints_by_category = dict(
            queryset.values_list('category').annotate(count=Count('id'))
        )
        
        # Complaints by priority
        complaints_by_priority = dict(
            queryset.values_list('priority').annotate(count=Count('id'))
        )
        
        return ComplaintAnalytics(
            total_complaints=total_complaints,
            resolved_complaints=resolved_complaints,
            pending_complaints=pending_complaints,
            average_resolution_time=avg_resolution_time,
            resolution_rate=resolution_rate,
            complaints_by_category=complaints_by_category,
            complaints_by_priority=complaints_by_priority
        )
    
    def get_complaints_near_location(self, latitude: float, longitude: float, 
                                    radius_km: float = 5.0) -> QuerySet:
        """Get complaints within specified radius of location"""
        return self._filter_by_location(self.get_queryset(), latitude, longitude, radius_km)
    
    def validate_before_save(self, instance: Complaint) -> None:
        """Additional validation before saving complaint"""
        if instance.priority not in [priority.value for priority in ComplaintPriority]:
            raise ValidationError(f"Invalid priority: {instance.priority}")
        
        if instance.status not in [status.value for status in ComplaintStatus]:
            raise ValidationError(f"Invalid status: {instance.status}")
    
    def create_audit_entry(self, instance: Complaint, action: str, user: AbstractUser) -> None:
        """Create audit trail entry for complaint"""
        AuditTrail.objects.create(
            complaint=instance,
            action=action,
            user=user,
            timestamp=timezone.now(),
            details=f"Complaint {action} by {user.username}"
        )
    
    # Private helper methods
    
    def _validate_complaint_data(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate complaint data using all registered validators"""
        all_errors = []
        for validator in self._validators:
            errors = validator.validate(complaint_data)
            all_errors.extend(errors)
        return all_errors
    
    def _auto_assign_department(self, category: str, latitude: float, longitude: float) -> Department:
        """Auto-assign department based on category and location"""
        # Simple implementation - can be enhanced with more complex logic
        try:
            return Department.objects.filter(
                categories__contains=[category]
            ).first() or Department.objects.first()
        except Department.DoesNotExist:
            raise ValidationError("No department available for assignment")
    
    def _calculate_priority(self, complaint_data: Dict[str, Any]) -> str:
        """Calculate complaint priority based on various factors"""
        # Simple priority calculation - can be enhanced with ML models
        category = complaint_data.get('category', '')
        description = complaint_data.get('description', '').lower()
        
        critical_keywords = ['emergency', 'urgent', 'critical', 'danger', 'life']
        high_keywords = ['serious', 'major', 'important', 'significant']
        
        if any(keyword in description for keyword in critical_keywords):
            return ComplaintPriority.CRITICAL.value
        elif any(keyword in description for keyword in high_keywords):
            return ComplaintPriority.HIGH.value
        elif category in ['health', 'infrastructure']:
            return ComplaintPriority.MEDIUM.value
        else:
            return ComplaintPriority.LOW.value
    
    def _create_gps_validation(self, complaint: Complaint, complaint_data: Dict[str, Any]) -> None:
        """Create GPS validation record"""
        gps_data = {
            'complaint': complaint,
            'latitude': complaint_data.get('latitude'),
            'longitude': complaint_data.get('longitude'),
            'accuracy': complaint_data.get('gps_accuracy', 0),
            'validated_at': timezone.now(),
            'is_valid': complaint_data.get('gps_accuracy', 0) <= 100
        }
        GPSValidation.objects.create(**gps_data)
    
    def _filter_by_location(self, queryset: QuerySet, latitude: float, 
                           longitude: float, radius_km: float) -> QuerySet:
        """Filter queryset by location using spatial queries"""
        # Simple distance calculation - in production, use PostGIS for better performance
        from math import radians, cos, sin, asin, sqrt
        
        def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate haversine distance between two points"""
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            return 2 * asin(sqrt(a)) * 6371  # Earth radius in km
        
        # Filter complaints within radius
        nearby_complaints = []
        for complaint in queryset:
            if complaint.latitude and complaint.longitude:
                distance = haversine_distance(
                    latitude, longitude, 
                    float(complaint.latitude), float(complaint.longitude)
                )
                if distance <= radius_km:
                    nearby_complaints.append(complaint.id)
        
        return queryset.filter(id__in=nearby_complaints)
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
                                     created_by: Any = None) -> Complaint:
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
                               updated_by: Any, notes: str = None) -> Optional[Complaint]:
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
                           assigned_by: Any) -> Optional[Complaint]:
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
                       updated_by: Any, update_reason: str = 'correction') -> Optional[Complaint]:
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
    
    def create_audit_entry(self, instance: Complaint, action: str, user: Any) -> None:
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
                                user: Any, reason: str) -> None:
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