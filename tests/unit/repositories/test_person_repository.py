"""Unit tests for PersonRepository."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from josi.repositories.person_repository import PersonRepository
from josi.models.person_model import Person


class TestPersonRepository:
    """Test PersonRepository functionality."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.scalar = AsyncMock()
        return session
    
    @pytest.fixture
    def test_organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def person_repository(self, mock_db_session, test_organization_id):
        """Create a PersonRepository instance."""
        return PersonRepository(Person, mock_db_session, test_organization_id)
    
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
            timezone="America/New_York",
            email="john.doe@example.com"
        )
    
    @pytest.mark.asyncio
    async def test_find_by_email(self, person_repository, mock_db_session, test_person):
        """Test finding a person by email."""
        email = "john.doe@example.com"
        
        # Mock the database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = test_person
        mock_db_session.execute.return_value = mock_result
        
        result = await person_repository.find_by_email(email)
        
        assert result == test_person
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_by_email_not_found(self, person_repository, mock_db_session):
        """Test finding a person by email when not found."""
        email = "notfound@example.com"
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await person_repository.find_by_email(email)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_with_charts(self, person_repository, mock_db_session, test_person):
        """Test getting a person with charts."""
        person_id = test_person.person_id
        
        # Mock the database query
        mock_result = AsyncMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = test_person
        mock_db_session.execute.return_value = mock_result
        
        result = await person_repository.get_with_charts(person_id)
        
        assert result == test_person
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_with_charts_not_found(self, person_repository, mock_db_session):
        """Test getting a person with charts when not found."""
        person_id = uuid4()
        
        mock_result = AsyncMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await person_repository.get_with_charts(person_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_by_name(self, person_repository, mock_db_session, test_person):
        """Test searching persons by name."""
        search_term = "John"
        
        # Mock the database query
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [test_person]
        mock_db_session.execute.return_value = mock_result
        
        result = await person_repository.search_by_name(search_term)
        
        assert result == [test_person]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_by_name_no_results(self, person_repository, mock_db_session):
        """Test searching persons by name with no results."""
        search_term = "NonExistent"
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        result = await person_repository.search_by_name(search_term)
        
        assert result == []
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_external_id(self, person_repository, mock_db_session, test_person):
        """Test getting a person by external ID."""
        external_id = "ext-123"
        test_person.external_id = external_id
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = test_person
        mock_db_session.execute.return_value = mock_result
        
        result = await person_repository.get_by_external_id(external_id)
        
        assert result == test_person
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_external_id_not_found(self, person_repository, mock_db_session):
        """Test getting a person by external ID when not found."""
        external_id = "ext-404"
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await person_repository.get_by_external_id(external_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()