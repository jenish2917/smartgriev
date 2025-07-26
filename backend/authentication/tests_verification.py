from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import VerificationToken
from unittest.mock import patch

User = get_user_model()

class VerificationTests(APITestCase):
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

    def test_email_verification_flow(self):
        # Request verification email
        response = self.client.get(reverse('verify-email'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VerificationToken.objects.count(), 1)
        
        # Verify token
        token = VerificationToken.objects.first()
        response = self.client.post(reverse('verify-email'), {'token': token.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user is verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    @patch('authentication.utils.sms.send_otp_sms')
    def test_mobile_verification_flow(self, mock_send_sms):
        mock_send_sms.return_value = True
        
        # Request OTP
        response = self.client.post(reverse('verify-mobile'), {'mobile': '9876543210'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get OTP from database (in real scenario, this would be sent via SMS)
        token = VerificationToken.objects.filter(user=self.user, token_type='mobile').first()
        
        # Verify OTP
        response = self.client.post(reverse('verify-mobile'), {
            'mobile': '9876543210',
            'otp': token.otp
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user is verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.mobile_verified)

    def test_2fa_flow(self):
        # Enable 2FA
        response = self.client.get(reverse('2fa'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('secret', response.data)
        self.assertIn('qr_code', response.data)
        
        # Verify 2FA setup
        import pyotp
        totp = pyotp.TOTP(self.user.two_fa_secret)
        code = totp.now()
        
        response = self.client.post(reverse('2fa'), {'code': code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check 2FA is enabled
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_2fa_enabled)

    def test_password_reset_flow(self):
        # Request password reset
        response = self.client.post(reverse('reset-password-request'), {
            'email': self.user_data['email']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get token from database
        token = VerificationToken.objects.filter(
            user=self.user,
            token_type='password'
        ).first()
        
        # Reset password
        new_password = 'NewTestPass123!'
        response = self.client.post(reverse('reset-password-confirm'), {
            'token': token.token,
            'new_password': new_password,
            'confirm_password': new_password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Try logging in with new password
        self.client.logout()
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': self.user_data['username'],
            'password': new_password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
