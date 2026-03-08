"""Repository for ApiKey database operations."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_

from josi.auth.schemas import CurrentUser
from josi.db.async_db import get_async_session
from josi.models.api_key_model import ApiKey


class ApiKeyRepository:
    """All ApiKey table access goes through here."""

    def __init__(self, current_user: Optional[CurrentUser] = None):
        self.current_user = current_user
        self.user_id = current_user.user_id if current_user else None

    async def get_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        async with get_async_session() as session:
            result = await session.execute(
                select(ApiKey).where(
                    and_(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
                )
            )
            return result.scalar_one_or_none()

    async def get_by_id_and_user(
        self, key_id: UUID, user_id: UUID, active_only: bool = False
    ) -> Optional[ApiKey]:
        conditions = [ApiKey.api_key_id == key_id, ApiKey.user_id == user_id]
        if active_only:
            conditions.append(ApiKey.is_active == True)
        async with get_async_session() as session:
            result = await session.execute(
                select(ApiKey).where(and_(*conditions))
            )
            return result.scalar_one_or_none()

    async def list_active_by_user(self, user_id: UUID) -> List[ApiKey]:
        async with get_async_session() as session:
            result = await session.execute(
                select(ApiKey).where(
                    and_(ApiKey.user_id == user_id, ApiKey.is_active == True)
                )
            )
            return list(result.scalars().all())

    async def create(self, api_key: ApiKey) -> ApiKey:
        async with get_async_session() as session:
            session.add(api_key)
            await session.flush()
            await session.refresh(api_key)
            return api_key

    async def update(self, api_key: ApiKey) -> ApiKey:
        async with get_async_session() as session:
            merged = await session.merge(api_key)
            await session.flush()
            await session.refresh(merged)
            return merged
