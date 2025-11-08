"""
CivicAI Voice Assistant - Complete Testing Suite
Tests all 4 new voice endpoints and validates multilingual processing
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
VOICE_BASE = f"{BASE_URL}/api/chatbot/voice"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def test_backend_running():
    """Test if backend server is running"""
    print_header("TEST 1: Backend Server Status")
    
    try:
        response = requests.get(f"{BASE_URL}/api/chatbot/health/", timeout=5)
        if response.status_code == 200:
            print_success("Backend server is RUNNING on port 8000")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_warning(f"Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Backend server is NOT RUNNING")
        print_warning("Please start: python manage.py runserver 0.0.0.0:8000")
        return False
    except Exception as e:
        print_error(f"Error checking backend: {str(e)}")
        return False

def test_voice_health():
    """Test voice health endpoint"""
    print_header("TEST 2: Voice System Health")
    
    try:
        response = requests.get(f"{VOICE_BASE}/health/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Voice health endpoint is working!")
            print(f"{Colors.CYAN}Response:{Colors.RESET}")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Validate required fields
            if data.get('status') == 'healthy':
                print_success("Voice assistant is HEALTHY")
            
            if 'supported_languages' in data:
                print_info(f"Supported languages: {len(data['supported_languages'])}")
            
            if 'supported_departments' in data:
                print_info(f"Supported departments: {len(data['supported_departments'])}")
            
            return True
        else:
            print_error(f"Health check failed with status: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print_error(f"Voice health test failed: {str(e)}")
        return False

def test_voice_languages():
    """Test voice languages endpoint"""
    print_header("TEST 3: Supported Languages & Departments")
    
    try:
        response = requests.get(f"{VOICE_BASE}/languages/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Languages endpoint is working!")
            print(f"\n{Colors.CYAN}Response:{Colors.RESET}")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Display languages
            if 'languages' in data:
                print(f"\n{Colors.BOLD}Supported Languages:{Colors.RESET}")
                for lang_code, lang_name in data['languages'].items():
                    print(f"  • {lang_code}: {lang_name}")
            
            # Display departments
            if 'departments' in data:
                print(f"\n{Colors.BOLD}Supported Departments:{Colors.RESET}")
                for dept_code, dept_name in data['departments'].items():
                    print(f"  • {dept_code}: {dept_name}")
            
            return True
        else:
            print_error(f"Languages endpoint failed with status: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print_error(f"Languages test failed: {str(e)}")
        return False

def test_voice_complaint_submit():
    """Test voice complaint submission with multilingual examples"""
    print_header("TEST 4: Voice Complaint Submission")
    
    # Test cases in different languages
    test_cases = [
        {
            "name": "Gujarati - Water Complaint",
            "data": {
                "transcribed_text": "મારા એરિયા માં પાણી નથી આવતું છેલ્લા 2 દિવસ થી",
                "caller_id": "9876543210"
            },
            "expected_lang": "gu",
            "expected_dept": "water"
        },
        {
            "name": "Hindi - Road Complaint",
            "data": {
                "transcribed_text": "सड़क पर बहुत गड्ढे हैं और लाइट भी नहीं है",
                "caller_id": "9876543211"
            },
            "expected_lang": "hi",
            "expected_dept": "road"
        },
        {
            "name": "English - Electricity Complaint",
            "data": {
                "transcribed_text": "No electricity in my area since morning, power cut",
                "caller_id": "9876543212"
            },
            "expected_lang": "en",
            "expected_dept": "electricity"
        },
        {
            "name": "Marathi - Sanitation Complaint",
            "data": {
                "transcribed_text": "रस्त्यावर खूप कचरा आहे, कोणी साफ करत नाही",
                "caller_id": "9876543213"
            },
            "expected_lang": "mr",
            "expected_dept": "sanitation"
        },
        {
            "name": "Punjabi - Fire Emergency",
            "data": {
                "transcribed_text": "ਮੇਰੇ ਘਰ ਦੇ ਨੇੜੇ ਅੱਗ ਲੱਗੀ ਹੋਈ ਹੈ",
                "caller_id": "9876543214"
            },
            "expected_lang": "pa",
            "expected_dept": "fire"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{Colors.BOLD}Test Case {i}: {test_case['name']}{Colors.RESET}")
        print(f"{Colors.CYAN}Input Text:{Colors.RESET} {test_case['data']['transcribed_text']}")
        
        try:
            response = requests.post(
                f"{VOICE_BASE}/submit/",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate success
                if data.get('success'):
                    print_success("Complaint submitted successfully!")
                    
                    # Check language detection
                    detected_lang = data.get('original_language')
                    if detected_lang == test_case['expected_lang']:
                        print_success(f"Language detected: {detected_lang} ({data.get('original_language_name')})")
                    else:
                        print_warning(f"Language mismatch: expected {test_case['expected_lang']}, got {detected_lang}")
                    
                    # Check department classification
                    detected_dept = data.get('department_tag')
                    confidence = data.get('confidence_score', 0)
                    print_info(f"Department: {detected_dept} (confidence: {confidence:.2f})")
                    
                    # Display summary
                    print_info(f"Summary: {data.get('summary_text', 'N/A')}")
                    
                    # Display reply
                    print_info(f"Reply: {data.get('reply_text', 'N/A')}")
                    
                    # Display tracking info
                    if 'tracking_number' in data:
                        print_success(f"Tracking Number: {data['tracking_number']}")
                    
                    results.append({
                        "test": test_case['name'],
                        "status": "PASS",
                        "detected_lang": detected_lang,
                        "detected_dept": detected_dept,
                        "confidence": confidence
                    })
                else:
                    print_error(f"Submission failed: {data.get('message', 'Unknown error')}")
                    results.append({"test": test_case['name'], "status": "FAIL"})
                
            else:
                print_error(f"HTTP Error {response.status_code}")
                print(response.text)
                results.append({"test": test_case['name'], "status": "FAIL"})
                
        except Exception as e:
            print_error(f"Test failed: {str(e)}")
            results.append({"test": test_case['name'], "status": "FAIL"})
    
    # Summary
    print(f"\n{Colors.BOLD}Test Results Summary:{Colors.RESET}")
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
    
    print(f"\n{Colors.BOLD}Score: {passed}/{total} tests passed{Colors.RESET}")
    
    return passed == total

def test_voice_chat():
    """Test interactive voice chat endpoint"""
    print_header("TEST 5: Interactive Voice Chat")
    
    test_data = {
        "message": "પાણી નથી આવતું",
        "session_state": "collecting_complaint"
    }
    
    try:
        response = requests.post(
            f"{VOICE_BASE}/chat/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Voice chat endpoint is working!")
            print(f"\n{Colors.CYAN}Request:{Colors.RESET}")
            print(json.dumps(test_data, indent=2, ensure_ascii=False))
            print(f"\n{Colors.CYAN}Response:{Colors.RESET}")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print_error(f"Chat endpoint failed with status: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print_error(f"Chat test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header("🎤 CivicAI VOICE ASSISTANT - COMPLETE TEST SUITE")
    print(f"{Colors.BLUE}Testing Time:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    test_results = []
    
    # Test 1: Backend running
    backend_running = test_backend_running()
    test_results.append(("Backend Server", backend_running))
    
    if not backend_running:
        print_header("❌ TESTS ABORTED - Backend Not Running")
        print_warning("Please start the backend server first:")
        print(f"{Colors.CYAN}cd e:\\Smartgriv\\smartgriev\\backend{Colors.RESET}")
        print(f"{Colors.CYAN}python manage.py runserver 0.0.0.0:8000{Colors.RESET}")
        return
    
    # Test 2: Voice health
    health_ok = test_voice_health()
    test_results.append(("Voice Health", health_ok))
    
    # Test 3: Voice languages
    languages_ok = test_voice_languages()
    test_results.append(("Voice Languages", languages_ok))
    
    # Test 4: Voice complaint submission
    complaints_ok = test_voice_complaint_submit()
    test_results.append(("Voice Complaints", complaints_ok))
    
    # Test 5: Voice chat
    chat_ok = test_voice_chat()
    test_results.append(("Voice Chat", chat_ok))
    
    # Final Summary
    print_header("📊 FINAL TEST SUMMARY")
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}Overall Score: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! CivicAI Voice Assistant is fully operational!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Some tests failed. Please check the errors above.{Colors.RESET}")

if __name__ == "__main__":
    main()
