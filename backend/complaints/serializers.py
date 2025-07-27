from rest_framework import serializers
from .models import Complaint, Department, AuditTrail, IncidentLocationHistory, GPSValidation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

class DepartmentSerializer(serializers.ModelSerializer):
    officer = UserMiniSerializer(read_only=True)
    officer_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.filter(is_officer=True),
        source='officer'
    )

    class Meta:
        model = Department
        fields = ('id', 'name', 'zone', 'officer', 'officer_id')

class ComplaintSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Department.objects.all(),
        source='department'
    )
    incident_coordinates = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Complaint
        fields = ('id', 'user', 'title', 'description', 'media', 'category',
                 'sentiment', 'department', 'department_id', 'status', 'priority',
                 'incident_latitude', 'incident_longitude', 'incident_address', 
                 'incident_landmark', 'gps_accuracy', 'location_method', 'area_type',
                 'location_lat', 'location_lon', 'incident_coordinates',
                 'created_at', 'updated_at')
        read_only_fields = ('user', 'sentiment', 'created_at', 'updated_at')

    def get_incident_coordinates(self, obj):
        """Return formatted incident coordinates"""
        return obj.get_incident_coordinates()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        """Validate GPS coordinates"""
        incident_lat = data.get('incident_latitude')
        incident_lon = data.get('incident_longitude')
        
        if incident_lat is not None and incident_lon is not None:
            # Validate latitude range (-90 to 90)
            if not (-90 <= incident_lat <= 90):
                raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
            
            # Validate longitude range (-180 to 180)
            if not (-180 <= incident_lon <= 180):
                raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
            
            # Check GPS accuracy
            accuracy = data.get('gps_accuracy')
            if accuracy is not None and accuracy > 100:  # More than 100 meters
                raise serializers.ValidationError("GPS accuracy is too low. Please try again for better accuracy.")
        
        return data

class ComplaintStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ('status', 'priority')
        read_only_fields = ('priority',)

    def update(self, instance, validated_data):
        old_status = instance.status
        updated_instance = super().update(instance, validated_data)
        
        # Create audit trail
        if old_status != updated_instance.status:
            AuditTrail.objects.create(
                complaint=updated_instance,
                action=f'status_changed_from_{old_status}_to_{updated_instance.status}',
                by_user=self.context['request'].user
            )
        
        return updated_instance

class AuditTrailSerializer(serializers.ModelSerializer):
    by_user = UserMiniSerializer(read_only=True)
    complaint = ComplaintSerializer(read_only=True)
    
    class Meta:
        model = AuditTrail
        fields = ('id', 'complaint', 'action', 'by_user', 'timestamp')

class AuditTrailSerializer(serializers.ModelSerializer):
    by_user = UserMiniSerializer(read_only=True)
    complaint = serializers.SerializerMethodField()

    class Meta:
        model = AuditTrail
        fields = ('id', 'complaint', 'action', 'by_user', 'timestamp')

    def get_complaint(self, obj):
        return {
            'id': obj.complaint.id,
            'title': obj.complaint.title
        }

class IncidentLocationHistorySerializer(serializers.ModelSerializer):
    updated_by = UserMiniSerializer(read_only=True)
    complaint_title = serializers.CharField(source='complaint.title', read_only=True)
    
    class Meta:
        model = IncidentLocationHistory
        fields = ('id', 'complaint', 'complaint_title', 'latitude', 'longitude', 
                 'accuracy', 'address', 'updated_by', 'update_reason', 
                 'is_verified', 'verification_method', 'created_at')
        read_only_fields = ('updated_by', 'created_at')
    
    def create(self, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

class GPSValidationSerializer(serializers.ModelSerializer):
    validated_by = UserMiniSerializer(read_only=True)
    complaint_title = serializers.CharField(source='complaint.title', read_only=True)
    
    class Meta:
        model = GPSValidation
        fields = ('id', 'complaint', 'complaint_title', 'is_valid', 'validation_score',
                 'accuracy_check', 'range_check', 'duplicate_check', 'speed_check',
                 'validation_notes', 'validated_at', 'validated_by')
        read_only_fields = ('validated_by', 'validated_at')

class ComplaintLocationUpdateSerializer(serializers.ModelSerializer):
    """Specialized serializer for updating incident location"""
    
    class Meta:
        model = Complaint
        fields = ('incident_latitude', 'incident_longitude', 'incident_address', 
                 'incident_landmark', 'gps_accuracy', 'location_method', 'area_type')
    
    def validate(self, data):
        """Validate GPS coordinates for location updates"""
        incident_lat = data.get('incident_latitude')
        incident_lon = data.get('incident_longitude')
        
        if incident_lat is not None and incident_lon is not None:
            # Validate latitude range
            if not (-90 <= incident_lat <= 90):
                raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
            
            # Validate longitude range
            if not (-180 <= incident_lon <= 180):
                raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
        
        return data
