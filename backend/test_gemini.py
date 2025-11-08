"""
Test script for Gemini AI Chatbot
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from chatbot.gemini_service import gemini_chatbot
import uuid

def test_gemini_chatbot():
    """Test Gemini chatbot with various scenarios"""
    
    print("=" * 60)
    print("GEMINI AI CHATBOT TEST")
    print("=" * 60)
    
    # Test 1: English conversation
    print("\n### Test 1: English Conversation ###")
    session_id = str(uuid.uuid4())
    
    test_messages = [
        "Hello, I want to report a problem",
        "There is no water supply in my area for the last 3 days",
        "I live in Sector 15, Noida",
        "This is very urgent, please help",
        "Yes, please file the complaint"
    ]
    
    for msg in test_messages:
        print(f"\nUser: {msg}")
        result = gemini_chatbot.chat(session_id, msg, 'en')
        print(f"Bot: {result['response']}")
        print(f"Intent: {result['intent']}")
        if result['complaint_data']:
            print(f"Extracted Data: {result['complaint_data']}")
        print(f"Complete: {result['conversation_complete']}")
    
    # Get summary
    summary = gemini_chatbot.get_conversation_summary(session_id)
    print(f"\n### Conversation Summary ###")
    print(f"Messages: {summary['message_count']}")
    print(f"Ready to Submit: {summary['ready_to_submit']}")
    print(f"Complaint Data: {summary['complaint_data']}")
    
    # Clean up
    gemini_chatbot.end_conversation(session_id)
    
    # Test 2: Hindi conversation
    print("\n\n### Test 2: Hindi Conversation ###")
    session_id_hindi = str(uuid.uuid4())
    
    hindi_messages = [
        "नमस्ते, मुझे शिकायत दर्ज करनी है",
        "मेरे इलाके में सड़क पर बड़ा गड्ढा है",
        "यह दिल्ली के करोल बाग में है"
    ]
    
    for msg in hindi_messages:
        print(f"\nUser: {msg}")
        result = gemini_chatbot.chat(session_id_hindi, msg, 'hi')
        print(f"Bot: {result['response']}")
        print(f"Intent: {result['intent']}")
    
    gemini_chatbot.end_conversation(session_id_hindi)
    
    # Test 3: Greeting in different languages
    print("\n\n### Test 3: Greetings in Multiple Languages ###")
    
    languages = {
        'en': 'Hello',
        'hi': 'नमस्ते',
        'ta': 'வணக்கம்',
        'te': 'నమస్కారం'
    }
    
    for lang, greeting in languages.items():
        session = str(uuid.uuid4())
        print(f"\n{lang.upper()}: {greeting}")
        result = gemini_chatbot.chat(session, greeting, lang)
        print(f"Response: {result['response']}")
        gemini_chatbot.end_conversation(session)
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_gemini_chatbot()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
