"""
Test suite for Voice & Vision AI Features (Feature 10)
Tests image analysis, video analysis, audio transcription, and multimodal APIs
"""

import os
import sys
import django
import json

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from complaints.services import get_vision_service, get_audio_service


def test_vision_service():
    """Test Gemini Vision Service initialization"""
    print("\n🔍 Testing Vision Service...")
    try:
        vision_service = get_vision_service()
        print(f"✅ Vision service initialized: {vision_service.model._model_name}")
        print(f"   Supported image formats: {', '.join(vision_service.SUPPORTED_IMAGE_FORMATS)}")
        print(f"   Supported video formats: {', '.join(vision_service.SUPPORTED_VIDEO_FORMATS)}")
        print(f"   Max image size: {vision_service.MAX_IMAGE_SIZE_MB}MB")
        print(f"   Max video size: {vision_service.MAX_VIDEO_SIZE_MB}MB")
        return True
    except Exception as e:
        print(f"❌ Vision service initialization failed: {str(e)}")
        return False


def test_audio_service():
    """Test Audio Transcription Service initialization"""
    print("\n🎙️ Testing Audio Service...")
    try:
        audio_service = get_audio_service()
        print(f"✅ Audio service initialized: {audio_service.model._model_name}")
        print(f"   Supported audio formats: {', '.join(audio_service.SUPPORTED_AUDIO_FORMATS)}")
        print(f"   Max audio size: {audio_service.MAX_AUDIO_SIZE_MB}MB")
        print(f"   Max audio duration: {audio_service.MAX_AUDIO_DURATION}s")
        print(f"   Supported languages: {len(audio_service.SUPPORTED_LANGUAGES)} languages")
        print(f"   Languages: {', '.join(audio_service.SUPPORTED_LANGUAGES.values())}")
        return True
    except Exception as e:
        print(f"❌ Audio service initialization failed: {str(e)}")
        return False


def test_image_validation():
    """Test image file validation"""
    print("\n📸 Testing Image Validation...")
    try:
        vision_service = get_vision_service()
        
        # Test with non-existent file
        result = vision_service._validate_image("nonexistent.jpg")
        if not result['valid']:
            print(f"✅ Correctly rejects non-existent file: {result['error']}")
        else:
            print(f"❌ Should reject non-existent file")
            return False
        
        # Test with unsupported format
        result = vision_service._validate_image("test.gif")
        if not result['valid']:
            print(f"✅ Correctly rejects unsupported format: {result['error']}")
        else:
            print(f"❌ Should reject unsupported format")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Image validation test failed: {str(e)}")
        return False


def test_audio_validation():
    """Test audio file validation"""
    print("\n🔊 Testing Audio Validation...")
    try:
        audio_service = get_audio_service()
        
        # Test with non-existent file
        result = audio_service._validate_audio("nonexistent.mp3")
        if not result['valid']:
            print(f"✅ Correctly rejects non-existent file: {result['error']}")
        else:
            print(f"❌ Should reject non-existent file")
            return False
        
        # Test with unsupported format
        result = audio_service._validate_audio("test.xyz")
        if not result['valid']:
            print(f"✅ Correctly rejects unsupported format: {result['error']}")
        else:
            print(f"❌ Should reject unsupported format")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Audio validation test failed: {str(e)}")
        return False


def test_api_endpoints():
    """Test Voice & Vision API endpoints availability"""
    print("\n🌐 Testing API Endpoints...")
    from django.urls import resolve, reverse
    from django.conf import settings
    
    try:
        endpoints = [
            ('analyze-image', 'POST /api/complaints/analyze/image/'),
            ('analyze-multi-image', 'POST /api/complaints/analyze/multi-image/'),
            ('analyze-video', 'POST /api/complaints/analyze/video/'),
            ('transcribe-audio', 'POST /api/complaints/analyze/audio/transcribe/'),
            ('analyze-voice-complaint', 'POST /api/complaints/analyze/audio/complete/'),
            ('analyze-multimodal', 'POST /api/complaints/analyze/multimodal/'),
        ]
        
        all_ok = True
        for name, description in endpoints:
            try:
                url = reverse(name)
                print(f"✅ {description} -> {url}")
            except Exception as e:
                print(f"❌ {description} -> Not found: {str(e)}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        return False


def test_response_parsing():
    """Test vision/audio response parsing"""
    print("\n📄 Testing Response Parsing...")
    try:
        vision_service = get_vision_service()
        audio_service = get_audio_service()
        
        # Test vision response parsing with JSON
        json_response = '''
        {
            "issue_type": "Pothole",
            "severity": "High",
            "description": "Large pothole on main road",
            "detected_objects": ["road", "pothole", "vehicle"],
            "location_context": "main road",
            "suggested_department": "Roads",
            "urgency": "high",
            "key_observations": ["deep pothole", "safety hazard"]
        }
        '''
        
        result = vision_service._parse_vision_response(json_response)
        if result.get('issue_type') == 'Pothole':
            print(f"✅ Vision JSON parsing works: {result.get('issue_type')}")
        else:
            print(f"❌ Vision JSON parsing failed: {result}")
            return False
        
        # Test audio response parsing
        audio_json = '''
        {
            "transcription": "There is no water supply in our area",
            "language": "en",
            "issue_type": "Water Shortage",
            "sentiment": "negative",
            "urgency": "high",
            "suggested_department": "Water Supply"
        }
        '''
        
        result = audio_service._parse_analysis_response(audio_json)
        if result.get('issue_type') == 'Water Shortage':
            print(f"✅ Audio JSON parsing works: {result.get('issue_type')}")
        else:
            print(f"❌ Audio JSON parsing failed: {result}")
            return False
        
        # Test fallback for non-JSON response
        plain_text = "This is a plain text response without JSON"
        result = vision_service._parse_vision_response(plain_text)
        if result.get('description') == plain_text:
            print(f"✅ Fallback parsing works for non-JSON responses")
        else:
            print(f"❌ Fallback parsing failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Response parsing test failed: {str(e)}")
        return False


def test_prompt_generation():
    """Test prompt generation for vision and audio"""
    print("\n💬 Testing Prompt Generation...")
    try:
        vision_service = get_vision_service()
        audio_service = get_audio_service()
        
        # Test image analysis prompt
        prompt = vision_service._create_image_analysis_prompt("broken streetlight")
        if "civic complaint" in prompt.lower() and "JSON" in prompt:
            print(f"✅ Image analysis prompt generated correctly")
        else:
            print(f"❌ Image analysis prompt missing required content")
            return False
        
        # Test video analysis prompt
        prompt = vision_service._create_video_analysis_prompt("garbage accumulation")
        if "video" in prompt.lower() and "timeline" in prompt.lower():
            print(f"✅ Video analysis prompt generated correctly")
        else:
            print(f"❌ Video analysis prompt missing required content")
            return False
        
        # Test multi-image prompt
        prompt = vision_service._create_multi_image_analysis_prompt("road damage", 3)
        if "3 images" in prompt and "combine" in prompt.lower():
            print(f"✅ Multi-image analysis prompt generated correctly")
        else:
            print(f"❌ Multi-image analysis prompt missing required content")
            return False
        
        # Test transcription prompt
        prompt = audio_service._create_transcription_prompt("hi", "complaint about water")
        if "Hindi" in prompt and "transcribe" in prompt.lower():
            print(f"✅ Transcription prompt generated correctly")
        else:
            print(f"❌ Transcription prompt missing required content")
            return False
        
        # Test analysis prompt
        prompt = audio_service._create_analysis_prompt("ta")
        if "Tamil" in prompt and "comprehensive" in prompt.lower():
            print(f"✅ Analysis prompt generated correctly")
        else:
            print(f"❌ Analysis prompt missing required content")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Prompt generation test failed: {str(e)}")
        return False


def test_configuration():
    """Test service configuration and API key"""
    print("\n⚙️ Testing Configuration...")
    try:
        from django.conf import settings
        
        # Check environment variable first
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if api_key:
            print(f"✅ GOOGLE_AI_API_KEY configured (environment)")
            print(f"   Key length: {len(api_key)} characters")
            print(f"   Key prefix: {api_key[:10]}...")
        else:
            # Check Django settings
            api_key = getattr(settings, 'GOOGLE_AI_API_KEY', None) or getattr(settings, 'GEMINI_API_KEY', None)
            if api_key:
                print(f"✅ GOOGLE_AI_API_KEY configured (Django settings)")
                print(f"   Key length: {len(api_key)} characters")
                print(f"   Key prefix: {api_key[:10]}...")
            else:
                print(f"❌ GOOGLE_AI_API_KEY not found in environment or Django settings")
                return False
        
        # Test service initialization with API key
        try:
            vision_service = get_vision_service()
            audio_service = get_audio_service()
            print(f"✅ Services initialized with API key")
            return True
        except Exception as e:
            print(f"❌ Service initialization failed: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("SMARTGRIEV - VOICE & VISION AI TESTS (FEATURE 10)")
    print("="*60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Vision Service", test_vision_service),
        ("Audio Service", test_audio_service),
        ("Image Validation", test_image_validation),
        ("Audio Validation", test_audio_validation),
        ("API Endpoints", test_api_endpoints),
        ("Response Parsing", test_response_parsing),
        ("Prompt Generation", test_prompt_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Voice & Vision AI tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
    
    print("="*60)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
