"""Unit tests for Person controller router endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from josi.models.person_model import Person, PersonEntity
from josi.models.organization_model import Organization
from josi.api.response import ResponseModel


class TestPersonControllerRouter:
    """Test coverage for Person controller router endpoints."""
    
    @pytest.fixture
    def mock_person_service(self):
        """Mock person service."""
        with patch('josi.api.v1.controllers.person_controller.PersonService') as mock:
            service = AsyncMock()
            mock.return_value = service
            yield service
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def mock_organization(self):
        """Mock organization."""
        return Organization(
            organization_id=uuid4(),
            name="Test Org",
            api_key="test-api-key"
        )
    
    @pytest.fixture
    def test_person_entity(self):
        """Test person entity for creation."""
        return PersonEntity(
            name="John Doe",
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )
    
    @pytest.fixture
    def test_person(self):
        """Test person instance."""
        return Person(
            person_id=uuid4(),
            name="John Doe",
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
            organization_id=uuid4()
        )
    
    @pytest.mark.asyncio
    async def test_create_person_success(self, mock_person_service, mock_db_session, mock_organization, test_person_entity, test_person):
        """Test successful person creation."""
        # Import here to avoid circular imports
        from josi.api.v1.controllers.person_controller import create_person
        
        # Setup mock
        mock_person_service.create.return_value = test_person
        
        # Call endpoint function directly
        with patch('josi.api.v1.controllers.person_controller.get_current_organization', return_value=mock_organization):
            with patch('josi.api.v1.controllers.person_controller.get_async_db', return_value=mock_db_session):
                result = await create_person(
                    payload=test_person_entity,
                    organization=mock_organization,
                    db=mock_db_session
                )
        
        # Assertions
        assert isinstance(result, ResponseModel)
        assert result.success is True
        assert result.message == "Person created successfully"
        assert result.data["id"] == str(test_person.person_id)
        
        # Verify service was called
        mock_person_service.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_person_success(self, mock_person_service, mock_db_session, mock_organization, test_person):
        """Test successful person retrieval."""
        from josi.api.v1.controllers.person_controller import get_person
        
        # Setup mock
        mock_person_service.get_by_id.return_value = test_person
        
        # Call endpoint
        with patch('josi.api.v1.controllers.person_controller.get_current_organization', return_value=mock_organization):
            with patch('josi.api.v1.controllers.person_controller.get_async_db', return_value=mock_db_session):
                result = await get_person(
                    person_id=test_person.person_id,
                    organization=mock_organization,
                    db=mock_db_session
                )
        
        # Assertions
        assert isinstance(result, ResponseModel)
        assert result.success is True
        assert result.data["id"] == str(test_person.person_id)
    
    @pytest.mark.asyncio
    async def test_get_person_not_found(self, mock_person_service, mock_db_session, mock_organization):
        """Test person not found."""
        from josi.api.v1.controllers.person_controller import get_person
        from fastapi import HTTPException
        
        # Setup mock
        mock_person_service.get_by_id.return_value = None
        person_id = uuid4()
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            with patch('josi.api.v1.controllers.person_controller.get_current_organization', return_value=mock_organization):
                with patch('josi.api.v1.controllers.person_controller.get_async_db', return_value=mock_db_session):
                    await get_person(
                        person_id=person_id,
                        organization=mock_organization,
                        db=mock_db_session
                    )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Person not found"
    
    @pytest.mark.asyncio
    async def test_list_persons_success(self, mock_person_service, mock_db_session, mock_organization, test_person):
        """Test listing persons."""
        from josi.api.v1.controllers.person_controller import list_persons
        
        # Setup mock
        mock_person_service.list.return_value = [test_person]
        
        # Call endpoint
        with patch('josi.api.v1.controllers.person_controller.get_current_organization', return_value=mock_organization):
            with patch('josi.api.v1.controllers.person_controller.get_async_db', return_value=mock_db_session):
                result = await list_persons(
                    search=None,
                    skip=0,
                    limit=100,
                    organization=mock_organization,
                    db=mock_db_session
                )
        
        # Assertions
        assert isinstance(result, ResponseModel)
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["id"] == str(test_person.person_id)
    
    @pytest.mark.asyncio
    async def test_update_person_success(self, mock_person_service, mock_db_session, mock_organization, test_person, test_person_entity):
        """Test updating a person."""
        from josi.api.v1.controllers.person_controller import update_person
        
        # Setup mock
        mock_person_service.update.return_value = test_person
        
        # Call endpoint
        with patch('josi.api.v1.controllers.person_controller.get_current_organization', return_value=mock_organization):
            with patch('josi.api.v1.controllers.person_controller.get_async_db', return_value=mock_db_session):
                result = await update_person(
                    person_id=test_person.person_id,
                    payload=test_person_entity,
                    organization=mock_organization,
                    db=mock_db_session
                )
        
        # Assertions
        assert isinstance(result, ResponseModel)
        assert result.success is True
        assert result.message == "Person updated successfully"
    
    @pytest.mark.asyncio
    async def test_delete_person_success(self, mock_person_service, mock_db_session, mock_organization, test_person):
        """Test deleting a person."""
        from josi.api.v1.controllers.person_controller import delete_person
        
        # Setup mock
        mock_person_service.delete.return_value = True
        
        # Call endpoint
        with patch('josi.api.v1.controllers.person_controller.get_current_organization', return_value=mock_organization):
            with patch('josi.api.v1.controllers.person_controller.get_async_db', return_value=mock_db_session):
                result = await delete_person(
                    person_id=test_person.person_id,
                    organization=mock_organization,
                    db=mock_db_session
                )
        
        # Assertions
        assert isinstance(result, ResponseModel)
        assert result.success is True
        assert result.message == "Person deleted successfully"