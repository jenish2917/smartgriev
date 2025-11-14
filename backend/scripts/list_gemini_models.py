"""
List available Gemini models
"""
import google.generativeai as genai
import os

# Configure API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyA6jaqmJJOF69GjtYGz8d7lZ2DLg9nImWk')
genai.configure(api_key=GEMINI_API_KEY)

print("Available Gemini models:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print()
