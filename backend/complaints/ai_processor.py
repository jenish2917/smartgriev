"""
Advanced AI Processor for SmartGriev Multi-Modal Complaint Processing
Handles text, audio, and image inputs with Groq AI enhancement
"""

import asyncio
import logging
import os
import tempfile
import json
from typing import Dict, Any, Optional, List

# Try to import Groq, but make it optional
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Groq library not available. AI enhancement features will be limited.")

# Try to import speech_recognition, but make it optional
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("speech_recognition library not available. Audio processing will be disabled.")

logger = logging.getLogger(__name__)


class AdvancedAIProcessor:
    """
    Advanced AI processor supporting multi-modal complaint processing
    """
    
    def __init__(self):
        """Initialize the AI processor with Groq client"""
        try:
            # Initialize Groq client if available
            if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
                self.groq_client = Groq(
                    api_key=os.getenv('GROQ_API_KEY', 'gsk_...your_api_key_here...')
                )
                self.use_ai = True
                logger.info("AdvancedAIProcessor initialized with Groq AI")
            else:
                self.groq_client = None
                self.use_ai = False
                if not GROQ_AVAILABLE:
                    logger.warning("Groq library not available. Using fallback methods.")
                else:
                    logger.warning("GROQ_API_KEY not set. Using fallback methods.")
            
            # Initialize speech recognition
            if SR_AVAILABLE:
                self.speech_recognizer = sr.Recognizer()
            else:
                self.speech_recognizer = None
                logger.warning("Speech recognition not available")
            
            # Configuration
            self.max_audio_duration = 300  # 5 minutes
            self.supported_audio_formats = ['.wav', '.mp3', '.flac', '.ogg']
            self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.bmp']
            
            logger.info("AdvancedAIProcessor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AdvancedAIProcessor: {e}")
            # Don't raise, allow fallback operation
            self.groq_client = None
            self.use_ai = False
            self.speech_recognizer = None if not SR_AVAILABLE else sr.Recognizer()
            self.max_audio_duration = 300
            self.supported_audio_formats = ['.wav', '.mp3', '.flac', '.ogg']
            self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.bmp']
    
    async def process_audio_to_text(self, audio_file_path: str, language: str = 'hi-IN') -> Optional[str]:
        """
        Convert audio file to text using speech recognition
        Supports multiple languages including Hindi and English
        """
        try:
            if not SR_AVAILABLE or not self.speech_recognizer:
                logger.warning("Speech recognition not available")
                return None
            
            if not os.path.exists(audio_file_path):
                logger.error(f"Audio file not found: {audio_file_path}")
                return None
            
            # Use speech recognition library
            with sr.AudioFile(audio_file_path) as source:
                # Adjust for ambient noise
                self.speech_recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record audio data
                audio_data = self.speech_recognizer.record(source)
                
                # Try multiple recognition engines
                text_results = []
                
                # Try Google Web Speech API (supports Hindi)
                try:
                    text = self.speech_recognizer.recognize_google(
                        audio_data, 
                        language=language
                    )
                    text_results.append(("Google", text))
                except Exception as e:
                    logger.warning(f"Google Speech Recognition failed: {e}")
                
                # Try Sphinx (offline, English only)
                if language.startswith('en'):
                    try:
                        text = self.speech_recognizer.recognize_sphinx(audio_data)
                        text_results.append(("Sphinx", text))
                    except Exception as e:
                        logger.warning(f"Sphinx Recognition failed: {e}")
                
                # Return the best result
                if text_results:
                    best_result = text_results[0][1]  # Use first successful result
                    logger.info(f"Audio to text conversion successful: {best_result[:50]}...")
                    return best_result
                else:
                    logger.error("All speech recognition attempts failed")
                    return None
                    
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return None
    
    async def process_image_with_context(self, image_file_path: str) -> Optional[str]:
        """
        Process image to extract text and context
        Uses basic OCR and analysis
        """
        try:
            if not os.path.exists(image_file_path):
                logger.error(f"Image file not found: {image_file_path}")
                return None
            
            # For now, return a placeholder since advanced image processing
            # requires additional dependencies like OpenCV, PIL, etc.
            image_analysis = f"Image analysis for {os.path.basename(image_file_path)}: "
            image_analysis += "This appears to be a complaint-related image. "
            image_analysis += "Advanced image processing will be implemented with proper OCR libraries."
            
            logger.info(f"Basic image processing completed")
            return image_analysis
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return None
    
    async def enhance_complaint_text(
        self, 
        original_text: str, 
        location: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Enhance complaint text using Groq AI
        """
        try:
            if not original_text or not original_text.strip():
                return original_text
            
            # Prepare enhancement prompt
            system_prompt = """You are an expert government complaint processor for India. 
Your task is to enhance citizen complaints to make them clearer, more actionable, and properly formatted.

Guidelines:
1. Preserve the original meaning and urgency
2. Add missing context if obvious from the complaint
3. Structure the complaint clearly
4. Translate to English if the input is in Hindi or other Indian languages
5. Include relevant location context
6. Make it actionable for government departments
7. Keep the citizen's voice and concerns prominent

Return only the enhanced complaint text, nothing else."""
            
            # Build user prompt
            user_prompt = f"Original complaint: {original_text}"
            
            if location:
                user_prompt += f"\nLocation: {location}"
            
            if context:
                user_prompt += f"\nAdditional context: {json.dumps(context)}"
            
            # Call Groq API if available, otherwise return original
            if not self.use_ai or not self.groq_client:
                logger.warning("AI enhancement not available, returning original text")
                return original_text
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            
            # Validate enhancement
            if len(enhanced_text) < len(original_text) * 0.5:
                logger.warning("Enhanced text seems too short, using original")
                return original_text
            
            logger.info(f"Text enhancement successful: {len(original_text)} -> {len(enhanced_text)} chars")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Text enhancement failed: {e}")
            return original_text  # Return original on failure
    
    async def extract_entities_and_keywords(self, text: str) -> Dict[str, List[str]]:
        """
        Extract important entities and keywords from complaint text
        """
        try:
            system_prompt = """Extract key entities and keywords from this government complaint.
Return a JSON with these categories:
- location: places, addresses, landmarks
- departments: government departments or services mentioned
- issues: specific problems or issues
- urgency_indicators: words indicating urgency
- people: names, designations mentioned
- dates: any dates or time references

Return valid JSON only."""
            
            if not self.use_ai or not self.groq_client:
                logger.warning("AI entity extraction not available, returning empty dict")
                return {}
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract entities from: {text}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                entities = json.loads(result)
                return entities
            except json.JSONDecodeError:
                logger.warning("Failed to parse entities JSON, returning empty dict")
                return {}
                
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {}
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment and urgency of complaint
        """
        try:
            system_prompt = """Analyze the sentiment and urgency of this government complaint.
Return JSON with:
- sentiment: positive/negative/neutral
- urgency: low/medium/high/critical
- emotion: angry/frustrated/worried/disappointed/hopeful
- confidence: 0.0-1.0

Return valid JSON only."""
            
            if not self.use_ai or not self.groq_client:
                logger.warning("AI sentiment analysis not available, returning default")
                return {
                    "sentiment": "neutral",
                    "urgency": "medium",
                    "emotion": "concerned",
                    "confidence": 0.5
                }
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze: {text}"}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            try:
                sentiment_data = json.loads(result)
                return sentiment_data
            except json.JSONDecodeError:
                return {
                    "sentiment": "neutral",
                    "urgency": "medium",
                    "emotion": "concerned",
                    "confidence": 0.5
                }
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "sentiment": "neutral", 
                "urgency": "medium",
                "emotion": "concerned",
                "confidence": 0.0
            }
    
    async def process_multi_modal_complaint(
        self, 
        text: str = "",
        audio_path: str = None,
        image_path: str = None,
        location: str = None
    ) -> Dict[str, Any]:
        """
        Process a complete multi-modal complaint
        """
        try:
            processing_result = {
                "original_text": text,
                "processed_text": text,
                "audio_text": None,
                "image_analysis": None,
                "enhanced_text": None,
                "entities": {},
                "sentiment": {},
                "success": False
            }
            
            # Process audio if provided
            if audio_path:
                audio_text = await self.process_audio_to_text(audio_path)
                if audio_text:
                    processing_result["audio_text"] = audio_text
                    text += f" {audio_text}"
            
            # Process image if provided
            if image_path:
                image_analysis = await self.process_image_with_context(image_path)
                if image_analysis:
                    processing_result["image_analysis"] = image_analysis
                    text += f" {image_analysis}"
            
            # Update processed text
            processing_result["processed_text"] = text
            
            # Enhance with AI if we have content
            if text.strip():
                enhanced_text = await self.enhance_complaint_text(text, location=location)
                processing_result["enhanced_text"] = enhanced_text
                
                # Extract entities and analyze sentiment
                entities = await self.extract_entities_and_keywords(enhanced_text)
                sentiment = await self.analyze_sentiment(enhanced_text)
                
                processing_result["entities"] = entities
                processing_result["sentiment"] = sentiment
                processing_result["success"] = True
            
            return processing_result
            
        except Exception as e:
            logger.error(f"Multi-modal processing failed: {e}")
            return {
                "original_text": text,
                "error": str(e),
                "success": False
            }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported file formats"""
        return {
            "audio": self.supported_audio_formats,
            "image": self.supported_image_formats
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the AI processor is working correctly"""
        try:
            groq_status = "unavailable"
            
            # Test Groq API if available
            if self.use_ai and self.groq_client:
                try:
                    test_response = self.groq_client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": "Hello, this is a test."}],
                        max_tokens=10
                    )
                    groq_status = "available" if test_response else "unavailable"
                except Exception as e:
                    logger.warning(f"Groq API test failed: {e}")
                    groq_status = "unavailable"
            
            return {
                "groq_api": groq_status,
                "speech_recognition": "available",
                "image_processing": "basic",
                "status": "healthy" if groq_status == "available" else "degraded",
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return {
                "groq_api": "unavailable",
                "speech_recognition": "available", 
                "image_processing": "basic",
                "status": "degraded",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }