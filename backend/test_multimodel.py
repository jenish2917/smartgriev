"""
Test script for Advanced Multi-Model Image Processing
"""

import os
import sys
import logging
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_test_image():
    """Create a test image with text and objects"""
    logger.info("Creating test image...")
    
    # Create a 800x600 image with some text and shapes
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Add some text
    text = "POTHOLE ON MAIN ROAD"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, (50, 100), font, 1.5, (0, 0, 0), 3)
    
    # Add some shapes to simulate objects
    cv2.rectangle(img, (100, 200), (300, 400), (128, 128, 128), -1)  # Gray rectangle (road)
    cv2.circle(img, (200, 300), 50, (64, 64, 64), -1)  # Dark circle (pothole)
    
    # Add more text
    cv2.putText(img, "URGENT REPAIR NEEDED", (50, 500), font, 1, (255, 0, 0), 2)
    
    # Save the test image
    test_img_path = backend_dir / "test_complaint_image.jpg"
    cv2.imwrite(str(test_img_path), img)
    logger.info(f"✓ Test image created: {test_img_path}")
    
    return str(test_img_path)


def test_advanced_image_processor(image_path):
    """Test the advanced image processor"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Advanced Multi-Model Image Processor")
    logger.info("=" * 60)
    
    try:
        from machine_learning.advanced_image_processor import get_image_processor
        
        # Initialize processor
        logger.info("\nInitializing advanced image processor...")
        processor = get_image_processor()
        
        # Analyze the image
        logger.info(f"\nAnalyzing image: {image_path}")
        result = processor.analyze_image(image_path)
        
        if not result.get('success'):
            logger.error(f"Analysis failed: {result.get('error')}")
            return False
        
        # Display results
        logger.info("\n" + "=" * 60)
        logger.info("ANALYSIS RESULTS")
        logger.info("=" * 60)
        
        logger.info(f"\n📊 Models Used: {', '.join(result.get('models_used', []))}")
        logger.info(f"📐 Image Size: {result.get('image_size', 'Unknown')}")
        
        # YOLO Detection Results
        if 'yolo_detection' in result and result['yolo_detection'].get('success'):
            yolo = result['yolo_detection']
            logger.info(f"\n🎯 YOLO Object Detection:")
            logger.info(f"  Objects Detected: {yolo.get('objects_detected', 0)}")
            logger.info(f"  Object Classes: {', '.join(yolo.get('object_classes', []))}")
            
            for i, obj in enumerate(yolo.get('objects', [])[:5], 1):
                logger.info(f"  {i}. {obj['class']} (confidence: {obj['confidence']:.2f})")
        
        # OCR Results
        if 'ocr_extraction' in result:
            ocr = result['ocr_extraction']
            logger.info(f"\n📝 OCR Text Extraction:")
            logger.info(f"  Text Found: {ocr.get('text_found', False)}")
            logger.info(f"  Methods Used: {', '.join(ocr.get('methods_used', []))}")
            if ocr.get('text_found'):
                text = ocr.get('extracted_text', '')
                logger.info(f"  Extracted Text ({len(text)} chars):")
                for line in text.split('\n')[:5]:
                    if line.strip():
                        logger.info(f"    {line.strip()}")
        
        # Scene Analysis
        if 'scene_analysis' in result and result['scene_analysis'].get('success'):
            scene = result['scene_analysis']
            logger.info(f"\n🏞️ Scene Classification (CLIP):")
            logger.info(f"  Primary Scene: {scene.get('primary_scene', 'Unknown')}")
            logger.info(f"  Confidence: {scene.get('primary_confidence', 0):.2%}")
            
            if 'all_scenes' in scene:
                logger.info(f"  Top Scenes:")
                for i, s in enumerate(scene['all_scenes'][:3], 1):
                    logger.info(f"    {i}. {s['scene']} ({s['confidence']:.2%})")
        
        # ResNet Classification
        if 'image_classification' in result and result['image_classification'].get('success'):
            resnet = result['image_classification']
            logger.info(f"\n🧠 Image Classification (ResNet):")
            logger.info(f"  Primary Class: {resnet.get('primary_class', 'Unknown')}")
            logger.info(f"  Confidence: {resnet.get('confidence', 0):.2%}")
        
        # Complaint Analysis
        if 'complaint_analysis' in result:
            comp = result['complaint_analysis']
            logger.info(f"\n⚠️ Complaint-Specific Analysis:")
            logger.info(f"  Category: {comp.get('category', 'general')}")
            logger.info(f"  Severity: {comp.get('severity', 'low')}")
            logger.info(f"  Damage Detected: {comp.get('damage_detected', False)}")
            logger.info(f"  Waste Detected: {comp.get('waste_detected', False)}")
            logger.info(f"  Infrastructure Issue: {comp.get('infrastructure_issue', False)}")
            if comp.get('keywords'):
                logger.info(f"  Keywords: {', '.join(comp['keywords'])}")
        
        # Image Quality
        if 'image_quality' in result:
            quality = result['image_quality']
            logger.info(f"\n📷 Image Quality Assessment:")
            logger.info(f"  Quality Score: {quality.get('quality_score', 0):.1f}/100")
            logger.info(f"  Sharpness: {quality.get('sharpness', 0):.2f}")
            logger.info(f"  Brightness: {quality.get('brightness', 0):.2f}")
            logger.info(f"  Contrast: {quality.get('contrast', 0):.2f}")
            logger.info(f"  Acceptable: {'Yes' if quality.get('is_acceptable', False) else 'No'}")
        
        # Summary
        if 'summary' in result:
            summary = result['summary']
            logger.info(f"\n📋 Analysis Summary:")
            logger.info(f"  Overall Confidence: {summary.get('overall_confidence', 0):.2%}")
            logger.info(f"  Recommended Category: {summary.get('recommended_category', 'general')}")
            logger.info(f"  Recommended Priority: {summary.get('recommended_priority', 'medium')}")
            
            if summary.get('detected_items'):
                logger.info(f"  Detected Items: {', '.join(summary['detected_items'][:10])}")
            
            if summary.get('extracted_text_summary'):
                logger.info(f"  Text Summary: {summary['extracted_text_summary'][:100]}...")
            
            if summary.get('analysis_notes'):
                logger.info(f"  Notes:")
                for note in summary['analysis_notes']:
                    logger.info(f"    • {note}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Test Completed Successfully!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    logger.info("SmartGriev Advanced Multi-Model Image Processing Test\n")
    
    # Check if test image exists or create one
    test_img = backend_dir / "test_complaint_image.jpg"
    
    if not test_img.exists():
        logger.info("Test image not found. Creating one...")
        image_path = create_test_image()
    else:
        logger.info(f"Using existing test image: {test_img}")
        image_path = str(test_img)
    
    # Run the test
    success = test_advanced_image_processor(image_path)
    
    if success:
        logger.info("\n✅ All tests passed!")
        logger.info("\n💡 The multi-model image processing system is working correctly.")
        logger.info("   It will automatically process complaint images using:")
        logger.info("   - YOLO for object detection")
        logger.info("   - Multiple OCR engines for text extraction")
        logger.info("   - CLIP for scene understanding")
        logger.info("   - ResNet for image classification")
        logger.info("   - Custom complaint analysis")
    else:
        logger.error("\n❌ Tests failed!")
        logger.error("   Please check the error messages above.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
