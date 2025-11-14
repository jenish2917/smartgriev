"""
Test script for AI-based complaint submission decision
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from chatbot.gemini_service import GeminiChatbotService
import json

def test_ai_submission():
    """Test the AI submission decision logic"""
    
    print("\n" + "="*80)
    print("Testing AI-Based Complaint Submission Decision")
    print("="*80 + "\n")
    
    # Initialize service
    service = GeminiChatbotService()
    
    # Start a conversation
    session_id = "test_session_001"
    
    # Simulate a conversation
    messages = [
        "Hello, I want to file a complaint",
        "There is garbage piling up near my house",
        "It's at MG Road, near the park",
        "It's very urgent, health hazard",
        "Yes, that's correct"  # This should trigger AI submission decision
    ]
    
    print("Starting conversation simulation...\n")
    
    for i, msg in enumerate(messages, 1):
        print(f"\n{'─'*80}")
        print(f"Turn {i}: USER → {msg}")
        print('─'*80)
        
        response = service.chat(session_id, msg, 'en')
        
        print(f"\n📱 BOT RESPONSE:")
        print(response['response'])
        
        print(f"\n📊 METADATA:")
        print(f"   Intent: {response.get('intent', 'N/A')}")
        print(f"   Conversation Complete: {response.get('conversation_complete', False)}")
        print(f"   Auto-Submit (AI Decision): {response.get('auto_submit', False)}")
        
        if response.get('complaint_data'):
            print(f"\n📝 EXTRACTED DATA:")
            for key, value in response['complaint_data'].items():
                if value:
                    print(f"   {key}: {value}")
        
        if response.get('auto_submit'):
            print("\n" + "🎯"*40)
            print("AI DECIDED TO AUTO-SUBMIT THE COMPLAINT!")
            print("🎯"*40)
            break
    
    # Test AI decision method directly
    print("\n\n" + "="*80)
    print("Testing AI Decision Method Directly")
    print("="*80 + "\n")
    
    test_cases = [
        {
            'message': 'yes, submit it',
            'complaint': {
                'title': 'Garbage issue',
                'description': 'Garbage piling up near my house at MG Road',
                'category': 'Health & Sanitation',
                'location': 'MG Road, near the park',
                'urgency': 'urgent'
            }
        },
        {
            'message': 'no, that looks good',
            'complaint': {
                'title': 'Street light not working',
                'description': 'Street light broken for 2 weeks',
                'category': 'Infrastructure',
                'location': 'Park Street',
                'urgency': 'medium'
            }
        },
        {
            'message': 'wait, I want to change something',
            'complaint': {
                'title': 'Road pothole',
                'description': 'Big pothole on main road',
                'category': 'Infrastructure',
                'location': 'Main Road',
                'urgency': 'high'
            }
        },
        {
            'message': 'all correct',
            'complaint': {
                'title': 'Water supply issue',
                'description': 'No water supply for 3 days',
                'category': 'Infrastructure',
                'location': 'Colony Area',
                'urgency': 'urgent'
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Message: '{test['message']}'")
        print(f"Complaint: {test['complaint']['title']}")
        
        decision = service._ai_should_submit(
            test['message'],
            test['message'],
            test['complaint']
        )
        
        result_icon = "✅" if decision else "❌"
        print(f"AI Decision: {result_icon} {'SUBMIT' if decision else 'WAIT'}")
        print("─" * 60)
    
    print("\n" + "="*80)
    print("Test Complete!")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_ai_submission()
