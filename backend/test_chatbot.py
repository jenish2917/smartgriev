import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from chatbot.gemini_service import gemini_chatbot

print('Gemini chatbot initialized successfully')

try:
    result = gemini_chatbot.chat('test123', 'Hello, I want to file a complaint', 'en')
    print(f'Success! Response: {result.get("response")[:200]}')
    print(f'Intent: {result.get("intent")}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()
