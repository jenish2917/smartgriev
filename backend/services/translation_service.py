"""
Translation Service for SmartGriev
Supports multiple translation providers with fallback mechanism
- Google Cloud Translation API (primary)
- Bhashini API (Government of India - for Indian languages)
- Google Translate (free tier fallback)
"""

import os
import logging
from typing import Dict, Optional, Tuple
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

# Language codes mapping (ISO 639-1)
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'or': 'Odia',
    'as': 'Assamese',
}

class TranslationService:
    """
    Main translation service with multi-provider support
    """
    
    def __init__(self):
        self.google_translate_available = False
        self.bhashini_available = False
        self.google_cloud_available = False
        
        # Initialize available services
        self._init_services()
        
    def _init_services(self):
        """Initialize translation service providers"""
        
        # Try Google Cloud Translation (best quality)
        try:
            from google.cloud import translate_v2 as translate
            credentials_path = os.getenv('GOOGLE_CLOUD_CREDENTIALS_PATH')
            if credentials_path and os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                self.google_cloud_client = translate.Client()
                self.google_cloud_available = True
                logger.info("Google Cloud Translation API initialized")
        except Exception as e:
            logger.warning(f"Google Cloud Translation not available: {e}")
        
        # Try Bhashini API (Government of India)
        try:
            bhashini_api_key = os.getenv('BHASHINI_API_KEY')
            bhashini_user_id = os.getenv('BHASHINI_USER_ID')
            if bhashini_api_key and bhashini_user_id:
                self.bhashini_api_key = bhashini_api_key
                self.bhashini_user_id = bhashini_user_id
                self.bhashini_available = True
                logger.info("Bhashini API initialized")
        except Exception as e:
            logger.warning(f"Bhashini API not available: {e}")
        
        # Google Translate (free tier fallback)
        try:
            from deep_translator import GoogleTranslator
            self.google_translator = GoogleTranslator
            self.google_translate_available = True
            logger.info("Google Translate (deep-translator) initialized as fallback")
        except Exception as e:
            logger.warning(f"Google Translate (deep-translator) not available: {e}")
    
    @lru_cache(maxsize=1000)
    def translate(
        self, 
        text: str, 
        target_language: str, 
        source_language: Optional[str] = None
    ) -> Tuple[str, bool]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'hi' for Hindi)
            source_language: Source language code (optional, will auto-detect)
        
        Returns:
            Tuple of (translated_text, success)
        """
        
        if not text or not text.strip():
            return text, False
        
        # If target is English and source is None or English, no translation needed
        if target_language == 'en' and (source_language is None or source_language == 'en'):
            return text, True
        
        # If source and target are the same, no translation needed
        if source_language == target_language:
            return text, True
        
        # Validate language codes
        if target_language not in SUPPORTED_LANGUAGES:
            logger.error(f"Unsupported target language: {target_language}")
            return text, False
        
        # Try translation providers in order of preference
        
        # 1. Try Google Cloud Translation (best quality)
        if self.google_cloud_available:
            try:
                result = self._translate_google_cloud(text, target_language, source_language)
                if result:
                    logger.info(f"Translated using Google Cloud: {source_language or 'auto'} -> {target_language}")
                    return result, True
            except Exception as e:
                logger.error(f"Google Cloud translation failed: {e}")
        
        # 2. Try Bhashini API (Government of India, good for Indian languages)
        if self.bhashini_available and self._is_indian_language_pair(source_language, target_language):
            try:
                result = self._translate_bhashini(text, target_language, source_language)
                if result:
                    logger.info(f"Translated using Bhashini: {source_language or 'auto'} -> {target_language}")
                    return result, True
            except Exception as e:
                logger.error(f"Bhashini translation failed: {e}")
        
        # 3. Fallback to Google Translate (free tier)
        if self.google_translate_available:
            try:
                result = self._translate_google_free(text, target_language, source_language)
                if result:
                    logger.info(f"Translated using Google Translate (free): {source_language or 'auto'} -> {target_language}")
                    return result, True
            except Exception as e:
                logger.error(f"Google Translate (free) failed: {e}")
        
        # All providers failed
        logger.error(f"All translation providers failed for {source_language or 'auto'} -> {target_language}")
        return text, False
    
    def _translate_google_cloud(
        self, 
        text: str, 
        target_language: str, 
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """Translate using Google Cloud Translation API"""
        try:
            result = self.google_cloud_client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            return result['translatedText']
        except Exception as e:
            logger.error(f"Google Cloud translation error: {e}")
            return None
    
    def _translate_bhashini(
        self, 
        text: str, 
        target_language: str, 
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """Translate using Bhashini API (Government of India)"""
        try:
            import requests
            
            # Bhashini API endpoint
            url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
            
            # Prepare request
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language or "en",
                                "targetLanguage": target_language
                            }
                        }
                    }
                ],
                "pipelineRequestConfig": {
                    "pipelineId": "64392f96daac500b55c543cd"
                }
            }
            
            headers = {
                "userID": self.bhashini_user_id,
                "ulcaApiKey": self.bhashini_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Extract translation from response
                # Note: Actual response structure may vary
                return data.get('pipelineResponse', [{}])[0].get('output', [{}])[0].get('target', text)
            else:
                logger.error(f"Bhashini API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Bhashini translation error: {e}")
            return None
    
    def _translate_google_free(
        self, 
        text: str, 
        target_language: str, 
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """Translate using deep-translator (Google Translate free tier)"""
        try:
            translator = self.google_translator(
                source=source_language or 'auto',
                target=target_language
            )
            result = translator.translate(text)
            return result
        except Exception as e:
            logger.error(f"Google Translate error: {e}")
            return None
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of input text
        
        Args:
            text: Text to analyze
        
        Returns:
            Language code (e.g., 'hi', 'en') or None
        """
        
        if not text or not text.strip():
            return None
        
        # Try Google Cloud (most accurate)
        if self.google_cloud_available:
            try:
                result = self.google_cloud_client.detect_language(text)
                if result and 'language' in result:
                    detected = result['language']
                    logger.info(f"Language detected (Google Cloud): {detected}")
                    return detected
            except Exception as e:
                logger.error(f"Google Cloud language detection failed: {e}")
        
        # Fallback to deep-translator language detection
        if self.google_translate_available:
            try:
                from deep_translator import single_detection
                result = single_detection(text, api_key=None)
                if result:
                    logger.info(f"Language detected (deep-translator): {result}")
                    return result
            except Exception as e:
                logger.error(f"deep-translator language detection failed: {e}")
        
        logger.warning("Language detection failed, defaulting to English")
        return 'en'
    
    def _is_indian_language_pair(
        self, 
        source_language: Optional[str], 
        target_language: str
    ) -> bool:
        """Check if both languages are Indian languages (better served by Bhashini)"""
        indian_languages = {'hi', 'bn', 'te', 'mr', 'ta', 'gu', 'kn', 'ml', 'pa', 'or', 'as'}
        
        if not source_language:
            return target_language in indian_languages
        
        return (source_language in indian_languages or target_language in indian_languages)
    
    def translate_batch(
        self, 
        texts: list, 
        target_language: str, 
        source_language: Optional[str] = None
    ) -> list:
        """
        Translate multiple texts at once
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code (optional)
        
        Returns:
            List of translated texts
        """
        results = []
        for text in texts:
            translated, success = self.translate(text, target_language, source_language)
            results.append(translated)
        return results
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names"""
        return SUPPORTED_LANGUAGES.copy()


# Singleton instance
_translation_service = None

def get_translation_service() -> TranslationService:
    """Get or create translation service singleton"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service


# Convenience functions
def translate_text(
    text: str, 
    target_language: str, 
    source_language: Optional[str] = None
) -> Tuple[str, bool]:
    """Translate text to target language"""
    service = get_translation_service()
    return service.translate(text, target_language, source_language)


def detect_language(text: str) -> Optional[str]:
    """Detect language of text"""
    service = get_translation_service()
    return service.detect_language(text)
