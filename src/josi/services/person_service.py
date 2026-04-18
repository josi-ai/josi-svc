"""
Person service - handles business logic for person management.
"""
from typing import Optional, List, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from josi.repositories.person_repository import PersonRepository
from josi.models.person_model import Person
from josi.models.person_model import PersonEntity, PersonModel
from josi.services.geocoding_service import GeocodingService


class PersonService:
    """Service for person-related operations."""
    
    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.person_repo = PersonRepository(Person, db, user_id)
        self.geocoding_service = GeocodingService()
    
    async def create_person(self, person_data: PersonEntity) -> Person:
        """Create a new person with geocoding."""
        # Parse place_of_birth string (may be None)
        city, state, country = "", "", ""
        lat, lon, tz = None, None, "UTC"

        if person_data.place_of_birth:
            place_parts = person_data.place_of_birth.split(',')
            city = place_parts[0].strip() if len(place_parts) > 0 else ""
            state = place_parts[1].strip() if len(place_parts) > 1 else ""
            country = place_parts[2].strip() if len(place_parts) > 2 else ""
            
            lat, lon, tz = self.geocoding_service.get_coordinates_and_timezone(
                city=city,
                state=state,
                country=country
            )
        
        # Combine date and time (if time is provided)
        birth_datetime = None
        if person_data.time_of_birth is not None:
            from datetime import datetime
            birth_datetime = datetime.combine(
                person_data.date_of_birth,
                person_data.time_of_birth.time() if hasattr(person_data.time_of_birth, 'time') else person_data.time_of_birth
            )
        
        # Create person
        person_dict = {
            "name": person_data.name,
            "email": person_data.email,
            "phone": person_data.phone,
            "date_of_birth": person_data.date_of_birth,
            "time_of_birth": birth_datetime,
            "place_of_birth_city": city,
            "place_of_birth_state": state,
            "place_of_birth_country": country,
            "place_of_birth": person_data.place_of_birth,
            "latitude": lat,
            "longitude": lon,
            "timezone": tz,
            "notes": getattr(person_data, 'notes', None)
        }
        
        return await self.person_repo.create(person_dict)
    
    async def get_person(self, person_id: UUID) -> Optional[Person]:
        """Get person by ID."""
        return await self.person_repo.get_with_charts(person_id)
    
    async def find_by_email(self, email: str) -> Optional[Person]:
        """Find person by email."""
        return await self.person_repo.find_by_email(email)
    
    async def search_persons(self, name: str, limit: int = 10) -> List[Person]:
        """Search persons by name."""
        return await self.person_repo.search_by_name(name, limit)
    
    async def update_person(self, person_id: UUID, update_data: dict) -> Optional[Person]:
        """Update person details."""
        # Re-geocode if any location field changed
        location_changed = any(
            key in update_data
            for key in ['place_of_birth', 'place_of_birth_city', 'place_of_birth_state', 'place_of_birth_country']
        )
        if location_changed:
            person = await self.person_repo.get(person_id)
            if person:
                # If the combined place_of_birth string was sent, parse it
                if 'place_of_birth' in update_data and update_data['place_of_birth']:
                    parts = update_data['place_of_birth'].split(',')
                    city = parts[0].strip() if len(parts) > 0 else ""
                    state = parts[1].strip() if len(parts) > 1 else ""
                    country = parts[2].strip() if len(parts) > 2 else ""
                else:
                    city = update_data.get('place_of_birth_city', getattr(person, 'place_of_birth_city', ''))
                    state = update_data.get('place_of_birth_state', getattr(person, 'place_of_birth_state', ''))
                    country = update_data.get('place_of_birth_country', getattr(person, 'place_of_birth_country', ''))

                try:
                    lat, lon, tz = self.geocoding_service.get_coordinates_and_timezone(city, state, country)
                    update_data.update({
                        'latitude': lat,
                        'longitude': lon,
                        'timezone': tz,
                    })
                except ValueError:
                    pass  # Geocoding failed — keep existing coordinates

        return await self.person_repo.update(person_id, update_data)
    
    async def delete_person(self, person_id: UUID) -> bool:
        """Delete person and all related data."""
        return await self.person_repo.delete(person_id)
    
    async def list_persons(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        selected_fields: Optional[List[str]] = None
    ) -> List[Person]:
        """List persons with optional search."""
        if search:
            return await self.search_persons(search, limit=limit)
        return await self.person_repo.get_multi(skip=skip, limit=limit)
    
    async def get_total_persons_count(self, search: Optional[str] = None) -> int:
        """Get total count of persons."""
        query = select(func.count(Person.person_id)).where(Person.is_deleted == False)

        if self.user_id:
            query = query.where(Person.user_id == self.user_id)
        
        if search:
            search_filter = or_(
                Person.name.ilike(f"%{search}%"),
                Person.email.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def get_persons_by_ids(
        self,
        person_ids: List[UUID],
        limit: int = 100,
        offset: int = 0,
        selected_fields: Optional[List[str]] = None
    ) -> List[Person]:
        """Get multiple persons by their IDs."""
        persons = []
        for person_id in person_ids[offset:offset+limit]:
            person = await self.get_person(person_id)
            if person:
                persons.append(person)
        return persons
    
    async def create_persons(self, persons_data: List[PersonEntity]) -> List[Person]:
        """Create multiple persons."""
        persons = []
        for person_data in persons_data:
            person = await self.create_person(person_data)
            persons.append(person)
        return persons
    
    async def update_persons(
        self,
        persons_data: List[PersonModel],
        updated_fields: Optional[List[str]] = None
    ) -> List[Person]:
        """Update multiple persons."""
        persons = []
        for person_data in persons_data:
            if hasattr(person_data, 'id'):
                update_dict = person_data.model_dump(exclude_unset=True, exclude={'id'})
                person = await self.update_person(person_data.id, update_dict)
                if person:
                    persons.append(person)
        return persons
    
    async def restore_person(self, person_id: UUID) -> Optional[Person]:
        """Restore a soft-deleted person."""
        person = await self.person_repo.get(person_id)
        if person and person.is_deleted:
            person.is_deleted = False
            person.deleted_at = None
            await self.db.commit()
            await self.db.refresh(person)
            return person
        return None
    
    async def find_default_profile(self) -> Optional[Person]:
        """Find the user's default birth profile."""
        result = await self.db.execute(
            select(Person).where(
                Person.user_id == self.user_id,
                Person.is_default == True,
                Person.is_deleted == False,
            )
        )
        return result.scalars().first()

    async def get_person_charts(self, person_id: UUID):
        """Get all charts for a person."""
        from josi.models.chart_model import AstrologyChart
        from sqlalchemy import select

        query = select(AstrologyChart).where(
            AstrologyChart.person_id == person_id,
            AstrologyChart.is_deleted == False,
        )
        if self.user_id:
            query = query.where(AstrologyChart.user_id == self.user_id)
        query = query.order_by(AstrologyChart.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()