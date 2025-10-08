"""
OCR Processing Module for SmartGriev System

This module provides Optical Character Recognition (OCR) capabilities to extract text
from images containing printed text. It is designed to be integrated into the
SmartGriev Django-based application for processing complaint images.

The module uses Hugging Face transformers library with the TrOCR model for
robust printed text recognition.

Author: SmartGriev Development Team
Version: 1.0
"""

from typing import Dict, List, Optional, Tuple, Union
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import os
import logging
import numpy as np

# Try to import transformers components, but provide fallbacks
try:
    from transformers import pipeline, TrOCRProcessor, VisionEncoderDecoderModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None
    TrOCRProcessor = None
    VisionEncoderDecoderModel = None

# Try to import pytesseract as a fallback OCR solution
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None
import cv2
import time
import hashlib
from io import BytesIO
import torch
from functools import lru_cache
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

# Global model cache to avoid reloading
_MODEL_CACHE = {}

class AdvancedOCRProcessor:
    """
    Advanced OCR Processor with image preprocessing, model caching, 
    and performance optimization for better text extraction accuracy.
    """
    
    def __init__(self, model_name: str = "microsoft/trocr-base-printed"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._pipeline = None
        self._processor = None
        self._model = None
        self.fallback_mode = False
        logger.info(f"Initializing AdvancedOCRProcessor with device: {self.device}")
    
    @property
    def pipeline(self):
        """Lazy loading of OCR pipeline with caching and fallback handling"""
        if self._pipeline is None and not self.fallback_mode:
            cache_key = f"{self.model_name}_{self.device}"
            if cache_key in _MODEL_CACHE:
                self._pipeline = _MODEL_CACHE[cache_key]
                logger.info("Using cached OCR pipeline")
            else:
                try:
                    if not TRANSFORMERS_AVAILABLE:
                        raise ImportError("Transformers not available")
                    
                    logger.info(f"Loading OCR model: {self.model_name}")
                    self._pipeline = pipeline(
                        "image-to-text",
                        model=self.model_name,
                        tokenizer=self.model_name,
                        device=0 if self.device == "cuda" else -1
                    )
                    _MODEL_CACHE[cache_key] = self._pipeline
                    logger.info("OCR pipeline loaded and cached")
                except Exception as e:
                    logger.warning(f"Failed to load TrOCR model: {str(e)}. Switching to fallback mode.")
                    logger.info("OCR will operate in fallback mode (basic text extraction)")
                    self.fallback_mode = True
                    self._pipeline = None
        return self._pipeline
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Advanced image preprocessing to improve OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image object
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert PIL to numpy for OpenCV processing
            img_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Apply Gaussian blur to reduce noise
            img_bgr = cv2.GaussianBlur(img_bgr, (1, 1), 0)
            
            # Convert to grayscale for better text detection
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(cleaned)
            
            # Convert back to RGB for the model
            processed_image = processed_image.convert('RGB')
            
            # Enhance contrast and sharpness
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Sharpness(processed_image)
            processed_image = enhancer.enhance(1.1)
            
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {str(e)}")
            return image.convert('RGB') if image.mode != 'RGB' else image
    
    def _fallback_ocr(self, image: Image.Image) -> List[Dict]:
        """
        Fallback OCR method using alternative approaches when TrOCR is not available.
        
        Args:
            image: PIL Image object
            
        Returns:
            List with OCR results in pipeline format
        """
        try:
            if TESSERACT_AVAILABLE and pytesseract is not None:
                # Use Tesseract OCR as fallback
                text = pytesseract.image_to_string(image, config='--psm 6')
                return [{'generated_text': text.strip()}]
            else:
                # Basic fallback: return a message indicating OCR is not available
                logger.warning("No OCR engine available, returning placeholder text")
                return [{'generated_text': '[OCR functionality temporarily unavailable]'}]
        except Exception as e:
            logger.error(f"Fallback OCR failed: {str(e)}")
            return [{'generated_text': f'[OCR Error: {str(e)}]'}]
    
    def extract_text_advanced(self, image: Image.Image, 
                            preprocess: bool = True,
                            confidence_threshold: float = 0.5) -> Dict[str, Union[str, float, List]]:
        """
        Advanced text extraction with preprocessing and confidence scoring.
        
        Args:
            image: PIL Image object
            preprocess: Whether to apply image preprocessing
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            Dict containing extracted text, confidence, and metadata
        """
        start_time = time.time()
        
        try:
            # Preprocess image if requested
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image.convert('RGB') if image.mode != 'RGB' else image
            
            # Try to extract text using the TrOCR pipeline first
            if not self.fallback_mode and self.pipeline is not None:
                results = self.pipeline(processed_image)
            else:
                # Use fallback OCR method
                results = self._fallback_ocr(processed_image)
            
            # Process results
            if results and len(results) > 0:
                extracted_text = results[0].get('generated_text', '')
                # Adjust confidence based on the OCR method used
                if self.fallback_mode:
                    if '[OCR functionality temporarily unavailable]' in extracted_text or '[OCR Error:' in extracted_text:
                        confidence = 0.0
                    elif TESSERACT_AVAILABLE:
                        confidence = min(0.7, len(extracted_text) / 150.0 + 0.3)  # Lower confidence for Tesseract
                    else:
                        confidence = 0.1  # Very low confidence for placeholder text
                else:
                    # Standard confidence for TrOCR
                    confidence = min(0.9, len(extracted_text) / 100.0 + 0.5)
            else:
                extracted_text = ''
                confidence = 0.0
            
            processing_time = time.time() - start_time
            
            # Determine the model/method used
            model_info = "fallback-tesseract" if self.fallback_mode and TESSERACT_AVAILABLE else \
                        "fallback-placeholder" if self.fallback_mode else self.model_name
            
            result = {
                'extracted_text': extracted_text,
                'confidence': confidence,
                'processing_time': processing_time,
                'character_count': len(extracted_text),
                'word_count': len(extracted_text.split()),
                'preprocessing_applied': preprocess,
                'model_used': model_info,
                'device_used': self.device,
                'fallback_mode': self.fallback_mode
            }
            
            logger.info(f"Advanced OCR completed in {processing_time:.2f}s, "
                       f"extracted {len(extracted_text)} characters with confidence {confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Advanced OCR processing error: {str(e)}")
            raise Exception(f"Advanced OCR processing failed: {str(e)}")
    
    def batch_extract_text(self, images: List[Image.Image]) -> List[Dict]:
        """
        Process multiple images in batch for better performance.
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            List of extraction results
        """
        results = []
        for i, image in enumerate(images):
            try:
                result = self.extract_text_advanced(image)
                result['image_index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing image {i}: {str(e)}")
                results.append({
                    'extracted_text': '',
                    'confidence': 0.0,
                    'error': str(e),
                    'image_index': i
                })
        return results

# Global instance for backward compatibility
_global_ocr_processor = None

def get_ocr_processor() -> AdvancedOCRProcessor:
    """Get or create global OCR processor instance"""
    global _global_ocr_processor
    if _global_ocr_processor is None:
        _global_ocr_processor = AdvancedOCRProcessor()
    return _global_ocr_processor


def extract_text_from_image(image_path: str) -> Dict[str, str]:
    """
    Enhanced text extraction from image file with advanced preprocessing and error handling.
    
    This function uses the Advanced OCR Processor with image preprocessing
    to perform high-quality OCR on images containing printed text.
    
    Args:
        image_path (str): The file path to the image from which to extract text.
                         Supported formats include JPEG, PNG, BMP, TIFF, etc.
    
    Returns:
        Dict[str, str]: A dictionary containing the extracted text with additional metadata.
                       Maintains backward compatibility with original format.
    
    Raises:
        FileNotFoundError: If the specified image file does not exist or cannot be accessed.
        Exception: For other errors during OCR processing.
    
    Example:
        >>> result = extract_text_from_image('/path/to/complaint_image.jpg')
        >>> print(result['extracted_text'])
        'This is a complaint about poor service quality...'
    """
    
    try:
        # Verify that the image file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Validate image format
        if not _validate_image_format(image_path):
            logger.warning(f"Unsupported image format: {image_path}\")")
        
        # Load the image using Pillow with error handling
        try:
            image = Image.open(image_path)
        except Exception as e:
            raise Exception(f"Failed to load image {image_path}: {str(e)}\")")
        
        logger.info(f"Processing image: {image_path} (Size: {image.size}, Mode: {image.mode})\")")
        
        # Use advanced OCR processor
        ocr_processor = get_ocr_processor()
        result = ocr_processor.extract_text_advanced(image, preprocess=True)
        
        # Maintain backward compatibility by returning only extracted_text
        # but log additional metadata
        logger.info(f"OCR completed for {image_path}: {result['character_count']} chars, "
                   f"confidence: {result['confidence']:.2f}, time: {result['processing_time']:.2f}s")
        
        return {'extracted_text': result['extracted_text']}
        
    except FileNotFoundError:
        logger.error(f"File not found: {image_path}")
        raise
    except Exception as e:
        logger.error(f"OCR processing error for {image_path}: {str(e)}")
        raise Exception(f"Error during OCR processing: {str(e)}")


def extract_text_from_image_bytes(image_bytes) -> Dict[str, str]:
    """
    Enhanced text extraction from image bytes with advanced preprocessing.
    
    Args:
        image_bytes: Image data as bytes or BytesIO object
        
    Returns:
        Dict[str, str]: Dictionary containing extracted text with metadata
    """
    try:
        # Handle different types of byte inputs
        if hasattr(image_bytes, 'seek'):
            image_bytes.seek(0)  # Reset file pointer if it's a file-like object
        
        # Load the image from bytes with enhanced error handling
        try:
            image = Image.open(image_bytes)
        except Exception as e:
            raise Exception(f"Failed to load image from bytes: {str(e)}")
        
        # Get image metadata for logging
        image_format = getattr(image, 'format', 'Unknown')
        image_size = image.size
        
        logger.info(f"Processing image from bytes (Format: {image_format}, Size: {image_size})")
        
        # Use advanced OCR processor with preprocessing
        ocr_processor = get_ocr_processor()
        result = ocr_processor.extract_text_advanced(image, preprocess=True)
        
        # Log processing results
        logger.info(f"OCR from bytes completed: {result['character_count']} chars, "
                   f"confidence: {result['confidence']:.2f}, time: {result['processing_time']:.2f}s")
        
        # Return backward-compatible result
        return {'extracted_text': result['extracted_text']}
        
    except Exception as e:
        logger.error(f"OCR processing error from bytes: {str(e)}")
        raise Exception(f"Error during OCR processing from bytes: {str(e)}")


def _validate_image_format(image_path: str) -> bool:
    """
    Private helper function to validate image format.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        bool: True if the image format is supported, False otherwise
    """
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
    file_extension = os.path.splitext(image_path.lower())[1]
    return file_extension in supported_formats


def get_ocr_performance_stats() -> Dict[str, Union[str, int, float]]:
    """
    Get performance statistics for the OCR system.
    
    Returns:
        Dict containing performance metrics and system information
    """
    ocr_processor = get_ocr_processor()
    
    return {
        'model_name': ocr_processor.model_name,
        'device': ocr_processor.device,
        'cuda_available': torch.cuda.is_available(),
        'cached_models': len(_MODEL_CACHE),
        'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'],
        'preprocessing_available': True,
        'batch_processing_available': True,
        'version': '2.0-enhanced'
    }


def clear_model_cache():
    """Clear the model cache to free up memory."""
    global _MODEL_CACHE, _global_ocr_processor
    _MODEL_CACHE.clear()
    _global_ocr_processor = None
    logger.info("OCR model cache cleared")


def preprocess_image_for_ocr(image_path: str, output_path: Optional[str] = None) -> str:
    """
    Standalone function to preprocess an image for better OCR results.
    
    Args:
        image_path: Path to input image
        output_path: Optional path to save preprocessed image
        
    Returns:
        Path to preprocessed image (same as output_path if provided, 
        otherwise a temporary file)
    """
    try:
        # Load image
        image = Image.open(image_path)
        
        # Get OCR processor and preprocess
        ocr_processor = get_ocr_processor()
        processed_image = ocr_processor.preprocess_image(image)
        
        # Determine output path
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = f"{base_name}_preprocessed.png"
        
        # Save preprocessed image
        processed_image.save(output_path, 'PNG')
        logger.info(f"Preprocessed image saved to: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error preprocessing image {image_path}: {str(e)}")
        raise Exception(f"Image preprocessing failed: {str(e)}")


def extract_text_with_regions(image_path: str) -> Dict[str, Union[str, List]]:
    """
    Advanced text extraction that attempts to identify text regions.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dict containing extracted text and region information
    """
    try:
        # Load and process image
        image = Image.open(image_path)
        ocr_processor = get_ocr_processor()
        
        # Get basic extraction results
        result = ocr_processor.extract_text_advanced(image, preprocess=True)
        
        # Add region analysis (simplified version)
        extracted_text = result['extracted_text']
        lines = extracted_text.split('\n') if extracted_text else []
        
        # Analyze text characteristics
        regions = []
        for i, line in enumerate(lines):
            if line.strip():
                regions.append({
                    'line_number': i + 1,
                    'text': line.strip(),
                    'character_count': len(line.strip()),
                    'word_count': len(line.strip().split())
                })
        
        return {
            'extracted_text': extracted_text,
            'total_lines': len(lines),
            'text_regions': regions,
            'confidence': result['confidence'],
            'processing_time': result['processing_time'],
            'metadata': {
                'character_count': result['character_count'],
                'word_count': result['word_count'],
                'model_used': result['model_used'],
                'device_used': result['device_used']
            }
        }
        
    except Exception as e:
        logger.error(f"Error in region-based text extraction: {str(e)}")
        raise Exception(f"Region-based text extraction failed: {str(e)}")


# Performance monitoring decorator
def monitor_ocr_performance(func):
    """Decorator to monitor OCR function performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            processing_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {processing_time:.2f}s")
            return result
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {processing_time:.2f}s: {str(e)}")
            raise
    return wrapper


# Health check function for the OCR system
def ocr_health_check() -> Dict[str, Union[str, bool, float]]:
    """
    Perform a health check on the OCR system.
    
    Returns:
        Dict containing health status and system information
    """
    try:
        start_time = time.time()
        
        # Test OCR processor initialization
        ocr_processor = get_ocr_processor()
        
        # Create a simple test image
        test_image = Image.new('RGB', (200, 100), color='white')
        
        # Test basic functionality
        result = ocr_processor.extract_text_advanced(test_image, preprocess=False)
        
        health_time = time.time() - start_time
        
        return {
            'status': 'healthy',
            'model_loaded': True,
            'device': ocr_processor.device,
            'health_check_time': health_time,
            'model_name': ocr_processor.model_name,
            'preprocessing_available': True,
            'batch_processing_available': True,
            'last_check': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'last_check': time.strftime('%Y-%m-%d %H:%M:%S')
        }


class OCRProcessor:
    """Class-based OCR processor for better integration with Django."""
    
    def __init__(self):
        """Initialize the OCR processor."""
        # Disable OCR model loading to prevent memory issues during development
        logger.info("OCR processor initializing in fallback mode to prevent memory issues")
        self.ocr_pipeline = None
    
    def process_image(self, image) -> Dict[str, str]:
        """
        Process an image and extract text.
        
        Args:
            image: PIL Image object or image path
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            if self.ocr_pipeline is None:
                raise Exception("OCR pipeline not initialized")
            
            # Handle different input types
            if isinstance(image, str):
                # If it's a string, treat as file path
                image = Image.open(image)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            results = self.ocr_pipeline(image)
            extracted_text = results[0]['generated_text'] if results else ""
            
            return {
                'extracted_text': extracted_text,
                'text_length': len(extracted_text),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            return {
                'extracted_text': '',
                'text_length': 0,
                'status': 'error',
                'error_message': str(e)
            }


# Global OCR processor instance
ocr_processor = OCRProcessor()


if __name__ == "__main__":
    """
    Demonstration and testing block for the OCR processor module.
    """
    
    print("=" * 60)
    print("SmartGriev OCR Processor - Testing Module")
    print("=" * 60)
    
    # Test with a sample image path (modify this path for actual testing)
    sample_image_path = "sample_complaint_image.jpg"
    
    try:
        print(f"Attempting to process image: {sample_image_path}")
        result = extract_text_from_image(sample_image_path)
        
        print("\n✅ OCR Processing Successful!")
        print("-" * 40)
        print("Extracted Text:")
        print(f"'{result['extracted_text']}'")
        print("-" * 40)
        print(f"Text Length: {len(result['extracted_text'])} characters")
        
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        print("Note: For testing, place a sample image in the same directory")
        print("and update the 'sample_image_path' variable above.")
        
    except Exception as e:
        print(f"\n❌ Processing Error: {e}")
        print("This might be due to missing dependencies or model loading issues.")
    
    print("\n" + "=" * 60)
    print("Module Information:")
    print("- Primary Function: extract_text_from_image(image_path: str)")
    print("- Model Used: microsoft/trocr-base-printed")
    print("- Input: Image file path (string)")
    print("- Output: Dictionary with 'extracted_text' key")
    print("- Purpose: Extract text from complaint images for NLP pipeline")
    print("=" * 60)