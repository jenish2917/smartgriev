"""
Simple Multilingual Classification Test
Tests that complaints in different languages get translated and classified correctly
"""

import requests
import time

BASE_URL = "http://localhost:8000/api"

LOGIN_DATA = {"username": "admin", "password": "admin123"}

# Simple test: 2 languages, 2 departments each
TEST_CASES = [
    # English
    ("Road & Transportation", ["Large pothole on Main Street", "Surat city", "urgent"], "en", "English"),
    ("Water Supply & Sewerage", ["No water supply for 3 days", "Surat city", "urgent"], "en", "English"),
    
    # Hindi
    ("Road & Transportation", ["मुख्य सड़क पर बड़ा गड्ढा है", "सूरत शहर", "तत्काल"], "hi", "Hindi"),
    ("Sanitation & Cleanliness", ["कचरा नहीं उठाया जा रहा", "सूरत शहर", "तत्काल"], "hi", "Hindi"),
    
    # Gujarati
    ("Electricity Board", ["વીજળી બંધ છે", "સુરત શહેર", "તાત્કાલિક"], "gu", "Gujarati"),
    ("Water Supply & Sewerage", ["પાણીની સમસ્યા છે", "સુરત શહેર", "તાત્કાલિક"], "gu", "Gujarati"),
]


def test_simple_multilingual():
    print("=" * 70)
    print("SIMPLE MULTILINGUAL TEST")
    print("=" * 70)
    
    # Login
    print("\n1. Logging in...")
    token = requests.post(f"{BASE_URL}/auth/login/", json=LOGIN_DATA).json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Logged in")
    
    correct = 0
    total = len(TEST_CASES)
    
    print(f"\n2. Testing {total} complaints...\n")
    
    for expected_dept, messages, lang, lang_name in TEST_CASES:
        try:
            # Start conversation
            session = requests.post(f"{BASE_URL}/chatbot/gemini/start/", json={"language": lang})
            sid = session.json()["session_id"]
            time.sleep(1)
            
            # Send messages
            for msg in messages:
                requests.post(f"{BASE_URL}/chatbot/gemini/chat/", 
                            json={"message": msg, "session_id": sid, "language": lang})
                time.sleep(1.5)
            
            # Create complaint
            create_resp = requests.post(
                f"{BASE_URL}/chatbot/gemini/create-complaint/",
                json={"session_id": sid, "confirm": True},
                headers=headers,
                timeout=15
            )
            
            if create_resp.status_code == 201:
                cid = create_resp.json()["complaint_id"]
                verify = requests.get(f"{BASE_URL}/complaints/{cid}/", headers=headers)
                actual = verify.json()["department"]["name"]
                
                if actual == expected_dept:
                    correct += 1
                    print(f"[OK] {lang_name:10} | {expected_dept[:35]}")
                else:
                    print(f"[FAIL] {lang_name:10} | Expected: {expected_dept}")
                    print(f"       Got: {actual}")
            else:
                error = create_resp.json().get('error', 'Unknown')
                print(f"[ERROR] {lang_name:10} | {expected_dept[:35]}")
                print(f"        {error}")
                
        except Exception as e:
            print(f"[ERROR] {lang_name:10} | {expected_dept[:35]}")
            print(f"        {str(e)[:60]}")
    
    # Results
    accuracy = (correct / total) * 100
    print("\n" + "=" * 70)
    print(f"RESULTS: {correct}/{total} correct ({accuracy:.1f}%)")
    print("=" * 70)
    
    if accuracy == 100:
        print("✓ PERFECT! All languages working correctly!")
    elif accuracy >= 75:
        print("✓ GOOD! Translation and classification working well")
    else:
        print("✗ NEEDS IMPROVEMENT")


if __name__ == "__main__":
    test_simple_multilingual()
