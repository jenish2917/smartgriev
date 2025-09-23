"""
Chatbot Utilities Module

This module provides a comprehensive NLP service layer for chatbot operations
following SOLID principles and clean architecture patterns.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
import logging

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Enumeration for conversation intents"""
    GREETING = "greeting"
    COMPLAINT_FILING = "complaint_filing"
    COMPLAINT_STATUS = "complaint_status"
    HELP = "help"
    UNKNOWN = "unknown"


class Sentiment(Enum):
    """Enumeration for sentiment analysis results"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Priority(Enum):
    """Enumeration for complaint priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConversationContext:
    """Data class for conversation context"""
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = None
    user_preferences: Dict[str, Any] = None
    language: str = "en"
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.user_preferences is None:
            self.user_preferences = {}


@dataclass
class ConversationResponse:
    """Data class for conversation response"""
    message: str
    intent: str
    sentiment: str
    language: str
    urgency: str
    category: Optional[str]
    entities: List[str]
    conversation_state: str
    suggested_actions: List[str]
    quick_replies: List[str]
    needs_escalation: bool
    confidence: float


class TranslatorInterface(ABC):
    """Interface for translation services"""
    
    @abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        pass
    
    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        pass


class GoogleTranslatorService(TranslatorInterface):
    """Google Translate implementation"""
    
    def __init__(self):
        from googletrans import Translator
        self._translator = Translator()
    
    def translate(self, text: str, target_language: str) -> str:
        """Translate text using Google Translate"""
        try:
            result = self._translator.translate(text, dest=target_language)
            return result.text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def detect_language(self, text: str) -> str:
        """Detect language using Google Translate"""
        try:
            from langdetect import detect
            return detect(text)
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return 'en'


class NLPProcessorInterface(ABC):
    """Interface for NLP processing services"""
    
    @abstractmethod
    def extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        pass
    
    @abstractmethod
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        pass
    
    @abstractmethod
    def detect_intent(self, text: str) -> str:
        """Detect intent from text"""
        pass


class SpacyNLPProcessor(NLPProcessorInterface):
    """spaCy NLP implementation"""
    
    def __init__(self):
        import spacy
        try:
            self._nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            self._nlp = None
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract entities using spaCy"""
        if not self._nlp:
            return []
        
        try:
            doc = self._nlp(text)
            entities = []
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC', 'PRODUCT']:
                    entities.append(ent.text)
            return entities
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis using keywords"""
        positive_words = ['good', 'great', 'excellent', 'thank', 'appreciate', 'satisfied', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'angry', 'frustrated', 'disappointed', 'upset', 'problem', 'issue', 'complaint']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return Sentiment.POSITIVE.value
        elif negative_count > positive_count:
            return Sentiment.NEGATIVE.value
        else:
            return Sentiment.NEUTRAL.value
    
    def detect_intent(self, text: str) -> str:
        """Detect intent using pattern matching"""
        text_lower = text.lower()
        
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        complaint_patterns = ['complaint', 'problem', 'issue', 'file', 'report', 'submit']
        status_patterns = ['status', 'check', 'track', 'update', 'progress']
        help_patterns = ['help', 'assist', 'support', 'how', 'what', 'guide']
        
        # Check status patterns first (more specific)
        if any(pattern in text_lower for pattern in status_patterns):
            return Intent.COMPLAINT_STATUS.value
        elif any(pattern in text_lower for pattern in greeting_patterns):
            return Intent.GREETING.value
        elif any(pattern in text_lower for pattern in complaint_patterns):
            return Intent.COMPLAINT_FILING.value
        elif any(pattern in text_lower for pattern in help_patterns):
            return Intent.HELP.value
        else:
            return Intent.UNKNOWN.value


class ComplaintAnalyzerInterface(ABC):
    """Interface for complaint analysis services"""
    
    @abstractmethod
    def analyze_urgency(self, text: str) -> str:
        """Analyze urgency level of complaint"""
        pass
    
    @abstractmethod
    def extract_category(self, text: str) -> Optional[str]:
        """Extract complaint category from text"""
        pass


class ComplaintAnalyzer(ComplaintAnalyzerInterface):
    """Implementation of complaint analysis"""
    
    def analyze_urgency(self, text: str) -> str:
        """Analyze message to determine complaint urgency level"""
        text_lower = text.lower()
        
        critical_keywords = ['emergency', 'urgent', 'critical', 'immediate', 'dangerous', 'safety', 'life', 'death']
        high_keywords = ['serious', 'major', 'important', 'significant', 'severe']
        medium_keywords = ['moderate', 'concerning', 'issue', 'problem']
        
        if any(keyword in text_lower for keyword in critical_keywords):
            return Priority.CRITICAL.value
        elif any(keyword in text_lower for keyword in high_keywords):
            return Priority.HIGH.value
        elif any(keyword in text_lower for keyword in medium_keywords):
            return Priority.MEDIUM.value
        else:
            return Priority.LOW.value
    
    def extract_category(self, text: str) -> Optional[str]:
        """Extract likely complaint category from message content"""
        text_lower = text.lower()
        
        categories = {
            'infrastructure': ['road', 'bridge', 'building', 'construction', 'repair', 'maintenance'],
            'environment': ['pollution', 'noise', 'air', 'water', 'waste', 'garbage', 'trash'],
            'transportation': ['bus', 'traffic', 'parking', 'vehicle', 'transport', 'metro'],
            'health': ['hospital', 'medical', 'health', 'clinic', 'doctor', 'medicine'],
            'education': ['school', 'teacher', 'education', 'student', 'college', 'university'],
            'public_services': ['electricity', 'power', 'water', 'gas', 'internet', 'phone']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return None


class ResponseGeneratorInterface(ABC):
    """Interface for response generation strategies"""
    
    @abstractmethod
    def generate_response(self, intent: str, context: ConversationContext, 
                         language: str = 'en') -> str:
        """Generate response based on intent and context"""
        pass
    
    @abstractmethod
    def generate_quick_replies(self, intent: str) -> List[str]:
        """Generate quick reply options"""
        pass


class SmartResponseGenerator(ResponseGeneratorInterface):
    """Smart response generator implementation"""
    
    def __init__(self, translator: TranslatorInterface):
        self._translator = translator
    
    def generate_response(self, intent: str, context: ConversationContext, 
                         language: str = 'en') -> str:
        """Generate contextual response"""
        if intent == Intent.GREETING.value:
            message = "Hello! I'm here to help you with your complaints and inquiries. How can I assist you today?"
        elif intent == Intent.COMPLAINT_FILING.value:
            message = "I'll help you file a complaint. Could you please tell me what type of issue you're experiencing?"
        elif intent == Intent.COMPLAINT_STATUS.value:
            message = "I can help you check your complaint status. Do you have your complaint ID, or would you like me to search by other details?"
        elif intent == Intent.HELP.value:
            message = "I'm here to help! I can assist you with filing complaints, checking status, or answering questions about our services. What would you like to know?"
        else:
            message = "I want to make sure I understand you correctly. Could you please rephrase your question or tell me how I can help you today?"
        
        if language != 'en':
            message = self._translator.translate(message, language)
        
        return message
    
    def generate_quick_replies(self, intent: str) -> List[str]:
        """Generate contextual quick reply options"""
        quick_replies = {
            Intent.GREETING.value: [
                "File a new complaint",
                "Check complaint status", 
                "Get help"
            ],
            Intent.COMPLAINT_FILING.value: [
                "Infrastructure issue",
                "Environmental concern",
                "Public service problem",
                "Other issue"
            ],
            Intent.COMPLAINT_STATUS.value: [
                "I have complaint ID",
                "I don't have complaint ID",
                "Check recent complaints"
            ],
            Intent.HELP.value: [
                "How to file complaint",
                "Complaint tracking",
                "Contact support",
                "FAQ"
            ]
        }
        
        return quick_replies.get(intent, ["Yes", "No", "Get help"])


class ConversationFlowManager:
    """Manages conversation flow and orchestrates all NLP services"""
    
    def __init__(self, 
                 translator: TranslatorInterface = None,
                 nlp_processor: NLPProcessorInterface = None,
                 complaint_analyzer: ComplaintAnalyzerInterface = None,
                 response_generator: ResponseGeneratorInterface = None):
        
        self._translator = translator or GoogleTranslatorService()
        self._nlp_processor = nlp_processor or SpacyNLPProcessor()
        self._complaint_analyzer = complaint_analyzer or ComplaintAnalyzer()
        self._response_generator = response_generator or SmartResponseGenerator(self._translator)
    
    def process_message(self, message: str, context: ConversationContext = None) -> ConversationResponse:
        """Process user message and return comprehensive response"""
        if context is None:
            context = ConversationContext()
        
        # Detect language and intent
        language = self._translator.detect_language(message)
        intent = self._nlp_processor.detect_intent(message)
        
        # Analyze message content
        sentiment = self._nlp_processor.analyze_sentiment(message)
        entities = self._nlp_processor.extract_entities(message)
        urgency = self._complaint_analyzer.analyze_urgency(message)
        category = self._complaint_analyzer.extract_category(message)
        
        # Generate response and quick replies
        response_message = self._response_generator.generate_response(intent, context, language)
        quick_replies = self._response_generator.generate_quick_replies(intent)
        
        # Determine conversation state and actions
        conversation_state = self._determine_conversation_state(context.conversation_history, intent)
        suggested_actions = self._generate_suggested_actions(intent, category, urgency)
        needs_escalation = sentiment == Sentiment.NEGATIVE.value and urgency in [Priority.HIGH.value, Priority.CRITICAL.value]
        
        # Calculate confidence based on intent detection
        confidence = 0.9 if intent != Intent.UNKNOWN.value else 0.3
        
        return ConversationResponse(
            message=response_message,
            intent=intent,
            sentiment=sentiment,
            language=language,
            urgency=urgency,
            category=category,
            entities=entities,
            conversation_state=conversation_state,
            suggested_actions=suggested_actions,
            quick_replies=quick_replies,
            needs_escalation=needs_escalation,
            confidence=confidence
        )
    
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


# Legacy compatibility functions
def get_sentiment_analyzer():
    """Legacy compatibility function"""
    return None


def get_nlp_model():
    """Legacy compatibility function"""
    return None


def process_message_with_context(message: str, context: Dict[str, Any], user) -> tuple:
    """Legacy compatibility function"""
    flow_manager = ConversationFlowManager()
    conversation_context = ConversationContext(
        conversation_history=context.get('conversation_history', [])
    )
    response = flow_manager.process_message(message, conversation_context)
    
    return response.intent, response.confidence, response.message


def get_quick_replies_for_intent(intent: str) -> List[str]:
    """Legacy compatibility function"""
    return generate_quick_replies(intent)


def should_escalate(message: str, intent: str, confidence: float) -> bool:
    """Legacy compatibility function"""
    nlp_processor = SpacyNLPProcessor()
    complaint_analyzer = ComplaintAnalyzer()
    
    sentiment = nlp_processor.analyze_sentiment(message)
    urgency = complaint_analyzer.analyze_urgency(message)
    
    return (sentiment == Sentiment.NEGATIVE.value and 
            urgency in [Priority.HIGH.value, Priority.CRITICAL.value]) or confidence < 0.5
