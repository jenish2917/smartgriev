import google.generativeai as genai
import os

# Configure API
api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDZnzRiecwjRWNZ9PqwRtz1oszQOtl4bhU')
genai.configure(api_key=api_key)

# List all available models
print("Available Gemini Models:")
print("=" * 60)
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print()
