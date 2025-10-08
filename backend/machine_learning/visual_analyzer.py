"""
Visual Analysis Module for SmartGriev Multimodal Complaint Analysis

This module handles visual content analysis including:
- Object detection (potholes, garbage, broken pipes, etc.)
- Scene classification (public road, government office, etc.)
- Text extraction from images (street signs, building names, etc.)
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    import torch
    import torchvision
    from torchvision import transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Visual analysis will be limited.")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Import OCR processor from existing module
try:
    from .ocr_processor import get_ocr_processor
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class VisualAnalyzer:
    """
    Handles visual content analysis for complaint videos and images.
    """
    
    # Complaint-related objects to detect
    COMPLAINT_OBJECTS = {
        'infrastructure': ['pothole', 'crack', 'broken_road', 'construction', 'barrier'],
        'cleanliness': ['garbage', 'trash', 'waste', 'dirt', 'litter'],
        'utilities': ['broken_pipe', 'water_leak', 'electrical_wire', 'streetlight'],
        'traffic': ['traffic_cone', 'sign', 'vehicle', 'traffic_light'],
        'general': ['building', 'person', 'tree', 'bench']
    }
    
    # Scene contexts for complaints
    SCENE_CONTEXTS = [
        'public_road',
        'residential_area',
        'government_office',
        'public_park',
        'commercial_area',
        'construction_site',
        'water_body',
        'public_facility'
    ]
    
    def __init__(self):
        """Initialize Visual Analyzer with detection models."""
        self._object_detector = None
        self._scene_classifier = None
        self.fallback_mode = False
        logger.info("VisualAnalyzer initialized")
    
    def detect_objects(self, image_path: str) -> Dict[str, Any]:
        """
        Detect objects in image relevant to complaints.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with detected objects and their locations
        """
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': 'Image file not found'
                }
            
            # Load image
            image = Image.open(image_path)
            
            # Use rule-based detection with OpenCV if available
            detected_objects = []
            
            if CV2_AVAILABLE:
                # Simple color-based and edge detection
                img_cv = cv2.imread(image_path)
                
                # Detect dark patches (potential potholes)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if len(contours) > 0:
                    # Analyze largest contours
                    large_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
                    for contour in large_contours:
                        area = cv2.contourArea(contour)
                        if area > 1000:  # Minimum area threshold
                            x, y, w, h = cv2.boundingRect(contour)
                            detected_objects.append({
                                'object': 'potential_damage',
                                'confidence': 0.6,
                                'bbox': [x, y, w, h],
                                'area': area
                            })
                
                # Detect edges (potential cracks)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                
                if edge_density > 0.1:  # High edge density might indicate cracks
                    detected_objects.append({
                        'object': 'potential_crack',
                        'confidence': 0.5,
                        'edge_density': edge_density
                    })
            
            # Use PyTorch models if available
            if TORCH_AVAILABLE and self._object_detector is None:
                try:
                    # Load pretrained object detection model
                    self._object_detector = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
                    self._object_detector.eval()
                except:
                    pass
            
            ml_detections = []
            if self._object_detector is not None and TORCH_AVAILABLE:
                try:
                    # Preprocess image
                    transform = transforms.Compose([
                        transforms.ToTensor(),
                    ])
                    img_tensor = transform(image).unsqueeze(0)
                    
                    # Detect objects
                    with torch.no_grad():
                        predictions = self._object_detector(img_tensor)
                    
                    # Filter relevant objects
                    if predictions and len(predictions) > 0:
                        pred = predictions[0]
                        boxes = pred['boxes'].cpu().numpy()
                        labels = pred['labels'].cpu().numpy()
                        scores = pred['scores'].cpu().numpy()
                        
                        # COCO labels
                        coco_labels = {
                            1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle',
                            5: 'airplane', 6: 'bus', 7: 'train', 8: 'truck',
                            9: 'boat', 10: 'traffic_light', 11: 'fire_hydrant',
                            13: 'stop_sign', 14: 'parking_meter', 15: 'bench'
                        }
                        
                        for box, label, score in zip(boxes, labels, scores):
                            if score > 0.5:  # Confidence threshold
                                ml_detections.append({
                                    'object': coco_labels.get(label, f'object_{label}'),
                                    'confidence': float(score),
                                    'bbox': box.tolist()
                                })
                except Exception as e:
                    logger.warning(f"ML object detection failed: {str(e)}")
            
            # Combine detections
            all_detections = detected_objects + ml_detections
            
            # Categorize objects
            categorized = self._categorize_objects(all_detections)
            
            return {
                'success': True,
                'detected_objects': all_detections,
                'categorized_objects': categorized,
                'total_objects': len(all_detections),
                'method': 'hybrid' if ml_detections else 'rule-based'
            }
            
        except Exception as e:
            logger.error(f"Object detection error: {str(e)}")
            return {
                'success': False,
                'error': f'Object detection failed: {str(e)}'
            }
    
    def _categorize_objects(self, detections: List[Dict]) -> Dict[str, List[str]]:
        """Categorize detected objects into complaint categories."""
        categorized = {category: [] for category in self.COMPLAINT_OBJECTS.keys()}
        
        for detection in detections:
            obj_name = detection['object']
            
            # Map to categories
            for category, objects in self.COMPLAINT_OBJECTS.items():
                if any(keyword in obj_name.lower() for keyword in objects):
                    categorized[category].append(obj_name)
                    break
            else:
                categorized['general'].append(obj_name)
        
        return {k: list(set(v)) for k, v in categorized.items() if v}
    
    def classify_scene(self, image_path: str) -> Dict[str, Any]:
        """
        Classify the scene context of the image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with scene classification results
        """
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': 'Image file not found'
                }
            
            # Rule-based scene classification using color and texture analysis
            if CV2_AVAILABLE:
                img = cv2.imread(image_path)
                
                # Analyze color distribution
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                
                # Calculate color histograms
                hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
                hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
                hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])
                
                # Determine scene based on color patterns
                avg_brightness = np.mean(hsv[:, :, 2])
                avg_saturation = np.mean(hsv[:, :, 1])
                
                # Simple heuristics
                if avg_brightness < 100:
                    scene = 'indoor_or_night'
                elif avg_saturation < 50:
                    scene = 'urban_road'
                elif avg_saturation > 100:
                    scene = 'outdoor_natural'
                else:
                    scene = 'urban_area'
                
                return {
                    'success': True,
                    'scene_context': scene,
                    'confidence': 0.6,
                    'method': 'rule-based',
                    'features': {
                        'brightness': float(avg_brightness),
                        'saturation': float(avg_saturation)
                    }
                }
            else:
                # Fallback
                return {
                    'success': True,
                    'scene_context': 'unknown',
                    'confidence': 0.3,
                    'method': 'fallback'
                }
                
        except Exception as e:
            logger.error(f"Scene classification error: {str(e)}")
            return {
                'success': False,
                'error': f'Scene classification failed: {str(e)}'
            }
    
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with extracted text
        """
        try:
            if OCR_AVAILABLE:
                ocr_processor = get_ocr_processor()
                result = ocr_processor.extract_text_advanced(
                    Image.open(image_path),
                    preprocess=True
                )
                
                return {
                    'success': True,
                    'extracted_text': result.get('extracted_text', ''),
                    'confidence': result.get('confidence', 0.0),
                    'method': 'ocr'
                }
            else:
                return {
                    'success': True,
                    'extracted_text': '',
                    'confidence': 0.0,
                    'method': 'unavailable'
                }
                
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return {
                'success': False,
                'error': f'Text extraction failed: {str(e)}'
            }
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Comprehensive visual analysis of an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Complete visual analysis results
        """
        try:
            # Detect objects
            object_results = self.detect_objects(image_path)
            
            # Classify scene
            scene_results = self.classify_scene(image_path)
            
            # Extract text
            text_results = self.extract_text(image_path)
            
            return {
                'success': True,
                'objects': object_results,
                'scene': scene_results,
                'text': text_results
            }
            
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Image analysis failed: {str(e)}'
            }
    
    def analyze_frames(self, frame_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple frames and aggregate results.
        
        Args:
            frame_paths: List of paths to frame images
            
        Returns:
            Aggregated visual analysis results
        """
        try:
            all_objects = []
            all_scenes = []
            all_texts = []
            
            for frame_path in frame_paths:
                result = self.analyze_image(frame_path)
                
                if result.get('success'):
                    if result['objects'].get('success'):
                        all_objects.extend(result['objects'].get('detected_objects', []))
                    
                    if result['scene'].get('success'):
                        all_scenes.append(result['scene'].get('scene_context', 'unknown'))
                    
                    if result['text'].get('success'):
                        text = result['text'].get('extracted_text', '')
                        if text:
                            all_texts.append(text)
            
            # Aggregate results
            unique_objects = list({obj['object']: obj for obj in all_objects}.values())
            most_common_scene = max(set(all_scenes), key=all_scenes.count) if all_scenes else 'unknown'
            combined_text = ' '.join(all_texts)
            
            return {
                'success': True,
                'aggregated_objects': unique_objects,
                'dominant_scene': most_common_scene,
                'combined_text': combined_text,
                'frames_analyzed': len(frame_paths)
            }
            
        except Exception as e:
            logger.error(f"Frames analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Frames analysis failed: {str(e)}'
            }


# Global instance
_visual_analyzer = None


def get_visual_analyzer() -> VisualAnalyzer:
    """Get or create global visual analyzer instance."""
    global _visual_analyzer
    if _visual_analyzer is None:
        _visual_analyzer = VisualAnalyzer()
    return _visual_analyzer
