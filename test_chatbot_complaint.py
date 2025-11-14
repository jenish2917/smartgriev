"""
Test chatbot complaint submission with classification
Run: python test_chatbot_complaint.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Test user credentials (use your actual test user)
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

def test_chatbot_complaint_flow():
    """Test the complete chatbot complaint submission flow"""
    
    print("=" * 60)
    print("CHATBOT COMPLAINT SUBMISSION TEST")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login/", json=LOGIN_DATA)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    tokens = response.json()
    access_token = tokens.get('access')
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"✅ Logged in successfully")
    
    # Step 2: Start conversation
    print("\n2. Starting chatbot conversation...")
    import time
    session_id = f"test-session-{int(time.time())}"
    
    # Step 3: Send messages to build complaint
    messages = [
        "There is a big pothole on Main Street",
        "It's in Kamrej, Surat",
        "It's very urgent, causing accidents"
    ]
    
    print("\n3. Building complaint through conversation...")
    for msg in messages:
        print(f"   User: {msg}")
        response = requests.post(
            f"{BASE_URL}/chatbot/gemini/chat/",
            json={
                "message": msg,
                "session_id": session_id,
                "language": "en"
            },
            headers=headers
        )
        if response.status_code == 200:
            bot_response = response.json().get('response', '')
            print(f"   Bot: {bot_response[:100]}...")
        else:
            print(f"   ⚠️ Response: {response.status_code}")
    
    # Step 4: Get conversation summary
    print("\n4. Getting conversation summary...")
    response = requests.get(
        f"{BASE_URL}/chatbot/gemini/summary/{session_id}/",
        headers=headers
    )
    if response.status_code == 200:
        summary = response.json()
        print(f"✅ Conversation summary:")
        print(f"   - Messages: {summary.get('message_count')}")
        print(f"   - Ready to submit: {summary.get('ready_to_submit')}")
        print(f"   - Complaint data: {json.dumps(summary.get('complaint_data'), indent=4)}")
    else:
        print(f"❌ Failed to get summary: {response.text}")
    
    # Step 5: Create complaint from chat
    print("\n5. Submitting complaint to database...")
    response = requests.post(
        f"{BASE_URL}/chatbot/gemini/create-complaint/",
        json={
            "session_id": session_id,
            "confirm": True
        },
        headers=headers
    )
    
    if response.status_code == 201:
        result = response.json()
        complaint_id = result.get('complaint_id')
        print(f"✅ Complaint created successfully!")
        print(f"   - ID: {complaint_id}")
        print(f"   - Title: {result.get('complaint', {}).get('title')}")
        print(f"   - Status: {result.get('complaint', {}).get('status')}")
        
        # Step 6: Verify complaint in database
        print("\n6. Verifying complaint in database...")
        response = requests.get(
            f"{BASE_URL}/complaints/{complaint_id}/",
            headers=headers
        )
        if response.status_code == 200:
            complaint = response.json()
            print(f"✅ Complaint verified in database:")
            print(f"   - Title: {complaint.get('title')}")
            print(f"   - Description: {complaint.get('description')[:100]}...")
            print(f"   - Department: {complaint.get('department', {}).get('name')}")
            print(f"   - Priority: {complaint.get('priority')}")
            print(f"   - Status: {complaint.get('status')}")
            print(f"   - Location: {complaint.get('location')}")
            
            # Verify department classification
            dept_name = complaint.get('department', {}).get('name', '')
            if 'Road' in dept_name or 'Transportation' in dept_name:
                print(f"✅ CORRECT: Pothole complaint classified to Roads department")
            else:
                print(f"⚠️ Department might need adjustment: {dept_name}")
        else:
            print(f"❌ Failed to verify: {response.text}")
    else:
        print(f"❌ Failed to create complaint: {response.text}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_chatbot_complaint_flow()
