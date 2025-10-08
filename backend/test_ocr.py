#!/usr/bin/env python
"""
Test script for OCR functionality in SmartGriev backend.

This script tests the OCR endpoints by creating a test image with text
and sending it to the OCR API endpoints.
"""

import os
import sys
import django
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Add the backend directory to the Python path
sys.path.append('E:/Smartgriv/smartgriev/backend')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def create_test_image():
    """Create a simple test image with text."""
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    
    # Get a drawing context
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Add text to the image
    text = "This is a test complaint.\nPlease process this text."
    draw.text((20, 50), text, fill='black', font=font)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def get_or_create_test_user():
    """Get or create a test user and return a JWT token."""
    username = 'test_ocr_user'
    email = 'test@smartgriev.com'
    password = 'testpass123'
    
    # Get or create user
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_active': True}
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"Created test user: {username}")
    else:
        print(f"Using existing test user: {username}")
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    return access_token

def test_ocr_health():
    """Test the OCR health endpoint."""
    print("\n" + "="*50)
    print("Testing OCR Health Endpoint")
    print("="*50)
    
    # Get JWT token
    token = get_or_create_test_user()
    
    # Test health endpoint
    url = "http://127.0.0.1:8000/api/ml/ocr/health/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Health Check Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_ocr_process():
    """Test the OCR image processing endpoint."""
    print("\n" + "="*50)
    print("Testing OCR Image Processing")
    print("="*50)
    
    # Get JWT token
    token = get_or_create_test_user()
    
    # Create test image
    print("Creating test image...")
    img_bytes = create_test_image()
    
    # Test OCR processing endpoint
    url = "http://127.0.0.1:8000/api/ml/ocr/"
    headers = {"Authorization": f"Bearer {token}"}
    files = {"image": ("test_image.png", img_bytes, "image/png")}
    
    try:
        print("Sending image to OCR endpoint...")
        response = requests.post(url, headers=headers, files=files)
        print(f"OCR Processing Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Extracted Text: '{result.get('extracted_text', 'No text found')}'")
            print(f"Text Length: {result.get('text_length', 0)} characters")
            print(f"Processing Time: {result.get('processing_time', 0):.2f} seconds")
            print(f"Status: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"OCR processing failed: {e}")
        return False

def test_complaint_ocr():
    """Test the complaint OCR endpoint with NLP processing."""
    print("\n" + "="*50)
    print("Testing Complaint OCR with NLP")
    print("="*50)
    
    # Get JWT token
    token = get_or_create_test_user()
    
    # Create test image
    print("Creating test complaint image...")
    img_bytes = create_test_image()
    
    # Test complaint OCR endpoint
    url = "http://127.0.0.1:8000/api/ml/ocr/complaint/"
    headers = {"Authorization": f"Bearer {token}"}
    files = {"image": ("complaint_image.png", img_bytes, "image/png")}
    data = {
        "extract_entities": True,
        "classify_complaint": True
    }
    
    try:
        print("Sending image to complaint OCR endpoint...")
        response = requests.post(url, headers=headers, files=files, data=data)
        print(f"Complaint OCR Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Extracted Text: '{result.get('extracted_text', 'No text found')}'")
            print(f"Text Length: {result.get('text_length', 0)} characters")
            print(f"Processing Time: {result.get('processing_time', 0):.2f} seconds")
            print(f"Status: {result.get('status', 'unknown')}")
            
            # Show NLP results if available
            if 'entities' in result:
                print(f"Entities: {result['entities']}")
            if 'classification' in result:
                print(f"Classification: {result['classification']}")
            if 'sentiment' in result:
                print(f"Sentiment: {result['sentiment']}")
            
            return True
        else:
            print(f"Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Complaint OCR processing failed: {e}")
        return False

def main():
    """Run all OCR tests."""
    print("SmartGriev OCR Testing Suite")
    print("=" * 60)
    
    # Test results
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_ocr_health()))
    
    # Test 2: Basic OCR Processing
    results.append(("Basic OCR", test_ocr_process()))
    
    # Test 3: Complaint OCR with NLP
    results.append(("Complaint OCR", test_complaint_ocr()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print(f"\nTests Passed: {passed}/{len(results)}")
    print("="*60)
    
    if passed == len(results):
        print("🎉 All OCR tests passed! The OCR system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    print("\nOCR API Endpoints:")
    print("- Health Check: GET  /api/ml/ocr/health/")
    print("- Basic OCR:    POST /api/ml/ocr/")
    print("- Complaint OCR: POST /api/ml/ocr/complaint/")
    print("\nNote: All endpoints require JWT authentication.")

if __name__ == "__main__":
    main()