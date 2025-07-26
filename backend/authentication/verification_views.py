from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import VerificationToken
from .verification_serializers import (
    EmailVerificationSerializer,
    MobileVerificationSerializer,
    TwoFactorEnableSerializer,
    TwoFactorVerifySerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
import random
import qrcode
import io
import base64

from .throttling import (
    EmailVerificationRateThrottle,
    MobileVerificationRateThrottle,
    PasswordResetRateThrottle,
    TwoFactorRateThrottle
)

class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    throttle_classes = [EmailVerificationRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_obj = serializer.validated_data['token_obj']
        
        user = token_obj.user
        user.email_verified = True
        user.save()
        
        token_obj.is_used = True
        token_obj.save()
        
        return Response({
            "message": "Email verified successfully"
        })

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Create verification token
        token = VerificationToken.objects.create(
            user=request.user,
            token_type='email'
        )

        # Send verification email
        context = {
            'user': request.user,
            'verification_url': f"{settings.FRONTEND_URL}/verify-email/{token.token}"
        }
        
        html_message = render_to_string('email/verify_email.html', context)
        send_mail(
            'Verify your email - SmartGriev',
            'Please verify your email address',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            html_message=html_message
        )

        return Response({
            "message": "Verification email sent"
        })

class MobileVerificationView(generics.GenericAPIView):
    serializer_class = MobileVerificationSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [MobileVerificationRateThrottle]

    def generate_otp(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if 'otp' in serializer.validated_data:
            # Verify OTP
            token = VerificationToken.objects.filter(
                user=request.user,
                token_type='mobile',
                is_used=False,
                otp=serializer.validated_data['otp']
            ).first()

            if not token or not token.is_valid():
                return Response(
                    {"error": "Invalid or expired OTP"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request.user.mobile_verified = True
            request.user.save()
            
            token.is_used = True
            token.save()

            return Response({
                "message": "Mobile number verified successfully"
            })
        else:
            # Send OTP
            otp = self.generate_otp()
            VerificationToken.objects.create(
                user=request.user,
                token_type='mobile',
                otp=otp
            )

            # Send OTP via SMS
            from .utils.sms import send_otp_sms
            if send_otp_sms(request.user.mobile, otp):
                return Response({
                    "message": "OTP sent successfully to your mobile number"
                })
            else:
                return Response({
                    "error": "Failed to send OTP. Please try again."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TwoFactorAuthenticationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TwoFactorVerifySerializer
        return TwoFactorEnableSerializer

    def get(self, request, *args, **kwargs):
        """Enable 2FA and get QR code"""
        if request.user.is_2fa_enabled:
            return Response({
                "error": "2FA is already enabled"
            }, status=status.HTTP_400_BAD_REQUEST)

        secret = request.user.enable_2fa()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(request.user.get_2fa_uri())
        qr.make(fit=True)

        # Create QR code image
        img_buffer = io.BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()

        return Response({
            "secret": secret,
            "qr_code": f"data:image/png;base64,{img_str}"
        })

    def post(self, request, *args, **kwargs):
        """Verify 2FA code"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.verify_2fa(serializer.validated_data['code']):
            return Response({
                "message": "2FA code verified successfully"
            })
        
        return Response({
            "error": "Invalid 2FA code"
        }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])
        token = VerificationToken.objects.create(
            user=user,
            token_type='password'
        )

        # Send password reset email
        context = {
            'user': user,
            'reset_url': f"{settings.FRONTEND_URL}/reset-password/{token.token}"
        }
        
        html_message = render_to_string('email/reset_password.html', context)
        send_mail(
            'Reset your password - SmartGriev',
            'Click the link to reset your password',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message
        )

        return Response({
            "message": "Password reset email sent"
        })

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_obj = serializer.validated_data['token_obj']
        user = token_obj.user
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        token_obj.is_used = True
        token_obj.save()

        return Response({
            "message": "Password reset successful"
        })
