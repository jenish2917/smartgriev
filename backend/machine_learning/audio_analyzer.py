"""
Audio Analysis Module for SmartGriev Multimodal Complaint Analysis

This module handles audio transcription, language detection, emotion detection,
and urgency level assessment from audio files.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Try to import audio processing libraries
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available. Audio transcription will be limited.")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Try to import sentiment/emotion analysis
try:
    from transformers import pipeline as hf_pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class AudioAnalyzer:
    """
    Handles audio analysis including transcription, emotion detection, and urgency assessment.
    """
    
    # Emotion keywords for rule-based detection
    EMOTION_KEYWORDS = {
        'anger': ['angry', 'furious', 'outraged', 'mad', 'frustrated', 'annoyed'],
        'anxiety': ['worried', 'anxious', 'concerned', 'nervous', 'stressed'],
        'frustration': ['frustrated', 'annoying', 'irritating', 'fed up'],
        'urgency': ['urgent', 'emergency', 'immediately', 'asap', 'critical', 'dangerous']
    }
    
    # Urgency indicators
    URGENCY_HIGH_KEYWORDS = ['urgent', 'emergency', 'dangerous', 'critical', 'immediately', 'help']
    URGENCY_MEDIUM_KEYWORDS = ['soon', 'quickly', 'please fix', 'not working']
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize AudioAnalyzer with Whisper model.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self._whisper_model = None
        self._emotion_classifier = None
        self.fallback_mode = False
        
        logger.info(f"AudioAnalyzer initialized with model size: {model_size}")
    
    @property
    def whisper_model(self):
        """Lazy loading of Whisper model."""
        if self._whisper_model is None and WHISPER_AVAILABLE and not self.fallback_mode:
            try:
                logger.info(f"Loading Whisper model: {self.model_size}")
                self._whisper_model = whisper.load_model(self.model_size)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load Whisper model: {str(e)}. Using fallback mode.")
                self.fallback_mode = True
        return self._whisper_model
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio to text with language detection.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dict with transcription, language, and confidence
        """
        try:
            if not os.path.exists(audio_path):
                return {
                    'success': False,
                    'error': 'Audio file not found'
                }
            
            if self.whisper_model is not None:
                # Use Whisper for transcription
                result = self.whisper_model.transcribe(audio_path)
                
                return {
                    'success': True,
                    'text': result['text'].strip(),
                    'language': result.get('language', 'unknown'),
                    'segments': result.get('segments', []),
                    'method': 'whisper'
                }
            else:
                # Fallback: return placeholder
                return {
                    'success': True,
                    'text': '[Audio transcription temporarily unavailable]',
                    'language': 'unknown',
                    'method': 'fallback'
                }
                
        except Exception as e:
            logger.error(f"Audio transcription error: {str(e)}")
            return {
                'success': False,
                'error': f'Transcription failed: {str(e)}'
            }
    
    def detect_emotion(self, text: str) -> Dict[str, Any]:
        """
        Detect emotion from transcribed text using keyword matching and ML.
        
        Args:
            text: Transcribed text
            
        Returns:
            Dict with detected emotion and confidence
        """
        try:
            text_lower = text.lower()
            
            # Rule-based emotion detection using keywords
            emotion_scores = {}
            
            for emotion, keywords in self.EMOTION_KEYWORDS.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    emotion_scores[emotion] = score
            
            # Determine primary emotion
            if emotion_scores:
                primary_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = min(0.9, emotion_scores[primary_emotion] / 5.0)
            else:
                primary_emotion = 'neutral'
                confidence = 0.5
            
            # Try ML-based emotion detection if available
            if TRANSFORMERS_AVAILABLE and self._emotion_classifier is None:
                try:
                    self._emotion_classifier = hf_pipeline(
                        "text-classification",
                        model="j-hartmann/emotion-english-distilroberta-base",
                        top_k=None
                    )
                except:
                    pass
            
            ml_emotions = []
            if self._emotion_classifier is not None:
                try:
                    ml_result = self._emotion_classifier(text[:512])  # Limit text length
                    ml_emotions = ml_result[0] if ml_result else []
                except:
                    pass
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'all_emotions': emotion_scores,
                'ml_emotions': ml_emotions,
                'method': 'hybrid' if ml_emotions else 'rule-based'
            }
            
        except Exception as e:
            logger.error(f"Emotion detection error: {str(e)}")
            return {
                'primary_emotion': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def assess_urgency(self, text: str, emotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess urgency level based on text content and emotion.
        
        Args:
            text: Transcribed text
            emotion_data: Emotion detection results
            
        Returns:
            Dict with urgency level and reasoning
        """
        try:
            text_lower = text.lower()
            urgency_score = 0
            indicators = []
            
            # Check for high urgency keywords
            for keyword in self.URGENCY_HIGH_KEYWORDS:
                if keyword in text_lower:
                    urgency_score += 3
                    indicators.append(f"high_urgency_keyword: {keyword}")
            
            # Check for medium urgency keywords
            for keyword in self.URGENCY_MEDIUM_KEYWORDS:
                if keyword in text_lower:
                    urgency_score += 1
                    indicators.append(f"medium_urgency_keyword: {keyword}")
            
            # Consider emotion
            emotion = emotion_data.get('primary_emotion', 'neutral')
            if emotion in ['anger', 'anxiety']:
                urgency_score += 2
                indicators.append(f"high_emotion: {emotion}")
            elif emotion == 'frustration':
                urgency_score += 1
                indicators.append(f"moderate_emotion: {emotion}")
            
            # Determine urgency level
            if urgency_score >= 5:
                urgency_level = 'high'
            elif urgency_score >= 2:
                urgency_level = 'medium'
            else:
                urgency_level = 'low'
            
            return {
                'urgency_level': urgency_level,
                'urgency_score': urgency_score,
                'indicators': indicators,
                'confidence': min(0.95, urgency_score / 10.0 + 0.5)
            }
            
        except Exception as e:
            logger.error(f"Urgency assessment error: {str(e)}")
            return {
                'urgency_level': 'medium',
                'urgency_score': 0,
                'error': str(e)
            }
    
    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Comprehensive audio analysis including transcription, emotion, and urgency.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Complete audio analysis results
        """
        try:
            # Transcribe audio
            transcription = self.transcribe_audio(audio_path)
            
            if not transcription.get('success'):
                return {
                    'success': False,
                    'error': transcription.get('error', 'Transcription failed')
                }
            
            text = transcription.get('text', '')
            
            # Detect emotion
            emotion_data = self.detect_emotion(text)
            
            # Assess urgency
            urgency_data = self.assess_urgency(text, emotion_data)
            
            return {
                'success': True,
                'transcription': {
                    'text': text,
                    'language': transcription.get('language', 'unknown'),
                    'method': transcription.get('method', 'unknown')
                },
                'emotion': {
                    'primary_emotion': emotion_data.get('primary_emotion', 'unknown'),
                    'confidence': emotion_data.get('confidence', 0.0),
                    'all_emotions': emotion_data.get('all_emotions', {}),
                    'ml_emotions': emotion_data.get('ml_emotions', [])
                },
                'urgency': {
                    'level': urgency_data.get('urgency_level', 'medium'),
                    'score': urgency_data.get('urgency_score', 0),
                    'indicators': urgency_data.get('indicators', []),
                    'confidence': urgency_data.get('confidence', 0.5)
                }
            }
            
        except Exception as e:
            logger.error(f"Audio analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Audio analysis failed: {str(e)}'
            }


# Global instance
_audio_analyzer = None


def get_audio_analyzer(model_size: str = "base") -> AudioAnalyzer:
    """Get or create global audio analyzer instance."""
    global _audio_analyzer
    if _audio_analyzer is None:
        _audio_analyzer = AudioAnalyzer(model_size)
    return _audio_analyzer
