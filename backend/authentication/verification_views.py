from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import OTPVerification, User
from .models import VerificationToken
from .verification_serializers import (
    EmailVerificationSerializer,
    MobileVerificationSerializer,
    TwoFactorEnableSerializer,
    TwoFactorVerifySerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
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


class SendOTPView(generics.GenericAPIView):
    """Send OTP for mobile login/registration"""
    permission_classes = [AllowAny]
    # throttle_classes = [MobileVerificationRateThrottle]  # Disabled for development

    def generate_otp(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def post(self, request, *args, **kwargs):
        mobile_number = request.data.get('mobile_number')
        
        if not mobile_number:
            return Response({
                "error": "Mobile number is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists with this mobile number
        user = None
        try:
            user = User.objects.get(mobile=mobile_number)  # Changed from mobile_number to mobile
        except User.DoesNotExist:
            # Create a temporary user for OTP verification
            # We'll complete registration after OTP verification
            username = f"temp_{mobile_number[-10:]}"
            try:
                user = User.objects.create_user(
                    username=username,
                    mobile=mobile_number,  # Changed from mobile_number to mobile
                    is_active=False  # Mark as inactive until OTP verified
                )
            except Exception as e:
                # If user creation fails, we can still send OTP
                # The user will be created in verify step
                pass
        
        # Generate OTP
        otp = self.generate_otp()
        
        # Store OTP in OTPVerification model
        from django.utils import timezone
        from datetime import timedelta
        
        if user:
            OTPVerification.objects.create(
                user=user,
                phone_number=mobile_number,
                otp_code=otp,
                otp_type='login_register',
                expires_at=timezone.now() + timedelta(minutes=10)
            )
        
        # Send OTP via SMS
        # TODO: Integrate actual SMS service (Twilio, AWS SNS, etc.)
        # For now, just log it for development
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"OTP for {mobile_number}: {otp}")
        
        return Response({
            "message": f"OTP sent successfully to {mobile_number}",
            "debug_otp": otp if settings.DEBUG else None  # Only in debug mode
        })


class VerifyOTPView(generics.GenericAPIView):
    """Verify OTP and login/register user"""
    permission_classes = [AllowAny]
    # throttle_classes = [MobileVerificationRateThrottle]  # Disabled for development

    def post(self, request, *args, **kwargs):
        mobile_number = request.data.get('mobile_number')
        otp = request.data.get('otp')
        
        if not mobile_number or not otp:
            return Response({
                "error": "Mobile number and OTP are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user by mobile number
        try:
            user = User.objects.get(mobile=mobile_number)  # Changed from mobile_number to mobile
        except User.DoesNotExist:
            return Response({
                "error": "Invalid mobile number"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        try:
            # Find the most recent OTP for this user
            otp_obj = OTPVerification.objects.filter(
                user=user,
                otp_code=otp,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not otp_obj:
                return Response({
                    "error": "Invalid OTP"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if expired
            if otp_obj.is_expired():
                return Response({
                    "error": "OTP has expired"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as verified
            from django.utils import timezone
            otp_obj.is_verified = True
            otp_obj.verified_at = timezone.now()
            otp_obj.save()
            
        except Exception as e:
            return Response({
                "error": f"OTP verification failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Activate user if inactive
        if not user.is_active:
            user.is_active = True
            user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_serializer.data
        })
