import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

# Check environment variable
from dotenv import load_dotenv
load_dotenv()

print(f"GEMINI_API_KEY from env: {os.getenv('GEMINI_API_KEY')}")
print(f"GROQ_API_KEY from env: {os.getenv('GROQ_API_KEY')}")

# Now test the chatbot
from chatbot.gemini_service import GeminiChatbotService

print("\n--- Creating new chatbot instance ---")
try:
    chatbot = GeminiChatbotService()
    print("[OK] Chatbot initialized successfully")
    print(f"  Gemini available: {chatbot.gemini_available}")
    print(f"  Groq available: {chatbot.groq_available}")
    
    print("\n--- Testing chat ---")
    result = chatbot.chat('test999', 'I want to file a complaint about water shortage', 'en')
    print(f"[OK] Response: {result['response'][:200]}")
    print(f"  Intent: {result['intent']}")
    print(f"  Has error: {'error' in result}")
    if 'error' in result:
        print(f"  Error: {result['error']}")
except Exception as e:
    print(f"[ERROR] Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
