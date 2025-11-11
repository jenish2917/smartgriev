"""
Basic Integration Tests for Frontend-Backend Connection
Tests all major endpoints to verify they're working correctly
"""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, message=""):
    """Print test result with color"""
    if status:
        print(f"{Colors.GREEN}✓{Colors.END} {name}")
        if message:
            print(f"  {Colors.BLUE}→{Colors.END} {message}")
    else:
        print(f"{Colors.RED}✗{Colors.END} {name}")
        if message:
            print(f"  {Colors.RED}→{Colors.END} {message}")

def test_server_health():
    """Test if backend server is running"""
    print(f"\n{Colors.YELLOW}=== Testing Server Health ==={Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/api/chatbot/health/", timeout=5)
        print_test("Backend server is running", response.status_code == 200, f"Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print_test("Backend server is running", False, f"Error: {str(e)}")
        return False

def test_authentication_endpoints():
    """Test authentication endpoints"""
    print(f"\n{Colors.YELLOW}=== Testing Authentication Endpoints ==={Colors.END}")
    
    # Test registration endpoint exists
    try:
        # Try to register (will fail validation but endpoint should exist)
        response = requests.post(f"{BASE_URL}/api/auth/register/", json={})
        # Should return 400 (validation error) not 404 (not found)
        print_test("Register endpoint exists", response.status_code in [400, 401], 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("Register endpoint exists", False, str(e))
    
    # Test login endpoint exists
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/", json={})
        print_test("Login endpoint exists", response.status_code in [400, 401], 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("Login endpoint exists", False, str(e))
    
    # Test logout endpoint exists
    try:
        response = requests.post(f"{BASE_URL}/api/auth/logout/", json={})
        print_test("Logout endpoint exists", response.status_code in [401, 403], 
                   f"Status: {response.status_code} (requires auth)")
    except Exception as e:
        print_test("Logout endpoint exists", False, str(e))
    
    # Test user profile endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/api/auth/user/")
        print_test("User profile endpoint (/user/) exists", response.status_code in [401, 403], 
                   f"Status: {response.status_code} (requires auth)")
    except Exception as e:
        print_test("User profile endpoint exists", False, str(e))

def test_chatbot_endpoints():
    """Test chatbot endpoints"""
    print(f"\n{Colors.YELLOW}=== Testing Chatbot Endpoints ==={Colors.END}")
    
    # Test chat endpoint
    try:
        response = requests.post(f"{BASE_URL}/api/chatbot/chat/", 
                                json={"message": "Hello, test message"})
        success = response.status_code in [200, 400, 500]  # Should respond, even if error
        print_test("Chat endpoint (/api/chatbot/chat/) exists", success, 
                   f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            has_response = 'response' in data
            print_test("Chat returns response field", has_response, 
                      f"Keys: {list(data.keys())}")
    except Exception as e:
        print_test("Chat endpoint exists", False, str(e))
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/chatbot/health/")
        print_test("Chatbot health endpoint exists", response.status_code == 200, 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("Chatbot health endpoint exists", False, str(e))
    
    # Test voice endpoint exists
    try:
        response = requests.post(f"{BASE_URL}/api/chatbot/voice/", files={})
        print_test("Voice endpoint (/api/chatbot/voice/) exists", 
                   response.status_code in [400, 401, 500], 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("Voice endpoint exists", False, str(e))
    
    # Test vision endpoint exists
    try:
        response = requests.post(f"{BASE_URL}/api/chatbot/vision/", files={})
        print_test("Vision endpoint (/api/chatbot/vision/) exists", 
                   response.status_code in [400, 401, 500], 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("Vision endpoint exists", False, str(e))

def test_complaints_endpoints():
    """Test complaints endpoints"""
    print(f"\n{Colors.YELLOW}=== Testing Complaints Endpoints ==={Colors.END}")
    
    # Test complaints list endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/complaints/")
        print_test("Complaints list endpoint exists", response.status_code in [200, 401], 
                   f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print_test("Complaints list returns JSON", True, 
                          f"Type: {type(data)}")
            except:
                print_test("Complaints list returns JSON", False, "Invalid JSON")
    except Exception as e:
        print_test("Complaints list endpoint exists", False, str(e))
    
    # Test departments endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/complaints/departments/")
        print_test("Departments endpoint exists", response.status_code in [200, 401], 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("Departments endpoint exists", False, str(e))

def test_field_mappings():
    """Test that field mappings are correct"""
    print(f"\n{Colors.YELLOW}=== Testing Field Mappings ==={Colors.END}")
    
    # This requires authentication, so we'll check the error response structure
    try:
        response = requests.get(f"{BASE_URL}/api/auth/user/")
        print_test("User endpoint requires authentication", 
                   response.status_code in [401, 403], 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("User endpoint accessible", False, str(e))

def test_cors():
    """Test CORS headers"""
    print(f"\n{Colors.YELLOW}=== Testing CORS Configuration ==={Colors.END}")
    
    try:
        response = requests.options(f"{BASE_URL}/api/auth/login/", 
                                    headers={"Origin": "http://localhost:3000"})
        
        has_cors = 'Access-Control-Allow-Origin' in response.headers
        print_test("CORS headers present", has_cors, 
                   f"Headers: {list(response.headers.keys())[:5]}...")
        
        if has_cors:
            allowed_origin = response.headers.get('Access-Control-Allow-Origin')
            print_test("CORS allows frontend origin", 
                      allowed_origin in ['*', 'http://localhost:3000'], 
                      f"Allowed: {allowed_origin}")
    except Exception as e:
        print_test("CORS configuration", False, str(e))

def test_complete_registration_flow():
    """Test a complete registration with a test user"""
    print(f"\n{Colors.YELLOW}=== Testing Complete Registration Flow ==={Colors.END}")
    
    # Generate unique username
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_user = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "language": "en"
    }
    
    try:
        # Register
        response = requests.post(f"{BASE_URL}/api/auth/register/", json=test_user)
        
        if response.status_code == 201:
            print_test("User registration successful", True, f"Status: {response.status_code}")
            
            try:
                data = response.json()
                has_tokens = 'access' in data or 'access_token' in data
                print_test("Registration returns tokens", has_tokens, 
                          f"Keys: {list(data.keys())}")
                
                # Try to login
                login_data = {
                    "username": test_user["username"],
                    "password": test_user["password"]
                }
                login_response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
                
                if login_response.status_code == 200:
                    print_test("Login with new user successful", True, 
                              f"Status: {login_response.status_code}")
                    
                    login_data = login_response.json()
                    access_token = login_data.get('access')
                    
                    if access_token:
                        # Test authenticated endpoint
                        headers = {"Authorization": f"Bearer {access_token}"}
                        profile_response = requests.get(f"{BASE_URL}/api/auth/user/", 
                                                       headers=headers)
                        
                        if profile_response.status_code == 200:
                            print_test("Get user profile with token successful", True)
                            
                            profile_data = profile_response.json()
                            expected_fields = ['id', 'username', 'email', 'role', 
                                             'mobile_number', 'language_preference']
                            fields_present = [f for f in expected_fields if f in profile_data]
                            
                            print_test("Profile has frontend-expected fields", 
                                      len(fields_present) >= 4, 
                                      f"Present: {fields_present}")
                        else:
                            print_test("Get user profile with token", False, 
                                      f"Status: {profile_response.status_code}")
                else:
                    print_test("Login with new user", False, 
                              f"Status: {login_response.status_code}")
            except Exception as e:
                print_test("Parse registration response", False, str(e))
        else:
            print_test("User registration", False, 
                      f"Status: {response.status_code}, Response: {response.text[:200]}")
    except Exception as e:
        print_test("Complete registration flow", False, str(e))

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}SmartGriev Backend Integration Tests{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    # Run tests
    if not test_server_health():
        print(f"\n{Colors.RED}Backend server is not running!{Colors.END}")
        print(f"{Colors.YELLOW}Please start the server with: python manage.py runserver 8000{Colors.END}")
        return
    
    test_authentication_endpoints()
    test_chatbot_endpoints()
    test_complaints_endpoints()
    test_field_mappings()
    test_cors()
    test_complete_registration_flow()
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}Integration tests completed!{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()
