"""Repository for User database operations."""
from typing import Optional

from sqlalchemy import select, and_

from josi.auth.schemas import CurrentUser
from josi.db.async_db import get_async_session
from josi.models.user_model import User


class UserRepository:
    """All User table access goes through here."""

    def __init__(self, current_user: Optional[CurrentUser] = None):
        self.current_user = current_user
        self.user_id = current_user.user_id if current_user else None

    async def get_by_id(self, user_id) -> Optional[User]:
        async with get_async_session() as session:
            result = await session.execute(
                select(User).where(
                    and_(User.user_id == user_id, User.is_deleted == False)
                )
            )
            return result.scalar_one_or_none()

    async def get_by_auth_provider_id(self, auth_provider_id: str) -> Optional[User]:
        async with get_async_session() as session:
            result = await session.execute(
                select(User).where(
                    and_(User.auth_provider_id == auth_provider_id, User.is_deleted == False)
                )
            )
            return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        async with get_async_session() as session:
            result = await session.execute(
                select(User).where(
                    and_(User.email == email, User.is_deleted == False)
                )
            )
            return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        async with get_async_session() as session:
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user

    async def update(self, user: User) -> User:
        async with get_async_session() as session:
            merged = await session.merge(user)
            await session.flush()
            await session.refresh(merged)
            return merged
