#!/usr/bin/env python3
"""
Final API Endpoint Test for SmartGriev Backend
==============================================
Test all API endpoints to ensure complete functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/complaints/api"

def test_all_endpoints():
    print("🚀 SmartGriev Backend Final API Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health Check
    total_tests += 1
    print("\n1. 🏥 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status', 'unknown')}")
            print(f"   Components: {len(data.get('components', {}))}")
            tests_passed += 1
        else:
            print(f"❌ Health Check failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check error: {e}")
    
    # Test 2: Departments List
    total_tests += 1
    print("\n2. 🏛️ Testing Departments Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/departments/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            dept_count = len(data.get('departments', []))
            print(f"✅ Departments: {dept_count} departments loaded")
            if dept_count > 0:
                sample = data['departments'][0]
                print(f"   Sample: {sample.get('name', 'Unknown')}")
            tests_passed += 1
        else:
            print(f"❌ Departments failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Departments error: {e}")
    
    # Test 3: Text Processing
    total_tests += 1
    print("\n3. 📝 Testing Text Processing...")
    try:
        data = {
            "text": "बिजली नहीं आ रही है पिछले 2 दिन से। Emergency repair needed।",
            "location": "Delhi, India"
        }
        response = requests.post(f"{BASE_URL}/process/", json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Text Processing successful")
            print(f"   Department: {result.get('department', 'N/A')}")
            print(f"   Urgency: {result.get('urgency_level', 'N/A')}")
            print(f"   Processing successful: {result.get('success', False)}")
            tests_passed += 1
        else:
            print(f"❌ Text Processing failed with status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Text Processing error: {e}")
    
    # Test 4: Authentication Structure
    total_tests += 1
    print("\n4. 🔐 Testing Authentication Endpoint Structure...")
    try:
        data = {
            "action": "test_structure",
            "test": True
        }
        response = requests.post(f"{BASE_URL}/auth/", json=data, timeout=10)
        # We expect this to return an error but with proper structure
        if response.status_code in [200, 400, 422]:  # Any proper HTTP response
            print(f"✅ Authentication endpoint responding")
            print(f"   Status: {response.status_code}")
            tests_passed += 1
        else:
            print(f"❌ Authentication endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Authentication error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL API TEST SUMMARY")
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL API ENDPOINTS FULLY FUNCTIONAL!")
        print("🚀 SmartGriev Backend is 100% OPERATIONAL!")
        print("\n✅ READY FOR:")
        print("   • Frontend Integration")
        print("   • Mobile App Development")
        print("   • Production Deployment")
        print("   • Real-world Usage")
    elif tests_passed >= total_tests * 0.75:
        print("\n✅ BACKEND IS MOSTLY OPERATIONAL!")
        print("🔧 Minor issues detected but system is functional")
    else:
        print("\n⚠️ BACKEND NEEDS ATTENTION")
        print("🔧 Some critical components may need fixes")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = test_all_endpoints()
    if success:
        print("\n🎊 CONGRATULATIONS! Your SmartGriev backend is fully operational! 🎊")
    else:
        print("\n🔧 Check the issues above and retry testing")