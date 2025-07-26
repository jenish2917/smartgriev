import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Dict, Tuple, List
import os

# Download required NLTK data
nltk.download('vader_lexicon')
nltk.download('punkt')

class ComplaintClassifier:
    def __init__(self):
        self.model_name = "ai4bharat/indic-bert-multilingual"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.labels = ['water', 'electricity', 'roads', 'sanitation', 'others']
        
    def classify(self, text: str) -> Dict[str, float]:
        """Classify the complaint text into predefined categories."""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        
        return {
            label: prob.item()
            for label, prob in zip(self.labels, probs[0])
        }

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.multilingual_sentiment = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of the text and return compound score."""
        # VADER sentiment for English
        vader_scores = self.sia.polarity_scores(text)
        
        # Multilingual BERT sentiment
        bert_result = self.multilingual_sentiment(text)[0]
        
        # Combine both scores
        return {
            'compound': vader_scores['compound'],
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'bert_score': float(bert_result['score']),
            'bert_label': bert_result['label']
        }

class EntityExtractor:
    def __init__(self):
        # Load English model for spaCy
        self.nlp = spacy.load('en_core_web_sm')
        
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract relevant entities from the complaint text."""
        doc = self.nlp(text)
        
        entities = {
            'locations': [],
            'dates': [],
            'organizations': [],
            'person_names': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'GPE' or ent.label_ == 'LOC':
                entities['locations'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ == 'PERSON':
                entities['person_names'].append(ent.text)
                
        return entities

def calculate_priority(sentiment_scores: Dict[str, float], 
                      keywords: List[str], 
                      text: str) -> Tuple[str, float]:
    """Calculate complaint priority based on sentiment and keywords."""
    # Priority keywords with weights
    priority_keywords = {
        'urgent': 1.0,
        'immediate': 1.0,
        'emergency': 1.0,
        'danger': 0.9,
        'critical': 0.9,
        'serious': 0.8,
        'important': 0.7,
    }
    
    # Base score from sentiment
    base_score = abs(sentiment_scores['compound'])
    
    # Add keyword weights
    text_lower = text.lower()
    keyword_score = sum(
        weight
        for keyword, weight in priority_keywords.items()
        if keyword in text_lower
    )
    
    # Calculate final score
    final_score = (base_score + keyword_score) / 2
    
    # Determine priority level
    if final_score >= 0.8:
        return 'HIGH', final_score
    elif final_score >= 0.5:
        return 'MEDIUM', final_score
    else:
        return 'LOW', final_score

# Initialize global instances
classifier = ComplaintClassifier()
sentiment_analyzer = SentimentAnalyzer()
entity_extractor = EntityExtractor()
