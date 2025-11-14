"""
Multilingual Department Classification Test
Tests classification accuracy across different languages
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

# Admin credentials
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

# Test cases in multiple languages
# Format: (expected_dept, complaint_text, language_code, language_name)
MULTILINGUAL_TEST_CASES = [
    # English
    ("Road & Transportation", "Large pothole on Main Street causing accidents", "en", "English"),
    ("Water Supply & Sewerage", "Water supply broken, no water for days", "en", "English"),
    
    # Hindi (हिंदी)
    ("Road & Transportation", "मुख्य सड़क पर बड़ा गड्ढा है जो दुर्घटना का कारण बन रहा है", "hi", "Hindi"),
    ("Water Supply & Sewerage", "पानी की आपूर्ति बंद है, कई दिनों से पानी नहीं आ रहा", "hi", "Hindi"),
    ("Sanitation & Cleanliness", "कचरा नहीं उठाया जा रहा है, गंदगी बहुत है", "hi", "Hindi"),
    
    # Gujarati (ગુજરાતી)
    ("Road & Transportation", "મુખ્ય રસ્તા પર મોટો ખાડો છે જે અકસ્માતનું કારણ બની રહ્યો છે", "gu", "Gujarati"),
    ("Electricity Board", "વીજળી બંધ છે, ટ્રાન્સફોર્મર કામ નથી કરતું", "gu", "Gujarati"),
    ("Sanitation & Cleanliness", "કચરો ઉપાડવામાં આવતો નથી, ગંદકી ઘણી છે", "gu", "Gujarati"),
    
    # Marathi (मराठी)
    ("Road & Transportation", "मुख्य रस्त्यावर मोठा खड्डा आहे ज्यामुळे अपघात होत आहेत", "mr", "Marathi"),
    ("Water Supply & Sewerage", "पाणीपुरवठा बंद आहे, अनेक दिवसांपासून पाणी नाही", "mr", "Marathi"),
    
    # Tamil (தமிழ்)
    ("Road & Transportation", "முக்கிய சாலையில் பெரிய குழி உள்ளது விபத்துக்கு காரணமாகிறது", "ta", "Tamil"),
    ("Electricity Board", "மின்சாரம் இல்லை, மின்மாற்றி வேலை செய்யவில்லை", "ta", "Tamil"),
    
    # Telugu (తెలుగు)
    ("Road & Transportation", "ప్రధాన రోడ్డుపై పెద్ద గొయ్యి ఉంది ప్రమాదాలకు కారణమవుతోంది", "te", "Telugu"),
    ("Sanitation & Cleanliness", "చెత్తను తీసుకోవడం లేదు, చాలా మురికిగా ఉంది", "te", "Telugu"),
    
    # Bengali (বাংলা)
    ("Road & Transportation", "প্রধান রাস্তায় বড় গর্ত আছে যা দুর্ঘটনার কারণ হচ্ছে", "bn", "Bengali"),
    ("Water Supply & Sewerage", "জল সরবরাহ বন্ধ আছে, অনেক দিন ধরে জল নেই", "bn", "Bengali"),
]


def test_multilingual_classification():
    print("=" * 80)
    print("MULTILINGUAL DEPARTMENT CLASSIFICATION TEST")
    print("Testing classification accuracy across different Indian languages")
    print("=" * 80)
    
    # Login
    print("\n1. Logging in...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=LOGIN_DATA)
        token = response.json()['access']
        headers = {"Authorization": f"Bearer {token}"}
        print("[OK] Logged in")
    except Exception as e:
        print(f"[FAIL] Login failed: {e}")
        return
    
    # Test each complaint in different languages
    print(f"\n2. Testing {len(MULTILINGUAL_TEST_CASES)} complaints in multiple languages...\n")
    
    correct = 0
    incorrect = 0
    errors = 0
    
    results_by_language = {}
    
    for expected_dept, complaint_text, lang_code, lang_name in MULTILINGUAL_TEST_CASES:
        if lang_name not in results_by_language:
            results_by_language[lang_name] = {'correct': 0, 'total': 0}
        
        results_by_language[lang_name]['total'] += 1
        
        try:
            # Start conversation in the specified language
            session_resp = requests.post(
                f"{BASE_URL}/chatbot/gemini/start/",
                json={"language": lang_code},
                timeout=10
            )
            session_id = session_resp.json()["session_id"]
            time.sleep(1)
            
            # Send complaint in native language
            requests.post(
                f"{BASE_URL}/chatbot/gemini/chat/",
                json={"message": complaint_text, "session_id": session_id, "language": lang_code},
                timeout=10
            )
            time.sleep(1)
            
            # Add location
            location_texts = {
                'en': 'Surat, Gujarat',
                'hi': 'सूरत, गुजरात',
                'gu': 'સુરત, ગુજરાત',
                'mr': 'सूरत, गुजरात',
                'ta': 'சூரத், குஜராத்',
                'te': 'సూరత్, గుజరాత్',
                'bn': 'সুরাট, গুজরাট'
            }
            requests.post(
                f"{BASE_URL}/chatbot/gemini/chat/",
                json={"message": location_texts.get(lang_code, "Surat"), "session_id": session_id, "language": lang_code},
                timeout=10
            )
            time.sleep(1)
            
            # Add urgency
            urgency_texts = {
                'en': 'urgent',
                'hi': 'तत्काल',
                'gu': 'તાત્કાલિક',
                'mr': 'तातडीचे',
                'ta': 'அவசரம்',
                'te': 'అత్యవసరం',
                'bn': 'জরুরি'
            }
            requests.post(
                f"{BASE_URL}/chatbot/gemini/chat/",
                json={"message": urgency_texts.get(lang_code, "urgent"), "session_id": session_id, "language": lang_code},
                timeout=10
            )
            time.sleep(1)
            
            # Create complaint
            create_resp = requests.post(
                f"{BASE_URL}/chatbot/gemini/create-complaint/",
                json={"session_id": session_id, "confirm": True},
                headers=headers,
                timeout=15
            )
            
            if create_resp.status_code == 201:
                complaint_id = create_resp.json()["complaint_id"]
                
                # Verify department
                verify_resp = requests.get(
                    f"{BASE_URL}/complaints/{complaint_id}/",
                    headers=headers,
                    timeout=5
                )
                actual_dept = verify_resp.json()["department"]["name"]
                
                if actual_dept == expected_dept:
                    correct += 1
                    results_by_language[lang_name]['correct'] += 1
                    print(f"[OK] {lang_name:10} | {expected_dept[:30]:30} -> {actual_dept}")
                else:
                    incorrect += 1
                    print(f"[FAIL] {lang_name:10} | {expected_dept[:30]:30}")
                    print(f"       Expected: {expected_dept}, Got: {actual_dept}")
            else:
                errors += 1
                error_msg = create_resp.json().get('error', 'Unknown error')
                print(f"[ERROR] {lang_name:10} | {expected_dept[:30]:30}")
                print(f"        Status: {create_resp.status_code}, Error: {error_msg[:50]}")
                
        except Exception as e:
            errors += 1
            print(f"[ERROR] {lang_name:10} | {expected_dept[:30]:30}")
            print(f"        Exception: {str(e)[:50]}")
    
    # Summary
    total = len(MULTILINGUAL_TEST_CASES)
    print("\n" + "=" * 80)
    print("OVERALL RESULTS")
    print("=" * 80)
    print(f"Total Tests: {total}")
    print(f"[OK] Correct: {correct} ({correct/total*100:.1f}%)")
    print(f"[FAIL] Wrong: {incorrect} ({incorrect/total*100:.1f}%)")
    print(f"[ERROR] Errors: {errors} ({errors/total*100:.1f}%)")
    
    # Per-language breakdown
    print("\n" + "=" * 80)
    print("RESULTS BY LANGUAGE")
    print("=" * 80)
    for lang, stats in results_by_language.items():
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{lang:10} | {stats['correct']}/{stats['total']} correct ({accuracy:.1f}%)")
    
    print("\n" + "=" * 80)
    accuracy = correct / total * 100
    if accuracy == 100:
        print("Result: PERFECT! 100% ACCURACY ACROSS ALL LANGUAGES!")
    elif accuracy >= 90:
        print("Result: EXCELLENT!")
    elif accuracy >= 75:
        print("Result: GOOD")
    elif accuracy >= 50:
        print("Result: NEEDS IMPROVEMENT")
    else:
        print("Result: POOR")
    print("=" * 80)


if __name__ == "__main__":
    test_multilingual_classification()
