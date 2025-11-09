"""
AI-powered Translation Service using Gemini
Generates translations for SmartGriev in 12 Indian languages
"""
import google.generativeai as genai
import os
import json
from django.conf import settings

class GeminiTranslationService:
    """Use Gemini AI to generate translations"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')  # Use stable API version
        else:
            self.model = None
    
    def translate_batch(self, texts, target_language):
        """
        Translate multiple texts to target language
        
        Args:
            texts: Dictionary of {key: english_text}
            target_language: Target language code (hi, bn, te, etc.)
        
        Returns:
            Dictionary of {key: translated_text}
        """
        if not self.model:
            return {key: text for key, text in texts.items()}
        
        language_names = {
            'hi': 'Hindi (हिन्दी)',
            'bn': 'Bengali (বাংলা)',
            'te': 'Telugu (తెలుగు)',
            'mr': 'Marathi (मराठी)',
            'ta': 'Tamil (தமிழ்)',
            'gu': 'Gujarati (ગુજરાતી)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)',
            'ur': 'Urdu (اردو)',
            'as': 'Assamese (অসমীয়া)',
            'or': 'Odia (ଓଡ଼ିଆ)',
        }
        
        language_name = language_names.get(target_language, target_language)
        
        prompt = f"""You are a professional translator for a government civic complaint system.
Translate the following English phrases to {language_name}.

Requirements:
1. Use formal, respectful language appropriate for government communication
2. Keep technical terms clear and understandable
3. Maintain consistency in terminology
4. Return ONLY a valid JSON object with the same keys

Input JSON:
{json.dumps(texts, indent=2, ensure_ascii=False)}

Output JSON (translated to {language_name}):"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON from markdown code blocks if present
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            translations = json.loads(text)
            return translations
        except Exception as e:
            print(f"Translation error for {target_language}: {e}")
            return {key: text for key, text in texts.items()}
    
    def generate_all_translations(self):
        """Generate translations for all supported languages"""
        
        # Base English strings
        base_strings = {
            # Navigation
            'home': 'Home',
            'complaints': 'Complaints',
            'submit_complaint': 'Submit Complaint',
            'my_complaints': 'My Complaints',
            'track': 'Track',
            'login': 'Login',
            'logout': 'Logout',
            'register': 'Register',
            'profile': 'Profile',
            'dashboard': 'Dashboard',
            
            # Complaint Form
            'title': 'Title',
            'description': 'Description',
            'category': 'Category',
            'department': 'Department',
            'location': 'Location',
            'upload_photo': 'Upload Photo',
            'upload_video': 'Upload Video',
            'submit': 'Submit',
            'cancel': 'Cancel',
            'save': 'Save',
            'edit': 'Edit',
            'delete': 'Delete',
            
            # Status
            'pending': 'Pending',
            'in_progress': 'In Progress',
            'resolved': 'Resolved',
            'rejected': 'Rejected',
            'closed': 'Closed',
            'status': 'Status',
            
            # Departments
            'water_supply': 'Water Supply',
            'electricity': 'Electricity',
            'roads': 'Roads',
            'sanitation': 'Sanitation',
            'street_lights': 'Street Lights',
            'drainage': 'Drainage',
            'parks': 'Parks & Gardens',
            'traffic': 'Traffic',
            'pollution': 'Pollution',
            'health': 'Health',
            'education': 'Education',
            'other': 'Other',
            
            # Messages
            'complaint_submitted': 'Complaint submitted successfully',
            'complaint_updated': 'Complaint updated successfully',
            'complaint_deleted': 'Complaint deleted successfully',
            'error_occurred': 'An error occurred. Please try again.',
            'required_field': 'This field is required',
            'invalid_input': 'Invalid input',
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information',
            
            # Chatbot
            'ask_question': 'Ask a question',
            'type_message': 'Type your message...',
            'send': 'Send',
            'chatbot_title': 'AI Assistant',
            'chatbot_greeting': 'Hello! How can I help you today?',
            
            # User
            'name': 'Name',
            'email': 'Email',
            'phone': 'Phone Number',
            'address': 'Address',
            'password': 'Password',
            'confirm_password': 'Confirm Password',
            'old_password': 'Old Password',
            'new_password': 'New Password',
            
            # Actions
            'search': 'Search',
            'filter': 'Filter',
            'sort': 'Sort',
            'view': 'View',
            'download': 'Download',
            'print': 'Print',
            'share': 'Share',
            'refresh': 'Refresh',
            
            # Accessibility
            'high_contrast': 'High Contrast Mode',
            'text_size': 'Text Size',
            'screen_reader': 'Screen Reader Mode',
            'accessibility': 'Accessibility Options',
            'increase_text': 'Increase Text Size',
            'decrease_text': 'Decrease Text Size',
            
            # Time
            'today': 'Today',
            'yesterday': 'Yesterday',
            'this_week': 'This Week',
            'this_month': 'This Month',
            'date': 'Date',
            'time': 'Time',
            
            # Common
            'yes': 'Yes',
            'no': 'No',
            'ok': 'OK',
            'back': 'Back',
            'next': 'Next',
            'previous': 'Previous',
            'close': 'Close',
            'help': 'Help',
            'about': 'About',
            'contact': 'Contact Us',
            'loading': 'Loading...',
            'please_wait': 'Please wait...',
        }
        
        all_translations = {'en': base_strings}
        
        language_codes = ['hi', 'bn', 'te', 'mr', 'ta', 'gu', 'kn', 'ml', 'pa', 'ur', 'as', 'or']
        
        for lang_code in language_codes:
            print(f"Generating translations for {lang_code}...")
            translations = self.translate_batch(base_strings, lang_code)
            all_translations[lang_code] = translations
        
        return all_translations
