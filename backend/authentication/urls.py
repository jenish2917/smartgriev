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

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('update-language/', UpdateLanguageView.as_view(), name='update-language'),
    
    # Translation API
    path('languages/', LanguageListView.as_view(), name='languages'),
    path('set-language/', SetLanguageView.as_view(), name='set-language'),
    path('translations/', TranslationsView.as_view(), name='translations'),
]
