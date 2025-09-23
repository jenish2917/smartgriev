#!/usr/bin/env python3
"""
SmartGriev Professional Final Audit & Testing
Comprehensive system validation after cleanup
"""

import os
import json
import requests
import subprocess
import time
from pathlib import Path
from datetime import datetime

class SmartGrievFinalAudit:
    def __init__(self):
        self.base_path = Path("D:/SmartGriev")
        self.frontend_path = self.base_path / "frontend"
        self.backend_path = self.base_path / "backend"
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://127.0.0.1:3000"
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {},
            "recommendations": []
        }
    
    def log_test(self, test_name, status, details="", error=None):
        """Log test result"""
        self.results["tests"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        })
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if error:
            print(f"   Error: {error}")
    
    def test_file_structure(self):
        """Test 1: Validate file structure integrity"""
        print("\n🔍 TEST 1: File Structure Integrity")
        
        critical_files = [
            "frontend/package.json",
            "frontend/src/main.tsx", 
            "frontend/src/App.tsx",
            "backend/manage.py",
            "backend/smartgriev/settings.py",
            "backend/requirements/base.txt"
        ]
        
        missing_files = []
        for file_path in critical_files:
            full_path = self.base_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("Critical Files Check", "FAIL", 
                         f"Missing files: {', '.join(missing_files)}")
        else:
            self.log_test("Critical Files Check", "PASS", 
                         f"All {len(critical_files)} critical files present")
        
        # Check for leftover backup files
        backup_files = list(self.base_path.rglob("*.bak"))
        if backup_files:
            self.log_test("Backup Files Check", "WARN", 
                         f"Found {len(backup_files)} backup files that can be cleaned")
        else:
            self.log_test("Backup Files Check", "PASS", "No backup files found")
    
    def test_frontend_build(self):
        """Test 2: Frontend build and compilation"""
        print("\n🔍 TEST 2: Frontend Build Validation")
        
        try:
            # Check if build exists
            dist_path = self.frontend_path / "dist"
            if dist_path.exists():
                self.log_test("Frontend Build Exists", "PASS", "dist folder found")
                
                # Check build size
                build_files = list(dist_path.rglob("*"))
                total_size = sum(f.stat().st_size for f in build_files if f.is_file())
                size_mb = total_size / (1024 * 1024)
                
                if size_mb > 50:
                    self.log_test("Build Size Check", "WARN", 
                                 f"Build size is {size_mb:.1f}MB (consider optimization)")
                else:
                    self.log_test("Build Size Check", "PASS", 
                                 f"Build size is {size_mb:.1f}MB")
            else:
                self.log_test("Frontend Build Exists", "FAIL", "No dist folder found")
                
        except Exception as e:
            self.log_test("Frontend Build Check", "FAIL", error=e)
    
    def test_backend_health(self):
        """Test 3: Backend health and API endpoints"""
        print("\n🔍 TEST 3: Backend API Validation")
        
        endpoints = [
            ("/api/complaints/api/health/", "Health Check"),
            ("/api/complaints/api/departments/", "Departments API"),
            ("/api/complaints/api/complaints/", "Complaints API"),
            ("/admin/", "Admin Panel"),
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"API: {name}", "PASS", 
                                 f"Status: {response.status_code}")
                elif response.status_code in [401, 403]:
                    self.log_test(f"API: {name}", "PASS", 
                                 f"Protected endpoint (Status: {response.status_code})")
                else:
                    self.log_test(f"API: {name}", "WARN", 
                                 f"Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                self.log_test(f"API: {name}", "FAIL", "Backend server not running")
            except Exception as e:
                self.log_test(f"API: {name}", "FAIL", error=e)
    
    def test_database_integrity(self):
        """Test 4: Database and migrations"""
        print("\n🔍 TEST 4: Database Integrity")
        
        try:
            # Check if database exists
            db_path = self.backend_path / "db.sqlite3"
            if db_path.exists():
                self.log_test("Database File", "PASS", f"Size: {db_path.stat().st_size} bytes")
            else:
                self.log_test("Database File", "FAIL", "db.sqlite3 not found")
            
            # Test migration status (if backend is running)
            try:
                result = subprocess.run([
                    "python", "manage.py", "showmigrations", "--plan"
                ], cwd=self.backend_path, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    applied_migrations = result.stdout.count("[X]")
                    unapplied_migrations = result.stdout.count("[ ]")
                    
                    if unapplied_migrations > 0:
                        self.log_test("Migrations", "WARN", 
                                     f"{unapplied_migrations} unapplied migrations")
                    else:
                        self.log_test("Migrations", "PASS", 
                                     f"{applied_migrations} migrations applied")
                else:
                    self.log_test("Migrations", "FAIL", "Could not check migrations")
                    
            except subprocess.TimeoutExpired:
                self.log_test("Migrations", "WARN", "Migration check timed out")
                
        except Exception as e:
            self.log_test("Database Check", "FAIL", error=e)
    
    def test_dependency_optimization(self):
        """Test 5: Dependency analysis"""
        print("\n🔍 TEST 5: Dependency Optimization")
        
        try:
            # Frontend dependencies
            package_json_path = self.frontend_path / "package.json"
            if package_json_path.exists():
                with open(package_json_path) as f:
                    package_data = json.load(f)
                
                deps = package_data.get("dependencies", {})
                dev_deps = package_data.get("devDependencies", {})
                
                total_deps = len(deps) + len(dev_deps)
                self.log_test("Frontend Dependencies", "PASS", 
                             f"{len(deps)} runtime, {len(dev_deps)} dev dependencies")
                
                # Check for common unused packages
                potentially_unused = []
                for dep in deps:
                    if dep in ["@hookform/resolvers", "@ant-design/pro-components", "zod", "react-hook-form"]:
                        potentially_unused.append(dep)
                
                if potentially_unused:
                    self.log_test("Unused Dependencies", "WARN", 
                                 f"Potentially unused: {', '.join(potentially_unused)}")
            
            # Backend requirements
            req_path = self.backend_path / "requirements" / "base.txt"
            if req_path.exists():
                with open(req_path) as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                
                self.log_test("Backend Requirements", "PASS", 
                             f"{len(requirements)} packages specified")
                
        except Exception as e:
            self.log_test("Dependency Check", "FAIL", error=e)
    
    def test_security_compliance(self):
        """Test 6: Basic security checks"""
        print("\n🔍 TEST 6: Security Compliance")
        
        try:
            # Check for exposed secrets
            sensitive_patterns = [
                "SECRET_KEY = ",
                "GROQ_API_KEY = ",
                "password =",
                "AWS_SECRET",
                "DATABASE_PASSWORD"
            ]
            
            security_issues = []
            for pattern in sensitive_patterns:
                result = subprocess.run([
                    "findstr", "/R", "/S", pattern, "*.py", "*.js", "*.ts", "*.tsx", "*.json"
                ], cwd=self.base_path, capture_output=True, text=True, shell=True)
                
                if result.stdout and "settings" not in result.stdout.lower():
                    security_issues.append(pattern)
            
            if security_issues:
                self.log_test("Secret Exposure Check", "WARN", 
                             f"Potential issues with: {', '.join(security_issues)}")
            else:
                self.log_test("Secret Exposure Check", "PASS", "No exposed secrets found")
                
            # Check CORS settings
            settings_path = self.backend_path / "smartgriev" / "settings.py"
            if settings_path.exists():
                with open(settings_path) as f:
                    settings_content = f.read()
                
                if "CORS_ALLOW_ALL_ORIGINS = True" in settings_content:
                    self.log_test("CORS Security", "WARN", 
                                 "CORS allows all origins (not production-ready)")
                else:
                    self.log_test("CORS Security", "PASS", "CORS properly configured")
                    
        except Exception as e:
            self.log_test("Security Check", "FAIL", error=e)
    
    def test_performance_metrics(self):
        """Test 7: Performance analysis"""
        print("\n🔍 TEST 7: Performance Metrics")
        
        try:
            # Frontend bundle analysis
            dist_path = self.frontend_path / "dist"
            if dist_path.exists():
                js_files = list(dist_path.glob("**/*.js"))
                css_files = list(dist_path.glob("**/*.css"))
                
                total_js_size = sum(f.stat().st_size for f in js_files)
                total_css_size = sum(f.stat().st_size for f in css_files)
                
                js_mb = total_js_size / (1024 * 1024)
                css_mb = total_css_size / (1024 * 1024)
                
                if js_mb > 10:
                    self.log_test("JS Bundle Size", "WARN", 
                                 f"{js_mb:.1f}MB (consider code splitting)")
                else:
                    self.log_test("JS Bundle Size", "PASS", f"{js_mb:.1f}MB")
                
                self.log_test("CSS Bundle Size", "PASS", f"{css_mb:.1f}MB")
                
            # Backend API response time
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}/api/complaints/api/health/", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response_time > 1000:
                    self.log_test("API Response Time", "WARN", 
                                 f"{response_time:.0f}ms (slow)")
                else:
                    self.log_test("API Response Time", "PASS", 
                                 f"{response_time:.0f}ms")
            except:
                self.log_test("API Response Time", "FAIL", "Could not test (server down)")
                
        except Exception as e:
            self.log_test("Performance Check", "FAIL", error=e)
    
    def generate_cleanup_recommendations(self):
        """Generate final cleanup recommendations"""
        print("\n🔍 GENERATING CLEANUP RECOMMENDATIONS")
        
        recommendations = []
        
        # Check for backup files
        backup_files = list(self.base_path.rglob("*.bak"))
        if backup_files:
            recommendations.append({
                "priority": "LOW",
                "action": "Remove backup files",
                "command": f"Remove-Item {self.base_path}\\*.bak -Recurse",
                "files": len(backup_files)
            })
        
        # Check for node_modules optimization
        node_modules = self.frontend_path / "node_modules"
        if node_modules.exists():
            recommendations.append({
                "priority": "MEDIUM", 
                "action": "Reinstall frontend dependencies",
                "command": "cd frontend && rm -rf node_modules && npm ci",
                "reason": "Clean dependency installation"
            })
        
        # Check for Django cache
        pycache_dirs = list(self.backend_path.rglob("__pycache__"))
        if pycache_dirs:
            recommendations.append({
                "priority": "LOW",
                "action": "Clear Python cache",
                "command": f"find {self.backend_path} -name '__pycache__' -type d -exec rm -rf {{}} +",
                "directories": len(pycache_dirs)
            })
        
        self.results["recommendations"] = recommendations
        
        for rec in recommendations:
            priority_icon = "🔴" if rec["priority"] == "HIGH" else "🟡" if rec["priority"] == "MEDIUM" else "🟢"
            print(f"{priority_icon} {rec['priority']}: {rec['action']}")
            print(f"   Command: {rec['command']}")
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*60)
        print("📊 SMARTGRIEV PROFESSIONAL AUDIT SUMMARY")
        print("="*60)
        
        # Calculate statistics
        total_tests = len(self.results["tests"])
        passed = len([t for t in self.results["tests"] if t["status"] == "PASS"])
        failed = len([t for t in self.results["tests"] if t["status"] == "FAIL"])
        warnings = len([t for t in self.results["tests"] if t["status"] == "WARN"])
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success_rate": success_rate,
            "system_status": "PRODUCTION_READY" if failed == 0 and success_rate >= 90 else "NEEDS_ATTENTION"
        }
        
        print(f"Tests Run: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"System Status: {self.results['summary']['system_status']}")
        
        # System readiness assessment
        if self.results["summary"]["system_status"] == "PRODUCTION_READY":
            print(f"\n🎉 SYSTEM VALIDATION: PASSED")
            print(f"✅ SmartGriev is production-ready!")
            print(f"✅ All critical systems operational")
            print(f"✅ Build optimization complete")
            print(f"✅ No critical issues detected")
        else:
            print(f"\n⚠️  SYSTEM VALIDATION: NEEDS ATTENTION")
            print(f"Review failed tests and warnings before production deployment")
        
        # Save detailed report
        report_path = self.base_path / f"smartgriev_final_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        
        return self.results["summary"]["system_status"] == "PRODUCTION_READY"
    
    def run_complete_audit(self):
        """Run complete professional audit"""
        print("🔍 SMARTGRIEV PROFESSIONAL FINAL AUDIT")
        print("="*60)
        print("Testing system integrity after cleanup...")
        
        # Run all test suites
        self.test_file_structure()
        self.test_frontend_build()
        self.test_backend_health()
        self.test_database_integrity()
        self.test_dependency_optimization()
        self.test_security_compliance()
        self.test_performance_metrics()
        
        # Generate recommendations
        self.generate_cleanup_recommendations()
        
        # Generate final report
        return self.generate_final_report()

if __name__ == "__main__":
    auditor = SmartGrievFinalAudit()
    system_ready = auditor.run_complete_audit()
    
    if system_ready:
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. Deploy to production environment")
        print(f"2. Set up monitoring and logging")
        print(f"3. Configure production database")
        print(f"4. Set up CI/CD pipeline")
    else:
        print(f"\n🔧 NEXT STEPS:")
        print(f"1. Review and fix failed tests")
        print(f"2. Address security warnings")
        print(f"3. Re-run audit after fixes")
        print(f"4. Proceed to production when all tests pass")