"""
Service layer for the complaints application.

This package implements the Service Layer pattern to encapsulate business logic
and provide a clean interface between views and models.
"""

from .base import BaseModelService, SearchableService, AuditableService, CacheableService
from .complaint_service import ComplaintService, DepartmentService
from .vision_service import GeminiVisionService, get_vision_service
from .audio_service import AudioTranscriptionService, get_audio_service

__all__ = [
    'BaseModelService',
    'SearchableService',
    'AuditableService', 
    'CacheableService',
    'ComplaintService',
    'DepartmentService',
    'GeminiVisionService',
    'get_vision_service',
    'AudioTranscriptionService',
    'get_audio_service',
]