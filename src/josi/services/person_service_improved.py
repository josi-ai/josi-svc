"""
Improved person service with repository pattern.
"""
from typing import List, Optional
from uuid import UUID
from josi.models.person_model import Person, PersonEntity
from josi.repositories.person_repository import PersonRepository
from josi.services.geocoding_service import GeocodingService


class PersonService:
    """
    Service layer handles business logic only.
    No direct database access - uses repository.
    """
    
    def __init__(
        self, 
        person_repository: PersonRepository,
        geocoding_service: GeocodingService
    ):
        self.person_repo = person_repository
        self.geocoding = geocoding_service
    
    async def create_person(self, data: PersonEntity) -> Person:
        """Create person with geocoding."""
        # Business logic: Geocode the location
        if data.place_of_birth and not data.latitude:
            location = await self.geocoding.geocode(data.place_of_birth)
            data.latitude = location.latitude
            data.longitude = location.longitude
            data.timezone = location.timezone
        
        # Delegate persistence to repository
        return await self.person_repo.create(data)
    
    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        """Get person by ID."""
        return await self.person_repo.get(person_id)
    
    async def list(
        self, 
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Person]:
        """List persons with optional search."""
        if search:
            return await self.person_repo.search(search, skip, limit)
        return await self.person_repo.get_multi(skip=skip, limit=limit)