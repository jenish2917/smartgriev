# Advanced AI Processing Services for SmartGriev
# Multi-modal complaint processing with cutting-edge AI

import os
import io
import base64
import asyncio
import logging
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime

# AI/ML Libraries
import openai
import speech_recognition as sr
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import librosa
from groq import Groq

# Django imports
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of AI processing"""
    text: str
    confidence: float
    processing_type: str
    metadata: Dict
    extracted_entities: Dict
    classification: Optional[str] = None

class AdvancedAIProcessor:
    """
    Cutting-edge AI processor for multi-modal complaint handling
    Supports text, audio, and image processing with context understanding
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize image processing models
        self.setup_vision_models()
        
        # Initialize audio processing
        self.setup_audio_models()
        
    def setup_vision_models(self):
        """Setup vision models for image understanding"""
        try:
            # Use Hugging Face transformers for image captioning and OCR
            self.image_captioner = pipeline(
                "image-to-text", 
                model="Salesforce/blip-image-captioning-large"
            )
            
            # OCR pipeline for text extraction from images
            self.ocr_pipeline = pipeline(
                "image-to-text",
                model="microsoft/trocr-base-printed"
            )
            
            logger.info("Vision models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vision models: {e}")
            self.image_captioner = None
            self.ocr_pipeline = None
    
    def setup_audio_models(self):
        """Setup audio processing models"""
        try:
            # Whisper for speech-to-text
            self.whisper_pipeline = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-base"
            )
            logger.info("Audio models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing audio models: {e}")
            self.whisper_pipeline = None
    
    async def process_text_complaint(self, text: str) -> ProcessingResult:
        """Process text-based complaints with NLP analysis"""
        try:
            # Extract entities and sentiment
            entities = await self.extract_entities(text)
            
            # Enhance text with context analysis
            enhanced_text = await self.enhance_text_context(text)
            
            return ProcessingResult(
                text=enhanced_text,
                confidence=0.95,
                processing_type="text",
                metadata={
                    "original_text": text,
                    "word_count": len(text.split()),
                    "language": "en",  # Could add language detection
                    "timestamp": datetime.now().isoformat()
                },
                extracted_entities=entities
            )
        except Exception as e:
            logger.error(f"Error processing text complaint: {e}")
            return ProcessingResult(
                text=text,
                confidence=0.5,
                processing_type="text",
                metadata={"error": str(e)},
                extracted_entities={}
            )
    
    async def process_audio_complaint(self, audio_file_path: str) -> ProcessingResult:
        """Process audio complaints with advanced speech-to-text"""
        try:
            # Load and preprocess audio
            audio_data, sample_rate = librosa.load(audio_file_path, sr=16000)
            
            # Enhance audio quality
            enhanced_audio = self.enhance_audio_quality(audio_data, sample_rate)
            
            # Convert to text using Whisper
            if self.whisper_pipeline:
                result = self.whisper_pipeline(enhanced_audio)
                text = result["text"]
                confidence = getattr(result, 'confidence', 0.8)
            else:
                # Fallback to speech_recognition
                text, confidence = await self.fallback_speech_recognition(audio_file_path)
            
            # Extract entities from transcribed text
            entities = await self.extract_entities(text)
            
            # Enhance with context
            enhanced_text = await self.enhance_text_context(text)
            
            return ProcessingResult(
                text=enhanced_text,
                confidence=confidence,
                processing_type="audio",
                metadata={
                    "original_audio_duration": len(audio_data) / sample_rate,
                    "sample_rate": sample_rate,
                    "audio_quality": "enhanced",
                    "transcription_model": "whisper-base",
                    "timestamp": datetime.now().isoformat()
                },
                extracted_entities=entities
            )
            
        except Exception as e:
            logger.error(f"Error processing audio complaint: {e}")
            return ProcessingResult(
                text="Error processing audio",
                confidence=0.0,
                processing_type="audio",
                metadata={"error": str(e)},
                extracted_entities={}
            )
    
    async def process_image_complaint(self, image_file_path: str) -> ProcessingResult:
        """Process image complaints with advanced computer vision"""
        try:
            # Load and enhance image
            image = Image.open(image_file_path)
            enhanced_image = self.enhance_image_quality(image)
            
            # Extract text from image (OCR)
            ocr_text = await self.extract_text_from_image(enhanced_image)
            
            # Generate image description
            image_description = await self.generate_image_description(enhanced_image)
            
            # Combine OCR and description for comprehensive understanding
            combined_text = self.combine_image_analysis(ocr_text, image_description)
            
            # Extract entities
            entities = await self.extract_entities(combined_text)
            
            # Enhance with context
            enhanced_text = await self.enhance_text_context(combined_text)
            
            return ProcessingResult(
                text=enhanced_text,
                confidence=0.85,
                processing_type="image",
                metadata={
                    "image_dimensions": image.size,
                    "image_format": image.format,
                    "ocr_text_length": len(ocr_text),
                    "description_length": len(image_description),
                    "analysis_type": "ocr+description",
                    "timestamp": datetime.now().isoformat()
                },
                extracted_entities=entities
            )
            
        except Exception as e:
            logger.error(f"Error processing image complaint: {e}")
            return ProcessingResult(
                text="Error processing image",
                confidence=0.0,
                processing_type="image",
                metadata={"error": str(e)},
                extracted_entities={}
            )
    
    def enhance_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance audio quality for better speech recognition"""
        try:
            # Noise reduction
            audio_data = librosa.effects.preemphasis(audio_data)
            
            # Normalize volume
            audio_data = librosa.util.normalize(audio_data)
            
            # Apply spectral gating for noise reduction
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Simple spectral subtraction for noise reduction
            noise_threshold = np.percentile(magnitude, 20)
            magnitude = np.maximum(magnitude - noise_threshold * 0.5, magnitude * 0.1)
            
            enhanced_stft = magnitude * np.exp(1j * phase)
            enhanced_audio = librosa.istft(enhanced_stft)
            
            return enhanced_audio
        except Exception as e:
            logger.warning(f"Audio enhancement failed: {e}")
            return audio_data
    
    def enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """Enhance image quality for better OCR and analysis"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # Resize if too small
            if image.size[0] < 800 or image.size[1] < 600:
                new_size = (max(800, image.size[0]), max(600, image.size[1]))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return image
    
    async def extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using OCR"""
        try:
            if self.ocr_pipeline:
                result = self.ocr_pipeline(image)
                return result[0]["generated_text"] if result else ""
            else:
                # Fallback to simple OCR
                import pytesseract
                return pytesseract.image_to_string(image)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    async def generate_image_description(self, image: Image.Image) -> str:
        """Generate contextual description of image"""
        try:
            if self.image_captioner:
                result = self.image_captioner(image)
                return result[0]["generated_text"] if result else ""
            else:
                return "Image analysis not available"
        except Exception as e:
            logger.error(f"Image description failed: {e}")
            return ""
    
    def combine_image_analysis(self, ocr_text: str, description: str) -> str:
        """Combine OCR text and image description for comprehensive understanding"""
        combined = []
        
        if description:
            combined.append(f"Image shows: {description}")
        
        if ocr_text:
            combined.append(f"Text visible in image: {ocr_text}")
        
        if not combined:
            combined.append("Unable to extract meaningful information from image")
        
        return " | ".join(combined)
    
    async def fallback_speech_recognition(self, audio_file_path: str) -> Tuple[str, float]:
        """Fallback speech recognition using Google Speech Recognition"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                return text, 0.7
        except Exception as e:
            logger.error(f"Fallback speech recognition failed: {e}")
            return "Unable to process audio", 0.0
    
    async def extract_entities(self, text: str) -> Dict:
        """Extract entities from text using NLP"""
        try:
            # Use Groq for entity extraction
            response = await self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": """Extract entities from the complaint text. Return JSON with:
                        - location: any locations mentioned
                        - person_names: any person names
                        - organizations: any organizations/departments
                        - dates: any dates or times
                        - issues: main issues/problems identified
                        - urgency_keywords: words indicating urgency
                        """
                    },
                    {
                        "role": "user", 
                        "content": f"Extract entities from: {text}"
                    }
                ],
                temperature=0.3
            )
            
            import json
            entities = json.loads(response.choices[0].message.content)
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {
                "location": [],
                "person_names": [],
                "organizations": [],
                "dates": [],
                "issues": [],
                "urgency_keywords": []
            }
    
    async def enhance_text_context(self, text: str) -> str:
        """Enhance text with better context and structure"""
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": """Improve and structure the complaint text while preserving all original information.
                        Make it more clear and formal for government processing. Add context where needed.
                        Keep the same language and don't change the core complaint.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Enhance this complaint text: {text}"
                    }
                ],
                temperature=0.2
            )
            
            enhanced_text = response.choices[0].message.content
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Text enhancement failed: {e}")
            return text

# Initialize global processor instance
ai_processor = AdvancedAIProcessor()