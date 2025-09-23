"""
Test script to check Groq API connectivity and identify the issue
"""
import os
import sys
import django

# Add the Django project root to Python path
sys.path.append('/d/SmartGriev/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from groq import Groq

def test_groq_api():
    """Test Groq API connectivity"""
    try:
        # Use API key from environment
        import os
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("❌ GROQ_API_KEY not set in environment variables")
            return False
            
        client = Groq(api_key=api_key)
        
        print("🧪 Testing Groq API connectivity...")
        
        # Test with the model we're using
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, this is a test. Please respond with 'API Working'."
                }
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        response = completion.choices[0].message.content
        print(f"✅ API Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_classification():
    """Test the classification function specifically"""
    try:
        from complaints.services.classification_service import ComplaintClassificationService
        
        print("🧪 Testing Classification Service...")
        
        classifier = ComplaintClassificationService()
        result = classifier.classify_complaint(
            "electricity is not coming til 3 days",
            "gutter lick"
        )
        
        print(f"✅ Classification Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Classification Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Groq API Diagnostic Tests...")
    print("=" * 50)
    
    # Test 1: Basic API connectivity
    api_works = test_groq_api()
    print("=" * 50)
    
    # Test 2: Classification service
    classification_works = test_classification()
    print("=" * 50)
    
    if api_works and classification_works:
        print("✅ All tests passed! The issue might be elsewhere.")
    else:
        print("❌ Found issues that need to be fixed.")