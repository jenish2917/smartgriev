"""
Fast Department Classification Test - One complaint per department
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

# One test case per department
TEST_CASES = [
    ("Road & Transportation", "Large pothole on Main Street causing accidents", "Transportation"),
    ("Water Supply & Sewerage", "Water supply disruption, pipe is broken", "Water"),
    ("Sanitation & Cleanliness", "Garbage not collected, trash piling up", "Sanitation"),
    ("Electricity Board", "Power outage, transformer not working", "Utilities"),
    ("Health & Medical Services", "Hospital has medicine shortage", "Healthcare"),
    ("Fire & Emergency Services", "Fire hazard, need emergency rescue", "Emergency"),
    ("Police & Law Enforcement", "Theft cases, need police patrol", "Crime"),
    ("Traffic Police", "Severe traffic jam, parking issues", "Transportation"),
    ("Environment & Pollution Control", "Industrial smoke causing air pollution", "Environment"),
    ("Parks & Gardens", "Park maintenance needed, plants dying", "Environment"),
    ("Municipal Corporation", "Property tax issue, license problem", "Administration"),
    ("Town Planning & Development", "Illegal construction, no planning permit", "Infrastructure"),
    ("Food Safety & Standards", "Restaurant hygiene issue, food quality problem", "Food Safety"),
    ("Animal Control & Welfare", "Stray dog problem, animal bite incident", "Animal Welfare"),
    ("Public Transport (BRTS/Bus)", "BRTS bus service irregular", "Transportation"),
    ("Education Department", "School has teacher shortage", "Education"),
]


def test_departments_fast():
    print("=" * 70)
    print("FAST DEPARTMENT CLASSIFICATION TEST (16 departments)")
    print("=" * 70)
    
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
    
    # Test each department
    print(f"\n2. Testing {len(TEST_CASES)} departments...\n")
    
    correct = 0
    incorrect = 0
    errors = 0
    
    for expected_dept, complaint_text, category in TEST_CASES:
        try:
            # Start conversation
            session_resp = requests.post(
                f"{BASE_URL}/chatbot/gemini/start/",
                json={"language": "en"},
                timeout=10
            )
            session_id = session_resp.json()["session_id"]
            time.sleep(0.5)  # Increased delay
            
            # Send complaint
            chat1 = requests.post(
                f"{BASE_URL}/chatbot/gemini/chat/",
                json={"message": complaint_text, "session_id": session_id, "language": "en"},
                timeout=10
            )
            time.sleep(1)
            
            # Add location
            chat2 = requests.post(
                f"{BASE_URL}/chatbot/gemini/chat/",
                json={"message": "Surat, Gujarat", "session_id": session_id, "language": "en"},
                timeout=10
            )
            time.sleep(1)
            
            # Confirm urgent
            chat3 = requests.post(
                f"{BASE_URL}/chatbot/gemini/chat/",
                json={"message": "urgent", "session_id": session_id, "language": "en"},
                timeout=10
            )
            time.sleep(1)
            
            # Create complaint
            create_resp = requests.post(
                f"{BASE_URL}/chatbot/gemini/create-complaint/",
                json={"session_id": session_id, "confirm": True},
                headers=headers,
                timeout=15  # Increased timeout
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
                    print(f"[OK] {expected_dept[:30]:30} -> {actual_dept}")
                else:
                    incorrect += 1
                    print(f"[FAIL] {expected_dept[:30]:30} -> Got: {actual_dept}")
            else:
                errors += 1
                print(f"[ERROR] {expected_dept[:30]:30} -> Status: {create_resp.status_code}")
                
        except Exception as e:
            errors += 1
            print(f"[ERROR] {expected_dept[:30]:30} -> {str(e)[:40]}")
    
    # Summary
    total = len(TEST_CASES)
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"[OK] Correct: {correct} ({correct/total*100:.1f}%)")
    print(f"[FAIL] Wrong: {incorrect} ({incorrect/total*100:.1f}%)")
    print(f"[ERROR] Errors: {errors} ({errors/total*100:.1f}%)")
    print("=" * 70)
    
    if correct/total >= 0.9:
        print("Result: EXCELLENT!")
    elif correct/total >= 0.75:
        print("Result: GOOD")
    elif correct/total >= 0.5:
        print("Result: NEEDS IMPROVEMENT")
    else:
        print("Result: POOR")


if __name__ == "__main__":
    test_departments_fast()
