"""Fixed comprehensive unit tests for PersonService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from josi.services.person_service import PersonService
from josi.models.person_model import Person, PersonEntity
from josi.repositories.person_repository import PersonRepository


class TestPersonServiceFixed:
    """Fixed comprehensive test coverage for PersonService."""
    
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
        session = AsyncMock()
        session.execute = AsyncMock()
        session.scalar = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session
    
    @pytest.fixture
    def test_organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def person_service(self, mock_db_session, mock_person_repository, mock_geocoding_service, test_organization_id):
        """Create a PersonService instance with mocked dependencies."""
        with patch('josi.services.person_service.PersonRepository', return_value=mock_person_repository):
            with patch('josi.services.person_service.GeocodingService', return_value=mock_geocoding_service):
                service = PersonService(mock_db_session, test_organization_id)
                # Override the instances created in __init__
                service.person_repo = mock_person_repository
                service.geocoding_service = mock_geocoding_service
                return service
    
    @pytest.fixture
    def test_person_data(self):
        """Create test person data."""
        return PersonEntity(
            name="John Doe",
            date_of_birth=datetime(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            email="john.doe@example.com"
        )
    
    @pytest.fixture
    def test_person(self, test_organization_id):
        """Create a test person instance."""
        return Person(
            person_id=uuid4(),
            organization_id=test_organization_id,
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            latitude=Decimal("40.7128"),
            longitude=Decimal("-74.0060"),
            timezone="America/New_York",
            email="john.doe@example.com"
        )
    
    @pytest.mark.asyncio
    async def test_create_person_success(self, person_service, mock_person_repository, mock_geocoding_service, test_person_data, test_person):
        """Test successful person creation with geocoding."""
        # Mock repository create
        mock_person_repository.create.return_value = test_person
        
        # Call service
        result = await person_service.create_person(test_person_data)
        
        # Verify geocoding was called
        mock_geocoding_service.get_coordinates_and_timezone.assert_called_once_with(
            city="New York",
            state="NY",
            country="USA"
        )
        
        # Verify person was created
        mock_person_repository.create.assert_called_once()
        created_data = mock_person_repository.create.call_args[0][0]
        assert created_data["name"] == "John Doe"
        assert created_data["latitude"] == 40.7128
        assert created_data["longitude"] == -74.0060
        assert created_data["timezone"] == "America/New_York"
        
        assert result == test_person
    
    @pytest.mark.asyncio
    async def test_create_person_simple_location(self, person_service, mock_person_repository, mock_geocoding_service, test_person):
        """Test creating person with simple location (city only)."""
        person_data = PersonEntity(
            name="Jane Doe",
            date_of_birth=datetime(1995, 5, 15),
            time_of_birth=datetime(1995, 5, 15, 8, 30, 0),
            place_of_birth="London",
            email="jane.doe@example.com"
        )
        
        mock_geocoding_service.get_coordinates_and_timezone.return_value = (51.5074, -0.1278, "Europe/London")
        mock_person_repository.create.return_value = test_person
        
        result = await person_service.create_person(person_data)
        
        # Verify geocoding was called with city only
        mock_geocoding_service.get_coordinates_and_timezone.assert_called_once_with(
            city="London",
            state="",
            country=""
        )
        
        assert result == test_person
    
    @pytest.mark.asyncio
    async def test_update_person_success(self, person_service, mock_person_repository, test_person):
        """Test successful person update."""
        person_id = test_person.person_id
        update_data = {"email": "newemail@example.com", "name": "John Updated"}
        
        mock_person_repository.update.return_value = test_person
        
        result = await person_service.update_person(person_id, update_data)
        
        assert result == test_person
        mock_person_repository.update.assert_called_once_with(person_id, update_data)
    
    @pytest.mark.asyncio
    async def test_update_person_not_found(self, person_service, mock_person_repository):
        """Test updating non-existent person."""
        person_id = uuid4()
        update_data = {"email": "newemail@example.com"}
        
        mock_person_repository.update.return_value = None
        
        result = await person_service.update_person(person_id, update_data)
        
        assert result is None
        mock_person_repository.update.assert_called_once_with(person_id, update_data)
    
    @pytest.mark.asyncio
    async def test_delete_person_success(self, person_service, mock_person_repository):
        """Test successful person deletion."""
        person_id = uuid4()
        
        mock_person_repository.soft_delete.return_value = True
        
        result = await person_service.delete_person(person_id)
        
        assert result is True
        mock_person_repository.soft_delete.assert_called_once_with(person_id)
    
    @pytest.mark.asyncio
    async def test_delete_person_not_found(self, person_service, mock_person_repository):
        """Test deleting non-existent person."""
        person_id = uuid4()
        
        mock_person_repository.soft_delete.return_value = False
        
        result = await person_service.delete_person(person_id)
        
        assert result is False
        mock_person_repository.soft_delete.assert_called_once_with(person_id)
    
    @pytest.mark.asyncio
    async def test_get_person_success(self, person_service, mock_person_repository, test_person):
        """Test getting person by ID."""
        person_id = test_person.person_id
        
        mock_person_repository.get_with_charts.return_value = test_person
        
        result = await person_service.get_person(person_id)
        
        assert result == test_person
        mock_person_repository.get_with_charts.assert_called_once_with(person_id)
    
    @pytest.mark.asyncio
    async def test_get_person_not_found(self, person_service, mock_person_repository):
        """Test getting non-existent person."""
        person_id = uuid4()
        
        mock_person_repository.get_with_charts.return_value = None
        
        result = await person_service.get_person(person_id)
        
        assert result is None
        mock_person_repository.get_with_charts.assert_called_once_with(person_id)
    
    @pytest.mark.asyncio
    async def test_list_persons_success(self, person_service, mock_person_repository, test_person):
        """Test listing persons with pagination."""
        persons = [test_person]
        
        mock_person_repository.get_multi.return_value = persons
        
        result = await person_service.list_persons(skip=0, limit=10)
        
        assert result == persons
        mock_person_repository.get_multi.assert_called_once_with(skip=0, limit=10)
    
    @pytest.mark.asyncio
    async def test_list_persons_empty(self, person_service, mock_person_repository):
        """Test listing persons when none exist."""
        mock_person_repository.get_multi.return_value = []
        
        result = await person_service.list_persons(skip=0, limit=10)
        
        assert result == []
        mock_person_repository.get_multi.assert_called_once_with(skip=0, limit=10)
    
    @pytest.mark.asyncio
    async def test_find_by_email_success(self, person_service, mock_person_repository, test_person):
        """Test finding person by email."""
        email = "john.doe@example.com"
        
        mock_person_repository.find_by_email.return_value = test_person
        
        result = await person_service.find_by_email(email)
        
        assert result == test_person
        mock_person_repository.find_by_email.assert_called_once_with(email)
    
    @pytest.mark.asyncio
    async def test_find_by_email_not_found(self, person_service, mock_person_repository):
        """Test finding person by email when not found."""
        email = "notfound@example.com"
        
        mock_person_repository.find_by_email.return_value = None
        
        result = await person_service.find_by_email(email)
        
        assert result is None
        mock_person_repository.find_by_email.assert_called_once_with(email)
    
    @pytest.mark.asyncio
    async def test_get_persons_by_name_success(self, person_service, mock_db_session, test_person):
        """Test getting persons by name."""
        name = "John"
        
        # Mock the query execution
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [test_person]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await person_service.get_persons_by_name(name)
        
        assert result == [test_person]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_persons_by_name_empty(self, person_service, mock_db_session):
        """Test getting persons by name when none match."""
        name = "NonExistent"
        
        # Mock empty result
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await person_service.get_persons_by_name(name)
        
        assert result == []
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_db_session, test_organization_id):
        """Test PersonService initialization."""
        with patch('josi.services.person_service.PersonRepository') as mock_repo_class:
            with patch('josi.services.person_service.GeocodingService') as mock_geo_class:
                service = PersonService(mock_db_session, test_organization_id)
                
                # Verify dependencies were initialized
                mock_repo_class.assert_called_once_with(Person, mock_db_session, test_organization_id)
                mock_geo_class.assert_called_once()
                
                assert service.db == mock_db_session
                assert service.organization_id == test_organization_id
    
    @pytest.mark.asyncio
    async def test_create_person_with_city_state_country(self, person_service, mock_person_repository, mock_geocoding_service, test_person):
        """Test creating person with full location details."""
        person_data = PersonEntity(
            name="Alice Smith",
            date_of_birth=datetime(1985, 3, 20),
            time_of_birth=datetime(1985, 3, 20, 14, 45, 0),
            place_of_birth="Los Angeles, California, United States",
            email="alice@example.com"
        )
        
        mock_geocoding_service.get_coordinates_and_timezone.return_value = (34.0522, -118.2437, "America/Los_Angeles")
        mock_person_repository.create.return_value = test_person
        
        result = await person_service.create_person(person_data)
        
        # Verify proper parsing of location
        mock_geocoding_service.get_coordinates_and_timezone.assert_called_once_with(
            city="Los Angeles",
            state="California",
            country="United States"
        )
        
        assert result == test_person
    
    @pytest.mark.asyncio
    async def test_create_person_timezone_handling(self, person_service, mock_person_repository, mock_geocoding_service, test_person):
        """Test timezone handling during person creation."""
        person_data = PersonEntity(
            name="Bob Wilson",
            date_of_birth=datetime(1992, 7, 10),
            time_of_birth=datetime(1992, 7, 10, 9, 15, 0),
            place_of_birth="Tokyo, Japan",
            email="bob@example.com"
        )
        
        # Mock timezone object
        mock_tz = MagicMock()
        mock_tz.localize = MagicMock(return_value=datetime(1992, 7, 10, 9, 15, 0))
        
        mock_geocoding_service.get_coordinates_and_timezone.return_value = (35.6762, 139.6503, "Asia/Tokyo")
        mock_geocoding_service.get_timezone.return_value = mock_tz
        mock_person_repository.create.return_value = test_person
        
        result = await person_service.create_person(person_data)
        
        # Verify timezone methods were called
        mock_geocoding_service.get_timezone.assert_called_once_with("Asia/Tokyo")
        mock_tz.localize.assert_called_once()
        
        assert result == test_person