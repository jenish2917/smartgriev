"""
SmartGriev Backend Services
Core services for translation, government integration, and external APIs
"""

from .translation_service import (
    TranslationService,
    get_translation_service,
    translate_text,
    detect_language,
    SUPPORTED_LANGUAGES
)

__all__ = [
    'TranslationService',
    'get_translation_service',
    'translate_text',
    'detect_language',
    'SUPPORTED_LANGUAGES',
]
