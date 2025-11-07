"""
Advanced Multi-Model Image Processing for SmartGriev
Combines YOLO, OCR, Scene Detection, and other models for comprehensive analysis
"""

import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import json

logger = logging.getLogger(__name__)

# Import detection models
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("YOLO not available - install with: pip install ultralytics")

# Import OCR
try:
    import pytesseract
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR not available - install with: pip install pytesseract easyocr")

# Import scene classification
try:
    import torch
    from transformers import pipeline, CLIPProcessor, CLIPModel
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None
    CLIPProcessor = None
    CLIPModel = None
    torch = None
    logger.warning(f"Transformers not available: {e}")
except Exception as e:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None
    CLIPProcessor = None
    CLIPModel = None
    torch = None
    logger.warning(f"Failed to import transformers: {e}")

# Import image classification
try:
    import tensorflow
    from tensorflow.keras.applications import ResNet50, VGG16
    # Import image classification
    try:
        import tensorflow
        from tensorflow.keras.applications import ResNet50, VGG16
        from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
        from tensorflow.keras.preprocessing import image as keras_image
        KERAS_AVAILABLE = True
    except ImportError as e:
        KERAS_AVAILABLE = False
        ResNet50 = None
        VGG16 = None
        resnet_preprocess = None
        keras_image = None
        logger.warning(f"Keras/TensorFlow not available: {e}")
    except Exception as e:
        KERAS_AVAILABLE = False
        ResNet50 = None
        VGG16 = None
        resnet_preprocess = None
        keras_image = None
        logger.warning(f"Failed to import TensorFlow: {e}")
    from tensorflow.keras.preprocessing import image as keras_image
    KERAS_AVAILABLE = True
except ImportError as e:
    KERAS_AVAILABLE = False
    ResNet50 = None
    VGG16 = None
    resnet_preprocess = None
    keras_image = None
    logger.warning(f"Keras/TensorFlow not available: {e}")
except Exception as e:
    KERAS_AVAILABLE = False
    ResNet50 = None
    VGG16 = None
    resnet_preprocess = None
    keras_image = None
    logger.warning(f"Failed to import TensorFlow: {e}")


class AdvancedImageProcessor:
    """
    Comprehensive image analysis using multiple models:
    - YOLO: Object detection
    - OCR: Text extraction (Tesseract + EasyOCR)
    - CLIP: Scene understanding
    - ResNet/VGG: Image classification
    - Custom complaint-specific detection
    """
    
    # Complaint-related object categories
    COMPLAINT_OBJECTS = {
        'infrastructure': ['road', 'pothole', 'crack', 'pavement', 'sidewalk', 'bridge'],
        'waste': ['garbage', 'trash', 'waste', 'litter', 'bin', 'dump'],
        'water': ['water', 'pipe', 'leak', 'flood', 'drain', 'sewer'],
        'electrical': ['wire', 'pole', 'light', 'cable', 'transformer'],
        'traffic': ['car', 'traffic light', 'sign', 'barrier', 'vehicle'],
        'environment': ['tree', 'plant', 'smoke', 'fire', 'pollution'],
        'construction': ['construction', 'building', 'excavation', 'debris']
    }
    
    def __init__(self):
        """Initialize all available models"""
        self.yolo_model = None
        self.ocr_reader = None
        self.clip_model = None
        self.clip_processor = None
        self.resnet_model = None
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Load all available AI models"""
        try:
            # Initialize YOLO
            if YOLO_AVAILABLE:
                logger.info("Loading YOLO model...")
                self.yolo_model = YOLO('yolov8n.pt')  # Using YOLOv8 nano for speed
                logger.info("✓ YOLO model loaded")
            
            # Initialize OCR
            if OCR_AVAILABLE:
                logger.info("Loading OCR models...")
                self.ocr_reader = easyocr.Reader(['en', 'hi'])  # English and Hindi
                logger.info("✓ OCR models loaded")
            
            # Initialize CLIP for scene understanding
            if TRANSFORMERS_AVAILABLE:
                logger.info("Loading CLIP model...")
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                logger.info("✓ CLIP model loaded")
            
            # Initialize ResNet for classification
            if KERAS_AVAILABLE:
                logger.info("Loading ResNet model...")
                self.resnet_model = ResNet50(weights='imagenet')
                logger.info("✓ ResNet model loaded")
            
            logger.info("Advanced Image Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization error: {str(e)}")
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive image analysis using all available models
        
        Args:
            image_path: Path to image file
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Starting comprehensive image analysis: {image_path}")
        
        try:
            # Load image
            if not os.path.exists(image_path):
                return {'success': False, 'error': 'Image file not found'}
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return {'success': False, 'error': 'Failed to read image'}
            
            pil_img = Image.open(image_path)
            
            results = {
                'success': True,
                'image_path': image_path,
                'image_size': img.shape[:2],
                'models_used': []
            }
            
            # 1. YOLO Object Detection
            if self.yolo_model:
                logger.info("Running YOLO detection...")
                yolo_results = self._run_yolo_detection(image_path)
                results['yolo_detection'] = yolo_results
                results['models_used'].append('YOLOv8')
            
            # 2. OCR Text Extraction (Multiple methods)
            logger.info("Running OCR extraction...")
            ocr_results = self._run_ocr_extraction(img, pil_img)
            results['ocr_extraction'] = ocr_results
            results['models_used'].append('OCR')
            
            # 3. Scene Classification
            if self.clip_model:
                logger.info("Running scene classification...")
                scene_results = self._classify_scene(pil_img)
                results['scene_analysis'] = scene_results
                results['models_used'].append('CLIP')
            
            # 4. ResNet Classification
            if self.resnet_model:
                logger.info("Running ResNet classification...")
                resnet_results = self._classify_with_resnet(image_path)
                results['image_classification'] = resnet_results
                results['models_used'].append('ResNet50')
            
            # 5. Complaint-Specific Analysis
            logger.info("Running complaint-specific analysis...")
            complaint_analysis = self._analyze_for_complaints(results)
            results['complaint_analysis'] = complaint_analysis
            
            # 6. Quality Assessment
            quality = self._assess_image_quality(img)
            results['image_quality'] = quality
            
            # 7. Generate Summary
            summary = self._generate_analysis_summary(results)
            results['summary'] = summary
            
            logger.info("Image analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def _run_yolo_detection(self, image_path: str) -> Dict[str, Any]:
        """Run YOLO object detection"""
        if not YOLO_AVAILABLE or not self.yolo_model:
            return {'success': False, 'error': 'YOLO model not available'}
            
        try:
            results = self.yolo_model(image_path)
            
            detected_objects = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    obj = {
                        'class': result.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'bbox': box.xyxy[0].tolist()
                    }
                    detected_objects.append(obj)
            
            return {
                'success': True,
                'objects_detected': len(detected_objects),
                'objects': detected_objects,
                'object_classes': list(set([obj['class'] for obj in detected_objects]))
            }
        except Exception as e:
            logger.error(f"YOLO detection error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_ocr_extraction(self, cv_img, pil_img) -> Dict[str, Any]:
        """Extract text using multiple OCR methods"""
        extracted_texts = []
        methods_used = []
        
        # Method 1: EasyOCR
        if self.ocr_reader:
            try:
                easy_results = self.ocr_reader.readtext(cv_img)
                easy_text = ' '.join([text[1] for text in easy_results])
                if easy_text.strip():
                    extracted_texts.append(easy_text)
                    methods_used.append('EasyOCR')
            except Exception as e:
                logger.warning(f"EasyOCR failed: {str(e)}")
        
        # Method 2: Tesseract
        try:
            tess_text = pytesseract.image_to_string(pil_img)
            if tess_text.strip():
                extracted_texts.append(tess_text)
                methods_used.append('Tesseract')
        except Exception as e:
            logger.warning(f"Tesseract failed: {str(e)}")
        
        # Method 3: Tesseract with preprocessing
        try:
            # Preprocess image for better OCR
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            tess_enhanced = pytesseract.image_to_string(thresh)
            if tess_enhanced.strip() and tess_enhanced not in extracted_texts:
                extracted_texts.append(tess_enhanced)
                methods_used.append('Tesseract-Enhanced')
        except Exception as e:
            logger.warning(f"Enhanced Tesseract failed: {str(e)}")
        
        # Combine all extracted text
        combined_text = '\n'.join(extracted_texts)
        
        return {
            'success': True,
            'text_found': bool(combined_text.strip()),
            'extracted_text': combined_text.strip(),
            'methods_used': methods_used,
            'text_length': len(combined_text.strip())
        }
    
    def _classify_scene(self, pil_img) -> Dict[str, Any]:
        """Classify scene using CLIP model"""
        if not TRANSFORMERS_AVAILABLE or not self.clip_model:
            return {'success': False, 'error': 'CLIP model not available'}
            
        try:
            # Complaint-related scene categories
            scene_categories = [
                "damaged road with potholes",
                "garbage and waste dumping",
                "water leakage and flooding",
                "broken street light",
                "illegal construction",
                "traffic congestion",
                "tree cutting or damage",
                "public property damage",
                "cleanliness issue",
                "infrastructure problem"
            ]
            
            inputs = self.clip_processor(
                text=scene_categories,
                images=pil_img,
                return_tensors="pt",
                padding=True
            )
            
            outputs = self.clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            
            # Get top 3 scenes
            top_probs, top_indices = torch.topk(probs[0], k=3)
            
            scenes = []
            for prob, idx in zip(top_probs, top_indices):
                scenes.append({
                    'scene': scene_categories[idx],
                    'confidence': float(prob)
                })
            
            return {
                'success': True,
                'primary_scene': scenes[0]['scene'],
                'primary_confidence': scenes[0]['confidence'],
                'all_scenes': scenes
            }
        except Exception as e:
            logger.error(f"Scene classification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _classify_with_resnet(self, image_path: str) -> Dict[str, Any]:
        """Classify image using ResNet"""
        if not KERAS_AVAILABLE or not self.resnet_model:
            return {'success': False, 'error': 'ResNet model not available'}
            
        try:
            img = keras_image.load_img(image_path, target_size=(224, 224))
            img_array = keras_image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = resnet_preprocess(img_array)
            
            predictions = self.resnet_model.predict(img_array)
            
            from tensorflow.keras.applications.resnet50 import decode_predictions
            decoded = decode_predictions(predictions, top=5)[0]
            
            classifications = []
            for pred in decoded:
                classifications.append({
                    'class': pred[1],
                    'description': pred[1].replace('_', ' '),
                    'confidence': float(pred[2])
                })
            
            return {
                'success': True,
                'primary_class': classifications[0]['description'],
                'confidence': classifications[0]['confidence'],
                'all_classes': classifications
            }
        except Exception as e:
            logger.error(f"ResNet classification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_for_complaints(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image specifically for complaint-related content"""
        complaint_indicators = {
            'damage_detected': False,
            'waste_detected': False,
            'infrastructure_issue': False,
            'environmental_issue': False,
            'severity': 'low',
            'category': 'general',
            'keywords': []
        }
        
        # Extract detected objects
        detected_objects = []
        if 'yolo_detection' in analysis_results and analysis_results['yolo_detection'].get('success'):
            detected_objects = analysis_results['yolo_detection'].get('object_classes', [])
        
        # Extract text keywords
        text_keywords = []
        if 'ocr_extraction' in analysis_results:
            text = analysis_results['ocr_extraction'].get('extracted_text', '').lower()
            text_keywords = text.split()
        
        # Check for complaint categories
        for category, keywords in self.COMPLAINT_OBJECTS.items():
            for keyword in keywords:
                # Check in detected objects
                if any(keyword in obj.lower() for obj in detected_objects):
                    complaint_indicators['keywords'].append(keyword)
                    complaint_indicators['category'] = category
                
                # Check in OCR text
                if any(keyword in word for word in text_keywords):
                    complaint_indicators['keywords'].append(keyword)
                    if complaint_indicators['category'] == 'general':
                        complaint_indicators['category'] = category
        
        # Determine severity based on keywords and scene
        severity_keywords = ['broken', 'damaged', 'critical', 'urgent', 'danger', 'leak', 'flood']
        severity_count = sum(1 for kw in severity_keywords if kw in ' '.join(text_keywords))
        
        if severity_count >= 3:
            complaint_indicators['severity'] = 'critical'
        elif severity_count >= 2:
            complaint_indicators['severity'] = 'high'
        elif severity_count >= 1:
            complaint_indicators['severity'] = 'medium'
        
        # Set flags
        complaint_indicators['damage_detected'] = complaint_indicators['category'] == 'infrastructure'
        complaint_indicators['waste_detected'] = complaint_indicators['category'] == 'waste'
        complaint_indicators['infrastructure_issue'] = complaint_indicators['category'] in ['infrastructure', 'construction']
        complaint_indicators['environmental_issue'] = complaint_indicators['category'] == 'environment'
        
        return complaint_indicators
    
    def _assess_image_quality(self, img) -> Dict[str, Any]:
        """Assess image quality metrics"""
        try:
            # Calculate sharpness (Laplacian variance)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate contrast
            contrast = np.std(gray)
            
            # Determine quality score (0-100)
            quality_score = min(100, (sharpness / 1000 * 50) + (contrast / 64 * 30) + 20)
            
            return {
                'sharpness': float(sharpness),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'quality_score': float(quality_score),
                'is_acceptable': quality_score > 40
            }
        except Exception as e:
            logger.error(f"Quality assessment error: {str(e)}")
            return {'quality_score': 0, 'is_acceptable': False}
    
    def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable summary of analysis"""
        summary = {
            'overall_confidence': 0.0,
            'detected_items': [],
            'extracted_text_summary': '',
            'recommended_category': 'general',
            'recommended_priority': 'medium',
            'analysis_notes': []
        }
        
        # Collect all detected items
        if results.get('yolo_detection', {}).get('success'):
            yolo_objects = results['yolo_detection'].get('object_classes', [])
            summary['detected_items'].extend(yolo_objects)
        
        if results.get('ocr_extraction', {}).get('text_found'):
            text = results['ocr_extraction'].get('extracted_text', '')
            summary['extracted_text_summary'] = text[:200] + ('...' if len(text) > 200 else '')
        
        # Get complaint analysis
        if 'complaint_analysis' in results:
            comp_analysis = results['complaint_analysis']
            summary['recommended_category'] = comp_analysis.get('category', 'general')
            
            severity = comp_analysis.get('severity', 'low')
            priority_map = {'critical': 'urgent', 'high': 'high', 'medium': 'medium', 'low': 'low'}
            summary['recommended_priority'] = priority_map.get(severity, 'medium')
        
        # Add analysis notes
        if results.get('image_quality', {}).get('quality_score', 0) > 70:
            summary['analysis_notes'].append('High quality image')
        
        if len(summary['detected_items']) > 5:
            summary['analysis_notes'].append('Multiple objects detected')
        
        if summary['extracted_text_summary']:
            summary['analysis_notes'].append('Text content found in image')
        
        # Calculate overall confidence
        confidences = []
        if results.get('yolo_detection', {}).get('success'):
            avg_yolo_conf = np.mean([obj['confidence'] for obj in results['yolo_detection'].get('objects', [])])
            if not np.isnan(avg_yolo_conf):
                confidences.append(avg_yolo_conf)
        
        if results.get('scene_analysis', {}).get('success'):
            confidences.append(results['scene_analysis'].get('primary_confidence', 0))
        
        if confidences:
            summary['overall_confidence'] = float(np.mean(confidences))
        
        return summary


# Global instance
_image_processor = None


def get_image_processor() -> AdvancedImageProcessor:
    """Get or create global image processor instance"""
    global _image_processor
    if _image_processor is None:
        _image_processor = AdvancedImageProcessor()
    return _image_processor
