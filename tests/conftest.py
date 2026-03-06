"""
Global test fixtures and configuration.

This module provides shared fixtures for both unit and integration tests.
"""
import os
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from josi.main import app
from josi.core.config import Settings
from josi.db.async_db import get_async_db
from josi.auth.middleware import resolve_current_user
from josi.auth.schemas import CurrentUser
from josi.models.organization_model import Organization
from josi.models.person_model import Person
from josi.repositories.organization_repository import OrganizationRepository


# Test settings with test database
@pytest.fixture(scope="session")
def test_settings():
    """Override settings for testing."""
    return Settings(
        database_url="postgresql+asyncpg://josi:josi@localhost:1962/josi_test",
        redis_url="redis://localhost:6380/1",  # Use different Redis DB for tests
        environment="test",
        debug=True,
        auto_db_migration=True,  # Enable auto migration for tests
        rate_limit_enabled=False,  # Disable rate limiting in tests
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_settings):
    """Create test database engine."""
    import subprocess
    import os
    
    # Set environment variable for alembic (convert asyncpg to psycopg2 URL)
    alembic_url = test_settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    os.environ["DATABASE_URL"] = alembic_url
    
    # Run migrations for test database
    try:
        result = subprocess.run(
            ["poetry", "run", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Migration output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Migration failed: {e.stderr}")
        # If migration fails, try creating tables directly
        engine = create_async_engine(
            test_settings.database_url,
            echo=False,
            future=True
        )
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    
    engine = create_async_engine(
        test_settings.database_url,
        echo=False,
        future=True
    )
    
    yield engine
    
    # Cleanup - drop all tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
    except Exception as e:
        print(f"Cleanup failed: {e}")
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """Create a test organization."""
    org_uuid = uuid4()
    org = Organization(
        organization_id=org_uuid,
        name="Test Organization",
        slug=f"test-organization-{str(org_uuid)[:8]}",
        api_key=f"test-api-key-{uuid4()}",
        is_active=True
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture
def override_dependencies(db_session: AsyncSession, test_organization: Organization):
    """Override FastAPI dependencies for testing."""
    async def override_get_db():
        yield db_session

    async def override_resolve_current_user():
        return CurrentUser(
            user_id=uuid4(),
            descope_id="test-descope-id",
            email="test@example.com",
            subscription_tier="free",
            roles=["user"],
        )

    app.dependency_overrides[get_async_db] = override_get_db
    app.dependency_overrides[resolve_current_user] = override_resolve_current_user

    yield

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_dependencies, test_organization: Organization) -> TestClient:
    """Create a test client with overridden dependencies."""
    client = TestClient(app)
    client.headers = {"X-API-Key": test_organization.api_key}
    return client


@pytest_asyncio.fixture
async def async_client(override_dependencies, test_organization: Organization) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": test_organization.api_key}
    ) as client:
        yield client


# Model fixtures
@pytest_asyncio.fixture
async def test_person(db_session: AsyncSession, test_organization: Organization) -> Person:
    """Create a test person."""
    person = Person(
        person_id=uuid4(),
        organization_id=test_organization.organization_id,
        name="John Doe",
        date_of_birth=datetime(1990, 1, 1).date(),
        time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
        place_of_birth="New York, NY, USA",
        latitude=Decimal("40.7128"),
        longitude=Decimal("-74.0060"),
        timezone="America/New_York",
        email="john.doe@example.com"
    )
    db_session.add(person)
    await db_session.commit()
    await db_session.refresh(person)
    return person


# Mock fixtures for unit tests
@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    return session


@pytest.fixture
def mock_redis():
    """Mock Redis client for unit tests."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    redis.exists = AsyncMock(return_value=False)
    return redis


@pytest.fixture
def mock_geocoding_service():
    """Mock geocoding service for unit tests."""
    service = AsyncMock()
    service.geocode = AsyncMock(return_value={
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
        "formatted_address": "New York, NY, USA"
    })
    service.reverse_geocode = AsyncMock(return_value={
        "formatted_address": "New York, NY, USA",
        "country": "United States",
        "state": "New York",
        "city": "New York"
    })
    return service


# Utility functions
def assert_response_success(response, status_code=200):
    """Assert that a response is successful."""
    assert response.status_code == status_code
    data = response.json()
    assert data["success"] is True
    return data["data"]


def assert_response_error(response, status_code=400):
    """Assert that a response is an error."""
    assert response.status_code == status_code
    data = response.json()
    assert data["success"] is False
    return data["errors"]


# Test data generators
def generate_person_data():
    """Generate test person data."""
    return {
        "name": "Test User",
        "date_of_birth": "1990-01-01",
        "time_of_birth": "1990-01-01T12:00:00",
        "place_of_birth": "New York, NY, USA",
        "latitude": "40.7128",
        "longitude": "-74.0060",
        "timezone": "America/New_York",
        "email": f"test_{uuid4()}@example.com"
    }


def generate_chart_request_data(person_id: UUID):
    """Generate test chart request data."""
    return {
        "person_id": str(person_id),
        "chart_type": "natal",
        "house_system": "placidus",
        "ayanamsa": "lahiri",
        "coordinate_system": "tropical"
    }