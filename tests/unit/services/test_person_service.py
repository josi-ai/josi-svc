"""Unit tests for PersonService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from josi.services.person_service import PersonService
from josi.models.person_model import Person, PersonEntity
from josi.repositories.person_repository import PersonRepository


class TestPersonService:
    """Test PersonService functionality."""
    
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
            localize=lambda dt: dt  # Just return the datetime as-is for testing
        ))
        return service
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def person_service(self, mock_db_session, mock_person_repository, mock_geocoding_service):
        """Create a PersonService instance."""
        # Mock the repository creation
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
    async def test_create_person_with_geocoding(self, person_service, mock_person_repository, mock_geocoding_service, test_organization_id):
        """Test creating a person with geocoding."""
        # Input data
        person_data = PersonEntity(
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            latitude=Decimal("0"),  # Will be updated by geocoding
            longitude=Decimal("0"),  # Will be updated by geocoding
            timezone="UTC"  # Will be updated by geocoding
        )
        
        # Expected created person
        expected_person = Person(
            person_id=uuid4(),
            organization_id=test_organization_id,
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            latitude=Decimal("40.7128"),
            longitude=Decimal("-74.0060"),
            timezone="America/New_York",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock repository response
        mock_person_repository.create.return_value = expected_person
        
        # Call service
        result = await person_service.create_person(person_data)
        
        # Verify geocoding was called
        mock_geocoding_service.get_coordinates_and_timezone.assert_called_once_with(
            city="New York",
            state="NY",
            country="USA"
        )
        
        # Verify repository was called
        assert mock_person_repository.create.called
        create_args = mock_person_repository.create.call_args[0][0]
        assert create_args["name"] == "John Doe"
        assert create_args["latitude"] == 40.7128
        assert create_args["longitude"] == -74.0060
        assert create_args["timezone"] == "America/New_York"
        
        # Verify result
        assert result == expected_person
    
    @pytest.mark.asyncio
    async def test_get_person_by_id(self, person_service, mock_person_repository, test_person):
        """Test getting a person by ID."""
        person_id = test_person.person_id
        
        # Mock repository response
        mock_person_repository.get_with_charts.return_value = test_person
        
        # Call service
        result = await person_service.get_person(person_id)
        
        # Verify repository was called
        mock_person_repository.get_with_charts.assert_called_once_with(person_id)
        
        # Verify result
        assert result == test_person
    
    @pytest.mark.asyncio
    async def test_find_person_by_email(self, person_service, mock_person_repository, test_person):
        """Test finding a person by email."""
        email = "john.doe@example.com"
        test_person.email = email
        
        # Mock repository response  
        mock_person_repository.find_by_email.return_value = test_person
        
        # Call service
        result = await person_service.find_by_email(email)
        
        # Verify repository was called
        mock_person_repository.find_by_email.assert_called_once_with(email)
        
        # Verify result
        assert result == test_person
    
    @pytest.mark.asyncio
    async def test_update_person(self, person_service, mock_person_repository, test_person):
        """Test updating a person."""
        person_id = test_person.person_id
        update_data = {"email": "john.doe@example.com", "phone": "+1234567890"}
        
        # Updated person
        updated_person = Person(
            **test_person.model_dump(),
            email="john.doe@example.com",
            phone="+1234567890"
        )
        
        # Mock repository response
        mock_person_repository.update.return_value = updated_person
        
        # Call service
        result = await person_service.update_person(person_id, update_data)
        
        # Verify repository was called
        mock_person_repository.update.assert_called_once_with(person_id, update_data)
        
        # Verify result
        assert result == updated_person
    
    @pytest.mark.asyncio 
    async def test_delete_person(self, person_service, mock_person_repository):
        """Test deleting a person."""
        person_id = uuid4()
        
        # Mock repository response
        mock_person_repository.soft_delete.return_value = True
        
        # Call service
        result = await person_service.delete_person(person_id)
        
        # Verify repository was called
        mock_person_repository.soft_delete.assert_called_once_with(person_id)
        
        # Verify result
        assert result is True
    
    @pytest.mark.asyncio
    async def test_list_persons(self, person_service, mock_person_repository, test_person):
        """Test listing persons."""
        # Mock repository response
        mock_person_repository.get_multi.return_value = [test_person]
        
        # Call service
        result = await person_service.list_persons(skip=0, limit=10)
        
        # Verify repository was called
        mock_person_repository.get_multi.assert_called_once_with(skip=0, limit=10)
        
        # Verify result
        assert result == [test_person]
    
    @pytest.mark.asyncio
    async def test_get_persons_by_name(self, person_service, mock_person_repository, test_person):
        """Test getting persons by name."""
        name = "John"
        
        # Mock db query
        mock_query = AsyncMock()
        mock_query.all.return_value = [test_person]
        mock_result = AsyncMock()
        mock_result.scalars.return_value = mock_query
        person_service.db.execute.return_value = mock_result
        
        # Call service
        result = await person_service.get_persons_by_name(name)
        
        # Verify db was queried
        person_service.db.execute.assert_called_once()
        
        # Verify result
        assert result == [test_person]