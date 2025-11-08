"""
CivicAI Grid - Smart Multilingual Voice Assistant
Advanced voice-based complaint processing system for SmartGrid Civic Connect Portal
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class CivicAIVoiceAssistant:
    """
    Multilingual Voice Assistant for processing citizen complaints through audio calls.
    
    Capabilities:
    - Real-time speech understanding in Gujarati, Hindi, Marathi, Punjabi, English
    - Automatic language detection
    - Complaint classification by department
    - Natural voice-based interaction
    - Fallback model support for reliability
    """
    
    SUPPORTED_LANGUAGES = {
        'gu': 'Gujarati',
        'hi': 'Hindi',
        'mr': 'Marathi',
        'pa': 'Punjabi',
        'en': 'English'
    }
    
    DEPARTMENTS = {
        'water': 'Water Supply',
        'road': 'Road Maintenance',
        'fire': 'Fire Department',
        'safety': 'Public Safety',
        'electricity': 'Electricity',
        'sanitation': 'Sanitation',
        'health': 'Health Services',
        'other': 'General Services'
    }
    
    GREETINGS = {
        'gu': 'નમસ્તે! હું તમારી મદદ કરવા આવ્યો છું.',
        'hi': 'नमस्ते! मैं आपकी मदद के लिए यहां हूं।',
        'mr': 'नमस्कार! मी तुमची मदत करण्यासाठी येथे आहे.',
        'pa': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡੀ ਮਦਦ ਲਈ ਇੱਥੇ ਹਾਂ।',
        'en': 'Hello! I am here to help you with your complaint.'
    }
    
    def __init__(self):
        """Initialize CivicAI Voice Assistant"""
        self.primary_api_key = getattr(settings, 'GOOGLE_AI_API_KEY', None)
        self.backup_endpoint = getattr(settings, 'CIVICAI_BACKUP_ENDPOINT', None)
        self.session_logs = []
        
    def detect_language(self, text: str) -> str:
        """
        Detect language from transcribed text
        
        Args:
            text: Transcribed text from audio
            
        Returns:
            Language code (gu, hi, mr, pa, en)
        """
        try:
            # Simple language detection based on script
            # In production, use Google Translate API or langdetect library
            
            # Gujarati: ગુજરાતી script
            if any('\u0A80' <= char <= '\u0AFF' for char in text):
                return 'gu'
            
            # Devanagari (Hindi/Marathi): देवनागरी
            if any('\u0900' <= char <= '\u097F' for char in text):
                # Distinguish between Hindi and Marathi
                marathi_markers = ['आहे', 'आहेत', 'होते', 'होती']
                if any(marker in text for marker in marathi_markers):
                    return 'mr'
                return 'hi'
            
            # Gurmukhi (Punjabi): ਗੁਰਮੁਖੀ
            if any('\u0A00' <= char <= '\u0A7F' for char in text):
                return 'pa'
            
            # Default to English
            return 'en'
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return 'en'
    
    def classify_department(self, text: str, language: str) -> Tuple[str, float]:
        """
        Classify complaint to appropriate department using AI
        
        Args:
            text: Complaint text
            language: Detected language code
            
        Returns:
            Tuple of (department_tag, confidence_score)
        """
        try:
            # Keywords for department classification
            department_keywords = {
                'water': ['water', 'પાણી', 'पानी', 'पाणी', 'ਪਾਣੀ', 'tap', 'supply', 'leak'],
                'road': ['road', 'રસ્તો', 'सड़क', 'रस्ता', 'ਸੜਕ', 'pothole', 'damage', 'repair'],
                'fire': ['fire', 'આગ', 'आग', 'ਅੱਗ', 'emergency', 'smoke'],
                'safety': ['light', 'લાઈટ', 'लाइट', 'ਲਾਈਟ', 'dark', 'safety', 'street'],
                'electricity': ['electricity', 'વીજળી', 'बिजली', 'वीज', 'ਬਿਜਲੀ', 'power', 'cut'],
                'sanitation': ['garbage', 'કચરો', 'कचरा', 'कचरा', 'ਕੂੜਾ', 'dirty', 'clean'],
            }
            
            text_lower = text.lower()
            scores = {}
            
            for dept, keywords in department_keywords.items():
                score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
                if score > 0:
                    scores[dept] = score
            
            if scores:
                best_dept = max(scores, key=scores.get)
                confidence = min(scores[best_dept] / 5.0, 1.0)  # Normalize to 0-1
                return best_dept, confidence
            
            return 'other', 0.5
            
        except Exception as e:
            logger.error(f"Department classification failed: {str(e)}")
            return 'other', 0.3
    
    def generate_summary(self, text: str, language: str) -> str:
        """
        Generate English summary of complaint for database storage
        
        Args:
            text: Original complaint text
            language: Language code
            
        Returns:
            English summary
        """
        try:
            if language == 'en':
                return text.strip()
            
            # Use Google AI for translation and summarization
            if self.primary_api_key:
                return self._translate_with_ai(text, language)
            
            # Fallback: Return original text with language tag
            return f"[{self.SUPPORTED_LANGUAGES.get(language, 'Unknown')}] {text}"
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return f"Complaint in {self.SUPPORTED_LANGUAGES.get(language, 'Unknown')}"
    
    def _translate_with_ai(self, text: str, source_lang: str) -> str:
        """Use Google AI to translate and summarize"""
        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.primary_api_key}"
            
            prompt = f"""Translate the following {self.SUPPORTED_LANGUAGES.get(source_lang)} complaint to English and provide a brief summary (1-2 sentences):

Complaint: {text}

Provide only the English summary, no explanations."""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 100
                }
            }
            
            response = requests.post(api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    summary = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    return summary
            
            return text
            
        except Exception as e:
            logger.error(f"AI translation failed: {str(e)}")
            return text
    
    def generate_response(self, complaint_text: str, language: str, department: str) -> str:
        """
        Generate appropriate voice response in user's language
        
        Args:
            complaint_text: User's complaint
            language: Detected language
            department: Classified department
            
        Returns:
            Response text in user's language
        """
        responses = {
            'gu': f'હું તમારી ફરિયાદ {self.DEPARTMENTS.get(department, "સંબંધિત વિભાગ")} માં મોકલી રહ્યો છું. આભાર તમારી જાણકારી માટે.',
            'hi': f'मैं आपकी शिकायत {self.DEPARTMENTS.get(department, "संबंधित विभाग")} को भेज रहा हूं। धन्यवाद!',
            'mr': f'मी तुमची तक्रार {self.DEPARTMENTS.get(department, "संबंधित विभाग")} कडे पाठवत आहे. धन्यवाद!',
            'pa': f'ਮੈਂ ਤੁਹਾਡੀ ਸ਼ਿਕਾਇਤ {self.DEPARTMENTS.get(department, "ਸਬੰਧਤ ਵਿਭਾਗ")} ਨੂੰ ਭੇਜ ਰਿਹਾ ਹਾਂ। ਧੰਨਵਾਦ!',
            'en': f'I am forwarding your complaint to the {self.DEPARTMENTS.get(department, "relevant department")}. Thank you!'
        }
        
        return responses.get(language, responses['en'])
    
    def process_voice_complaint(self, audio_url: str = None, transcribed_text: str = None, 
                               caller_id: str = None) -> Dict:
        """
        Main function to process voice-based complaint
        
        Args:
            audio_url: URL to audio file (if available)
            transcribed_text: Already transcribed text (if available)
            caller_id: Caller identification
            
        Returns:
            Complete response dictionary with all processed information
        """
        try:
            # If no transcribed text, we'd use speech-to-text here
            # For now, assuming text is provided
            if not transcribed_text:
                return {
                    'success': False,
                    'error': 'No transcribed text provided'
                }
            
            # 1. Detect language
            language = self.detect_language(transcribed_text)
            
            # 2. Classify department
            department, confidence = self.classify_department(transcribed_text, language)
            
            # 3. Generate English summary
            summary = self.generate_summary(transcribed_text, language)
            
            # 4. Generate response in user's language
            reply = self.generate_response(transcribed_text, language, department)
            
            # 5. Log the interaction
            log_entry = {
                'caller_id': caller_id,
                'audio_input_url': audio_url,
                'transcribed_text': transcribed_text,
                'language': language,
                'language_name': self.SUPPORTED_LANGUAGES.get(language, 'Unknown'),
                'department': department,
                'department_name': self.DEPARTMENTS.get(department, 'Unknown'),
                'timestamp': datetime.now().isoformat(),
                'confidence_score': confidence
            }
            self.session_logs.append(log_entry)
            
            # 6. Prepare response
            response = {
                'success': True,
                'summary_text': summary,
                'original_language': language,
                'original_language_name': self.SUPPORTED_LANGUAGES.get(language, 'Unknown'),
                'reply_text': reply,
                'department_tag': department,
                'department_name': self.DEPARTMENTS.get(department, 'Unknown'),
                'confidence_score': confidence,
                'greeting': self.GREETINGS.get(language, self.GREETINGS['en']),
                'log_entry': log_entry
            }
            
            logger.info(f"Voice complaint processed: {department} ({language})")
            return response
            
        except Exception as e:
            logger.error(f"Voice complaint processing failed: {str(e)}")
            
            # Try backup model
            if self.backup_endpoint:
                try:
                    return self._process_with_backup({
                        'transcribed_text': transcribed_text,
                        'caller_id': caller_id,
                        'audio_url': audio_url
                    })
                except Exception as backup_error:
                    logger.error(f"Backup model also failed: {str(backup_error)}")
            
            return {
                'success': False,
                'error': str(e),
                'fallback_message': 'We are experiencing technical difficulties. Please try again later.'
            }
    
    def _process_with_backup(self, request_data: Dict) -> Dict:
        """
        Process complaint using backup CivicAI model
        
        Args:
            request_data: Original request data
            
        Returns:
            Processed response from backup model
        """
        logger.info("Routing to backup CivicAI model...")
        
        try:
            response = requests.post(
                self.backup_endpoint,
                json=request_data,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            
            raise Exception(f"Backup model returned status {response.status_code}")
            
        except Exception as e:
            logger.error(f"Backup processing failed: {str(e)}")
            raise
    
    def get_session_logs(self) -> List[Dict]:
        """Get all logged interactions from current session"""
        return self.session_logs
    
    def clear_session_logs(self):
        """Clear session logs"""
        self.session_logs = []


# Global instance
civic_ai = CivicAIVoiceAssistant()
