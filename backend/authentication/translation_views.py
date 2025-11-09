"""
Translation API for SmartGriev
Provides endpoints for language switching and translation management
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import get_language, activate, gettext as _
from django.conf import settings

class LanguageListView(APIView):
    """Get list of supported languages"""
    permission_classes = []
    
    def get(self, request):
        languages = [
            {
                'code': code,
                'name': name,
                'native_name': name.split('(')[1].rstrip(')') if '(' in name else name
            }
            for code, name in settings.LANGUAGES
        ]
        return Response({
            'languages': languages,
            'current': get_language()
        })

class SetLanguageView(APIView):
    """Set user's preferred language"""
    permission_classes = []
    
    def post(self, request):
        language_code = request.data.get('language')
        
        if not language_code:
            return Response(
                {'error': 'Language code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate language code
        valid_languages = [lang[0] for lang in settings.LANGUAGES]
        if language_code not in valid_languages:
            return Response(
                {'error': f'Language {language_code} is not supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Activate language
        activate(language_code)
        request.session['django_language'] = language_code
        
        # Update user preference if authenticated
        if request.user.is_authenticated:
            request.user.language_preference = language_code
            request.user.save(update_fields=['language_preference'])
        
        return Response({
            'message': _('Language changed successfully'),
            'language': language_code
        })

class TranslationsView(APIView):
    """Get translations for common UI strings"""
    permission_classes = []
    
    def get(self, request):
        language = request.query_params.get('lang', get_language())
        activate(language)
        
        # Common translations
        translations = {
            # Navigation
            'home': _('Home'),
            'complaints': _('Complaints'),
            'submit_complaint': _('Submit Complaint'),
            'my_complaints': _('My Complaints'),
            'track': _('Track'),
            'login': _('Login'),
            'logout': _('Logout'),
            'register': _('Register'),
            'profile': _('Profile'),
            
            # Complaint Form
            'title': _('Title'),
            'description': _('Description'),
            'category': _('Category'),
            'department': _('Department'),
            'location': _('Location'),
            'upload_photo': _('Upload Photo'),
            'submit': _('Submit'),
            'cancel': _('Cancel'),
            
            # Status
            'pending': _('Pending'),
            'in_progress': _('In Progress'),
            'resolved': _('Resolved'),
            'rejected': _('Rejected'),
            
            # Departments
            'water_supply': _('Water Supply'),
            'electricity': _('Electricity'),
            'roads': _('Roads'),
            'sanitation': _('Sanitation'),
            'street_lights': _('Street Lights'),
            'drainage': _('Drainage'),
            'parks': _('Parks'),
            'traffic': _('Traffic'),
            'pollution': _('Pollution'),
            'other': _('Other'),
            
            # Messages
            'complaint_submitted': _('Complaint submitted successfully'),
            'complaint_updated': _('Complaint updated successfully'),
            'error_occurred': _('An error occurred. Please try again.'),
            'required_field': _('This field is required'),
            'invalid_input': _('Invalid input'),
            
            # Chatbot
            'ask_question': _('Ask a question'),
            'type_message': _('Type your message...'),
            'send': _('Send'),
            'chatbot_title': _('AI Assistant'),
            
            # Accessibility
            'high_contrast': _('High Contrast'),
            'text_size': _('Text Size'),
            'screen_reader': _('Screen Reader Mode'),
            'accessibility': _('Accessibility'),
        }
        
        return Response({
            'language': language,
            'translations': translations
        })
