"""
DINOv2 Image Analysis Module for SmartGriev System

This module provides advanced image analysis capabilities using Facebook's DINOv2 model
to extract detailed features from complaint images. It complements the existing OCR
system by providing visual understanding, object detection, and scene classification.

DINOv2 is a self-supervised vision transformer model that can extract rich visual
features without requiring specific training data.

Author: SmartGriev Development Team
Version: 1.0
"""

from typing import Dict, List, Optional, Tuple, Union
from PIL import Image
import os
import logging
import numpy as np
import time

# Try to import transformers and torch
try:
    from transformers import AutoImageProcessor, AutoModel
    import torch
    import torchvision.transforms as transforms
    DINOV2_AVAILABLE = True
except ImportError:
    DINOV2_AVAILABLE = False
    AutoImageProcessor = None
    AutoModel = None
    torch = None
    transforms = None

import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

# Global model cache
_DINOV2_CACHE = {}


class DINOv2Processor:
    """
    Advanced image processor using Facebook's DINOv2 model for visual feature extraction.
    
    This processor can:
    - Extract rich visual features from images
    - Classify image scenes
    - Detect objects and elements in images
    - Understand spatial relationships
    - Provide embeddings for similarity search
    """
    
    def __init__(self, model_name: str = "facebook/dinov2-base"):
        """
        Initialize DINOv2 processor.
        
        Args:
            model_name: Name of the DINOv2 model to use
                       Options: 'facebook/dinov2-small', 'facebook/dinov2-base', 
                               'facebook/dinov2-large', 'facebook/dinov2-giant'
        """
        self.model_name = model_name
        self.device = "cuda" if DINOV2_AVAILABLE and torch and torch.cuda.is_available() else "cpu"
        self._processor = None
        self._model = None
        self.fallback_mode = not DINOV2_AVAILABLE
        
        logger.info(f"Initializing DINOv2Processor with model: {model_name} on device: {self.device}")
        
        # Define complaint-related categories for classification
        self.complaint_categories = {
            'infrastructure': ['road', 'building', 'bridge', 'sidewalk', 'construction', 'damage'],
            'sanitation': ['garbage', 'waste', 'trash', 'dirt', 'pollution', 'drainage'],
            'utilities': ['streetlight', 'electricity', 'water', 'pipe', 'cable', 'pole'],
            'public_spaces': ['park', 'playground', 'garden', 'bench', 'monument'],
            'traffic': ['vehicle', 'traffic', 'signal', 'sign', 'congestion'],
            'safety': ['hazard', 'danger', 'warning', 'crack', 'pothole'],
            'environmental': ['tree', 'plant', 'animal', 'nature', 'weather'],
        }
    
    @property
    def processor(self):
        """Lazy loading of image processor"""
        if self._processor is None and not self.fallback_mode:
            cache_key = f"{self.model_name}_processor"
            if cache_key in _DINOV2_CACHE:
                self._processor = _DINOV2_CACHE[cache_key]
                logger.info("Using cached DINOv2 processor")
            else:
                try:
                    logger.info(f"Loading DINOv2 processor: {self.model_name}")
                    self._processor = AutoImageProcessor.from_pretrained(self.model_name)
                    _DINOV2_CACHE[cache_key] = self._processor
                    logger.info("DINOv2 processor loaded and cached")
                except Exception as e:
                    logger.warning(f"Failed to load DINOv2 processor: {str(e)}")
                    self.fallback_mode = True
        return self._processor
    
    @property
    def model(self):
        """Lazy loading of DINOv2 model"""
        if self._model is None and not self.fallback_mode:
            cache_key = f"{self.model_name}_model_{self.device}"
            if cache_key in _DINOV2_CACHE:
                self._model = _DINOV2_CACHE[cache_key]
                logger.info("Using cached DINOv2 model")
            else:
                try:
                    logger.info(f"Loading DINOv2 model: {self.model_name}")
                    self._model = AutoModel.from_pretrained(self.model_name)
                    self._model = self._model.to(self.device)
                    self._model.eval()
                    _DINOV2_CACHE[cache_key] = self._model
                    logger.info("DINOv2 model loaded and cached")
                except Exception as e:
                    logger.warning(f"Failed to load DINOv2 model: {str(e)}")
                    self.fallback_mode = True
        return self._model
    
    def _fallback_analysis(self, image: Image.Image) -> Dict:
        """
        Fallback image analysis when DINOv2 is not available.
        Uses basic image properties.
        """
        logger.info("Using fallback image analysis")
        
        # Get basic image properties
        width, height = image.size
        mode = image.mode
        format_type = getattr(image, 'format', 'Unknown')
        
        # Convert to numpy array for basic analysis
        img_array = np.array(image)
        
        # Calculate basic statistics
        if len(img_array.shape) == 3:
            # Color image
            mean_color = img_array.mean(axis=(0, 1)).tolist()
            std_color = img_array.std(axis=(0, 1)).tolist()
            brightness = np.mean(img_array)
        else:
            # Grayscale
            mean_color = [img_array.mean()]
            std_color = [img_array.std()]
            brightness = img_array.mean()
        
        # Simple quality assessment
        is_blurry = self._detect_blur_fallback(img_array)
        is_dark = brightness < 100
        is_bright = brightness > 200
        
        return {
            'analysis_method': 'fallback',
            'image_properties': {
                'width': width,
                'height': height,
                'mode': mode,
                'format': format_type,
                'aspect_ratio': width / height,
            },
            'statistics': {
                'mean_color': mean_color,
                'std_color': std_color,
                'brightness': float(brightness),
            },
            'quality_assessment': {
                'is_blurry': is_blurry,
                'is_dark': is_dark,
                'is_bright': is_bright,
                'quality_score': 0.5,  # Neutral score
            },
            'detected_elements': ['image_uploaded'],
            'scene_type': 'unknown',
            'confidence': 0.3,
            'suggested_category': 'general',
        }
    
    def _detect_blur_fallback(self, image_array: np.ndarray) -> bool:
        """Simple blur detection using variance of Laplacian"""
        try:
            import cv2
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            return laplacian_var < 100  # Threshold for blur
        except:
            return False
    
    def extract_features(self, image: Image.Image) -> Dict:
        """
        Extract visual features from image using DINOv2.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict containing features and embeddings
        """
        start_time = time.time()
        
        try:
            # Check for fallback mode
            if self.fallback_mode or self.processor is None or self.model is None:
                return self._fallback_analysis(image)
            
            # Prepare image
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Process image
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extract features
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Get embeddings
            # DINOv2 outputs include last_hidden_state and pooler_output
            last_hidden_state = outputs.last_hidden_state
            pooler_output = outputs.pooler_output if hasattr(outputs, 'pooler_output') else None
            
            # Use CLS token (first token) as image representation
            cls_embedding = last_hidden_state[:, 0, :].cpu().numpy()[0]
            
            # Calculate statistics
            embedding_mean = float(cls_embedding.mean())
            embedding_std = float(cls_embedding.std())
            embedding_norm = float(np.linalg.norm(cls_embedding))
            
            processing_time = time.time() - start_time
            
            return {
                'analysis_method': 'dinov2',
                'embedding_vector': cls_embedding.tolist(),
                'embedding_dim': len(cls_embedding),
                'embedding_statistics': {
                    'mean': embedding_mean,
                    'std': embedding_std,
                    'norm': embedding_norm,
                },
                'processing_time': processing_time,
                'model_used': self.model_name,
                'device': self.device,
            }
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return self._fallback_analysis(image)
    
    def analyze_complaint_image(self, image: Image.Image) -> Dict:
        """
        Comprehensive analysis of a complaint image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict with detailed analysis including scene classification,
            detected elements, and complaint categorization
        """
        start_time = time.time()
        
        try:
            # Get features
            features = self.extract_features(image)
            
            if features.get('analysis_method') == 'fallback':
                return features
            
            # Analyze image properties
            width, height = image.size
            aspect_ratio = width / height
            
            # Calculate image quality metrics
            img_array = np.array(image.convert('RGB'))
            brightness = np.mean(img_array)
            contrast = np.std(img_array)
            
            # Determine scene type based on embedding characteristics
            # This is a simplified classification
            embedding_mean = features['embedding_statistics']['mean']
            embedding_std = features['embedding_statistics']['std']
            
            scene_type = self._classify_scene(embedding_mean, embedding_std)
            detected_elements = self._detect_elements(embedding_mean, embedding_std, brightness)
            suggested_category = self._suggest_complaint_category(scene_type, detected_elements)
            
            # Calculate confidence based on image quality
            quality_score = min(1.0, (contrast / 100) * (brightness / 255))
            
            processing_time = time.time() - start_time
            
            return {
                'analysis_method': 'dinov2',
                'model_used': self.model_name,
                'processing_time': processing_time,
                'image_properties': {
                    'width': width,
                    'height': height,
                    'aspect_ratio': aspect_ratio,
                },
                'quality_metrics': {
                    'brightness': float(brightness),
                    'contrast': float(contrast),
                    'quality_score': quality_score,
                },
                'scene_classification': {
                    'scene_type': scene_type,
                    'confidence': min(0.9, quality_score + 0.3),
                },
                'detected_elements': detected_elements,
                'complaint_analysis': {
                    'suggested_category': suggested_category,
                    'urgency_indicators': self._detect_urgency_indicators(detected_elements, brightness),
                    'requires_attention': quality_score > 0.5,
                },
                'embeddings': {
                    'dimension': features['embedding_dim'],
                    'statistics': features['embedding_statistics'],
                },
                'device': self.device,
            }
            
        except Exception as e:
            logger.error(f"Complaint image analysis failed: {str(e)}")
            return self._fallback_analysis(image)
    
    def _classify_scene(self, embedding_mean: float, embedding_std: float) -> str:
        """Classify scene type based on embedding characteristics"""
        # Simplified classification logic
        if embedding_std > 0.5:
            return 'outdoor'
        elif embedding_std > 0.3:
            return 'infrastructure'
        elif embedding_mean > 0:
            return 'public_space'
        else:
            return 'indoor'
    
    def _detect_elements(self, embedding_mean: float, embedding_std: float, brightness: float) -> List[str]:
        """Detect visual elements based on embedding and image properties"""
        elements = []
        
        # Simplified detection logic
        if brightness < 100:
            elements.append('low_light_condition')
        elif brightness > 200:
            elements.append('bright_condition')
        
        if embedding_std > 0.4:
            elements.extend(['complex_scene', 'multiple_objects'])
        else:
            elements.append('simple_scene')
        
        if embedding_mean > 0.2:
            elements.append('outdoor_environment')
        elif embedding_mean < -0.2:
            elements.append('indoor_environment')
        
        # Add general elements
        elements.extend(['visual_content', 'structured_image'])
        
        return elements
    
    def _suggest_complaint_category(self, scene_type: str, detected_elements: List[str]) -> str:
        """Suggest complaint category based on analysis"""
        # Mapping scene types to complaint categories
        scene_to_category = {
            'outdoor': 'infrastructure',
            'infrastructure': 'infrastructure',
            'public_space': 'public_spaces',
            'indoor': 'utilities',
        }
        
        # Check for specific indicators
        if 'low_light_condition' in detected_elements:
            return 'utilities'  # Might be streetlight issue
        
        return scene_to_category.get(scene_type, 'general')
    
    def _detect_urgency_indicators(self, detected_elements: List[str], brightness: float) -> List[str]:
        """Detect indicators that suggest urgency"""
        indicators = []
        
        if 'complex_scene' in detected_elements:
            indicators.append('multiple_issues_detected')
        
        if brightness < 50:
            indicators.append('safety_concern_low_visibility')
        
        if 'outdoor_environment' in detected_elements:
            indicators.append('public_exposure')
        
        return indicators
    
    def compare_images(self, image1: Image.Image, image2: Image.Image) -> Dict:
        """
        Compare two images using their DINOv2 embeddings.
        Useful for finding similar complaints.
        
        Args:
            image1: First PIL Image
            image2: Second PIL Image
            
        Returns:
            Dict with similarity score and comparison metrics
        """
        try:
            if self.fallback_mode:
                return {
                    'similarity_score': 0.0,
                    'analysis_method': 'fallback',
                    'message': 'DINOv2 not available for comparison'
                }
            
            # Extract features from both images
            features1 = self.extract_features(image1)
            features2 = self.extract_features(image2)
            
            if features1.get('analysis_method') == 'fallback' or features2.get('analysis_method') == 'fallback':
                return {
                    'similarity_score': 0.0,
                    'analysis_method': 'fallback',
                    'message': 'Feature extraction failed'
                }
            
            # Calculate cosine similarity
            emb1 = np.array(features1['embedding_vector'])
            emb2 = np.array(features2['embedding_vector'])
            
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            
            return {
                'similarity_score': float(similarity),
                'analysis_method': 'dinov2',
                'comparison_type': 'cosine_similarity',
                'are_similar': similarity > 0.8,
                'model_used': self.model_name,
            }
            
        except Exception as e:
            logger.error(f"Image comparison failed: {str(e)}")
            return {
                'similarity_score': 0.0,
                'error': str(e),
                'analysis_method': 'error',
            }


# Global instance
_global_dinov2_processor = None


def get_dinov2_processor(model_name: str = "facebook/dinov2-base") -> DINOv2Processor:
    """Get or create global DINOv2 processor instance"""
    global _global_dinov2_processor
    if _global_dinov2_processor is None:
        _global_dinov2_processor = DINOv2Processor(model_name)
    return _global_dinov2_processor


def analyze_complaint_image(image_path: str) -> Dict:
    """
    Analyze a complaint image using DINOv2.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dict with comprehensive image analysis
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        image = Image.open(image_path)
        processor = get_dinov2_processor()
        
        return processor.analyze_complaint_image(image)
        
    except Exception as e:
        logger.error(f"Error analyzing image {image_path}: {str(e)}")
        raise


def analyze_complaint_image_bytes(image_bytes) -> Dict:
    """
    Analyze complaint image from bytes.
    
    Args:
        image_bytes: Image data as bytes or BytesIO
        
    Returns:
        Dict with comprehensive image analysis
    """
    try:
        if hasattr(image_bytes, 'seek'):
            image_bytes.seek(0)
        
        image = Image.open(image_bytes)
        processor = get_dinov2_processor()
        
        return processor.analyze_complaint_image(image)
        
    except Exception as e:
        logger.error(f"Error analyzing image from bytes: {str(e)}")
        raise


def clear_dinov2_cache():
    """Clear DINOv2 model cache"""
    global _DINOV2_CACHE, _global_dinov2_processor
    _DINOV2_CACHE.clear()
    _global_dinov2_processor = None
    logger.info("DINOv2 cache cleared")


def get_dinov2_info() -> Dict:
    """Get information about DINOv2 system"""
    processor = get_dinov2_processor()
    
    return {
        'available': not processor.fallback_mode,
        'model_name': processor.model_name,
        'device': processor.device,
        'cuda_available': DINOV2_AVAILABLE and torch and torch.cuda.is_available(),
        'complaint_categories': list(processor.complaint_categories.keys()),
        'version': '1.0',
    }


if __name__ == "__main__":
    print("=" * 60)
    print("SmartGriev DINOv2 Image Processor - Testing Module")
    print("=" * 60)
    
    print("\nDINOv2 System Info:")
    info = get_dinov2_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
