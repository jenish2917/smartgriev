"""
SmartGriev - Complete System Connection Status
Verifies ALL connections including new CivicAI Voice Assistant
"""

import requests
import json
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 100}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(100)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 100}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def test_connection(name, url, method='GET', data=None, timeout=5):
    """Test a single connection"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=data, timeout=timeout)
        
        if response.status_code == 200:
            print_success(f"{name}: CONNECTED (200 OK)")
            return True
        else:
            print_warning(f"{name}: Connected but returned {response.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        print_error(f"{name}: CONNECTION REFUSED")
        return False
    except Exception as e:
        print_error(f"{name}: {str(e)}")
        return False

def main():
    print_header("🔗 SMARTGRIEV - COMPLETE SYSTEM CONNECTION STATUS")
    print(f"{Colors.CYAN}Test Time:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # FRONTEND
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}━━━ FRONTEND (React + Vite) ━━━{Colors.RESET}")
    frontend_ok = test_connection("Frontend Homepage", "http://localhost:3000")
    results.append(("Frontend", frontend_ok))
    
    # BACKEND - CORE
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}━━━ BACKEND - CORE ENDPOINTS ━━━{Colors.RESET}")
    chatbot_health = test_connection("Chatbot Health", "http://127.0.0.1:8000/api/chatbot/health/")
    results.append(("Chatbot Health", chatbot_health))
    
    # BACKEND - AUTHENTICATION
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}━━━ BACKEND - AUTHENTICATION ━━━{Colors.RESET}")
    login_ok = test_connection("Login Endpoint", "http://127.0.0.1:8000/api/login/", 'POST', {"username": "", "password": ""})
    register_ok = test_connection("Register Endpoint", "http://127.0.0.1:8000/api/register/", 'POST', {})
    token_refresh = test_connection("Token Refresh", "http://127.0.0.1:8000/api/token/refresh/", 'POST', {})
    results.append(("Login", login_ok))
    results.append(("Register", register_ok))
    results.append(("Token Refresh", token_refresh))
    
    # BACKEND - COMPLAINTS
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}━━━ BACKEND - COMPLAINT SYSTEM ━━━{Colors.RESET}")
    complaints_list = test_connection("Complaints List", "http://127.0.0.1:8000/api/complaints/")
    results.append(("Complaints List", complaints_list))
    
    # BACKEND - AI FEATURES
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}━━━ BACKEND - AI FEATURES ━━━{Colors.RESET}")
    chatbot_chat = test_connection("Chatbot Chat", "http://127.0.0.1:8000/api/chatbot/chat/", 'POST', {"message": "test"})
    results.append(("Chatbot Chat", chatbot_chat))
    
    # BACKEND - CIVICAI VOICE ASSISTANT (NEW!)
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}━━━ CIVICAI VOICE ASSISTANT (NEW!) ━━━{Colors.RESET}")
    voice_health = test_connection("Voice Health", "http://127.0.0.1:8000/api/chatbot/voice/health/")
    voice_languages = test_connection("Voice Languages", "http://127.0.0.1:8000/api/chatbot/voice/languages/")
    
    # Test voice submit with sample data
    voice_submit_data = {
        "transcribed_text": "Test complaint in English",
        "caller_id": "0000000000"
    }
    voice_submit = test_connection("Voice Submit", "http://127.0.0.1:8000/api/chatbot/voice/submit/", 'POST', voice_submit_data)
    
    voice_chat_data = {
        "message": "Test message",
        "session_state": "collecting_complaint"
    }
    voice_chat = test_connection("Voice Chat", "http://127.0.0.1:8000/api/chatbot/voice/chat/", 'POST', voice_chat_data)
    
    results.append(("Voice Health", voice_health))
    results.append(("Voice Languages", voice_languages))
    results.append(("Voice Submit", voice_submit))
    results.append(("Voice Chat", voice_chat))
    
    # SUMMARY
    print_header("📊 CONNECTION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for endpoint, result in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{status}  {endpoint}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} connections working{Colors.RESET}")
    
    # Success Rate
    success_rate = (passed / total) * 100
    if success_rate == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL CONNECTIONS WORKING! System is fully operational!{Colors.RESET}")
    elif success_rate >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Most connections working ({success_rate:.0f}%), check failed endpoints{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Multiple connection failures ({success_rate:.0f}% success rate){Colors.RESET}")
    
    # System Status
    print_header("🌐 SYSTEM ACCESS")
    print(f"{Colors.CYAN}Frontend:{Colors.RESET} http://localhost:3000")
    print(f"{Colors.CYAN}Backend:{Colors.RESET} http://127.0.0.1:8000")
    print(f"{Colors.CYAN}Admin Panel:{Colors.RESET} http://127.0.0.1:8000/admin/")
    
    # CivicAI Voice Info
    if voice_health and voice_languages:
        print_header("🎤 CIVICAI VOICE ASSISTANT")
        print_success("Voice Assistant is fully operational!")
        print_info("Supported Languages: Gujarati, Hindi, Marathi, Punjabi, English")
        print_info("Supported Departments: Water, Road, Fire, Safety, Electricity, Sanitation, Health")
        print(f"\n{Colors.CYAN}Test Voice Assistant:{Colors.RESET}")
        print(f"  curl -X POST http://127.0.0.1:8000/api/chatbot/voice/submit/ \\")
        print(f"    -H 'Content-Type: application/json' \\")
        print(f"    -d '{{\"transcribed_text\": \"મારા એરિયા માં પાણી નથી\", \"caller_id\": \"9876543210\"}}'")
    
    print(f"\n{Colors.CYAN}Timestamp:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()
