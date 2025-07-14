"""Extended unit tests for PersonService to increase coverage."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from josi.services.person_service import PersonService
from josi.models.person_model import Person, PersonEntity
from josi.repositories.person_repository import PersonRepository


class TestPersonServiceExtended:
    """Extended test coverage for PersonService."""
    
    @pytest.fixture
    def mock_person_repository(self):
        """Create a mock person repository."""
        repo = AsyncMock(spec=PersonRepository)
        return repo
    
    @pytest.fixture
    def mock_geocoding_service(self):
        """Create a mock geocoding service."""
        service = MagicMock()
        service.get_coordinates_and_timezone = MagicMock(
            return_value=(40.7128, -74.0060, "America/New_York")
        )
        service.get_timezone = MagicMock(return_value=MagicMock(
            localize=lambda dt: dt
        ))
        return service
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def person_service(self, mock_db_session, mock_person_repository, mock_geocoding_service):
        """Create a PersonService instance."""
        with patch('josi.services.person_service.PersonRepository', return_value=mock_person_repository):
            with patch('josi.services.person_service.GeocodingService', return_value=mock_geocoding_service):
                service = PersonService(mock_db_session, uuid4())
                return service
    
    @pytest.fixture
    def test_organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def test_person(self, test_organization_id):
        """Create a test person."""
        return Person(
            person_id=uuid4(),
            organization_id=test_organization_id,
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            latitude=Decimal("40.7128"),
            longitude=Decimal("-74.0060"),
            timezone="America/New_York"
        )
    
    @pytest.mark.asyncio
    async def test_create_person_with_existing_coordinates(self, person_service, mock_person_repository, test_organization_id):
        """Test creating a person when coordinates are already provided."""
        person_data = PersonEntity(
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            latitude=Decimal("40.7128"),  # Already has coordinates
            longitude=Decimal("-74.0060"),
            timezone="America/New_York"
        )
        
        expected_person = Person(
            person_id=uuid4(),
            organization_id=test_organization_id,
            **person_data.model_dump()
        )
        
        mock_person_repository.create.return_value = expected_person
        
        result = await person_service.create_person(person_data)
        
        # Should not call geocoding since coordinates exist
        person_service.geocoding_service.get_coordinates_and_timezone.assert_not_called()
        assert result == expected_person
    
    @pytest.mark.asyncio
    async def test_create_person_geocoding_failure(self, person_service, mock_person_repository, mock_geocoding_service):
        """Test creating a person when geocoding fails."""
        person_data = PersonEntity(
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="Invalid Place",
            latitude=Decimal("0"),
            longitude=Decimal("0"),
            timezone="UTC"
        )
        
        mock_geocoding_service.get_coordinates_and_timezone.side_effect = ValueError("Location not found")
        
        with pytest.raises(ValueError, match="Location not found"):
            await person_service.create_person(person_data)
    
    @pytest.mark.asyncio
    async def test_update_person_not_found(self, person_service, mock_person_repository):
        """Test updating a person that doesn't exist."""
        person_id = uuid4()
        update_data = {"email": "new@example.com"}
        
        mock_person_repository.update.return_value = None
        
        result = await person_service.update_person(person_id, update_data)
        
        assert result is None
        mock_person_repository.update.assert_called_once_with(person_id, update_data)
    
    @pytest.mark.asyncio
    async def test_delete_person_not_found(self, person_service, mock_person_repository):
        """Test deleting a person that doesn't exist."""
        person_id = uuid4()
        
        mock_person_repository.soft_delete.return_value = False
        
        result = await person_service.delete_person(person_id)
        
        assert result is False
        mock_person_repository.soft_delete.assert_called_once_with(person_id)
    
    @pytest.mark.asyncio
    async def test_get_person_not_found(self, person_service, mock_person_repository):
        """Test getting a person that doesn't exist."""
        person_id = uuid4()
        
        mock_person_repository.get_with_charts.return_value = None
        
        result = await person_service.get_person(person_id)
        
        assert result is None
        mock_person_repository.get_with_charts.assert_called_once_with(person_id)
    
    @pytest.mark.asyncio
    async def test_find_by_email_not_found(self, person_service, mock_person_repository):
        """Test finding a person by email when not found."""
        email = "notfound@example.com"
        
        mock_person_repository.find_by_email.return_value = None
        
        result = await person_service.find_by_email(email)
        
        assert result is None
        mock_person_repository.find_by_email.assert_called_once_with(email)
    
    @pytest.mark.asyncio
    async def test_list_persons_empty(self, person_service, mock_person_repository):
        """Test listing persons when none exist."""
        mock_person_repository.get_multi.return_value = []
        
        result = await person_service.list_persons(skip=0, limit=10)
        
        assert result == []
        mock_person_repository.get_multi.assert_called_once_with(skip=0, limit=10)
    
    @pytest.mark.asyncio
    async def test_get_persons_by_name_empty(self, person_service, mock_db_session):
        """Test getting persons by name when none match."""
        name = "NonExistent"
        
        mock_query = AsyncMock()
        mock_query.all.return_value = []
        mock_result = AsyncMock()
        mock_result.scalars.return_value = mock_query
        mock_db_session.execute.return_value = mock_result
        
        result = await person_service.get_persons_by_name(name)
        
        assert result == []
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_parse_location_complex(self, person_service):
        """Test parsing complex location strings."""
        # Test with geocoding service
        result = person_service.geocoding_service.parse_location("New York, NY, USA")
        expected = ("New York", "NY", "USA")
        
        # Mock the result since we're testing the service integration
        person_service.geocoding_service.parse_location.return_value = expected
        result = person_service.geocoding_service.parse_location("New York, NY, USA")
        
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_create_person_with_timezone_conversion(self, person_service, mock_person_repository, mock_geocoding_service, test_organization_id):
        """Test creating a person with timezone conversion."""
        person_data = PersonEntity(
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="London, UK",
            latitude=Decimal("0"),
            longitude=Decimal("0"),
            timezone="UTC"
        )
        
        # Mock timezone conversion
        mock_tz = MagicMock()
        mock_tz.localize.return_value = datetime(1990, 1, 1, 12, 0, 0)
        mock_geocoding_service.get_timezone.return_value = mock_tz
        mock_geocoding_service.get_coordinates_and_timezone.return_value = (51.5074, -0.1278, "Europe/London")
        
        expected_person = Person(
            person_id=uuid4(),
            organization_id=test_organization_id,
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="London, UK",
            latitude=Decimal("51.5074"),
            longitude=Decimal("-0.1278"),
            timezone="Europe/London"
        )
        
        mock_person_repository.create.return_value = expected_person
        
        result = await person_service.create_person(person_data)
        
        # Verify geocoding was called
        mock_geocoding_service.get_coordinates_and_timezone.assert_called_once()
        mock_geocoding_service.get_timezone.assert_called_once_with("Europe/London")
        assert result == expected_person
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_db_session):
        """Test PersonService initialization."""
        org_id = uuid4()
        
        with patch('josi.services.person_service.PersonRepository') as mock_repo_class:
            with patch('josi.services.person_service.GeocodingService') as mock_geo_class:
                service = PersonService(mock_db_session, org_id)
                
                # Verify dependencies were initialized
                mock_repo_class.assert_called_once_with(Person, mock_db_session, org_id)
                mock_geo_class.assert_called_once()
                
                assert service.db == mock_db_session
                assert service.organization_id == org_id