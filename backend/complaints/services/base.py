from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction


class BaseModelService(ABC):
    """
    Abstract base service class that provides common CRUD operations
    and business logic patterns for Django models.
    
    This follows the Service Layer pattern to encapsulate business logic
    outside of models and views, promoting clean architecture principles.
    """
    
    model: Type[models.Model] = None
    
    def __init__(self):
        if self.model is None:
            raise NotImplementedError("Service must define a model class")
    
    def get_queryset(self, **filters) -> models.QuerySet:
        """Get base queryset with optional filters"""
        queryset = self.model.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset
    
    def get_by_id(self, obj_id: int) -> Optional[models.Model]:
        """Get object by ID"""
        try:
            return self.model.objects.get(id=obj_id)
        except self.model.DoesNotExist:
            return None
    
    def create(self, data: Dict[str, Any], **kwargs) -> models.Model:
        """Create new object with validation"""
        with transaction.atomic():
            instance = self.model(**data, **kwargs)
            self.validate_before_save(instance)
            instance.full_clean()
            instance.save()
            self.post_create_actions(instance)
            return instance
    
    def update(self, obj_id: int, data: Dict[str, Any]) -> Optional[models.Model]:
        """Update object with validation"""
        instance = self.get_by_id(obj_id)
        if not instance:
            return None
        
        with transaction.atomic():
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.validate_before_save(instance)
            instance.full_clean()
            instance.save()
            self.post_update_actions(instance, data)
            return instance
    
    def delete(self, obj_id: int) -> bool:
        """Delete object by ID"""
        instance = self.get_by_id(obj_id)
        if not instance:
            return False
        
        with transaction.atomic():
            self.pre_delete_actions(instance)
            instance.delete()
            self.post_delete_actions(obj_id)
            return True
    
    def list_with_pagination(self, page: int = 1, page_size: int = 20, **filters) -> Dict[str, Any]:
        """Get paginated list of objects"""
        queryset = self.get_queryset(**filters)
        total = queryset.count()
        
        offset = (page - 1) * page_size
        objects = list(queryset[offset:offset + page_size])
        
        return {
            'objects': objects,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'has_next': offset + page_size < total,
                'has_previous': page > 1
            }
        }
    
    # Hook methods for subclasses to override
    def validate_before_save(self, instance: models.Model) -> None:
        """Override to add custom validation logic"""
        pass
    
    def post_create_actions(self, instance: models.Model) -> None:
        """Override to add post-creation logic"""
        pass
    
    def post_update_actions(self, instance: models.Model, updated_data: Dict[str, Any]) -> None:
        """Override to add post-update logic"""
        pass
    
    def pre_delete_actions(self, instance: models.Model) -> None:
        """Override to add pre-deletion logic"""
        pass
    
    def post_delete_actions(self, obj_id: int) -> None:
        """Override to add post-deletion logic"""
        pass


class SearchableService(BaseModelService):
    """
    Service mixin that adds search capabilities to model services.
    """
    
    search_fields: List[str] = []
    
    def search(self, query: str, **filters) -> models.QuerySet:
        """Search objects by query string across defined fields"""
        if not self.search_fields:
            raise NotImplementedError("Service must define search_fields for search functionality")
        
        from django.db.models import Q
        
        queryset = self.get_queryset(**filters)
        if not query:
            return queryset
        
        # Build search query across all search fields
        search_q = Q()
        for field in self.search_fields:
            search_q |= Q(**{f"{field}__icontains": query})
        
        return queryset.filter(search_q)


class AuditableService(BaseModelService):
    """
    Service mixin that adds audit trail functionality.
    """
    
    def create(self, data: Dict[str, Any], created_by: models.Model = None, **kwargs) -> models.Model:
        """Create with audit trail"""
        instance = super().create(data, **kwargs)
        if created_by:
            self.create_audit_entry(instance, 'created', created_by)
        return instance
    
    def update(self, obj_id: int, data: Dict[str, Any], updated_by: models.Model = None) -> Optional[models.Model]:
        """Update with audit trail"""
        instance = super().update(obj_id, data)
        if instance and updated_by:
            self.create_audit_entry(instance, 'updated', updated_by)
        return instance
    
    def delete(self, obj_id: int, deleted_by: models.Model = None) -> bool:
        """Delete with audit trail"""
        instance = self.get_by_id(obj_id)
        if instance and deleted_by:
            self.create_audit_entry(instance, 'deleted', deleted_by)
        return super().delete(obj_id)
    
    @abstractmethod
    def create_audit_entry(self, instance: models.Model, action: str, user: models.Model) -> None:
        """Create audit trail entry - must be implemented by subclass"""
        pass


class CacheableService(BaseModelService):
    """
    Service mixin that adds caching capabilities.
    """
    
    cache_timeout: int = 3600  # 1 hour default
    cache_key_prefix: str = ""
    
    def __init__(self):
        super().__init__()
        if not self.cache_key_prefix:
            self.cache_key_prefix = f"{self.model._meta.label_lower}"
    
    def get_cache_key(self, key: str) -> str:
        """Generate cache key with prefix"""
        return f"{self.cache_key_prefix}:{key}"
    
    def get_by_id_cached(self, obj_id: int) -> Optional[models.Model]:
        """Get object by ID with caching"""
        from django.core.cache import cache
        
        cache_key = self.get_cache_key(f"id:{obj_id}")
        cached_obj = cache.get(cache_key)
        
        if cached_obj is None:
            cached_obj = self.get_by_id(obj_id)
            if cached_obj:
                cache.set(cache_key, cached_obj, self.cache_timeout)
        
        return cached_obj
    
    def invalidate_cache(self, obj_id: int) -> None:
        """Invalidate cache for specific object"""
        from django.core.cache import cache
        cache_key = self.get_cache_key(f"id:{obj_id}")
        cache.delete(cache_key)
    
    def post_update_actions(self, instance: models.Model, updated_data: Dict[str, Any]) -> None:
        """Invalidate cache on update"""
        super().post_update_actions(instance, updated_data)
        self.invalidate_cache(instance.id)
    
    def post_delete_actions(self, obj_id: int) -> None:
        """Invalidate cache on delete"""
        super().post_delete_actions(obj_id)
        self.invalidate_cache(obj_id)