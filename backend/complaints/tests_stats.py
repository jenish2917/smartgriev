from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Department, Complaint, AuditTrail

User = get_user_model()

class DepartmentStatisticsTests(APITestCase):
    def setUp(self):
        # Create users
        self.officer = User.objects.create_user(
            username='officer',
            password='testpass123',
            is_officer=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create department
        self.department = Department.objects.create(
            name='Test Department',
            zone='Test Zone',
            officer=self.officer
        )

        # Create complaints with different statuses
        self.create_test_complaints()

    def create_test_complaints(self):
        statuses = ['pending', 'in_progress', 'resolved', 'rejected']
        priorities = ['low', 'medium', 'high', 'urgent']

        for i in range(10):
            Complaint.objects.create(
                user=self.user,
                title=f'Test Complaint {i}',
                description='Test Description',
                category='Test Category',
                department=self.department,
                status=statuses[i % len(statuses)],
                priority=priorities[i % len(priorities)],
                location_lat=0.0,
                location_lon=0.0
            )

    def test_department_statistics(self):
        # Authenticate as officer
        self.client.force_authenticate(user=self.officer)

        # Get department stats
        response = self.client.get(
            reverse('department-stats', kwargs={'pk': self.department.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Verify statistics
        self.assertEqual(data['total_complaints'], 10)
        self.assertEqual(data['pending'], 3)  # 10 complaints / 4 statuses ≈ 3
        self.assertEqual(data['in_progress'], 3)
        self.assertEqual(data['resolved'], 2)
        self.assertEqual(data['rejected'], 2)
        self.assertEqual(data['high_priority'], 3)  # 10 complaints / 4 priorities ≈ 3
        self.assertEqual(data['urgent_priority'], 2)

    def test_department_statistics_unauthorized(self):
        # Try to access stats without authentication
        response = self.client.get(
            reverse('department-stats', kwargs={'pk': self.department.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Try to access stats as regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('department-stats', kwargs={'pk': self.department.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complaint_workflow(self):
        # Create complaint as user
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('complaint-list-create'), {
            'title': 'New Complaint',
            'description': 'Test Description',
            'category': 'Test Category',
            'department_id': self.department.id,
            'priority': 'high',
            'location_lat': 0.0,
            'location_lon': 0.0
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        complaint_id = response.data['id']

        # Verify audit trail creation
        response = self.client.get(
            reverse('complaint-audit-trail', kwargs={'complaint_id': complaint_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should have one 'created' entry

        # Update status as officer
        self.client.force_authenticate(user=self.officer)
        response = self.client.patch(
            reverse('complaint-status-update', kwargs={'pk': complaint_id}),
            {'status': 'in_progress'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify audit trail update
        response = self.client.get(
            reverse('complaint-audit-trail', kwargs={'complaint_id': complaint_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should have 'created' and 'status_changed' entries
