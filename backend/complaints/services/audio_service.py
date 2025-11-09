"""
Audio Transcription Service for SmartGriev
Handles speech-to-text conversion for voice complaints in 12 Indian languages
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


class AudioTranscriptionService:
    """
    Audio transcription service using Google Gemini for speech-to-text
    Supports 12 Indian languages
    """
    
    # Supported audio formats
    SUPPORTED_AUDIO_FORMATS = {
        '.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.opus', '.webm'
    }
    
    # Maximum audio file size (in MB)
    MAX_AUDIO_SIZE_MB = 25
    
    # Maximum audio duration (in seconds)
    MAX_AUDIO_DURATION = 600  # 10 minutes
    
    # Supported languages (12 Indian languages)
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
        'ur': 'Urdu',
        'as': 'Assamese',
        'or': 'Odia'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Audio Transcription Service
        
        Args:
            api_key: Google AI API key (defaults to environment variable or Django settings)
        """
        from django.conf import settings
        
        self.api_key = (
            api_key or 
            os.getenv('GOOGLE_AI_API_KEY') or 
            getattr(settings, 'GOOGLE_AI_API_KEY', None) or
            getattr(settings, 'GEMINI_API_KEY', None)
        )
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY not found in environment variables or Django settings")
        
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 1.5 Pro for audio transcription
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        logger.info("AudioTranscriptionService initialized with Gemini 1.5 Pro")
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to the audio file
            language: Language code (auto-detected if not provided)
            context: Optional context about the complaint
            
        Returns:
            Transcription results with text, language, confidence
        """
        try:
            # Validate audio file
            validation = self._validate_audio(audio_path)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # Upload audio file
            logger.info(f"Uploading audio file: {audio_path}")
            audio_file = genai.upload_file(audio_path)
            
            # Wait for processing
            import time
            while audio_file.state.name == "PROCESSING":
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)
            
            if audio_file.state.name == "FAILED":
                return {
                    'success': False,
                    'error': 'Audio file processing failed'
                }
            
            # Create transcription prompt
            prompt = self._create_transcription_prompt(language, context)
            
            # Generate transcription
            response = self.model.generate_content([audio_file, prompt])
            
            # Parse response
            result = self._parse_transcription_response(response.text)
            
            # Clean up uploaded file
            genai.delete_file(audio_file.name)
            
            return {
                'success': True,
                'text': result.get('text', ''),
                'language': result.get('language', 'unknown'),
                'language_name': self.SUPPORTED_LANGUAGES.get(
                    result.get('language', 'en'),
                    'Unknown'
                ),
                'confidence': result.get('confidence', 0.0),
                'issue_summary': result.get('issue_summary', ''),
                'detected_emotion': result.get('detected_emotion', 'neutral'),
                'urgency_level': result.get('urgency_level', 'medium'),
                'metadata': validation['metadata']
            }
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            return {
                'success': False,
                'error': f'Audio transcription failed: {str(e)}'
            }
    
    def analyze_voice_complaint(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive voice complaint analysis
        Includes transcription + sentiment + complaint classification
        
        Args:
            audio_path: Path to the audio file
            language: Language code (auto-detected if not provided)
            
        Returns:
            Complete analysis with transcription, sentiment, classification
        """
        try:
            # Validate audio file
            validation = self._validate_audio(audio_path)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # Upload audio file
            logger.info(f"Analyzing voice complaint: {audio_path}")
            audio_file = genai.upload_file(audio_path)
            
            # Wait for processing
            import time
            while audio_file.state.name == "PROCESSING":
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)
            
            if audio_file.state.name == "FAILED":
                return {
                    'success': False,
                    'error': 'Audio file processing failed'
                }
            
            # Create comprehensive analysis prompt
            prompt = self._create_analysis_prompt(language)
            
            # Generate analysis
            response = self.model.generate_content([audio_file, prompt])
            
            # Parse response
            result = self._parse_analysis_response(response.text)
            
            # Clean up uploaded file
            genai.delete_file(audio_file.name)
            
            return {
                'success': True,
                'transcription': result.get('transcription', ''),
                'language': result.get('language', 'unknown'),
                'language_name': self.SUPPORTED_LANGUAGES.get(
                    result.get('language', 'en'),
                    'Unknown'
                ),
                'issue_type': result.get('issue_type', 'Unknown'),
                'description': result.get('description', ''),
                'sentiment': result.get('sentiment', 'neutral'),
                'emotion': result.get('emotion', 'neutral'),
                'urgency': result.get('urgency', 'medium'),
                'suggested_department': result.get('suggested_department', 'Other'),
                'location_mentioned': result.get('location_mentioned', ''),
                'key_points': result.get('key_points', []),
                'confidence': result.get('confidence', 0.0),
                'metadata': validation['metadata']
            }
            
        except Exception as e:
            logger.error(f"Voice complaint analysis failed: {str(e)}")
            return {
                'success': False,
                'error': f'Voice complaint analysis failed: {str(e)}'
            }
    
    def _validate_audio(self, audio_path: str) -> Dict[str, Any]:
        """Validate audio file format and size"""
        try:
            if not os.path.exists(audio_path):
                return {'valid': False, 'error': 'Audio file not found'}
            
            # Check file extension
            file_ext = Path(audio_path).suffix.lower()
            if file_ext not in self.SUPPORTED_AUDIO_FORMATS:
                return {
                    'valid': False,
                    'error': f'Unsupported audio format: {file_ext}'
                }
            
            # Check file size
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            if file_size_mb > self.MAX_AUDIO_SIZE_MB:
                return {
                    'valid': False,
                    'error': f'Audio file too large: {file_size_mb:.2f}MB (max: {self.MAX_AUDIO_SIZE_MB}MB)'
                }
            
            metadata = {
                'format': file_ext,
                'file_size_mb': file_size_mb,
                'mime_type': mimetypes.guess_type(audio_path)[0]
            }
            
            return {
                'valid': True,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Audio validation failed: {str(e)}'
            }
    
    def _create_transcription_prompt(
        self,
        language: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """Create prompt for audio transcription"""
        base_prompt = """Transcribe this audio recording accurately. The audio contains a civic complaint in one of these Indian languages:
English, Hindi (हिंदी), Bengali (বাংলা), Telugu (తెలుగు), Marathi (मराठी), Tamil (தமிழ்), Gujarati (ગુજરાતી), Kannada (ಕನ್ನಡ), Malayalam (മലയാളം), Punjabi (ਪੰਜਾਬੀ), Urdu (اردو), Assamese (অসমীয়া), Odia (ଓଡ଼ିଆ)

Provide the output in JSON format:
{
    "text": "Complete transcription in the original language",
    "language": "language code (e.g., 'hi', 'en', 'ta')",
    "confidence": 0.95,
    "issue_summary": "Brief summary of the complaint in English",
    "detected_emotion": "neutral | concerned | frustrated | angry | calm",
    "urgency_level": "low | medium | high | critical"
}

IMPORTANT:
- Transcribe exactly what is said, preserving the original language
- Use proper script for the language (Devanagari for Hindi, Tamil script for Tamil, etc.)
- Identify speaker emotion from tone and speech patterns
- Assess urgency based on keywords and tone
"""
        
        if language:
            lang_name = self.SUPPORTED_LANGUAGES.get(language, language)
            base_prompt += f"\n\nExpected language: {lang_name}"
        
        if context:
            base_prompt += f"\n\nAdditional context: {context}"
        
        return base_prompt
    
    def _create_analysis_prompt(self, language: Optional[str] = None) -> str:
        """Create prompt for comprehensive voice complaint analysis"""
        base_prompt = """Analyze this audio recording of a civic complaint in India. Provide a comprehensive analysis in JSON format:

{
    "transcription": "Complete transcription in the original language",
    "language": "language code",
    "issue_type": "Brief name of the issue (e.g., 'Water Shortage', 'Road Pothole')",
    "description": "Detailed description of the complaint in English",
    "sentiment": "positive | neutral | negative | very_negative",
    "emotion": "neutral | concerned | frustrated | angry | upset | calm",
    "urgency": "low | medium | high | critical",
    "suggested_department": "Water Supply | Electricity | Roads | Sanitation | Streetlights | Waste Management | Parks & Gardens | Building Permits | Fire Safety | Other",
    "location_mentioned": "Any location details mentioned in audio (street, area, landmark)",
    "key_points": ["point1", "point2", "..."],
    "confidence": 0.95
}

DEPARTMENTS:
- Water Supply: Water shortage, leakage, quality issues
- Electricity: Power cuts, faulty meters, line issues
- Roads: Potholes, damaged roads, construction delays
- Sanitation: Garbage collection, cleanliness, drainage
- Streetlights: Non-functional lights, damaged poles
- Waste Management: Waste disposal, recycling issues
- Parks & Gardens: Maintenance, cleanliness issues
- Building Permits: Construction violations, illegal buildings
- Fire Safety: Fire hazards, safety concerns
- Other: Miscellaneous civic issues

IMPORTANT:
- Transcribe in the original language
- Translate and summarize the complaint in English
- Detect emotion from speech patterns, tone, and word choice
- Classify urgency based on severity keywords and emotional intensity
- Extract any location information mentioned
"""
        
        if language:
            lang_name = self.SUPPORTED_LANGUAGES.get(language, language)
            base_prompt += f"\n\nExpected language: {lang_name}"
        
        return base_prompt
    
    def _parse_transcription_response(self, response_text: str) -> Dict[str, Any]:
        """Parse transcription response into structured data"""
        try:
            import json
            import re
            
            # Find JSON block in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return result
            
            # Fallback: Return raw text
            return {
                'text': response_text,
                'language': 'unknown',
                'confidence': 0.0,
                'issue_summary': '',
                'detected_emotion': 'neutral',
                'urgency_level': 'medium'
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse transcription response: {str(e)}")
            return {
                'text': response_text,
                'language': 'unknown',
                'confidence': 0.0,
                'issue_summary': '',
                'detected_emotion': 'neutral',
                'urgency_level': 'medium'
            }
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse comprehensive analysis response into structured data"""
        try:
            import json
            import re
            
            # Find JSON block in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return result
            
            # Fallback
            return {
                'transcription': response_text,
                'language': 'unknown',
                'issue_type': 'Unknown',
                'description': response_text,
                'sentiment': 'neutral',
                'emotion': 'neutral',
                'urgency': 'medium',
                'suggested_department': 'Other',
                'location_mentioned': '',
                'key_points': [],
                'confidence': 0.0
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse analysis response: {str(e)}")
            return {
                'transcription': response_text,
                'language': 'unknown',
                'issue_type': 'Unknown',
                'description': response_text,
                'sentiment': 'neutral',
                'emotion': 'neutral',
                'urgency': 'medium',
                'suggested_department': 'Other',
                'location_mentioned': '',
                'key_points': [],
                'confidence': 0.0
            }


# Global instance
_audio_service = None

def get_audio_service(api_key: Optional[str] = None) -> AudioTranscriptionService:
    """Get or create global AudioTranscriptionService instance"""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioTranscriptionService(api_key)
    return _audio_service
