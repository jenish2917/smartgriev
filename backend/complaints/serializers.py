from rest_framework import serializers
from .models import Complaint, Department, AuditTrail
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

    class Meta:
        model = Complaint
        fields = ('id', 'user', 'title', 'description', 'media', 'category',
                 'sentiment', 'department', 'department_id', 'status', 'priority',
                 'location_lat', 'location_lon', 'created_at', 'updated_at')
        read_only_fields = ('user', 'sentiment', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

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
