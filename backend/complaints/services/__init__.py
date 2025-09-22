"""
Service layer for the complaints application.

This package implements the Service Layer pattern to encapsulate business logic
and provide a clean interface between views and models.
"""

from .base import BaseModelService, SearchableService, AuditableService, CacheableService
from .complaint_service import ComplaintService, DepartmentService

__all__ = [
    'BaseModelService',
    'SearchableService',
    'AuditableService', 
    'CacheableService',
    'ComplaintService',
    'DepartmentService',
]