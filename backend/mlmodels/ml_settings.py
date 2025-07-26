from pathlib import Path
import os

# ML Models settings
MODELS_ROOT = os.path.join(Path(__file__).resolve().parent.parent, 'models')

# Language codes and names mapping
LANGUAGE_CHOICES = {
    'en': 'English',
    'hi': 'Hindi',
    'te': 'Telugu',
    'ta': 'Tamil',
    'bn': 'Bengali',
    'ml': 'Malayalam',
    'gu': 'Gujarati',
    'mr': 'Marathi',
    'pa': 'Punjabi',
    'ur': 'Urdu',
    'kn': 'Kannada',
    'or': 'Odia',
    'as': 'Assamese',
    'kok': 'Konkani',
    'mni': 'Manipuri',
    'sat': 'Santali',
    'sd': 'Sindhi',
    'ne': 'Nepali',
    'ks': 'Kashmiri',
    'doi': 'Dogri',
    'brx': 'Bodo',
    'mni': 'Manipuri',
    'mai': 'Maithili',
    'sa': 'Sanskrit'
}

# Model specific settings
MODEL_SETTINGS = {
    'COMPLAINT_CLASSIFIER': {
        'max_length': 512,
        'categories': [
            'INFRASTRUCTURE',
            'SANITATION',
            'HEALTH',
            'EDUCATION',
            'TRANSPORTATION',
            'LAW_AND_ORDER',
            'UTILITIES',
            'ENVIRONMENT'
        ]
    },
    'SENTIMENT_ANALYZER': {
        'max_length': 256,
        'labels': ['NEGATIVE', 'NEUTRAL', 'POSITIVE']
    },
    'NER': {
        'max_length': 384,
        'entities': [
            'PERSON',
            'LOCATION',
            'ORGANIZATION',
            'DATE',
            'FACILITY'
        ]
    },
    'TRANSLATOR': {
        'max_length': 512,
        'beam_size': 5,
        'length_penalty': 1.0,
        'temperature': 0.7
    }
}

# Batch processing settings
BATCH_SIZE = 32
MAX_CONCURRENT_INFERENCES = 10

# Model loading settings
LAZY_LOADING = True
USE_CUDA = True
FALLBACK_TO_CPU = True

# Cache settings
MODEL_CACHE_TTL = 3600  # 1 hour
PREDICTION_CACHE_TTL = 300  # 5 minutes

# Rate limiting
RATE_LIMIT = {
    'PREDICTION_RATE': '100/hour',
    'BATCH_PREDICTION_RATE': '10/hour'
}

# Error thresholds
CONFIDENCE_THRESHOLD = 0.6
MAX_RETRY_ATTEMPTS = 3
TIMEOUT = 30  # seconds
