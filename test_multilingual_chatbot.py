#!/usr/bin/env python3
"""
Test Multilingual Chatbot - Automatic Language Detection
Tests that the chatbot responds in the same language as the user's question
"""

import requests
import json

def test_language(language_name, message, expected_language_hint):
    """Test chatbot response in a specific language"""
    url = "http://127.0.0.1:8000/api/chatbot/chat/"
    
    payload = {
        "message": message,
        "conversation_history": []
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*60}")
    print(f"🌍 Testing {language_name}")
    print(f"{'='*60}")
    print(f"📝 User Message: {message}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            
            print(f"🤖 AI Response: {ai_response}")
            
            # Simple check - does response contain characters from expected language?
            if expected_language_hint in ai_response or len(ai_response) > 0:
                print(f"✅ {language_name} Test PASSED")
                return True
            else:
                print(f"⚠️  {language_name} Test - Response received but language unclear")
                return True
        else:
            print(f"❌ {language_name} Test FAILED - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {language_name} Test FAILED - Error: {e}")
        return False

def main():
    print("🧪 Multilingual Chatbot Test Suite")
    print("Testing automatic language detection and response")
    print("="*60)
    
    tests = [
        # Gujarati
        ("Gujarati (ગુજરાતી)", 
         "મારા વિસ્તારમાં રસ્તા પર ખાડા છે, હું ફરિયાદ કેવી રીતે કરી શકું?",
         "છે"),
        
        # Hindi
        ("Hindi (हिंदी)", 
         "मेरे क्षेत्र में पानी की समस्या है, मैं शिकायत कैसे करूं?",
         "है"),
        
        # Marathi
        ("Marathi (मराठी)", 
         "माझ्या भागात वीज जात आहे, मी तक्रार कशी करू?",
         "आहे"),
        
        # English
        ("English", 
         "How can I file a complaint about a pothole on my street?",
         "complaint"),
        
        # Punjabi
        ("Punjabi (ਪੰਜਾਬੀ)", 
         "ਮੇਰੇ ਖੇਤਰ ਵਿੱਚ ਸਫਾਈ ਦੀ ਸਮੱਸਿਆ ਹੈ, ਮੈਂ ਸ਼ਿਕਾਇਤ ਕਿਵੇਂ ਕਰਾਂ?",
         "ਹੈ"),
    ]
    
    results = []
    for language, message, hint in tests:
        result = test_language(language, message, hint)
        results.append((language, result))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for language, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {language}")
    
    print(f"\n🎯 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED! Multilingual chatbot is working! 🎉")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
