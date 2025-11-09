from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    ChangePasswordView,
    UpdateLanguageView,
)
from .translation_views import (
    LanguageListView,
    SetLanguageView,
    TranslationsView,
)
from .verification_views import (
    EmailVerificationView,
    MobileVerificationView,
    TwoFactorAuthenticationView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('update-language/', UpdateLanguageView.as_view(), name='update-language'),
    
    # Verification Endpoints
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('verify-mobile/', MobileVerificationView.as_view(), name='verify-mobile'),
    path('2fa/', TwoFactorAuthenticationView.as_view(), name='two-factor-auth'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Translation API
    path('languages/', LanguageListView.as_view(), name='languages'),
    path('set-language/', SetLanguageView.as_view(), name='set-language'),
    path('translations/', TranslationsView.as_view(), name='translations'),
]
