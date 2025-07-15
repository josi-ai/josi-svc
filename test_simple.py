#!/usr/bin/env python3
"""Test simple person creation without middleware complications."""
import sys
sys.path.insert(0, 'src')

import asyncio
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from josi.db.async_db import get_async_session
from josi.models.person_model import Person
from josi.services.person_service import PersonService
from josi.services.geocoding_service import GeocodingService
from josi.repositories.person_repository import PersonRepository

async def test_create_person():
    """Test creating a person directly."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as AS
    from sqlalchemy.orm import sessionmaker
    
    engine = create_async_engine("postgresql+asyncpg://josi:josi@localhost:5432/josi")
    SessionLocal = sessionmaker(engine, class_=AS, expire_on_commit=False)
    
    async with SessionLocal() as session:
        try:
            # Create services
            from josi.repositories.base_repository import BaseRepository
            person_repo = BaseRepository(Person, session, UUID('00000000-0000-0000-0000-000000000000'))
            geocoding_service = GeocodingService()
            person_service = PersonService(person_repo, geocoding_service)
            
            # Create person data
            person = Person(
                organization_id=UUID('00000000-0000-0000-0000-000000000000'),
                name="Test Person Direct",
                date_of_birth=date(1990, 1, 1),
                time_of_birth=datetime(1990, 1, 1, 14, 30),
                place_of_birth="New York, NY, USA",
                latitude=Decimal('40.7128'),
                longitude=Decimal('-74.0060'),
                timezone="America/New_York"
            )
            
            # Save person
            created = await person_repo.create(person)
            await session.commit()
            
            print(f"Person created successfully!")
            print(f"ID: {created.person_id}")
            print(f"Name: {created.name}")
            print(f"Time of birth: {created.time_of_birth}")
            
            # Test retrieving
            retrieved = await person_repo.get(created.person_id)
            print(f"Retrieved: {retrieved.name}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(test_create_person())