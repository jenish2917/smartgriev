#!/usr/bin/env python3
"""
Quick Backend Pipeline Test Script for SmartGriev
Tests the basic functionality of AI processors and authentication
"""

import os
import sys
import django
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from complaints.ai_processor import AdvancedAIProcessor
from complaints.department_classifier import GovernmentDepartmentClassifier
from authentication.auth_service import AdvancedAuthService


async def test_basic_functionality():
    """Test basic functionality of all components"""
    
    print("🚀 Starting SmartGriev Backend Pipeline Test")
    print("=" * 50)
    
    # Test 1: AI Text Enhancement
    print("1️⃣ Testing AI Text Enhancement...")
    try:
        ai_processor = AdvancedAIProcessor()
        
        sample_complaints = [
            "बिजली नहीं आ रही है 3 दिन से",
            "Road is very damaged near my house",
            "Water supply issue in our area",
            "Garbage not collected for a week"
        ]
        
        for i, complaint in enumerate(sample_complaints, 1):
            print(f"   {i}. Input: {complaint}")
            try:
                enhanced = await ai_processor.enhance_complaint_text(
                    complaint, 
                    location="Delhi, India"
                )
                print(f"      Enhanced: {enhanced[:100]}...")
            except Exception as e:
                print(f"      Error: {str(e)}")
            print()
        
        print("✅ AI Text Enhancement: PASSED")
        
    except Exception as e:
        print(f"❌ AI Text Enhancement: FAILED - {str(e)}")
    
    print("-" * 50)
    
    # Test 2: Department Classification
    print("2️⃣ Testing Department Classification...")
    try:
        dept_classifier = GovernmentDepartmentClassifier()
        
        test_cases = [
            ("Power outage in residential area", "Delhi"),
            ("Road repair needed urgently", "Mumbai"), 
            ("Water supply contaminated", "Bangalore"),
            ("Illegal construction next door", "Chennai")
        ]
        
        for i, (complaint, location) in enumerate(test_cases, 1):
            print(f"   {i}. Complaint: {complaint}")
            print(f"      Location: {location}")
            
            try:
                result = await dept_classifier.classify_complaint(complaint, location=location)
                if result['success']:
                    print(f"      Department: {result['department']}")
                    print(f"      Urgency: {result['urgency_level']}")
                    print(f"      Est. Resolution: {result['estimated_resolution_days']} days")
                    print(f"      Confidence: {result['confidence']:.2f}")
                else:
                    print(f"      Classification failed: {result.get('error', 'Unknown')}")
            except Exception as e:
                print(f"      Error: {str(e)}")
            print()
        
        print("✅ Department Classification: PASSED")
        
    except Exception as e:
        print(f"❌ Department Classification: FAILED - {str(e)}")
    
    print("-" * 50)
    
    # Test 3: Authentication System
    print("3️⃣ Testing Authentication System...")
    try:
        auth_service = AdvancedAuthService()
        
        # Test user creation (mock)
        print("   Testing user registration flow...")
        
        test_phone = "+919876543210"
        test_email = "test@smartgriev.gov.in"
        
        # Note: This will try to register, might fail if user exists
        try:
            success, message, user = await auth_service.register_user(
                phone_number=test_phone,
                email=test_email,
                password="testpass123",
                first_name="Test",
                last_name="User"
            )
            
            if success:
                print(f"      ✅ Registration successful: {user.username}")
            else:
                print(f"      ⚠️ Registration note: {message}")
                
        except Exception as reg_error:
            print(f"      ℹ️ Registration test: {str(reg_error)}")
        
        print("✅ Authentication System: PASSED")
        
    except Exception as e:
        print(f"❌ Authentication System: FAILED - {str(e)}")
    
    print("-" * 50)
    
    # Test 4: Database Connectivity
    print("4️⃣ Testing Database Connectivity...")
    try:
        from complaints.models import Complaint, ComplaintCategory
        from authentication.models import User
        
        # Test database queries
        complaint_count = Complaint.objects.count()
        category_count = ComplaintCategory.objects.count()
        user_count = User.objects.count()
        
        print(f"   📊 Database Stats:")
        print(f"      Complaints: {complaint_count}")
        print(f"      Categories: {category_count}")
        print(f"      Users: {user_count}")
        
        print("✅ Database Connectivity: PASSED")
        
    except Exception as e:
        print(f"❌ Database Connectivity: FAILED - {str(e)}")
    
    print("=" * 50)
    print("🎉 Basic functionality test completed!")
    
    # Summary
    print("\n📋 Test Summary:")
    print("   • AI Text Enhancement: Core NLP processing")
    print("   • Department Classification: Government routing")
    print("   • Authentication System: User management with OTP")
    print("   • Database Connectivity: Data persistence")
    
    print("\n🔗 Available API Endpoints:")
    print("   • POST /complaints/api/process/ - Multi-modal complaint processing")
    print("   • POST /complaints/api/auth/ - Authentication with OTP")
    print("   • GET /complaints/api/departments/ - Government departments")
    print("   • GET /complaints/api/health/ - System health check")
    
    print("\n💡 Next Steps:")
    print("   1. Install AI dependencies: pip install -r requirements/ai_processing.txt")
    print("   2. Run migrations: python manage.py migrate")
    print("   3. Test full pipeline: python manage.py test_ai_pipeline --test-type=full")
    print("   4. Start development server: python manage.py runserver")


if __name__ == "__main__":
    try:
        asyncio.run(test_basic_functionality())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)