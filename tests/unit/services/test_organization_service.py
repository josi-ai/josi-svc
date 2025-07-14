"""Unit tests for OrganizationService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from josi.services.organization_service import OrganizationService
from josi.models.organization_model import Organization, OrganizationEntity


class TestOrganizationService:
    """Test OrganizationService functionality."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_organization_repository(self):
        """Create a mock organization repository."""
        repo = AsyncMock()
        return repo
    
    @pytest.fixture
    def organization_service(self, mock_db_session, mock_organization_repository):
        """Create an OrganizationService instance."""
        with patch('josi.services.organization_service.OrganizationRepository', return_value=mock_organization_repository):
            service = OrganizationService(mock_db_session)
            service.repository = mock_organization_repository
            return service
    
    @pytest.fixture
    def test_organization(self):
        """Create a test organization."""
        return Organization(
            organization_id=uuid4(),
            name="Test Organization",
            slug="test-org",
            api_key="test-api-key-12345",
            is_active=True,
            plan_type="free",
            monthly_api_limit=1000,
            current_month_usage=0,
            contact_email="admin@testorg.com",
            contact_name="Test Admin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_create_organization(self, organization_service, mock_organization_repository):
        """Test creating an organization."""
        # Input data
        org_data = OrganizationEntity(
            name="New Organization",
            slug="new-org",
            contact_email="admin@neworg.com",
            contact_name="New Admin"
        )
        
        # Expected organization
        expected_org = Organization(
            organization_id=uuid4(),
            name="New Organization",
            slug="new-org",
            api_key="generated-api-key",
            is_active=True,
            plan_type="free",
            monthly_api_limit=1000,
            current_month_usage=0,
            contact_email="admin@neworg.com",
            contact_name="New Admin"
        )
        
        # Mock repository response
        mock_organization_repository.create.return_value = expected_org
        
        # Call service
        result = await organization_service.create_organization(org_data)
        
        # Verify repository was called
        assert mock_organization_repository.create.called
        create_args = mock_organization_repository.create.call_args[0][0]
        assert create_args.name == "New Organization"
        assert create_args.slug == "new-org"
        
        # Verify result
        assert result == expected_org
    
    @pytest.mark.asyncio
    async def test_get_organization_by_id(self, organization_service, mock_organization_repository, test_organization):
        """Test getting an organization by ID."""
        org_id = test_organization.organization_id
        
        # Mock repository response
        mock_organization_repository.get.return_value = test_organization
        
        # Call service
        result = await organization_service.get_organization(org_id)
        
        # Verify repository was called
        mock_organization_repository.get.assert_called_once_with(org_id)
        
        # Verify result
        assert result == test_organization
    
    @pytest.mark.asyncio
    async def test_get_organization_not_found(self, organization_service, mock_organization_repository):
        """Test getting a non-existent organization."""
        org_id = uuid4()
        
        # Mock repository response
        mock_organization_repository.get.return_value = None
        
        # Call service and expect exception
        with pytest.raises(ValueError, match="Organization not found"):
            await organization_service.get_organization(org_id)
    
    @pytest.mark.asyncio
    async def test_get_organization_by_api_key(self, organization_service, mock_organization_repository, test_organization):
        """Test getting an organization by API key."""
        api_key = test_organization.api_key
        
        # Mock repository response
        mock_organization_repository.get_by_api_key.return_value = test_organization
        
        # Call service
        result = await organization_service.get_organization_by_api_key(api_key)
        
        # Verify repository was called
        mock_organization_repository.get_by_api_key.assert_called_once_with(api_key)
        
        # Verify result
        assert result == test_organization
    
    @pytest.mark.asyncio
    async def test_update_organization(self, organization_service, mock_organization_repository, test_organization):
        """Test updating an organization."""
        org_id = test_organization.organization_id
        update_data = {
            "contact_email": "newemail@testorg.com",
            "contact_phone": "+1234567890",
            "plan_type": "premium"
        }
        
        # Updated organization
        updated_org = Organization(
            **test_organization.model_dump(),
            contact_email="newemail@testorg.com",
            contact_phone="+1234567890",
            plan_type="premium",
            monthly_api_limit=10000  # Premium limit
        )
        
        # Mock repository responses
        mock_organization_repository.get.return_value = test_organization
        mock_organization_repository.update.return_value = updated_org
        
        # Call service
        result = await organization_service.update_organization(org_id, update_data)
        
        # Verify repository was called
        mock_organization_repository.get.assert_called_once_with(org_id)
        mock_organization_repository.update.assert_called_once()
        
        # Verify result
        assert result == updated_org
    
    @pytest.mark.asyncio
    async def test_deactivate_organization(self, organization_service, mock_organization_repository, test_organization):
        """Test deactivating an organization."""
        org_id = test_organization.organization_id
        
        # Deactivated organization
        deactivated_org = Organization(
            **test_organization.model_dump(),
            is_active=False
        )
        
        # Mock repository responses
        mock_organization_repository.get.return_value = test_organization
        mock_organization_repository.update.return_value = deactivated_org
        
        # Call service
        result = await organization_service.deactivate_organization(org_id)
        
        # Verify repository was called
        mock_organization_repository.get.assert_called_once_with(org_id)
        mock_organization_repository.update.assert_called_once()
        update_args = mock_organization_repository.update.call_args[0][1]
        assert update_args["is_active"] is False
        
        # Verify result
        assert result == deactivated_org
        assert result.is_active is False
    
    @pytest.mark.asyncio
    async def test_rotate_api_key(self, organization_service, mock_organization_repository, test_organization):
        """Test rotating an organization's API key."""
        org_id = test_organization.organization_id
        
        # Organization with new API key
        updated_org = Organization(
            **test_organization.model_dump(),
            api_key="new-api-key-67890"
        )
        
        # Mock repository responses
        mock_organization_repository.get.return_value = test_organization
        mock_organization_repository.update.return_value = updated_org
        
        # Call service
        result = await organization_service.rotate_api_key(org_id)
        
        # Verify repository was called
        mock_organization_repository.get.assert_called_once_with(org_id)
        mock_organization_repository.update.assert_called_once()
        update_args = mock_organization_repository.update.call_args[0][1]
        assert "api_key" in update_args
        assert update_args["api_key"] != test_organization.api_key
        
        # Verify result
        assert result == updated_org
    
    @pytest.mark.asyncio
    async def test_increment_usage(self, organization_service, mock_organization_repository, test_organization):
        """Test incrementing organization usage."""
        org_id = test_organization.organization_id
        
        # Organization with incremented usage
        updated_org = Organization(
            **test_organization.model_dump(),
            current_month_usage=1
        )
        
        # Mock repository responses
        mock_organization_repository.get.return_value = test_organization
        mock_organization_repository.update.return_value = updated_org
        
        # Call service
        result = await organization_service.increment_usage(org_id)
        
        # Verify repository was called
        mock_organization_repository.get.assert_called_once_with(org_id)
        mock_organization_repository.update.assert_called_once()
        update_args = mock_organization_repository.update.call_args[0][1]
        assert update_args["current_month_usage"] == 1
        
        # Verify result
        assert result == updated_org
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_ok(self, organization_service, mock_organization_repository, test_organization):
        """Test checking rate limit when under limit."""
        org_id = test_organization.organization_id
        
        # Organization under limit
        test_organization.current_month_usage = 500
        test_organization.monthly_api_limit = 1000
        
        # Mock repository response
        mock_organization_repository.get.return_value = test_organization
        
        # Call service
        result = await organization_service.check_rate_limit(org_id)
        
        # Verify result
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, organization_service, mock_organization_repository, test_organization):
        """Test checking rate limit when exceeded."""
        org_id = test_organization.organization_id
        
        # Organization over limit
        test_organization.current_month_usage = 1001
        test_organization.monthly_api_limit = 1000
        
        # Mock repository response
        mock_organization_repository.get.return_value = test_organization
        
        # Call service
        result = await organization_service.check_rate_limit(org_id)
        
        # Verify result
        assert result is False
    
    @pytest.mark.asyncio
    async def test_list_organizations(self, organization_service, mock_organization_repository, test_organization):
        """Test listing organizations."""
        # Mock repository response
        mock_organization_repository.get_multi.return_value = [test_organization]
        
        # Call service
        result = await organization_service.list_organizations(skip=0, limit=10)
        
        # Verify repository was called
        mock_organization_repository.get_multi.assert_called_once_with(skip=0, limit=10)
        
        # Verify result
        assert result == [test_organization]