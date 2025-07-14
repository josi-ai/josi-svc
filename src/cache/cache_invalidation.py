"""
Cache invalidation mechanism for database updates.

This module provides automatic cache invalidation when database records
are updated or deleted, ensuring cache consistency.
"""
import logging
from typing import Optional, List, Dict, Any, Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import event, inspect
from sqlmodel import SQLModel

from .client import get_redis
from .cache_decorator import invalidate_cache

logger = logging.getLogger(__name__)


class CacheInvalidator:
    """
    Handles cache invalidation for database operations.
    
    This class tracks relationships between cache keys and database records,
    and automatically invalidates related caches when records are modified.
    """
    
    def __init__(self):
        self.model_cache_patterns: Dict[str, List[str]] = {
            # Model name -> cache key patterns
            "Person": ["person:*", "chart:*", "prediction:*", "compatibility:*"],
            "AstrologyChart": ["chart:*", "prediction:*"],
            "Organization": ["*:org:{id}:*"],
            # Add more models as needed
        }
    
    async def on_model_update(
        self,
        model: SQLModel,
        db: AsyncSession,
        updated_fields: Optional[List[str]] = None
    ):
        """
        Called when a model is updated.
        
        Args:
            model: The updated model instance
            db: Database session
            updated_fields: List of fields that were updated
        """
        model_name = model.__class__.__name__
        patterns = self.model_cache_patterns.get(model_name, [])
        
        if not patterns:
            return
        
        # Get model ID
        model_id = getattr(model, 'id', None) or getattr(model, f'{model_name.lower()}_id', None)
        
        if not model_id:
            logger.warning(f"Could not find ID for model {model_name}")
            return
        
        # Invalidate caches based on patterns
        for pattern in patterns:
            if "{id}" in pattern:
                # Replace {id} with actual ID
                pattern = pattern.replace("{id}", str(model_id))
            elif "*" not in pattern:
                # Add model ID to pattern
                pattern = f"{pattern}:{model_id}:*"
            
            await invalidate_cache(pattern=pattern)
        
        # Special handling for specific models
        if model_name == "Person":
            await self._invalidate_person_caches(model, db)
        elif model_name == "AstrologyChart":
            await self._invalidate_chart_caches(model, db)
    
    async def on_model_delete(self, model: SQLModel, db: AsyncSession):
        """
        Called when a model is deleted.
        
        Args:
            model: The deleted model instance
            db: Database session
        """
        # Same as update but more aggressive
        await self.on_model_update(model, db)
    
    async def _invalidate_person_caches(self, person: Any, db: AsyncSession):
        """Invalidate all caches related to a person."""
        person_id = str(person.person_id if hasattr(person, 'person_id') else person.id)
        
        # Invalidate specific cache patterns
        patterns = [
            f"person:get_person:{person_id}*",
            f"person:list_persons:*{person_id}*",
            f"chart:*:{person_id}:*",
            f"prediction:*:{person_id}:*",
            f"compatibility:*:{person_id}*",
            f"dasha:*:{person_id}:*",
            f"transit:*:{person_id}:*",
            f"remedies:*:{person_id}:*",
        ]
        
        for pattern in patterns:
            await invalidate_cache(pattern=pattern)
    
    async def _invalidate_chart_caches(self, chart: Any, db: AsyncSession):
        """Invalidate all caches related to a chart."""
        chart_id = str(chart.chart_id if hasattr(chart, 'chart_id') else chart.id)
        person_id = str(chart.person_id)
        
        patterns = [
            f"chart:*:{chart_id}:*",
            f"chart:*:{person_id}:*",
            f"prediction:*:{person_id}:*",
        ]
        
        for pattern in patterns:
            await invalidate_cache(pattern=pattern)


# Global cache invalidator instance
cache_invalidator = CacheInvalidator()


def setup_cache_invalidation_hooks():
    """
    Set up SQLAlchemy event listeners for automatic cache invalidation.
    
    This should be called during application startup.
    """
    # We'll use SQLModel's underlying SQLAlchemy events
    # This is a simplified version - in production, you might want more sophisticated tracking
    
    from josi.models import Person, AstrologyChart, Organization
    
    models_to_track = [Person, AstrologyChart, Organization]
    
    for model_class in models_to_track:
        # After update
        @event.listens_for(model_class, 'after_update')
        def receive_after_update(mapper, connection, target):
            # Mark for cache invalidation
            if hasattr(target, '_invalidate_cache'):
                target._invalidate_cache = True
        
        # After delete
        @event.listens_for(model_class, 'after_delete')
        def receive_after_delete(mapper, connection, target):
            # Mark for cache invalidation
            if hasattr(target, '_invalidate_cache'):
                target._invalidate_cache = True


class CacheInvalidationMixin:
    """
    Mixin for SQLModel classes to support automatic cache invalidation.
    
    Add this to your model classes to enable cache tracking.
    """
    
    _invalidate_cache: bool = False
    
    async def save(self, db: AsyncSession, **kwargs):
        """Save model and invalidate related caches."""
        # Detect if this is an update or insert
        is_update = bool(inspect(self).persistent)
        
        # Call parent save if exists
        if hasattr(super(), 'save'):
            await super().save(db, **kwargs)
        else:
            db.add(self)
            await db.commit()
            await db.refresh(self)
        
        # Invalidate caches if needed
        if is_update or self._invalidate_cache:
            await cache_invalidator.on_model_update(self, db)
    
    async def delete(self, db: AsyncSession):
        """Delete model and invalidate related caches."""
        await cache_invalidator.on_model_delete(self, db)
        
        # Perform deletion
        if hasattr(self, 'is_deleted'):
            # Soft delete
            self.is_deleted = True
            await db.commit()
        else:
            # Hard delete
            await db.delete(self)
            await db.commit()


# Repository-level cache invalidation
class CachedRepository:
    """
    Base repository class with automatic cache invalidation.
    
    Extend your repositories from this class to get automatic
    cache invalidation on create, update, and delete operations.
    """
    
    def __init__(self, model_class: Type[SQLModel], db: AsyncSession, organization_id: Optional[UUID] = None):
        self.model_class = model_class
        self.db = db
        self.organization_id = organization_id
    
    async def create(self, data: dict) -> SQLModel:
        """Create a new record."""
        instance = self.model_class(**data)
        if self.organization_id and hasattr(instance, 'organization_id'):
            instance.organization_id = self.organization_id
        
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        
        # No cache invalidation needed for create
        return instance
    
    async def update(self, id: UUID, data: dict) -> Optional[SQLModel]:
        """Update a record and invalidate caches."""
        instance = await self.get(id)
        if not instance:
            return None
        
        # Update fields
        for key, value in data.items():
            setattr(instance, key, value)
        
        await self.db.commit()
        await self.db.refresh(instance)
        
        # Invalidate related caches
        await cache_invalidator.on_model_update(instance, self.db, list(data.keys()))
        
        return instance
    
    async def delete(self, id: UUID) -> bool:
        """Delete a record and invalidate caches."""
        instance = await self.get(id)
        if not instance:
            return False
        
        # Invalidate caches before deletion
        await cache_invalidator.on_model_delete(instance, self.db)
        
        # Perform deletion
        if hasattr(instance, 'is_deleted'):
            # Soft delete
            instance.is_deleted = True
            await self.db.commit()
        else:
            # Hard delete
            await self.db.delete(instance)
            await self.db.commit()
        
        return True
    
    async def get(self, id: UUID) -> Optional[SQLModel]:
        """Get a record by ID (implement in subclass)."""
        raise NotImplementedError