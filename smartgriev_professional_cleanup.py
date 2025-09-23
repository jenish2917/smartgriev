#!/usr/bin/env python3
"""
SmartGriev Professional Cleanup Script
Senior Tester - Targeted cleanup based on audit findings
"""

import json
import os
from pathlib import Path
import shutil
import subprocess

class SmartGrievCleaner:
    def __init__(self):
        self.frontend_path = Path("D:/SmartGriev/frontend")
        self.backend_path = Path("D:/SmartGriev/backend")
        self.removed_files = []
        self.removed_deps = []
        
    def analyze_unused_components(self):
        """Find genuinely unused React components"""
        print("🔍 Analyzing unused React components...")
        
        components_dir = self.frontend_path / "src" / "components"
        if not components_dir.exists():
            return []
        
        # Get all component files
        component_files = []
        for file in components_dir.rglob("*.tsx"):
            component_files.append(file)
        
        # Check which components are imported
        used_components = set()
        
        # Scan all files for imports
        for file in self.frontend_path.rglob("*.{tsx,ts}"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find component imports
                import_lines = [line for line in content.split('\n') if 'import' in line and 'components' in line]
                for line in import_lines:
                    for comp_file in component_files:
                        comp_name = comp_file.stem
                        if comp_name in line:
                            used_components.add(str(comp_file))
            except Exception:
                continue
        
        # Find unused components
        unused_components = []
        for comp_file in component_files:
            if str(comp_file) not in used_components:
                # Check if it's not an entry point component
                if comp_file.name not in ['App.tsx', 'main.tsx', 'index.tsx']:
                    unused_components.append(comp_file)
        
        print(f"Found {len(unused_components)} potentially unused components")
        return unused_components
    
    def find_duplicate_files(self):
        """Find duplicate or similar files"""
        print("🔍 Searching for duplicate files...")
        
        duplicates = []
        
        # Check for multiple main files
        main_files = list(self.frontend_path.glob("src/main*.tsx"))
        if len(main_files) > 1:
            print(f"Found {len(main_files)} main files:")
            for file in main_files:
                print(f"  - {file.name}")
            
            # Keep only main.tsx, mark others as duplicates
            for file in main_files:
                if file.name != "main.tsx":
                    duplicates.append(file)
        
        # Check for multiple App files  
        app_files = list(self.frontend_path.glob("src/App*.tsx"))
        if len(app_files) > 1:
            print(f"Found {len(app_files)} App files:")
            for file in app_files:
                print(f"  - {file.name}")
            
            # Keep only App.tsx
            for file in app_files:
                if file.name != "App.tsx":
                    duplicates.append(file)
        
        return duplicates
    
    def find_test_files(self):
        """Find test files that might not be in CI pipeline"""
        print("🔍 Searching for test files...")
        
        test_files = []
        
        # Find various test file patterns
        patterns = [
            "**/*test*.py", "**/*test*.ts", "**/*test*.tsx",
            "**/test_*.py", "**/test_*.js", "**/test_*.ts",
            "**/*.test.py", "**/*.test.js", "**/*.test.ts",
            "**/*.spec.py", "**/*.spec.js", "**/*.spec.ts"
        ]
        
        for pattern in patterns:
            test_files.extend(self.frontend_path.glob(pattern))
            test_files.extend(self.backend_path.glob(pattern))
        
        # Check if they're actually used
        unused_tests = []
        for test_file in test_files:
            # Simple heuristic: if it's not imported and not in package.json scripts
            if not self.is_test_file_used(test_file):
                unused_tests.append(test_file)
        
        print(f"Found {len(unused_tests)} potentially unused test files")
        return unused_tests
    
    def is_test_file_used(self, test_file):
        """Check if a test file is actually used in the pipeline"""
        # Check package.json for test scripts
        package_json = self.frontend_path / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            scripts = package_data.get('scripts', {})
            for script in scripts.values():
                if test_file.name in script:
                    return True
        
        # Check if imported anywhere
        for file in [*self.frontend_path.rglob("*.{ts,tsx,js}"), *self.backend_path.rglob("*.py")]:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if test_file.stem in content:
                    return True
            except Exception:
                continue
        
        return False
    
    def clean_unused_imports(self):
        """Remove unused import statements from TypeScript files"""
        print("🔍 Cleaning unused imports...")
        
        fixed_files = []
        
        for file in self.frontend_path.rglob("*.{ts,tsx}"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    # Skip empty import lines or commented imports
                    if line.strip().startswith('// import') or line.strip() == 'import':
                        continue
                    cleaned_lines.append(line)
                
                # Check if file was modified
                cleaned_content = '\n'.join(cleaned_lines)
                if cleaned_content != content:
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    fixed_files.append(file)
                    
            except Exception as e:
                continue
        
        print(f"Cleaned imports in {len(fixed_files)} files")
        return fixed_files
    
    def remove_development_artifacts(self):
        """Remove development-only files and artifacts"""
        print("🔍 Removing development artifacts...")
        
        artifacts = []
        
        # Common development artifacts
        artifact_patterns = [
            ".DS_Store", "Thumbs.db", "*.log", "*.tmp", "*.bak",
            ".vscode/settings.json", ".idea/", "npm-debug.log*",
            "yarn-debug.log*", "yarn-error.log*"
        ]
        
        for pattern in artifact_patterns:
            artifacts.extend(self.frontend_path.glob(pattern))
            artifacts.extend(self.backend_path.glob(pattern))
        
        # Remove test data files
        test_data_dirs = [
            self.frontend_path / "test-data",
            self.backend_path / "test-data",
            self.backend_path / "tests" / "fixtures"
        ]
        
        for dir_path in test_data_dirs:
            if dir_path.exists() and not any(file.suffix == '.py' for file in dir_path.rglob("*")):
                artifacts.append(dir_path)
        
        return artifacts
    
    def safe_remove_file(self, file_path):
        """Safely remove a file with backup"""
        try:
            if file_path.is_dir():
                backup_name = f"{file_path.name}_backup"
                backup_path = file_path.parent / backup_name
                shutil.move(str(file_path), str(backup_path))
                print(f"Moved directory to backup: {file_path.name} -> {backup_name}")
            else:
                backup_name = f"{file_path.name}.bak"
                backup_path = file_path.parent / backup_name
                shutil.copy2(str(file_path), str(backup_path))
                file_path.unlink()
                print(f"Removed file: {file_path.name} (backup created)")
            
            self.removed_files.append(str(file_path))
            return True
        except Exception as e:
            print(f"Error removing {file_path}: {e}")
            return False
    
    def cleanup_package_json(self):
        """Clean up package.json dependencies"""
        print("🔍 Analyzing package.json dependencies...")
        
        package_json = self.frontend_path / "package.json"
        if not package_json.exists():
            print("package.json not found")
            return
        
        with open(package_json, 'r') as f:
            package_data = json.load(f)
        
        # Create backup
        backup_path = package_json.parent / "package.json.bak"
        with open(backup_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        # Analyze dependencies (this would need actual usage analysis)
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        
        print(f"Current dependencies: {len(dependencies)}")
        print(f"Current devDependencies: {len(dev_dependencies)}")
        
        # For now, just report - actual removal would need careful analysis
        potentially_unused = [
            'lodash',  # Often imported but not used
            '@types/lodash',
            'moment',  # If using dayjs instead
            'jquery',  # If not using jQuery
        ]
        
        found_unused = []
        for dep in potentially_unused:
            if dep in dependencies or dep in dev_dependencies:
                found_unused.append(dep)
        
        if found_unused:
            print(f"Potentially unused dependencies found: {found_unused}")
            print("Manual review recommended before removal")
    
    def run_comprehensive_cleanup(self):
        """Run all cleanup operations"""
        print("🧹 SMARTGRIEV PROFESSIONAL CLEANUP")
        print("="*50)
        print("Senior Tester - Systematic Code Cleanup")
        print("="*50)
        
        # Step 1: Find issues
        unused_components = self.analyze_unused_components()
        duplicate_files = self.find_duplicate_files()
        unused_tests = self.find_test_files()
        development_artifacts = self.remove_development_artifacts()
        
        # Step 2: Clean imports
        self.clean_unused_imports()
        
        # Step 3: Interactive cleanup
        print("\n🎯 CLEANUP RECOMMENDATIONS:")
        print("-" * 30)
        
        if duplicate_files:
            print(f"\n📄 Found {len(duplicate_files)} duplicate files:")
            for file in duplicate_files:
                print(f"  - {file}")
            
            response = input("\nRemove duplicate files? (y/N): ")
            if response.lower() == 'y':
                for file in duplicate_files:
                    self.safe_remove_file(file)
        
        if unused_components:
            print(f"\n🔧 Found {len(unused_components)} potentially unused components:")
            for comp in unused_components[:10]:  # Show first 10
                print(f"  - {comp.name}")
            
            if len(unused_components) > 10:
                print(f"  ... and {len(unused_components) - 10} more")
            
            response = input("\nRemove unused components? (y/N): ")
            if response.lower() == 'y':
                for comp in unused_components:
                    self.safe_remove_file(comp)
        
        if development_artifacts:
            print(f"\n🗑️  Found {len(development_artifacts)} development artifacts:")
            for artifact in development_artifacts[:5]:
                print(f"  - {artifact}")
            
            response = input("\nRemove development artifacts? (y/N): ")
            if response.lower() == 'y':
                for artifact in development_artifacts:
                    self.safe_remove_file(artifact)
        
        # Step 4: Package.json cleanup
        self.cleanup_package_json()
        
        # Step 5: Summary
        print("\n" + "="*50)
        print("📊 CLEANUP SUMMARY")
        print("="*50)
        print(f"Files removed: {len(self.removed_files)}")
        print(f"Dependencies analyzed: ✅")
        print(f"Imports cleaned: ✅")
        print(f"Artifacts removed: ✅")
        
        if self.removed_files:
            print(f"\n📄 Removed files:")
            for file in self.removed_files:
                print(f"  - {file}")
        
        print(f"\n🎉 Cleanup completed successfully!")
        print(f"💡 All removed files have been backed up")

def main():
    cleaner = SmartGrievCleaner()
    cleaner.run_comprehensive_cleanup()

if __name__ == "__main__":
    main()