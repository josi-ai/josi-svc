"""
Minimal database module for testing purposes.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Mock async database session for testing."""
    # This is a stub for testing - in real implementation would connect to database
    yield None


def get_db():
    """Mock database dependency."""
    return None