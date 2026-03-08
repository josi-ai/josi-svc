"""Repository for UserUsage database operations."""
from typing import Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update, and_

from josi.auth.schemas import CurrentUser
from josi.db.async_db import get_async_session
from josi.models.user_usage_model import UserUsage


class UsageRepository:
    def __init__(self, current_user: Optional[CurrentUser] = None):
        self.current_user = current_user

    @staticmethod
    def _current_period() -> str:
        return datetime.utcnow().strftime("%Y-%m")

    async def get_or_create(self, user_id: UUID, period: Optional[str] = None) -> UserUsage:
        period = period or self._current_period()
        async with get_async_session() as session:
            result = await session.execute(
                select(UserUsage).where(
                    and_(UserUsage.user_id == user_id, UserUsage.period == period)
                )
            )
            usage = result.scalar_one_or_none()
            if not usage:
                usage = UserUsage(user_id=user_id, period=period)
                session.add(usage)
                await session.flush()
                await session.refresh(usage)
            return usage

    async def increment(self, user_id: UUID, field: str, amount: int = 1) -> UserUsage:
        period = self._current_period()
        await self.get_or_create(user_id, period)
        async with get_async_session() as session:
            await session.execute(
                update(UserUsage)
                .where(and_(UserUsage.user_id == user_id, UserUsage.period == period))
                .values(
                    **{field: getattr(UserUsage, field) + amount},
                    updated_at=datetime.utcnow(),
                )
            )
            await session.flush()
            result = await session.execute(
                select(UserUsage).where(
                    and_(UserUsage.user_id == user_id, UserUsage.period == period)
                )
            )
            return result.scalar_one()
