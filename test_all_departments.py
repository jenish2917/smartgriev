"""
Test Department Classification for All 21 Civic Service Departments
"""

import requests
import json
import time
import sys
import io

# Fix Windows console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000/api"

# Admin credentials
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

# Test cases for each department with relevant complaints
DEPARTMENT_TEST_CASES = [
    {
        "department": "Road & Transportation",
        "complaints": [
            {
                "title": "Large pothole on Main Street",
                "description": "There is a dangerous pothole on Main Street causing vehicle damage and accidents",
                "category": "Transportation",
                "urgency": "urgent"
            },
            {
                "title": "Road repair needed",
                "description": "The highway pavement is cracked and needs repair. Heavy traffic area",
                "category": "Infrastructure",
                "urgency": "high"
            },
            {
                "title": "Damaged footpath",
                "description": "Footpath is broken near the crossing. Pedestrians at risk",
                "category": "Transportation",
                "urgency": "medium"
            }
        ]
    },
    {
        "department": "Water Supply & Sewerage",
        "complaints": [
            {
                "title": "Water supply disruption",
                "description": "No water supply in our area for 3 days. Water pipe seems broken",
                "category": "Water",
                "urgency": "urgent"
            },
            {
                "title": "Sewage overflow",
                "description": "Sewage is overflowing from drainage system creating health hazard",
                "category": "Sanitation",
                "urgency": "urgent"
            },
            {
                "title": "Leaking water tap",
                "description": "Public water tap is leaking continuously, wasting water",
                "category": "Water",
                "urgency": "medium"
            }
        ]
    },
    {
        "department": "Sanitation & Cleanliness",
        "complaints": [
            {
                "title": "Garbage not collected",
                "description": "Garbage has not been collected for a week. Trash is piling up and creating smell",
                "category": "Sanitation",
                "urgency": "high"
            },
            {
                "title": "Dirty public area",
                "description": "The market area is very dirty and needs immediate sweeping and cleaning",
                "category": "Cleanliness",
                "urgency": "medium"
            },
            {
                "title": "Waste management issue",
                "description": "Waste bins are overflowing with garbage creating unsanitary conditions",
                "category": "Sanitation",
                "urgency": "high"
            }
        ]
    },
    {
        "department": "Electricity Board",
        "complaints": [
            {
                "title": "Power outage",
                "description": "Electricity has been out for 6 hours. Transformer issue suspected",
                "category": "Utilities",
                "urgency": "urgent"
            },
            {
                "title": "Streetlight not working",
                "description": "Multiple streetlights are not working making the area dark and unsafe",
                "category": "Infrastructure",
                "urgency": "high"
            },
            {
                "title": "Damaged electric wire",
                "description": "Electric wire is hanging dangerously low near pole creating risk",
                "category": "Utilities",
                "urgency": "urgent"
            }
        ]
    },
    {
        "department": "Health & Medical Services",
        "complaints": [
            {
                "title": "Hospital staff shortage",
                "description": "Government hospital has severe doctor and medical staff shortage",
                "category": "Healthcare",
                "urgency": "high"
            },
            {
                "title": "Medicine unavailable",
                "description": "Essential medicines are not available at the health clinic",
                "category": "Healthcare",
                "urgency": "urgent"
            },
            {
                "title": "Hygiene issues in hospital",
                "description": "Poor hygiene conditions in the medical facility creating disease risk",
                "category": "Healthcare",
                "urgency": "high"
            }
        ]
    },
    {
        "department": "Fire & Emergency Services",
        "complaints": [
            {
                "title": "Fire hazard",
                "description": "Building on fire, need immediate emergency rescue services",
                "category": "Emergency",
                "urgency": "urgent"
            },
            {
                "title": "Disaster preparedness",
                "description": "Area lacks fire safety equipment and emergency response plan",
                "category": "Safety",
                "urgency": "medium"
            }
        ]
    },
    {
        "department": "Police & Law Enforcement",
        "complaints": [
            {
                "title": "Theft incident",
                "description": "Multiple theft cases reported in the area. Need police patrolling",
                "category": "Crime",
                "urgency": "high"
            },
            {
                "title": "Illegal activity",
                "description": "Illegal activities and law violations happening in the neighborhood",
                "category": "Safety",
                "urgency": "high"
            },
            {
                "title": "Safety concern",
                "description": "Security issues in the area, need police presence for safety",
                "category": "Safety",
                "urgency": "medium"
            }
        ]
    },
    {
        "department": "Traffic Police",
        "complaints": [
            {
                "title": "Severe traffic jam",
                "description": "Daily traffic jam causing major congestion and delays",
                "category": "Transportation",
                "urgency": "high"
            },
            {
                "title": "Illegal parking",
                "description": "Vehicles parked illegally blocking the road and causing traffic issues",
                "category": "Transportation",
                "urgency": "medium"
            },
            {
                "title": "Traffic challan issue",
                "description": "Wrong vehicle challan issued, need to contact traffic police",
                "category": "Transportation",
                "urgency": "medium"
            }
        ]
    },
    {
        "department": "Environment & Pollution Control",
        "complaints": [
            {
                "title": "Air pollution",
                "description": "Industrial smoke causing severe air quality and pollution problems",
                "category": "Environment",
                "urgency": "high"
            },
            {
                "title": "Noise pollution",
                "description": "Excessive noise from construction creating environment pollution",
                "category": "Environment",
                "urgency": "medium"
            }
        ]
    },
    {
        "department": "Parks & Gardens",
        "complaints": [
            {
                "title": "Park maintenance needed",
                "description": "Public park is poorly maintained, plants and trees are dying",
                "category": "Environment",
                "urgency": "medium"
            },
            {
                "title": "Playground equipment broken",
                "description": "Children's playground equipment in garden is broken and unsafe",
                "category": "Infrastructure",
                "urgency": "medium"
            },
            {
                "title": "Garden beautification",
                "description": "Green space needs better landscaping and more trees and plants",
                "category": "Environment",
                "urgency": "low"
            }
        ]
    },
    {
        "department": "Municipal Corporation",
        "complaints": [
            {
                "title": "Property tax issue",
                "description": "Problem with property tax calculation and civic records",
                "category": "Administration",
                "urgency": "medium"
            },
            {
                "title": "Building permit delay",
                "description": "Building permit license application is pending for months",
                "category": "Administration",
                "urgency": "medium"
            },
            {
                "title": "Municipal registration",
                "description": "Need to complete civic registration process with municipality",
                "category": "Administration",
                "urgency": "low"
            }
        ]
    },
    {
        "department": "Town Planning & Development",
        "complaints": [
            {
                "title": "Illegal construction",
                "description": "Illegal building construction happening without proper planning permission",
                "category": "Infrastructure",
                "urgency": "high"
            },
            {
                "title": "Development project delay",
                "description": "Town development project is delayed affecting urban planning",
                "category": "Infrastructure",
                "urgency": "medium"
            }
        ]
    },
    {
        "department": "Food Safety & Standards",
        "complaints": [
            {
                "title": "Restaurant hygiene issue",
                "description": "Food quality and hygiene standards not maintained in restaurant",
                "category": "Food Safety",
                "urgency": "high"
            },
            {
                "title": "Food adulteration",
                "description": "Adulteration suspected in food items being sold in the market",
                "category": "Food Safety",
                "urgency": "urgent"
            },
            {
                "title": "Expired food products",
                "description": "Shop is selling expired eating products endangering health",
                "category": "Food Safety",
                "urgency": "urgent"
            }
        ]
    },
    {
        "department": "Animal Control & Welfare",
        "complaints": [
            {
                "title": "Stray dog problem",
                "description": "Multiple stray dogs in the area causing safety concerns",
                "category": "Animal Welfare",
                "urgency": "medium"
            },
            {
                "title": "Animal bite incident",
                "description": "Stray cat bite incident, need veterinary assistance and animal control",
                "category": "Animal Welfare",
                "urgency": "high"
            },
            {
                "title": "Pet vaccination",
                "description": "Need veterinary services for pet vaccination and welfare",
                "category": "Animal Welfare",
                "urgency": "low"
            }
        ]
    },
    {
        "department": "Public Transport (BRTS/Bus)",
        "complaints": [
            {
                "title": "Bus service irregular",
                "description": "BRTS bus service is very irregular and unreliable",
                "category": "Transportation",
                "urgency": "medium"
            },
            {
                "title": "Bus stop maintenance",
                "description": "Bus stop shelter is damaged and needs repair",
                "category": "Infrastructure",
                "urgency": "low"
            },
            {
                "title": "Bus conductor behavior",
                "description": "Bus conductor was rude and unhelpful to passengers",
                "category": "Service",
                "urgency": "medium"
            }
        ]
    },
    {
        "department": "Education Department",
        "complaints": [
            {
                "title": "School infrastructure poor",
                "description": "Government school building is in poor condition affecting education",
                "category": "Education",
                "urgency": "high"
            },
            {
                "title": "Teacher shortage",
                "description": "School has severe teacher shortage impacting student learning",
                "category": "Education",
                "urgency": "high"
            },
            {
                "title": "College facility issue",
                "description": "College lacks basic facilities for students and education",
                "category": "Education",
                "urgency": "medium"
            }
        ]
    }
]


def test_all_departments():
    """Test classification for all civic departments"""
    
    print("=" * 80)
    print("COMPREHENSIVE DEPARTMENT CLASSIFICATION TEST")
    print("=" * 80)
    print()
    
    # Step 1: Login
    print("1. Logging in as admin...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=LOGIN_DATA)
        response.raise_for_status()
        token = response.json()['access']
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Logged in successfully\n")
    except Exception as e:
        print(f"❌ Login failed: {e}\n")
        return
    
    # Statistics
    total_tests = 0
    correct_classifications = 0
    incorrect_classifications = 0
    errors = 0
    
    results = []
    
    # Step 2: Test each department
    print("2. Testing classification for all departments...")
    print("-" * 80)
    
    for dept_test in DEPARTMENT_TEST_CASES:
        expected_dept = dept_test["department"]
        complaints = dept_test["complaints"]
        
        print(f"\n🏛️  Testing: {expected_dept}")
        print(f"   Number of test cases: {len(complaints)}")
        
        for i, complaint_data in enumerate(complaints, 1):
            total_tests += 1
            
            try:
                # Start conversation
                session_response = requests.post(
                    f"{BASE_URL}/chatbot/gemini/start/",
                    json={"language": "en"}
                )
                
                if session_response.status_code != 200:
                    raise Exception(f"Start conversation failed: {session_response.status_code} - {session_response.text[:200]}")
                
                session_id = session_response.json()["session_id"]
                
                # Simulate conversation
                messages = [
                    complaint_data["title"],
                    f"Location: {dept_test['department']} area, Surat",
                    f"It's {complaint_data['urgency']} priority"
                ]
                
                for msg in messages:
                    requests.post(
                        f"{BASE_URL}/chatbot/gemini/chat/",
                        json={"message": msg, "session_id": session_id, "language": "en"}
                    )
                    time.sleep(0.3)  # Small delay
                
                # Create complaint
                create_response = requests.post(
                    f"{BASE_URL}/chatbot/gemini/create-complaint/",
                    json={"session_id": session_id, "confirm": True},
                    headers=headers
                )
                
                if create_response.status_code == 201:
                    complaint_id = create_response.json()["complaint_id"]
                    
                    # Verify department
                    verify_response = requests.get(
                        f"{BASE_URL}/complaints/{complaint_id}/",
                        headers=headers
                    )
                    
                    actual_dept = verify_response.json()["department"]["name"]
                    
                    if actual_dept == expected_dept:
                        correct_classifications += 1
                        print(f"   ✅ Test {i}: '{complaint_data['title'][:40]}...' → {actual_dept}")
                        results.append({
                            "expected": expected_dept,
                            "actual": actual_dept,
                            "complaint": complaint_data["title"],
                            "status": "✅ PASS"
                        })
                    else:
                        incorrect_classifications += 1
                        print(f"   ❌ Test {i}: '{complaint_data['title'][:40]}...'")
                        print(f"      Expected: {expected_dept}, Got: {actual_dept}")
                        results.append({
                            "expected": expected_dept,
                            "actual": actual_dept,
                            "complaint": complaint_data["title"],
                            "status": "❌ FAIL"
                        })
                else:
                    errors += 1
                    print(f"   ⚠️  Test {i}: Failed to create complaint - {create_response.status_code}")
                    results.append({
                        "expected": expected_dept,
                        "actual": "ERROR",
                        "complaint": complaint_data["title"],
                        "status": "⚠️ ERROR"
                    })
                    
            except Exception as e:
                errors += 1
                print(f"   ⚠️  Test {i}: Exception - {str(e)[:50]}")
                results.append({
                    "expected": expected_dept,
                    "actual": "ERROR",
                    "complaint": complaint_data["title"],
                    "status": "⚠️ ERROR"
                })
    
    # Step 3: Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"\nTotal Tests Run: {total_tests}")
    print(f"✅ Correct Classifications: {correct_classifications} ({correct_classifications/total_tests*100:.1f}%)")
    print(f"❌ Incorrect Classifications: {incorrect_classifications} ({incorrect_classifications/total_tests*100:.1f}%)")
    print(f"⚠️  Errors: {errors} ({errors/total_tests*100:.1f}%)")
    
    # Step 4: Show failed tests
    if incorrect_classifications > 0:
        print("\n" + "-" * 80)
        print("FAILED CLASSIFICATIONS:")
        print("-" * 80)
        for result in results:
            if result["status"] == "❌ FAIL":
                print(f"❌ {result['complaint'][:50]}...")
                print(f"   Expected: {result['expected']}")
                print(f"   Got: {result['actual']}\n")
    
    # Step 5: Overall result
    print("\n" + "=" * 80)
    success_rate = correct_classifications / total_tests * 100
    if success_rate >= 90:
        print(f"🎉 EXCELLENT! Classification accuracy: {success_rate:.1f}%")
    elif success_rate >= 75:
        print(f"✅ GOOD! Classification accuracy: {success_rate:.1f}%")
    elif success_rate >= 50:
        print(f"⚠️  NEEDS IMPROVEMENT! Classification accuracy: {success_rate:.1f}%")
    else:
        print(f"❌ POOR! Classification accuracy: {success_rate:.1f}%")
    print("=" * 80)


if __name__ == "__main__":
    test_all_departments()
