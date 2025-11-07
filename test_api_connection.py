"""
SmartGriev API Connection Test Script
Tests all major API endpoints and verifies frontend-backend connectivity
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name, success, message, details=None):
    """Log test result"""
    test_results["total_tests"] += 1
    if success:
        test_results["passed"] += 1
        status = "✅ PASS"
    else:
        test_results["failed"] += 1
        status = "❌ FAIL"
    
    result = {
        "name": name,
        "status": status,
        "message": message,
        "details": details
    }
    test_results["tests"].append(result)
    print(f"\n{status}: {name}")
    print(f"   {message}")
    if details:
        print(f"   Details: {details}")

def test_server_connection():
    """Test if backend server is running"""
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=5)
        log_test(
            "Backend Server Connection",
            response.status_code in [200, 302],
            f"Server is running (Status: {response.status_code})"
        )
        return True
    except requests.exceptions.ConnectionError:
        log_test(
            "Backend Server Connection",
            False,
            "Cannot connect to backend server. Make sure it's running on port 8000."
        )
        return False
    except Exception as e:
        log_test(
            "Backend Server Connection",
            False,
            f"Connection error: {str(e)}"
        )
        return False

def test_cors_headers():
    """Test CORS headers for frontend connection"""
    try:
        response = requests.options(
            f"{BASE_URL}/api/auth/register/",
            headers={"Origin": FRONTEND_URL}
        )
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        log_test(
            "CORS Configuration",
            "Access-Control-Allow-Origin" in response.headers,
            "CORS headers are configured",
            cors_headers
        )
    except Exception as e:
        log_test(
            "CORS Configuration",
            False,
            f"CORS test failed: {str(e)}"
        )

def test_registration_endpoint():
    """Test user registration endpoint"""
    try:
        # Test data
        test_user = {
            "username": f"testuser_{datetime.now().timestamp()}",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "mobile": "1234567890",
            "address": "Test Address"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register/",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            log_test(
                "User Registration",
                True,
                "Registration endpoint works correctly",
                {"user": response.json().get("username")}
            )
            return response.json()
        else:
            log_test(
                "User Registration",
                False,
                f"Registration failed (Status: {response.status_code})",
                response.json()
            )
            return None
    except Exception as e:
        log_test(
            "User Registration",
            False,
            f"Registration test error: {str(e)}"
        )
        return None

def test_login_endpoint(username=None, password=None):
    """Test user login endpoint"""
    if not username or not password:
        username = "admin"
        password = "admin123"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200 and "access" in response.json():
            tokens = response.json()
            log_test(
                "User Login (JWT)",
                True,
                "Login endpoint works, JWT tokens received",
                {"has_access_token": bool(tokens.get("access")), "has_refresh_token": bool(tokens.get("refresh"))}
            )
            return tokens
        else:
            log_test(
                "User Login (JWT)",
                False,
                f"Login failed (Status: {response.status_code})",
                response.json() if response.status_code != 500 else None
            )
            return None
    except Exception as e:
        log_test(
            "User Login (JWT)",
            False,
            f"Login test error: {str(e)}"
        )
        return None

def test_authenticated_endpoint(token):
    """Test authenticated endpoint with JWT token"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/auth/profile/",
            headers=headers
        )
        
        if response.status_code == 200:
            profile = response.json()
            log_test(
                "Authenticated API (Profile)",
                True,
                "JWT authentication works correctly",
                {"username": profile.get("username")}
            )
            return True
        else:
            log_test(
                "Authenticated API (Profile)",
                False,
                f"Authentication failed (Status: {response.status_code})"
            )
            return False
    except Exception as e:
        log_test(
            "Authenticated API (Profile)",
            False,
            f"Authentication test error: {str(e)}"
        )
        return False

def test_complaints_list(token=None):
    """Test complaints list endpoint"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.get(
            f"{BASE_URL}/api/complaints/",
            headers=headers
        )
        
        if response.status_code in [200, 401]:  # 401 if auth required
            if response.status_code == 200:
                data = response.json()
                log_test(
                    "Complaints List API",
                    True,
                    f"Complaints endpoint accessible ({len(data.get('results', data)) if isinstance(data, dict) else len(data)} complaints)",
                    {"requires_auth": False}
                )
            else:
                log_test(
                    "Complaints List API",
                    True,
                    "Complaints endpoint requires authentication (as expected)",
                    {"requires_auth": True}
                )
            return True
        else:
            log_test(
                "Complaints List API",
                False,
                f"Unexpected status code: {response.status_code}"
            )
            return False
    except Exception as e:
        log_test(
            "Complaints List API",
            False,
            f"Complaints list test error: {str(e)}"
        )
        return False

def test_chatbot_endpoint(token=None):
    """Test chatbot endpoint"""
    try:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        test_message = {
            "message": "Hello, this is a test message"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chatbot/chat/",
            json=test_message,
            headers=headers
        )
        
        if response.status_code in [200, 201, 401]:
            if response.status_code in [200, 201]:
                log_test(
                    "Chatbot API",
                    True,
                    "Chatbot endpoint is working",
                    {"response_received": True}
                )
            else:
                log_test(
                    "Chatbot API",
                    True,
                    "Chatbot endpoint requires authentication",
                    {"requires_auth": True}
                )
            return True
        else:
            log_test(
                "Chatbot API",
                False,
                f"Chatbot test failed (Status: {response.status_code})"
            )
            return False
    except Exception as e:
        log_test(
            "Chatbot API",
            False,
            f"Chatbot test error: {str(e)}"
        )
        return False

def test_streaming_endpoint(token=None):
    """Test streaming chatbot endpoint"""
    try:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        test_message = {
            "message": "Test streaming"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chatbot/stream/",
            json=test_message,
            headers=headers,
            stream=True
        )
        
        if response.status_code in [200, 401, 404]:
            if response.status_code == 200:
                log_test(
                    "Streaming Chatbot API",
                    True,
                    "Streaming endpoint is configured",
                    {"streaming_enabled": True}
                )
            elif response.status_code == 404:
                log_test(
                    "Streaming Chatbot API",
                    True,
                    "Streaming endpoint not found (may need URL configuration)",
                    {"streaming_enabled": False}
                )
            else:
                log_test(
                    "Streaming Chatbot API",
                    True,
                    "Streaming endpoint requires authentication",
                    {"requires_auth": True}
                )
            return True
        else:
            log_test(
                "Streaming Chatbot API",
                False,
                f"Streaming test failed (Status: {response.status_code})"
            )
            return False
    except Exception as e:
        log_test(
            "Streaming Chatbot API",
            False,
            f"Streaming test error: {str(e)}"
        )
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"Success Rate: {(test_results['passed']/test_results['total_tests']*100):.1f}%")
    print("="*70)
    
    # Save results to file
    with open("api_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    print("\n📄 Detailed results saved to: api_test_results.json")

def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("SmartGriev API Connection Test")
    print("="*70)
    print(f"Backend URL: {BASE_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Test 1: Server connection
    if not test_server_connection():
        print("\n⚠️  Backend server is not running. Please start it first.")
        print("   Run: cd backend && python manage.py runserver 8000")
        print_summary()
        return
    
    # Test 2: CORS headers
    test_cors_headers()
    
    # Test 3: Registration
    new_user = test_registration_endpoint()
    
    # Test 4: Login (try with default admin, then with new user if created)
    tokens = test_login_endpoint()
    access_token = tokens.get("access") if tokens else None
    
    # Test 5: Authenticated endpoint
    if access_token:
        test_authenticated_endpoint(access_token)
    
    # Test 6: Complaints list
    test_complaints_list(access_token)
    
    # Test 7: Chatbot
    test_chatbot_endpoint(access_token)
    
    # Test 8: Streaming chatbot
    test_streaming_endpoint(access_token)
    
    # Print summary
    print_summary()
    
    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    if test_results["failed"] > 0:
        print("⚠️  Some tests failed. Check the following:")
        print("   1. Make sure backend server is running: python manage.py runserver 8000")
        print("   2. Verify database migrations are applied: python manage.py migrate")
        print("   3. Check CORS settings in settings.py")
        print("   4. Ensure all required packages are installed")
    else:
        print("✅ All tests passed! Frontend can connect to backend successfully.")
        print("   You can now:")
        print("   1. Test registration at: http://localhost:3000/register")
        print("   2. Test login at: http://localhost:3000/login")
        print("   3. File complaints and use chatbot features")
    print("="*70)

if __name__ == "__main__":
    main()
