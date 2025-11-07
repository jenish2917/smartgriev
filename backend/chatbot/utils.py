"""
Enhanced Chatbot Utilities with OOP Architecture
Implements international coding standards and clean architecture principles.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import logging
import spacy
from deep_translator import GoogleTranslator


# Configure logging
logger = logging.getLogger(__name__)


# Enums for type safety
class Intent(Enum):
    GREETING = "greeting"
    COMPLAINT_FILING = "complaint_filing"
    COMPLAINT_STATUS = "complaint_status"
    HELP = "help"
    GRATITUDE = "gratitude"
    FAREWELL = "farewell"
    UNKNOWN = "unknown"


class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Category(Enum):
    INFRASTRUCTURE = "infrastructure"
    ENVIRONMENT = "environment"
    TRANSPORTATION = "transportation"
    HEALTH = "health"
    EDUCATION = "education"
    PUBLIC_SERVICES = "public_services"


# Data Transfer Objects
@dataclass
class ConversationContext:
    """Encapsulates conversation state and context"""
    user_id: Optional[str] = None
    language: str = "en"
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatbotResponse:
    """Structured response from chatbot"""
    message: str
    intent: str
    confidence: float
    language: str
    sentiment: str
    urgency: str
    category: Optional[str]
    entities: List[str]
    conversation_state: str
    suggested_actions: List[str]
    quick_replies: List[str]
    needs_escalation: bool


# Abstract Interfaces
class TranslatorInterface(ABC):
    """Interface for translation services"""
    
    @abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        pass
    
    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        pass


class NLPProcessorInterface(ABC):
    """Interface for NLP processing services"""
    
    @abstractmethod
    def detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        pass
    
    @abstractmethod
    def analyze_sentiment(self, message: str) -> str:
        """Analyze sentiment of message"""
        pass
    
    @abstractmethod
    def extract_entities(self, message: str) -> List[str]:
        """Extract named entities from message"""
        pass


class ComplaintAnalyzerInterface(ABC):
    """Interface for complaint analysis services"""
    
    @abstractmethod
    def analyze_urgency(self, message: str) -> str:
        """Analyze urgency level of complaint"""
        pass
    
    @abstractmethod
    def extract_category(self, message: str) -> Optional[str]:
        """Extract complaint category from message"""
        pass


class ResponseGeneratorInterface(ABC):
    """Interface for response generation services"""
    
    @abstractmethod
    def generate_response(self, intent: str, context: ConversationContext, language: str) -> str:
        """Generate contextual response"""
        pass
    
    @abstractmethod
    def generate_quick_replies(self, intent: str) -> List[str]:
        """Generate quick reply options"""
        pass


# Concrete Implementations
class GoogleTranslatorService(TranslatorInterface):
    """Google Translator implementation using deep-translator"""
    
    def __init__(self):
        self.language_cache = {}
    
    def translate(self, text: str, target_language: str) -> str:
        """Translate text using Google Translate API via deep-translator"""
        try:
            if target_language == "en" or not text:
                return text
            
            translated = GoogleTranslator(source='auto', target=target_language).translate(text)
            return translated if translated else text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def detect_language(self, text: str) -> str:
        """Detect language - deep-translator doesn't have detection, default to 'en'"""
        try:
            if text in self.language_cache:
                return self.language_cache[text]
            
            # deep-translator doesn't have language detection
            # Default to English or use a simple heuristic
            language = "en"  # Default
            self.language_cache[text] = language
            return language
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en"


class SpacyNLPProcessor(NLPProcessorInterface):
    """spaCy-based NLP processor"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def detect_intent(self, message: str) -> str:
        """Detect user intent using pattern matching"""
        message_lower = message.lower()
        
        intent_patterns = {
            Intent.GREETING: ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
            Intent.COMPLAINT_FILING: ['complaint', 'problem', 'issue', 'file', 'report', 'submit'],
            Intent.COMPLAINT_STATUS: ['status', 'check', 'track', 'update', 'progress'],
            Intent.HELP: ['help', 'assist', 'support', 'how', 'what', 'guide'],
            Intent.GRATITUDE: ['thank', 'thanks', 'appreciate'],
            Intent.FAREWELL: ['bye', 'goodbye', 'exit', 'quit']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent.value
        
        return Intent.UNKNOWN.value
    
    def analyze_sentiment(self, message: str) -> str:
        """Analyze sentiment using keyword-based approach"""
        message_lower = message.lower()
        
        positive_words = ['good', 'great', 'excellent', 'thank', 'appreciate', 'satisfied', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'angry', 'frustrated', 'disappointed', 'upset', 'problem', 'issue', 'complaint']
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return Sentiment.POSITIVE.value
        elif negative_count > positive_count:
            return Sentiment.NEGATIVE.value
        else:
            return Sentiment.NEUTRAL.value
    
    def extract_entities(self, message: str) -> List[str]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(message)
            entities = []
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC', 'PRODUCT']:
                    entities.append(ent.text)
            return entities
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return []


class ComplaintAnalyzer(ComplaintAnalyzerInterface):
    """Analyzes complaint-specific content"""
    
    def analyze_urgency(self, message: str) -> str:
        """Analyze urgency level based on keywords"""
        message_lower = message.lower()
        
        urgency_keywords = {
            Priority.CRITICAL: ['emergency', 'urgent', 'critical', 'immediate', 'dangerous', 'safety', 'life', 'death'],
            Priority.HIGH: ['serious', 'major', 'important', 'significant', 'severe'],
            Priority.MEDIUM: ['moderate', 'concerning', 'issue', 'problem']
        }
        
        for priority, keywords in urgency_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return priority.value
        
        return Priority.LOW.value
    
    def extract_category(self, message: str) -> Optional[str]:
        """Extract complaint category from message content"""
        message_lower = message.lower()
        
        category_keywords = {
            Category.INFRASTRUCTURE: ['road', 'bridge', 'building', 'construction', 'repair', 'maintenance'],
            Category.ENVIRONMENT: ['pollution', 'noise', 'air', 'water', 'waste', 'garbage', 'trash'],
            Category.TRANSPORTATION: ['bus', 'traffic', 'parking', 'vehicle', 'transport', 'metro'],
            Category.HEALTH: ['hospital', 'medical', 'health', 'clinic', 'doctor', 'medicine'],
            Category.EDUCATION: ['school', 'teacher', 'education', 'student', 'college', 'university'],
            Category.PUBLIC_SERVICES: ['electricity', 'power', 'water', 'gas', 'internet', 'phone']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return category.value
        
        return None


class SmartResponseGenerator(ResponseGeneratorInterface):
    """Intelligent response generator with context awareness"""
    
    def __init__(self, translator: TranslatorInterface):
        self.translator = translator
        
    def generate_response(self, intent: str, context: ConversationContext, language: str) -> str:
        """Generate contextual response based on intent"""
        response_templates = {
            Intent.GREETING.value: "Hello! I'm here to help you with your complaints and inquiries. How can I assist you today?",
            Intent.COMPLAINT_FILING.value: "I'll help you file a complaint. Could you please tell me what type of issue you're experiencing?",
            Intent.COMPLAINT_STATUS.value: "I can help you check your complaint status. Do you have your complaint ID, or would you like me to search by other details?",
            Intent.HELP.value: "I'm here to help! I can assist you with filing complaints, checking status, or answering questions about our services. What would you like to know?",
            Intent.GRATITUDE.value: "You're welcome! Is there anything else I can help you with today?",
            Intent.FAREWELL.value: "Thank you for contacting us. Have a great day! Feel free to reach out if you need further assistance.",
            Intent.UNKNOWN.value: "I want to make sure I understand you correctly. Could you please rephrase your question or tell me how I can help you today?"
        }
        
        message = response_templates.get(intent, response_templates[Intent.UNKNOWN.value])
        return self.translator.translate(message, language)
    
    def generate_quick_replies(self, intent: str) -> List[str]:
        """Generate quick reply options based on intent"""
        quick_replies = {
            Intent.GREETING.value: ["File a new complaint", "Check complaint status", "Get help"],
            Intent.COMPLAINT_FILING.value: ["Infrastructure issue", "Environmental concern", "Public service problem", "Other issue"],
            Intent.COMPLAINT_STATUS.value: ["I have complaint ID", "I don't have complaint ID", "Check recent complaints"],
            Intent.HELP.value: ["How to file complaint", "Complaint tracking", "Contact support", "FAQ"]
        }
        
        return quick_replies.get(intent, ["Yes", "No", "Get help"])


class ConversationFlowManager:
    """Orchestrates conversation flow using dependency injection"""
    
    def __init__(self):
        self.translator = GoogleTranslatorService()
        self.nlp_processor = SpacyNLPProcessor()
        self.complaint_analyzer = ComplaintAnalyzer()
        self.response_generator = SmartResponseGenerator(self.translator)
    
    def process_message(self, message: str, context: ConversationContext) -> ChatbotResponse:
        """Process user message and generate comprehensive response"""
        try:
            # Language detection
            language = self.translator.detect_language(message)
            context.language = language
            
            # Core NLP analysis
            intent = self.nlp_processor.detect_intent(message)
            sentiment = self.nlp_processor.analyze_sentiment(message)
            entities = self.nlp_processor.extract_entities(message)
            
            # Complaint-specific analysis
            urgency = self.complaint_analyzer.analyze_urgency(message)
            category = self.complaint_analyzer.extract_category(message)
            
            # Response generation
            response_message = self.response_generator.generate_response(intent, context, language)
            quick_replies = self.response_generator.generate_quick_replies(intent)
            
            # Conversation management
            conversation_state = self._determine_conversation_state(context.conversation_history, intent)
            suggested_actions = self._generate_suggested_actions(intent, category, urgency)
            
            # Escalation logic
            needs_escalation = self._should_escalate(sentiment, urgency, intent, 0.8)
            
            return ChatbotResponse(
                message=response_message,
                intent=intent,
                confidence=0.8,  # Default confidence
                language=language,
                sentiment=sentiment,
                urgency=urgency,
                category=category,
                entities=entities,
                conversation_state=conversation_state,
                suggested_actions=suggested_actions,
                quick_replies=quick_replies,
                needs_escalation=needs_escalation
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._create_error_response(language)
    
    def _should_escalate(self, sentiment: str, urgency: str, intent: str, confidence: float) -> bool:
        """Determine if conversation needs escalation"""
        return (sentiment == Sentiment.NEGATIVE.value and 
                urgency in [Priority.HIGH.value, Priority.CRITICAL.value]) or confidence < 0.5
    
    def _determine_conversation_state(self, conversation_history: List[Dict[str, Any]], current_intent: str) -> str:
        """Determine current conversation state based on history and intent"""
        if not conversation_history:
            return 'initial'
        
        last_intent = conversation_history[-1].get('intent', 'unknown') if conversation_history else 'unknown'
        
        state_map = {
            ('initial', Intent.GREETING.value): 'welcomed',
            ('welcomed', Intent.COMPLAINT_FILING.value): 'filing_complaint',
            ('filing_complaint', Intent.COMPLAINT_FILING.value): 'collecting_details',
            ('welcomed', Intent.COMPLAINT_STATUS.value): 'checking_status',
            ('welcomed', Intent.HELP.value): 'providing_help'
        }
        
        return state_map.get((last_intent, current_intent), 'in_progress')
    
    def _generate_suggested_actions(self, intent: str, category: Optional[str], urgency: str) -> List[str]:
        """Generate suggested actions based on conversation context"""
        actions = []
        
        if intent == Intent.COMPLAINT_FILING.value:
            actions.append('initiate_complaint_form')
            if urgency in [Priority.HIGH.value, Priority.CRITICAL.value]:
                actions.append('escalate_priority')
            if category:
                actions.append(f'suggest_category_{category}')
        
        elif intent == Intent.COMPLAINT_STATUS.value:
            actions.append('show_status_form')
            actions.append('search_complaints')
        
        elif intent == Intent.HELP.value:
            actions.append('show_help_menu')
            actions.append('show_faq')
        
        return actions
    
    def _create_error_response(self, language: str = "en") -> ChatbotResponse:
        """Create error response when processing fails"""
        message = "I'm experiencing some technical difficulties. Please try again or contact support."
        if language != "en":
            message = self.translator.translate(message, language)
        
        return ChatbotResponse(
            message=message,
            intent=Intent.UNKNOWN.value,
            confidence=0.0,
            language=language,
            sentiment=Sentiment.NEUTRAL.value,
            urgency=Priority.LOW.value,
            category=None,
            entities=[],
            conversation_state='error',
            suggested_actions=['contact_support'],
            quick_replies=['Contact Support', 'Try Again'],
            needs_escalation=True
        )


# Legacy function wrappers for backward compatibility
def translate_text(text: str, target_language: str) -> str:
    """Legacy function wrapper"""
    translator = GoogleTranslatorService()
    return translator.translate(text, target_language)


def detect_language(text: str) -> str:
    """Legacy function wrapper"""
    translator = GoogleTranslatorService()
    return translator.detect_language(text)


def detect_intent(message: str) -> str:
    """Legacy function wrapper"""
    nlp_processor = SpacyNLPProcessor()
    return nlp_processor.detect_intent(message)


def analyze_sentiment(message: str) -> str:
    """Legacy function wrapper"""
    nlp_processor = SpacyNLPProcessor()
    return nlp_processor.analyze_sentiment(message)


def extract_entities(message: str) -> List[str]:
    """Legacy function wrapper"""
    nlp_processor = SpacyNLPProcessor()
    return nlp_processor.extract_entities(message)


def analyze_complaint_urgency(message: str) -> str:
    """Legacy function wrapper"""
    analyzer = ComplaintAnalyzer()
    return analyzer.analyze_urgency(message)


def extract_complaint_category(message: str) -> Optional[str]:
    """Legacy function wrapper"""
    analyzer = ComplaintAnalyzer()
    return analyzer.extract_category(message)


def generate_quick_replies(intent: str) -> List[str]:
    """Legacy function wrapper"""
    response_generator = SmartResponseGenerator(GoogleTranslatorService())
    return response_generator.generate_quick_replies(intent)


def manage_conversation_flow(message: str, conversation_history: List[Dict[str, Any]] = None, 
                            user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function wrapper"""
    context = ConversationContext(conversation_history=conversation_history or [])
    if user_context:
        context.user_preferences = user_context
    
    flow_manager = ConversationFlowManager()
    response = flow_manager.process_message(message, context)
    
    # Convert to legacy format
    return {
        'intent': response.intent,
        'language': response.language,
        'sentiment': response.sentiment,
        'urgency': response.urgency,
        'category': response.category,
        'entities': response.entities,
        'conversation_state': response.conversation_state,
        'suggested_actions': response.suggested_actions,
        'quick_replies': response.quick_replies,
        'needs_escalation': response.needs_escalation,
        'message': response.message
    }


def get_escalation_message(language: str) -> str:
    """Get escalation message in specified language"""
    message = "I understand this is a complex issue. Let me connect you with a human support agent who can provide specialized assistance."
    translator = GoogleTranslatorService()
    return translator.translate(message, language)


def get_greeting_response(language: str) -> str:
    """Get greeting response in specified language"""
    response_generator = SmartResponseGenerator(GoogleTranslatorService())
    context = ConversationContext(language=language)
    return response_generator.generate_response(Intent.GREETING.value, context, language)


def should_escalate(message: str, intent: str, confidence: float) -> bool:
    """Legacy compatibility function"""
    nlp_processor = SpacyNLPProcessor()
    complaint_analyzer = ComplaintAnalyzer()
    
    sentiment = nlp_processor.analyze_sentiment(message)
    urgency = complaint_analyzer.analyze_urgency(message)
    
    return (sentiment == Sentiment.NEGATIVE.value and 
            urgency in [Priority.HIGH.value, Priority.CRITICAL.value]) or confidence < 0.5


def get_quick_replies_for_intent(intent: str) -> List[str]:
    """Legacy compatibility function"""
    return generate_quick_replies(intent)


def process_message_with_context(message: str, context: Dict[str, Any], user) -> tuple:
    """Legacy compatibility function"""
    flow_manager = ConversationFlowManager()
    conversation_context = ConversationContext(
        conversation_history=context.get('conversation_history', [])
    )
    response = flow_manager.process_message(message, conversation_context)
    
    return response.intent, response.confidence, response.message


# Legacy compatibility functions
def get_sentiment_analyzer():
    """Legacy compatibility function"""
    return None


def get_nlp_model():
    """Legacy compatibility function"""
    return None