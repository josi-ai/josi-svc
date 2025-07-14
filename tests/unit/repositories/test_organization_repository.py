"""Unit tests for OrganizationRepository."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from josi.repositories.organization_repository import OrganizationRepository
from josi.models.organization_model import Organization


class TestOrganizationRepository:
    """Test OrganizationRepository functionality."""
    
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
    def organization_repository(self, mock_db_session):
        """Create an OrganizationRepository instance."""
        return OrganizationRepository(Organization, mock_db_session)
    
    @pytest.fixture
    def test_organization(self):
        """Create a test organization."""
        return Organization(
            organization_id=uuid4(),
            name="Test Organization",
            slug="test-organization",
            api_key="test-api-key-123",
            is_active=True
        )
    
    @pytest.mark.asyncio
    async def test_find_by_api_key(self, organization_repository, mock_db_session, test_organization):
        """Test finding an organization by API key."""
        api_key = "test-api-key-123"
        
        # Mock the database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = test_organization
        mock_db_session.execute.return_value = mock_result
        
        result = await organization_repository.find_by_api_key(api_key)
        
        assert result == test_organization
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_by_api_key_not_found(self, organization_repository, mock_db_session):
        """Test finding an organization by API key when not found."""
        api_key = "invalid-api-key"
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await organization_repository.find_by_api_key(api_key)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_by_slug(self, organization_repository, mock_db_session, test_organization):
        """Test finding an organization by slug."""
        slug = "test-organization"
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = test_organization
        mock_db_session.execute.return_value = mock_result
        
        result = await organization_repository.find_by_slug(slug)
        
        assert result == test_organization
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_by_slug_not_found(self, organization_repository, mock_db_session):
        """Test finding an organization by slug when not found."""
        slug = "non-existent-slug"
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await organization_repository.find_by_slug(slug)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_active_organizations(self, organization_repository, mock_db_session, test_organization):
        """Test getting active organizations."""
        # Mock the database query
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [test_organization]
        mock_db_session.execute.return_value = mock_result
        
        result = await organization_repository.get_active_organizations()
        
        assert result == [test_organization]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_active_organizations_empty(self, organization_repository, mock_db_session):
        """Test getting active organizations when none exist."""
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        result = await organization_repository.get_active_organizations()
        
        assert result == []
        mock_db_session.execute.assert_called_once()