"""
Setup script for Multi-Model Image Processing
Downloads and initializes all required models
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"✓ Python version: {sys.version}")
    return True


def install_requirements():
    """Install required packages"""
    logger.info("Installing required packages...")
    
    req_file = Path(__file__).parent / "requirements_multimodel.txt"
    
    if not req_file.exists():
        logger.error(f"Requirements file not found: {req_file}")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(req_file)
        ])
        logger.info("✓ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install packages: {e}")
        return False


def download_yolo_model():
    """Download YOLO model"""
    logger.info("Downloading YOLO model...")
    
    try:
        from ultralytics import YOLO
        
        # Download YOLOv8 nano model (lightweight)
        model = YOLO('yolov8n.pt')
        logger.info("✓ YOLO model downloaded")
        return True
    except Exception as e:
        logger.error(f"Failed to download YOLO model: {e}")
        return False


def download_clip_model():
    """Download CLIP model"""
    logger.info("Downloading CLIP model...")
    
    try:
        from transformers import CLIPModel, CLIPProcessor
        
        model_name = "openai/clip-vit-base-patch32"
        CLIPModel.from_pretrained(model_name)
        CLIPProcessor.from_pretrained(model_name)
        logger.info("✓ CLIP model downloaded")
        return True
    except Exception as e:
        logger.error(f"Failed to download CLIP model: {e}")
        return False


def download_resnet_model():
    """Download ResNet model"""
    logger.info("Downloading ResNet model...")
    
    try:
        from tensorflow.keras.applications import ResNet50
        
        ResNet50(weights='imagenet')
        logger.info("✓ ResNet model downloaded")
        return True
    except Exception as e:
        logger.error(f"Failed to download ResNet model: {e}")
        return False


def setup_easyocr():
    """Setup EasyOCR"""
    logger.info("Setting up EasyOCR...")
    
    try:
        import easyocr
        
        # Download English and Hindi models
        reader = easyocr.Reader(['en', 'hi'])
        logger.info("✓ EasyOCR models downloaded")
        return True
    except Exception as e:
        logger.error(f"Failed to setup EasyOCR: {e}")
        return False


def check_tesseract():
    """Check if Tesseract OCR is installed"""
    logger.info("Checking Tesseract OCR...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        logger.info(f"✓ Tesseract OCR version: {version}")
        return True
    except Exception as e:
        logger.warning(f"Tesseract not found: {e}")
        logger.warning("Please install Tesseract OCR:")
        logger.warning("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        logger.warning("  Linux: sudo apt-get install tesseract-ocr")
        logger.warning("  macOS: brew install tesseract")
        return False


def test_advanced_processor():
    """Test the advanced image processor"""
    logger.info("Testing advanced image processor...")
    
    try:
        from machine_learning.advanced_image_processor import get_image_processor
        
        processor = get_image_processor()
        logger.info("✓ Advanced image processor initialized")
        logger.info(f"  Models loaded: YOLO={processor.yolo_model is not None}, "
                   f"OCR={processor.ocr_reader is not None}, "
                   f"CLIP={processor.clip_model is not None}, "
                   f"ResNet={processor.resnet_model is not None}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize advanced processor: {e}")
        return False


def main():
    """Main setup function"""
    logger.info("=" * 60)
    logger.info("SmartGriev Multi-Model Image Processing Setup")
    logger.info("=" * 60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing requirements", install_requirements),
        ("Downloading YOLO model", download_yolo_model),
        ("Downloading CLIP model", download_clip_model),
        ("Downloading ResNet model", download_resnet_model),
        ("Setting up EasyOCR", setup_easyocr),
        ("Checking Tesseract OCR", check_tesseract),
        ("Testing advanced processor", test_advanced_processor),
    ]
    
    results = []
    for step_name, step_func in steps:
        logger.info(f"\n{step_name}...")
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            logger.error(f"Error in {step_name}: {e}")
            results.append((step_name, False))
    
    logger.info("\n" + "=" * 60)
    logger.info("Setup Summary")
    logger.info("=" * 60)
    
    for step_name, result in results:
        status = "✓ SUCCESS" if result else "✗ FAILED"
        logger.info(f"{status}: {step_name}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    logger.info(f"\n{success_count}/{total_count} steps completed successfully")
    
    if success_count == total_count:
        logger.info("\n🎉 Setup completed successfully!")
        logger.info("You can now use the advanced multi-model image processing system.")
    else:
        logger.warning("\n⚠️ Setup completed with some warnings.")
        logger.warning("The system will work with available models.")
    
    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
