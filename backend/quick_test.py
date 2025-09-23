#!/usr/bin/env python3
"""
Quick API validation for SmartGriev Backend
==========================================
"""

import requests
import json

def test_endpoints():
    base_url = "http://127.0.0.1:8000/api/complaints/api"
    
    print("🚀 SmartGriev Backend API Validation")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health/", timeout=10)
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
    
    # Test departments endpoint
    try:
        response = requests.get(f"{base_url}/departments/", timeout=10)
        data = response.json()
        print(f"✅ Departments: {response.status_code} - Found {len(data.get('departments', []))} departments")
    except Exception as e:
        print(f"❌ Departments failed: {e}")
    
    # Test text processing
    try:
        data = {"text": "बिजली की समस्या है", "location": "Delhi"}
        response = requests.post(f"{base_url}/process/", json=data, timeout=10)
        result = response.json()
        print(f"✅ Text Processing: {response.status_code} - Department: {result.get('department', 'N/A')}")
    except Exception as e:
        print(f"❌ Text Processing failed: {e}")
    
    print("\n🎉 API validation complete!")

if __name__ == "__main__":
    test_endpoints()