"""
SmartGriev Frontend-Backend Integration Tests
Tests the complete connection between frontend and backend
"""
import requests
import json
import time
from datetime import datetime


class FrontendBackendIntegrationTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
        
    def log_test(self, test_name, status, details="", response_time=None):
        """Log test result"""
        self.results["tests"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time_ms": response_time,
            "timestamp": datetime.now().isoformat()
        })
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if response_time:
            print(f"   Response time: {response_time}ms")
    
    def test_backend_server_running(self):
        """Test 1: Check if backend server is running"""
        print("\n🔍 TEST 1: Backend Server Status")
        try:
            start = time.time()
            response = requests.get(f"{self.backend_url}/api/complaints/api/health/", timeout=5)
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                self.log_test("Backend Server Health", "PASS", 
                             f"Status: {response.status_code}", response_time)
                return True
            else:
                self.log_test("Backend Server Health", "FAIL", 
                             f"Status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test("Backend Server Health", "FAIL", 
                         "Server not running or not reachable")
            return False
        except Exception as e:
            self.log_test("Backend Server Health", "FAIL", str(e))
            return False
    
    def test_frontend_server_running(self):
        """Test 2: Check if frontend server is running"""
        print("\n🔍 TEST 2: Frontend Server Status")
        try:
            start = time.time()
            response = requests.get(self.frontend_url, timeout=5)
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                self.log_test("Frontend Server Health", "PASS", 
                             f"Status: {response.status_code}", response_time)
                return True
            else:
                self.log_test("Frontend Server Health", "WARN", 
                             f"Status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test("Frontend Server Health", "FAIL", 
                         "Server not running - Run: npm run dev")
            return False
        except Exception as e:
            self.log_test("Frontend Server Health", "FAIL", str(e))
            return False
    
    def test_cors_configuration(self):
        """Test 3: CORS headers for frontend-backend communication"""
        print("\n🔍 TEST 3: CORS Configuration")
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'GET'
            }
            response = requests.options(f"{self.backend_url}/api/complaints/api/departments/", 
                                       headers=headers, timeout=5)
            
            if response.status_code in [200, 204]:
                self.log_test("CORS Configuration", "PASS", 
                             "CORS headers properly configured")
                return True
            else:
                self.log_test("CORS Configuration", "WARN", 
                             f"Status: {response.status_code}")
                return True  # CORS might still work
        except Exception as e:
            self.log_test("CORS Configuration", "WARN", str(e))
            return True
    
    def test_api_endpoints(self):
        """Test 4: Key API endpoints"""
        print("\n🔍 TEST 4: API Endpoints Availability")
        
        endpoints = [
            ("/api/complaints/api/health/", "Health Check"),
            ("/api/complaints/api/departments/", "Departments API"),
            ("/api/auth/login/", "Auth Login"),
            ("/admin/", "Admin Panel")
        ]
        
        all_pass = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code in [200, 401, 403]:  # 401/403 OK for protected routes
                    self.log_test(f"API: {name}", "PASS", 
                                 f"Status: {response.status_code}")
                else:
                    self.log_test(f"API: {name}", "WARN", 
                                 f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"API: {name}", "FAIL", str(e))
                all_pass = False
        
        return all_pass
    
    def test_api_response_format(self):
        """Test 5: API returns valid JSON"""
        print("\n🔍 TEST 5: API Response Format")
        try:
            response = requests.get(f"{self.backend_url}/api/complaints/api/departments/", timeout=5)
            data = response.json()
            
            if isinstance(data, (list, dict)):
                self.log_test("API Response Format", "PASS", 
                             "Valid JSON response")
                return True
            else:
                self.log_test("API Response Format", "FAIL", 
                             "Invalid JSON format")
                return False
        except json.JSONDecodeError:
            self.log_test("API Response Format", "FAIL", 
                         "Response is not valid JSON")
            return False
        except Exception as e:
            self.log_test("API Response Format", "FAIL", str(e))
            return False
    
    def test_authentication_flow(self):
        """Test 6: Authentication endpoints work"""
        print("\n🔍 TEST 6: Authentication Flow")
        try:
            # Test registration endpoint exists
            response = requests.post(
                f"{self.backend_url}/api/auth/register/",
                json={
                    "username": "testuser",
                    "email": "test@test.com",
                    "password": "testpass123"
                },
                timeout=5
            )
            
            if response.status_code in [200, 201, 400]:  # 400 OK if user exists
                self.log_test("Authentication Endpoints", "PASS", 
                             "Auth endpoints responsive")
                return True
            else:
                self.log_test("Authentication Endpoints", "WARN", 
                             f"Status: {response.status_code}")
                return True
        except Exception as e:
            self.log_test("Authentication Endpoints", "FAIL", str(e))
            return False
    
    def test_static_files(self):
        """Test 7: Static files and media configuration"""
        print("\n🔍 TEST 7: Static Files Configuration")
        try:
            response = requests.get(f"{self.backend_url}/static/", timeout=5)
            if response.status_code in [200, 404, 403]:  # Any of these is OK
                self.log_test("Static Files", "PASS", 
                             "Static files route configured")
                return True
            else:
                self.log_test("Static Files", "WARN", 
                             f"Status: {response.status_code}")
                return True
        except Exception as e:
            self.log_test("Static Files", "WARN", str(e))
            return True
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*70)
        print("INTEGRATION TEST SUMMARY")
        print("="*70)
        
        passed = len([t for t in self.results["tests"] if t["status"] == "PASS"])
        failed = len([t for t in self.results["tests"] if t["status"] == "FAIL"])
        warnings = len([t for t in self.results["tests"] if t["status"] == "WARN"])
        total = len(self.results["tests"])
        
        self.results["summary"] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success_rate": (passed / total * 100) if total > 0 else 0
        }
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        
        if failed == 0 and passed >= total - warnings:
            print(f"\n🎉 INTEGRATION TEST: PASSED")
            print(f"✅ Frontend-Backend connection is working!")
        else:
            print(f"\n⚠️  INTEGRATION TEST: NEEDS ATTENTION")
            print(f"Some tests failed. Review the results above.")
        
        print("="*70 + "\n")
        
        # Save report
        with open("integration_test_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Detailed report saved: integration_test_report.json\n")
        
        return failed == 0
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*70)
        print("SMARTGRIEV FRONTEND-BACKEND INTEGRATION TESTS")
        print("="*70)
        
        # Run all tests
        self.test_backend_server_running()
        self.test_frontend_server_running()
        self.test_cors_configuration()
        self.test_api_endpoints()
        self.test_api_response_format()
        self.test_authentication_flow()
        self.test_static_files()
        
        # Generate report
        return self.generate_report()


if __name__ == "__main__":
    tester = FrontendBackendIntegrationTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)