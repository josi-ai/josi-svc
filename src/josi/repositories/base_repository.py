from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import selectinload
from uuid import UUID
from sqlmodel import SQLModel
import logging

ModelType = TypeVar("ModelType", bound=SQLModel)

log = logging.getLogger("uvicorn")


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations and user-scoped tenant support."""

    def __init__(self, model: Type[ModelType], session: AsyncSession, user_id: Optional[UUID] = None):
        self.model = model
        self.session = session
        self.user_id = user_id
        # Check if model has user_id field for user-scoped tenancy
        self.is_user_scoped = hasattr(model, 'user_id')

    def _apply_tenant_filter(self, query):
        """Apply user_id filter if model supports user-scoped tenancy."""
        if self.is_user_scoped and self.user_id:
            return query.where(self.model.user_id == self.user_id)
        return query

    async def get(self, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID."""
        # Use SQLAlchemy inspect to find the primary key column
        mapper = sa_inspect(self.model)
        pk_columns = mapper.primary_key
        id_field = pk_columns[0]
        
        query = select(self.model).where(
            and_(
                id_field == id,
                self.model.is_deleted == False if hasattr(self.model, 'is_deleted') else True
            )
        )
        
        # Apply tenant filter
        query = self._apply_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        conditions = []
        if hasattr(self.model, 'is_deleted'):
            conditions.append(self.model.is_deleted == False)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
        
        query = select(self.model)
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply tenant filter
        query = self._apply_tenant_filter(query)
        
        # Apply ordering
        if order_by:
            for order in order_by:
                if order.startswith('-'):
                    query = query.order_by(getattr(self.model, order[1:]).desc())
                else:
                    query = query.order_by(getattr(self.model, order))
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        # Add user_id if model supports user-scoped tenancy
        if self.is_user_scoped and self.user_id:
            obj_in["user_id"] = self.user_id
        
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def update(self, id: UUID, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record."""
        # Get the entity first
        entity = await self.get(id)
        if not entity:
            return None
        
        # Update fields
        for field, value in obj_in.items():
            if hasattr(entity, field) and field not in ['id', 'created_at', 'organization_id', 'user_id']:
                setattr(entity, field, value)
        
        # Update timestamp if available
        if hasattr(entity, 'updated_at'):
            entity.updated_at = datetime.utcnow()
        
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def delete(self, id: UUID) -> bool:
        """Soft delete a record if supported, otherwise hard delete."""
        entity = await self.get(id)
        if not entity:
            return False
        
        if hasattr(entity, 'is_deleted'):
            # Soft delete
            entity.is_deleted = True
            if hasattr(entity, 'deleted_at'):
                entity.deleted_at = datetime.utcnow()
            await self.session.flush()
        else:
            # Hard delete
            await self.session.delete(entity)
            await self.session.flush()
        
        return True
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get count of records."""
        conditions = []
        if hasattr(self.model, 'is_deleted'):
            conditions.append(self.model.is_deleted == False)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
        
        query = select(func.count()).select_from(self.model)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply tenant filter
        query = self._apply_tenant_filter(query)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def exists(self, id: UUID) -> bool:
        """Check if a record exists."""
        entity = await self.get(id)
        return entity is not None
    
    async def bulk_create(self, objs_in: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records."""
        db_objs = []
        for obj_in in objs_in:
            # Add user_id if model supports user-scoped tenancy
            if self.is_user_scoped and self.user_id:
                obj_in["user_id"] = self.user_id
            db_objs.append(self.model(**obj_in))
        
        self.session.add_all(db_objs)
        await self.session.flush()
        
        # Refresh all objects
        for db_obj in db_objs:
            await self.session.refresh(db_obj)
        
        return db_objs
    
    async def bulk_update(self, updates: List[Dict[str, Any]]) -> List[ModelType]:
        """Update multiple records. Each update dict must contain the record ID."""
        updated_entities = []
        
        for update_data in updates:
            # Extract ID (handle different ID field names)
            id_value = update_data.get('id') or update_data.get(f'{self.model.__tablename__}_id')
            if not id_value:
                log.warning(f"No ID found in update data: {update_data}")
                continue
            
            # Remove ID from update data to avoid updating it
            update_fields = {k: v for k, v in update_data.items() 
                           if k not in ['id', f'{self.model.__tablename__}_id']}
            
            entity = await self.update(id_value, update_fields)
            if entity:
                updated_entities.append(entity)
        
        return updated_entities