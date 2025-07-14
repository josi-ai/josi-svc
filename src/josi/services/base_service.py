"""
Base service class with multi-tenant support.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from josi.db.async_db import get_async_session


class BaseService:
    """Base service class with multi-tenant session management."""
    
    def __init__(self, organization_id: Optional[UUID] = None):
        self.organization_id = organization_id
    
    async def get_session(self, is_read_replica: bool = False) -> AsyncSession:
        """Get an async database session for this service."""
        async with get_async_session(
            organization_id=self.organization_id,
            is_read_replica=is_read_replica
        ) as session:
            return session