from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .throttling import (
    EmailVerificationRateThrottle,
    MobileVerificationRateThrottle,
    PasswordResetRateThrottle
)

User = get_user_model()

class ThrottlingTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'TestPass123!',
            'email': 'test@example.com',
            'mobile': '9876543210',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_email_verification_throttling(self):
        throttle = EmailVerificationRateThrottle()
        
        # Make requests up to the limit
        for _ in range(throttle.rate_limit):
            response = self.client.get(reverse('verify-email'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Next request should be throttled
        response = self.client.get(reverse('verify-email'))
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_mobile_verification_throttling(self):
        throttle = MobileVerificationRateThrottle()
        
        # Make requests up to the limit
        for _ in range(throttle.rate_limit):
            response = self.client.post(reverse('verify-mobile'), {
                'mobile': '9876543210'
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Next request should be throttled
        response = self.client.post(reverse('verify-mobile'), {
            'mobile': '9876543210'
        })
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_password_reset_throttling(self):
        throttle = PasswordResetRateThrottle()
        
        # Make requests up to the limit
        for _ in range(throttle.rate_limit):
            response = self.client.post(reverse('reset-password-request'), {
                'email': self.user_data['email']
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Next request should be throttled
        response = self.client.post(reverse('reset-password-request'), {
            'email': self.user_data['email']
        })
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
