"""
Test Gemini Chatbot Server
"""
import requests
import json

# Test health endpoint
print("Testing health endpoint...")
try:
    response = requests.get('http://127.0.0.1:8000/api/chatbot/health/')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
except Exception as e:
    print(f"Error: {e}\n")

# Test chat endpoint - English
print("Testing chat endpoint (English)...")
try:
    data = {
        'message': 'Hello, I want to complain about a pothole near my house',
        'language': 'en'
    }
    response = requests.post('http://127.0.0.1:8000/api/chatbot/chat/', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
except Exception as e:
    print(f"Error: {e}\n")

# Test chat endpoint - Gujarati
print("Testing chat endpoint (Gujarati)...")
try:
    data = {
        'message': 'હેલો, મારે રસ્તામાં ખાડા વિશે ફરિયાદ કરવી છે',
        'language': 'gu'
    }
    response = requests.post('http://127.0.0.1:8000/api/chatbot/chat/', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")
except Exception as e:
    print(f"Error: {e}\n")

print("✅ All tests completed!")
