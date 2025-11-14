"""
Direct Classification Test - Tests classification function directly
This bypasses the chatbot to test only the department classification accuracy
"""

import sys
sys.path.append('d:\\SmartGriev\\backend')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')

import django
django.setup()

from chatbot.gemini_views import classify_department_from_complaint
from complaints.models import Department

# Test cases - (Expected Department, Title, Description, Category)
TEST_CASES = [
    ("Road & Transportation", "Large pothole on Main Street", "causing accidents and vehicle damage", "Transportation"),
    ("Water Supply & Sewerage", "Water supply disruption", "pipe is broken, no water for 3 days", "Water"),
    ("Sanitation & Cleanliness", "Garbage not collected", "trash piling up, bad smell", "Sanitation"),
    ("Electricity Board", "Power outage", "transformer not working, no electricity", "Utilities"),
    ("Health & Medical Services", "Hospital medicine shortage", "essential medicines unavailable", "Healthcare"),
    ("Fire & Emergency Services", "Fire hazard emergency", "building on fire, need rescue", "Emergency"),
    ("Police & Law Enforcement", "Theft cases reported", "need police patrol, security issue", "Crime"),
    ("Traffic Police", "Severe traffic jam", "parking issues, vehicles blocking road", "Transportation"),
    ("Environment & Pollution Control", "Industrial air pollution", "smoke causing environmental damage", "Environment"),
    ("Parks & Gardens", "Park maintenance needed", "plants dying, playground broken", "Environment"),
    ("Municipal Corporation", "Property tax issue", "building permit license problem", "Administration"),
    ("Town Planning & Development", "Illegal construction", "building without planning permit", "Infrastructure"),
    ("Food Safety & Standards", "Restaurant hygiene issue", "food quality problem, expired items", "Food Safety"),
    ("Animal Control & Welfare", "Stray dog problem", "animal bite incident reported", "Animal Welfare"),
    ("Public Transport (BRTS/Bus)", "BRTS bus service irregular", "route timing issues, conductor problem", "Transportation"),
    ("Education Department", "School teacher shortage", "education quality suffering, students affected", "Education"),
]

def test_classification_direct():
    print("=" * 70)
    print("DIRECT CLASSIFICATION FUNCTION TEST")
    print("Testing classification logic without chatbot")
    print("=" * 70)
    
    correct = 0
    wrong = 0
    
    for expected, title, desc, category in TEST_CASES:
        result_dept = classify_department_from_complaint(title, desc, category)
        actual = result_dept.name if result_dept else "None"
        
        if actual == expected:
            correct += 1
            print(f"[OK] {expected[:35]:35} -> {actual}")
        else:
            wrong += 1
            print(f"[FAIL] {expected[:35]:35}")
            print(f"       Expected: {expected}")
            print(f"       Got: {actual}")
    
    total = len(TEST_CASES)
    accuracy = (correct / total) * 100
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total: {total}")
    print(f"Correct: {correct} ({accuracy:.1f}%)")
    print(f"Wrong: {wrong} ({(wrong/total)*100:.1f}%)")
    print("=" * 70)
    
    if accuracy == 100:
        print("🎉 PERFECT! 100% ACCURACY ACHIEVED!")
    elif accuracy >= 90:
        print("✅ EXCELLENT!")
    elif accuracy >= 75:
        print("✅ GOOD")
    else:
        print("⚠️ NEEDS IMPROVEMENT")

if __name__ == "__main__":
    test_classification_direct()
