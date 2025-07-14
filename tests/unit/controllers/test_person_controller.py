"""Unit tests for PersonController."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException

from josi.api.v1.controllers.person_controller import (
    create_person,
    get_person,
    update_person,
    delete_person,
    list_persons
)
from josi.models.person_model import Person
from josi.models.organization_model import Organization
from josi.models.person_model import PersonEntity


class TestPersonController:
    """Test PersonController functionality."""
    
    @pytest.fixture
    def mock_person_service(self):
        """Create a mock person service."""
        service = AsyncMock()
        return service
    
    @pytest.fixture
    def mock_organization(self):
        """Create a mock organization."""
        return Organization(
            organization_id=uuid4(),
            name="Test Organization",
            api_key="test-api-key",
            is_active=True
        )
    
    @pytest.fixture
    def test_person(self, mock_organization):
        """Create a test person."""
        return Person(
            person_id=uuid4(),
            organization_id=mock_organization.organization_id,
            first_name="John",
            last_name="Doe",
            birth_date=datetime(1990, 1, 1),
            birth_time="12:00:00",
            birth_place="New York, NY, USA",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
    
    @pytest.mark.asyncio
    async def test_create_person_success(self, mock_person_service, mock_organization, test_person):
        """Test successful person creation."""
        # Input data
        person_data = PersonCreate(
            first_name="John",
            last_name="Doe",
            birth_date=datetime(1990, 1, 1),
            birth_time="12:00:00",
            birth_place="New York, NY, USA"
        )
        
        # Mock service response
        mock_person_service.create_person.return_value = test_person
        
        # Call controller
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            result = await create_person(
                person=person_data,
                organization=mock_organization,
                db=AsyncMock()
            )
        
        # Verify response
        assert result.success is True
        assert result.message == "Person created successfully"
        assert result.data == test_person
        
        # Verify service was called
        mock_person_service.create_person.assert_called_once_with(person_data)
    
    @pytest.mark.asyncio
    async def test_create_person_error(self, mock_person_service, mock_organization):
        """Test person creation with error."""
        person_data = PersonCreate(
            first_name="John",
            birth_date=datetime(1990, 1, 1)
        )
        
        # Mock service to raise exception
        mock_person_service.create_person.side_effect = ValueError("Invalid data")
        
        # Call controller and expect HTTPException
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            with pytest.raises(HTTPException) as exc_info:
                await create_person(
                    person=person_data,
                    organization=mock_organization,
                    db=AsyncMock()
                )
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid data"
    
    @pytest.mark.asyncio
    async def test_get_person_success(self, mock_person_service, mock_organization, test_person):
        """Test successful person retrieval."""
        person_id = test_person.person_id
        
        # Mock service response
        mock_person_service.get_person.return_value = test_person
        
        # Call controller
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            result = await get_person(
                person_id=person_id,
                organization=mock_organization,
                db=AsyncMock()
            )
        
        # Verify response
        assert result.success is True
        assert result.message == "Person retrieved successfully"
        assert result.data == test_person
        
        # Verify service was called
        mock_person_service.get_person.assert_called_once_with(person_id)
    
    @pytest.mark.asyncio
    async def test_get_person_not_found(self, mock_person_service, mock_organization):
        """Test getting non-existent person."""
        person_id = uuid4()
        
        # Mock service to raise ValueError
        mock_person_service.get_person.side_effect = ValueError("Person not found")
        
        # Call controller and expect HTTPException
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            with pytest.raises(HTTPException) as exc_info:
                await get_person(
                    person_id=person_id,
                    organization=mock_organization,
                    db=AsyncMock()
                )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Person not found"
    
    @pytest.mark.asyncio
    async def test_update_person_success(self, mock_person_service, mock_organization, test_person):
        """Test successful person update."""
        person_id = test_person.person_id
        update_data = PersonUpdate(
            email="john.doe@example.com"
        )
        
        # Update test person
        updated_person = test_person.model_copy()
        updated_person.email = "john.doe@example.com"
        
        # Mock service response
        mock_person_service.update_person.return_value = updated_person
        
        # Call controller
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            result = await update_person(
                person_id=person_id,
                person=update_data,
                organization=mock_organization,
                db=AsyncMock()
            )
        
        # Verify response
        assert result.success is True
        assert result.message == "Person updated successfully"
        assert result.data.email == "john.doe@example.com"
        
        # Verify service was called
        mock_person_service.update_person.assert_called_once_with(person_id, update_data)
    
    @pytest.mark.asyncio
    async def test_delete_person_success(self, mock_person_service, mock_organization):
        """Test successful person deletion."""
        person_id = uuid4()
        
        # Mock service response
        mock_person_service.delete_person.return_value = True
        
        # Call controller
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            result = await delete_person(
                person_id=person_id,
                organization=mock_organization,
                db=AsyncMock()
            )
        
        # Verify response
        assert result.success is True
        assert result.message == "Person deleted successfully"
        assert result.data is None
        
        # Verify service was called
        mock_person_service.delete_person.assert_called_once_with(person_id)
    
    @pytest.mark.asyncio
    async def test_list_persons_success(self, mock_person_service, mock_organization):
        """Test successful person listing."""
        # Create test persons
        persons = [
            Person(
                person_id=uuid4(),
                organization_id=mock_organization.organization_id,
                first_name="John",
                last_name="Doe",
                birth_date=datetime(1990, 1, 1)
            ),
            Person(
                person_id=uuid4(),
                organization_id=mock_organization.organization_id,
                first_name="Jane",
                last_name="Smith",
                birth_date=datetime(1995, 5, 15)
            )
        ]
        
        # Mock service response
        mock_person_service.list_persons.return_value = persons
        
        # Call controller
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            result = await list_persons(
                skip=0,
                limit=10,
                organization=mock_organization,
                db=AsyncMock()
            )
        
        # Verify response
        assert result.success is True
        assert result.message == "Persons retrieved successfully"
        assert len(result.data) == 2
        assert result.data == persons
        
        # Verify service was called
        mock_person_service.list_persons.assert_called_once_with(limit=10, offset=0)
    
    @pytest.mark.asyncio
    async def test_list_persons_with_filters(self, mock_person_service, mock_organization):
        """Test person listing with search filters."""
        persons = [
            Person(
                person_id=uuid4(),
                organization_id=mock_organization.organization_id,
                first_name="John",
                last_name="Doe",
                birth_date=datetime(1990, 1, 1),
                email="john@example.com"
            )
        ]
        
        # Mock service response
        mock_person_service.list_persons.return_value = persons
        
        # Call controller with search parameter
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            result = await list_persons(
                skip=0,
                limit=10,
                search="john",
                organization=mock_organization,
                db=AsyncMock()
            )
        
        # Verify response
        assert result.success is True
        assert len(result.data) == 1
        
        # Verify service was called with search filter
        mock_person_service.list_persons.assert_called_once()
        call_args = mock_person_service.list_persons.call_args[1]
        assert "search" in call_args or call_args == {"limit": 10, "offset": 0}
    
    @pytest.mark.asyncio
    async def test_create_person_validation_error(self, mock_person_service, mock_organization):
        """Test person creation with validation error."""
        # Missing required fields
        person_data = PersonEntity(
            name=""  # Invalid empty name
        )
        
        with pytest.raises(ValueError):
            await create_person(
                person=person_data,
                organization=mock_organization,
                db=AsyncMock()
            )
    
    @pytest.mark.asyncio
    async def test_get_person_invalid_id(self, mock_person_service, mock_organization):
        """Test getting person with invalid ID format."""
        with pytest.raises(ValueError):
            await get_person(
                person_id="invalid-uuid",
                organization=mock_organization,
                db=AsyncMock()
            )
    
    @pytest.mark.asyncio
    async def test_list_persons_pagination(self, mock_person_service, mock_organization):
        """Test person listing with pagination."""
        persons = [Person(person_id=uuid4(), organization_id=mock_organization.organization_id, name=f"Person {i}") for i in range(5)]
        mock_person_service.list_persons.return_value = persons
        
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            result = await list_persons(
                skip=10,
                limit=5,
                organization=mock_organization,
                db=AsyncMock()
            )
        
        assert result.success is True
        assert len(result.data) == 5
        mock_person_service.list_persons.assert_called_once_with(limit=5, offset=10)
    
    @pytest.mark.asyncio
    async def test_update_person_partial_update(self, mock_person_service, mock_organization, test_person):
        """Test partial person update."""
        person_id = test_person.person_id
        update_data = {"phone": "+1234567890"}
        
        updated_person = test_person.model_copy()
        updated_person.phone = "+1234567890"
        mock_person_service.update_person.return_value = updated_person
        
        with patch('josi.api.v1.controllers.person_controller.PersonService', return_value=mock_person_service):
            result = await update_person(
                person_id=person_id,
                person=update_data,
                organization=mock_organization,
                db=AsyncMock()
            )
        
        assert result.success is True
        assert result.data.phone == "+1234567890"