#!/usr/bin/env python3
"""
Test chatbot API endpoint
"""

import requests
import json

def test_chatbot():
    url = "http://127.0.0.1:8000/api/chatbot/chat/"
    
    payload = {
        "message": "I want to report a pothole on Main Street",
        "language": "en"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing Chatbot API...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Chatbot API Test PASSED!")
            print(f"Session ID: {data.get('session_id', 'N/A')}")
            print(f"AI Response: {data.get('response', 'N/A')}")
            print(f"Intent: {data.get('intent', 'N/A')}")
            return True
        else:
            print("\n❌ Chatbot API Test FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_chatbot()
