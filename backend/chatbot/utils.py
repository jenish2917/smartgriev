from transformers import pipeline
import spacy
from googletrans import Translator
from langdetect import detect
from .models import QuickReplyTemplate

def get_sentiment_analyzer():
    try:
        return pipeline('sentiment-analysis')
    except (ImportError, OSError):
        return None

def get_nlp_model():
    try:
        return spacy.load('en_core_web_sm')
    except (ImportError, OSError):
        return None

def translate_text(text, target_language):
    translator = Translator()
    try:
        return translator.translate(text, dest=target_language).text
    except Exception:
        return text

def detect_language(text):
    try:
        return detect(text)
    except Exception:
        return 'en'

def process_message_with_context(message, context, user):
    # This is a placeholder for a more sophisticated intent recognition system.
    # In a real-world application, you would use a library like Rasa or Dialogflow.
    message_lower = message.lower()
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return 'greeting', 0.9, f"Hello {user.first_name or user.username}! How can I assist you?"
    if any(word in message_lower for word in ['file', 'submit', 'register', 'complaint']):
        return 'complaint_filing', 0.8, "I can help you file a complaint. What is the issue?"
    if any(word in message_lower for word in ['status', 'track', 'progress']):
        return 'complaint_status', 0.8, "Please provide your complaint ID to check the status."
    return 'general', 0.5, "I'm sorry, I don't understand. Can you please rephrase?"

def get_quick_replies_for_intent(intent):
    try:
        template = QuickReplyTemplate.objects.get(intent=intent, is_active=True)
        return template.buttons.all()
    except QuickReplyTemplate.DoesNotExist:
        return []

def should_escalate(message, intent, confidence):
    if confidence < 0.4:
        return True
    escalation_keywords = ['legal', 'lawyer', 'court', 'urgent', 'emergency']
    if any(keyword in message.lower() for keyword in escalation_keywords):
        return True
    return False

def get_escalation_message(language):
    message = "I understand this is a complex issue. Let me connect you with a human support agent."
    return translate_text(message, language)
