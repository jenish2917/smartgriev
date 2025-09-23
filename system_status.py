#!/usr/bin/env python3
"""
SmartGriev System Status Dashboard
=================================
"""

import requests
import time
import json
from datetime import datetime

def print_header():
    print("🚀 SmartGriev System Status Dashboard")
    print("=" * 50)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_backend():
    print("🔧 Backend Status (Django):")
    print("-" * 30)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test root
    try:
        response = requests.get(f"{base_url}/", timeout=3)
        print(f"✅ Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint: {str(e)[:50]}...")
    
    # Test API health
    try:
        response = requests.get(f"{base_url}/api/complaints/api/health/", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data.get('status', 'OK')}")
        else:
            print(f"⚠️ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint: {str(e)[:50]}...")
    
    # Test departments
    try:
        response = requests.get(f"{base_url}/api/complaints/departments/", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Departments: {len(data)} loaded")
        else:
            print(f"⚠️ Departments: {response.status_code}")
    except Exception as e:
        print(f"❌ Departments: {str(e)[:30]}...")
    
    print()

def check_frontend():
    print("⚛️ Frontend Status (Vite + React):")
    print("-" * 35)
    
    # Test with different timeouts
    for timeout in [1, 3, 5]:
        try:
            response = requests.get("http://localhost:3000", timeout=timeout)
            if response.status_code == 200:
                content = response.text
                if "id=\"root\"" in content:
                    print(f"✅ React app: Running (timeout: {timeout}s)")
                    if "SmartGriev" in content:
                        print("✅ App content: SmartGriev detected")
                    break
                else:
                    print(f"⚠️ React structure: Not detected (timeout: {timeout}s)")
            else:
                print(f"⚠️ Frontend: Status {response.status_code} (timeout: {timeout}s)")
        except Exception as e:
            if timeout == 5:  # Last attempt
                print(f"❌ Frontend: {str(e)[:50]}...")
    
    print()

def show_urls():
    print("🌐 Application URLs:")
    print("-" * 20)
    print("• Frontend:    http://localhost:3000")
    print("• Backend API: http://127.0.0.1:8000/api/")
    print("• Admin Panel: http://127.0.0.1:8000/admin/")
    print("• Health Check: http://127.0.0.1:8000/api/complaints/api/health/")
    print()

def main():
    print_header()
    check_backend()
    check_frontend()
    show_urls()
    
    print("💡 Next Steps:")
    print("1. Test complaint submission on frontend")
    print("2. Verify multi-modal processing")
    print("3. Check department classification")
    print("4. Test authentication flow")

if __name__ == "__main__":
    main()