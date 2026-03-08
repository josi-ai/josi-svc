"""
Async database configuration and session management with multi-tenant support.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.exc import OperationalError, DBAPIError
from josi.core.config import settings

log = logging.getLogger("uvicorn")

DATABASE_URL = settings.database_url


class EngineManager:
    """Manages database engines for multi-tenant architecture."""
    
    def __init__(self):
        self.engines: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._default_engine = None
    
    async def get_engine(self, organization_id: Optional[UUID] = None):
        """Get or create an engine for the given organization."""
        # For now, use a single engine for all organizations
        # In a full multi-tenant setup, you would route to different databases/schemas
        async with self._lock:
            if not self._default_engine:
                self._default_engine = self._create_engine()
            return self._default_engine
    
    def _create_engine(self):
        """Create a new async engine."""
        # Create async engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=settings.debug,
            future=True,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
            poolclass=QueuePool,
        )
        
        # Add event listeners for debugging if enabled
        if settings.debug:
            @event.listens_for(engine.sync_engine, "connect")
            def on_connect(dbapi_conn, connection_record):
                connection_record.info['connect_time'] = datetime.utcnow()
                log.debug(f"New connection established: {id(dbapi_conn)}")
        
        return engine
    
    async def close_all(self):
        """Close all engines."""
        async with self._lock:
            if self._default_engine:
                await self._default_engine.dispose()
                self._default_engine = None
            
            for engine in self.engines.values():
                await engine.dispose()
            self.engines.clear()


# Global engine manager instance
engine_manager = EngineManager()

# Backward compatibility - keep existing engine for legacy code
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    future=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory for backward compatibility
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_async_session(
    organization_id: Optional[UUID] = None,
    is_read_replica: bool = False
) -> AsyncSession:
    """
    Get an async database session with multi-tenant support.
    
    Args:
        organization_id: Organization ID for multi-tenant filtering
        is_read_replica: Whether to use read replica (future enhancement)
    
    Yields:
        AsyncSession: Database session
    """
    # Get the appropriate engine
    engine = await engine_manager.get_engine(organization_id)
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            log.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session (backward compatibility)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    from sqlmodel import SQLModel
    from josi.models import (
        Organization,
        Person,
        AstrologyChart,
        ChartInterpretation,
        PlanetPosition
    )
    
    async with engine.begin() as conn:
        # Create UUID extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
        # Create tables
        await conn.run_sync(SQLModel.metadata.create_all)