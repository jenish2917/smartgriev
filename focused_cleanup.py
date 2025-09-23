#!/usr/bin/env python3
"""
SmartGriev Focused Cleanup Script
Based on professional audit findings - removes duplicate and unused files
"""

import os
import shutil
from pathlib import Path

def cleanup_duplicate_files():
    """Remove duplicate main and app files"""
    print("🔍 Cleaning up duplicate files...")
    
    frontend_path = Path("D:/SmartGriev/frontend")
    
    # Files to remove (keeping main.tsx and App.tsx as primary)
    files_to_remove = [
        "src/main-integrated.tsx",
        "src/main-simple.tsx", 
        "src/AppIntegrated.tsx"
    ]
    
    removed = []
    for file_rel_path in files_to_remove:
        file_path = frontend_path / file_rel_path
        if file_path.exists():
            try:
                # Create backup
                backup_path = file_path.parent / f"{file_path.name}.bak"
                shutil.copy2(file_path, backup_path)
                
                # Remove original
                file_path.unlink()
                removed.append(file_rel_path)
                print(f"✅ Removed: {file_rel_path} (backup created)")
            except Exception as e:
                print(f"❌ Error removing {file_rel_path}: {e}")
    
    return removed

def cleanup_test_artifacts():
    """Remove test files that are not in the pipeline"""
    print("🔍 Cleaning up test artifacts...")
    
    # Test files that can be safely removed
    test_files = [
        "D:/SmartGriev/test_complete_system.py",
        "D:/SmartGriev/test_fullstack_integration.py", 
        "D:/SmartGriev/quick_test.py",
        "D:/SmartGriev/core_validation.py",
        "D:/SmartGriev/professional_system_audit.py",
        "D:/SmartGriev/deployment_summary.py"
    ]
    
    removed = []
    for file_path_str in test_files:
        file_path = Path(file_path_str)
        if file_path.exists():
            try:
                # Create backup
                backup_path = file_path.parent / f"{file_path.name}.bak"
                shutil.copy2(file_path, backup_path)
                
                # Remove original
                file_path.unlink()
                removed.append(file_path.name)
                print(f"✅ Removed: {file_path.name} (backup created)")
            except Exception as e:
                print(f"❌ Error removing {file_path.name}: {e}")
    
    return removed

def cleanup_documentation_drafts():
    """Remove draft documentation files"""
    print("🔍 Cleaning up documentation drafts...")
    
    doc_files = [
        "D:/SmartGriev/NAMING_CONVENTIONS.md",
        "D:/SmartGriev/PROFESSIONAL_NAMING_COMPLETE.md",
        "D:/SmartGriev/CLEANUP_REPORT.md"
    ]
    
    removed = []
    for file_path_str in doc_files:
        file_path = Path(file_path_str)
        if file_path.exists():
            try:
                # Create backup
                backup_path = file_path.parent / f"{file_path.name}.bak"
                shutil.copy2(file_path, backup_path)
                
                # Remove original
                file_path.unlink()
                removed.append(file_path.name)
                print(f"✅ Removed: {file_path.name} (backup created)")
            except Exception as e:
                print(f"❌ Error removing {file_path.name}: {e}")
    
    return removed

def cleanup_unused_backend_files():
    """Remove unused backend test files"""
    print("🔍 Cleaning up unused backend files...")
    
    backend_files = [
        "D:/SmartGriev/backend/basic_functionality_test.py",
        "D:/SmartGriev/backend/comprehensive_system_test.py",
        "D:/SmartGriev/backend/system_integration_test.py"
    ]
    
    removed = []
    for file_path_str in backend_files:
        file_path = Path(file_path_str)
        if file_path.exists():
            try:
                # Create backup
                backup_path = file_path.parent / f"{file_path.name}.bak"
                shutil.copy2(file_path, backup_path)
                
                # Remove original
                file_path.unlink()
                removed.append(file_path.name)
                print(f"✅ Removed: {file_path.name} (backup created)")
            except Exception as e:
                print(f"❌ Error removing {file_path.name}: {e}")
    
    return removed

def cleanup_generated_reports():
    """Remove generated report files"""
    print("🔍 Cleaning up generated reports...")
    
    # Find all generated report files
    root_path = Path("D:/SmartGriev")
    report_patterns = [
        "smartgriev_*_report_*.json",
        "smartgriev_audit_report.json",
        "smartgriev_cleanup.py"
    ]
    
    removed = []
    for pattern in report_patterns:
        for file_path in root_path.glob(pattern):
            try:
                file_path.unlink()
                removed.append(file_path.name)
                print(f"✅ Removed: {file_path.name}")
            except Exception as e:
                print(f"❌ Error removing {file_path.name}: {e}")
    
    return removed

def verify_core_files():
    """Verify that core files are still present"""
    print("🔍 Verifying core files are intact...")
    
    core_files = [
        "D:/SmartGriev/frontend/src/main.tsx",
        "D:/SmartGriev/frontend/src/App.tsx", 
        "D:/SmartGriev/frontend/package.json",
        "D:/SmartGriev/backend/manage.py",
        "D:/SmartGriev/backend/smartgriev/settings.py"
    ]
    
    all_present = True
    for file_path_str in core_files:
        file_path = Path(file_path_str)
        if file_path.exists():
            print(f"✅ Core file present: {file_path.name}")
        else:
            print(f"❌ MISSING core file: {file_path.name}")
            all_present = False
    
    return all_present

def main():
    print("🧹 SMARTGRIEV FOCUSED CLEANUP")
    print("="*50)
    print("Removing duplicate files and test artifacts")
    print("="*50)
    
    # Run cleanup operations
    duplicate_files = cleanup_duplicate_files()
    test_files = cleanup_test_artifacts()
    doc_files = cleanup_documentation_drafts()
    backend_files = cleanup_unused_backend_files()
    report_files = cleanup_generated_reports()
    
    # Verify core files
    print("\n" + "="*50)
    core_intact = verify_core_files()
    
    # Summary
    print("\n" + "="*50)
    print("📊 CLEANUP SUMMARY")
    print("="*50)
    
    total_removed = len(duplicate_files) + len(test_files) + len(doc_files) + len(backend_files) + len(report_files)
    
    print(f"Duplicate files removed: {len(duplicate_files)}")
    print(f"Test artifacts removed: {len(test_files)}")
    print(f"Documentation drafts removed: {len(doc_files)}")
    print(f"Backend test files removed: {len(backend_files)}")
    print(f"Generated reports removed: {len(report_files)}")
    print(f"Total files removed: {total_removed}")
    
    if core_intact:
        print(f"✅ All core system files intact")
    else:
        print(f"⚠️  Some core files missing - check system")
    
    print(f"\n🎉 Focused cleanup completed!")
    print(f"💡 All removed files have been backed up with .bak extension")
    
    # Final recommendations
    print(f"\n📋 NEXT STEPS:")
    print(f"1. Test the system to ensure everything still works")
    print(f"2. Remove .bak files if system is stable")
    print(f"3. Run npm run build to verify frontend builds")
    print(f"4. Run backend tests to verify backend works")

if __name__ == "__main__":
    main()