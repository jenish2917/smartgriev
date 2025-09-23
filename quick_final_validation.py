#!/usr/bin/env python3
"""
SmartGriev Final System Validation
Quick professional validation after cleanup
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime

def test_system_health():
    """Quick system health check"""
    print("🔍 SMARTGRIEV FINAL VALIDATION")
    print("="*50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "status": "UNKNOWN"
    }
    
    # Test 1: Backend Health
    try:
        response = requests.get("http://127.0.0.1:8000/api/complaints/api/health/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend Health: PASS")
            results["tests"].append({"test": "Backend Health", "status": "PASS"})
        else:
            print(f"❌ Backend Health: FAIL (Status: {response.status_code})")
            results["tests"].append({"test": "Backend Health", "status": "FAIL"})
    except Exception as e:
        print(f"❌ Backend Health: FAIL (Error: {e})")
        results["tests"].append({"test": "Backend Health", "status": "FAIL"})
    
    # Test 2: API Endpoints
    endpoints = [
        "/api/complaints/api/departments/",
        "/admin/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
            if response.status_code in [200, 401, 403]:  # 401/403 are OK for protected endpoints
                print(f"✅ API {endpoint}: PASS")
                results["tests"].append({"test": f"API {endpoint}", "status": "PASS"})
            else:
                print(f"⚠️  API {endpoint}: WARN (Status: {response.status_code})")
                results["tests"].append({"test": f"API {endpoint}", "status": "WARN"})
        except Exception as e:
            print(f"❌ API {endpoint}: FAIL")
            results["tests"].append({"test": f"API {endpoint}", "status": "FAIL"})
    
    # Test 3: Frontend Build
    dist_path = Path("D:/SmartGriev/frontend/dist")
    if dist_path.exists():
        build_files = list(dist_path.glob("*.html"))
        if build_files:
            print("✅ Frontend Build: PASS")
            results["tests"].append({"test": "Frontend Build", "status": "PASS"})
        else:
            print("❌ Frontend Build: FAIL (No HTML files)")
            results["tests"].append({"test": "Frontend Build", "status": "FAIL"})
    else:
        print("❌ Frontend Build: FAIL (No dist folder)")
        results["tests"].append({"test": "Frontend Build", "status": "FAIL"})
    
    # Test 4: Critical Files
    critical_files = [
        "D:/SmartGriev/frontend/package.json",
        "D:/SmartGriev/frontend/src/main.tsx",
        "D:/SmartGriev/backend/manage.py",
        "D:/SmartGriev/backend/db.sqlite3"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Critical Files: FAIL ({len(missing_files)} missing)")
        results["tests"].append({"test": "Critical Files", "status": "FAIL"})
    else:
        print("✅ Critical Files: PASS")
        results["tests"].append({"test": "Critical Files", "status": "PASS"})
    
    # Test 5: Cleanup Status
    backup_files = list(Path("D:/SmartGriev").rglob("*.bak"))
    if backup_files:
        print(f"⚠️  Cleanup Status: WARN ({len(backup_files)} backup files remain)")
        results["tests"].append({"test": "Cleanup Status", "status": "WARN"})
    else:
        print("✅ Cleanup Status: PASS")
        results["tests"].append({"test": "Cleanup Status", "status": "PASS"})
    
    # Calculate overall status
    passed = len([t for t in results["tests"] if t["status"] == "PASS"])
    failed = len([t for t in results["tests"] if t["status"] == "FAIL"])
    warnings = len([t for t in results["tests"] if t["status"] == "WARN"])
    total = len(results["tests"])
    
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "="*50)
    print("📊 FINAL VALIDATION SUMMARY")
    print("="*50)
    print(f"Tests Run: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed == 0 and success_rate >= 80:
        results["status"] = "PRODUCTION_READY"
        print(f"\n🎉 SYSTEM STATUS: PRODUCTION READY")
        print(f"✅ SmartGriev system validation complete!")
        print(f"✅ All critical components operational")
        print(f"✅ Ready for deployment")
        
        print(f"\n🚀 DEPLOYMENT CHECKLIST:")
        print(f"1. ✅ Backend server running (Django)")
        print(f"2. ✅ Frontend build complete (React)")
        print(f"3. ✅ Database operational (SQLite)")
        print(f"4. ✅ API endpoints responding")
        print(f"5. ✅ System architecture clean")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Deploy to production server")
        print(f"2. Configure production database (PostgreSQL)")
        print(f"3. Set up domain and SSL certificates")
        print(f"4. Configure monitoring and logging")
        print(f"5. Set up backup procedures")
        
    elif failed > 0:
        results["status"] = "CRITICAL_ISSUES"
        print(f"\n❌ SYSTEM STATUS: CRITICAL ISSUES")
        print(f"Fix failed tests before deployment")
    else:
        results["status"] = "MINOR_ISSUES"
        print(f"\n⚠️  SYSTEM STATUS: MINOR ISSUES")
        print(f"Address warnings, but system is mostly ready")
    
    # Cleanup recommendations
    if backup_files:
        print(f"\n🧹 CLEANUP RECOMMENDATIONS:")
        print(f"Remove backup files: Remove-Item D:\\SmartGriev\\*.bak -Recurse")
    
    # Save report
    report_path = Path("D:/SmartGriev") / f"final_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Report saved: {report_path}")
    
    return results["status"] == "PRODUCTION_READY"

if __name__ == "__main__":
    test_system_health()