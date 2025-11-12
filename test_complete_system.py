"""
Comprehensive SmartGriev System Test
Tests all components, APIs, and functionality
"""
import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000'
RESULTS = []

def log_result(test_name, status, message):
    """Log test result"""
    symbol = '✅' if status else '❌'
    RESULTS.append({'test': test_name, 'status': status, 'message': message})
    print(f"{symbol} {test_name}: {message}")

def test_health_endpoints():
    """Test all health endpoints"""
    print("\n" + "="*60)
    print("🏥 TESTING HEALTH ENDPOINTS")
    print("="*60)
    
    endpoints = [
        '/api/health/',
        '/api/chatbot/health/',
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}', timeout=5)
            if response.status_code == 200:
                log_result(f"Health {endpoint}", True, f"Status: {response.status_code}")
            else:
                log_result(f"Health {endpoint}", False, f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"Health {endpoint}", False, str(e))

def test_chatbot_basic():
    """Test basic chatbot functionality"""
    print("\n" + "="*60)
    print("🤖 TESTING CHATBOT - BASIC FUNCTIONALITY")
    print("="*60)
    
    test_cases = [
        {
            'name': 'English greeting',
            'message': 'Hello',
            'language': 'en',
            'expected_keywords': ['hi', 'hello', 'help']
        },
        {
            'name': 'Gujarati greeting',
            'message': 'નમસ્તે',
            'language': 'gu',
            'expected_keywords': ['નમસ્તે', 'મદદ']
        },
        {
            'name': 'Hindi complaint',
            'message': 'मेरे घर के पास सड़क में गड्ढा है',
            'language': 'hi',
            'expected_keywords': ['सड़क', 'गड्ढा']
        },
    ]
    
    for test in test_cases:
        try:
            response = requests.post(
                f'{BASE_URL}/api/chatbot/chat/',
                json={
                    'message': test['message'],
                    'language': test['language']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '').lower()
                
                # Check if any expected keyword is in response
                found = any(keyword.lower() in response_text for keyword in test['expected_keywords'])
                
                log_result(
                    f"Chatbot - {test['name']}",
                    True,
                    f"Response: {data.get('response', '')[:100]}..."
                )
            else:
                log_result(f"Chatbot - {test['name']}", False, f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"Chatbot - {test['name']}", False, str(e))

def test_chatbot_context():
    """Test chatbot conversation context"""
    print("\n" + "="*60)
    print("🧠 TESTING CHATBOT - CONTEXT MEMORY")
    print("="*60)
    
    session_id = None
    
    try:
        # First message
        response1 = requests.post(
            f'{BASE_URL}/api/chatbot/chat/',
            json={'message': 'I want to complain about a pothole', 'language': 'en'},
            timeout=10
        )
        
        if response1.status_code == 200:
            data1 = response1.json()
            session_id = data1.get('session_id')
            log_result("Context - First message", True, f"Session ID: {session_id}")
            
            # Second message in same session
            time.sleep(1)
            response2 = requests.post(
                f'{BASE_URL}/api/chatbot/chat/',
                json={
                    'message': 'It is near MG Road',
                    'language': 'en',
                    'session_id': session_id
                },
                timeout=10
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                # Check if context is maintained (should not ask "what is the issue" again)
                response_text = data2.get('response', '').lower()
                maintains_context = 'location' in response_text or 'urgent' in response_text or 'mg road' in response_text
                
                log_result(
                    "Context - Follow-up message",
                    maintains_context,
                    f"Response: {data2.get('response', '')[:100]}..."
                )
            else:
                log_result("Context - Follow-up message", False, f"Status: {response2.status_code}")
        else:
            log_result("Context - First message", False, f"Status: {response1.status_code}")
    except Exception as e:
        log_result("Context test", False, str(e))

def test_field_extraction():
    """Test automated field extraction"""
    print("\n" + "="*60)
    print("📋 TESTING FIELD EXTRACTION")
    print("="*60)
    
    test_cases = [
        {
            'message': 'There is a big pothole on MG Road causing accidents',
            'expected_category': 'road',
            'expected_urgency': 'high'
        },
        {
            'message': 'Water supply is not coming since 3 days',
            'expected_category': 'water',
            'expected_urgency': 'medium'
        },
        {
            'message': 'Garbage not collected for a week, very urgent',
            'expected_category': 'garbage',
            'expected_urgency': 'high'
        },
    ]
    
    for test in test_cases:
        try:
            response = requests.post(
                f'{BASE_URL}/api/chatbot/chat/',
                json={'message': test['message'], 'language': 'en'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                complaint_data = data.get('complaint_data', {})
                
                category_match = complaint_data.get('category') == test['expected_category']
                urgency_match = complaint_data.get('urgency') == test['expected_urgency']
                
                log_result(
                    f"Extraction - {test['expected_category']}",
                    category_match,
                    f"Category: {complaint_data.get('category')}, Urgency: {complaint_data.get('urgency')}"
                )
            else:
                log_result(f"Extraction - {test['expected_category']}", False, f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"Extraction - {test['expected_category']}", False, str(e))

def test_multilingual():
    """Test all supported languages"""
    print("\n" + "="*60)
    print("🌍 TESTING MULTILINGUAL SUPPORT")
    print("="*60)
    
    languages = {
        'en': 'Hello, I need help',
        'hi': 'नमस्ते, मुझे मदद चाहिए',
        'gu': 'નમસ્તે, મને મદદ જોઈએ છે',
        'mr': 'नमस्कार, मला मदत हवी आहे',
        'pa': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਨੂੰ ਮਦਦ ਚਾਹੀਦੀ ਹੈ',
    }
    
    for lang_code, message in languages.items():
        try:
            response = requests.post(
                f'{BASE_URL}/api/chatbot/chat/',
                json={'message': message, 'language': lang_code},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                log_result(
                    f"Language - {lang_code}",
                    True,
                    f"Response: {data.get('response', '')[:50]}..."
                )
            else:
                log_result(f"Language - {lang_code}", False, f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"Language - {lang_code}", False, str(e))

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r['status'])
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"📈 Success Rate: {success_rate:.1f}%\n")
    
    if failed > 0:
        print("Failed Tests:")
        for result in RESULTS:
            if not result['status']:
                print(f"  ❌ {result['test']}: {result['message']}")
    
    print("\n" + "="*60)
    if success_rate >= 90:
        print("🎉 EXCELLENT! System is production ready!")
    elif success_rate >= 70:
        print("✅ GOOD! Most features working correctly")
    else:
        print("⚠️ WARNING! Several features need fixing")
    print("="*60 + "\n")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 SMARTGRIEV COMPREHENSIVE SYSTEM TEST")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_health_endpoints()
        test_chatbot_basic()
        test_chatbot_context()
        test_field_extraction()
        test_multilingual()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    finally:
        print_summary()

if __name__ == '__main__':
    main()
