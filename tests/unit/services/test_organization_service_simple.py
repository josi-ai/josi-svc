"""Simple unit tests for Organization service."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from josi.services.organization_service import OrganizationService
from josi.models.organization_model import Organization


class TestOrganizationServiceSimple:
    """Simple test coverage for OrganizationService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock organization repository."""
        return AsyncMock()
    
    @pytest.fixture
    def organization_service(self, mock_repository):
        """Create OrganizationService with mocked repository."""
        return OrganizationService(organization_repository=mock_repository)
    
    @pytest.fixture
    def test_organization(self):
        """Test organization instance."""
        return Organization(
            organization_id=str(uuid4()),
            name="Test Organization",
            contact_email="test@example.com",
            plan_type="premium",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_create_organization(self, organization_service, mock_repository, test_organization):
        """Test creating an organization."""
        org_data = {
            'name': 'New Organization',
            'contact_email': 'new@example.com',
            'plan_type': 'basic'
        }
        
        mock_repository.create.return_value = test_organization
        
        result = await organization_service.create_organization(org_data)
        
        assert result == test_organization
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_organization(self, organization_service, mock_repository, test_organization):
        """Test getting an organization."""
        mock_repository.get.return_value = test_organization
        
        result = await organization_service.get_organization(test_organization.organization_id)
        
        assert result == test_organization
        mock_repository.get.assert_called_once_with(test_organization.organization_id)
    
    @pytest.mark.asyncio
    async def test_update_organization(self, organization_service, mock_repository, test_organization):
        """Test updating an organization."""
        update_data = {'contact_email': 'updated@example.com'}
        updated_org = test_organization.model_copy(update={'contact_email': 'updated@example.com'})
        
        mock_repository.get.return_value = test_organization
        mock_repository.update.return_value = updated_org
        
        result = await organization_service.update_organization(
            test_organization.organization_id,
            update_data
        )
        
        assert result.contact_email == 'updated@example.com'
    
    @pytest.mark.asyncio
    async def test_delete_organization(self, organization_service, mock_repository, test_organization):
        """Test deleting an organization."""
        mock_repository.get.return_value = test_organization
        mock_repository.soft_delete.return_value = True
        
        result = await organization_service.delete_organization(test_organization.organization_id)
        
        assert result is True
        mock_repository.soft_delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_organizations(self, organization_service, mock_repository, test_organization):
        """Test listing organizations."""
        mock_repository.list.return_value = [test_organization]
        
        result = await organization_service.list_organizations(skip=0, limit=10)
        
        assert len(result) == 1
        assert result[0] == test_organization
    
    @pytest.mark.asyncio
    async def test_get_by_api_key(self, organization_service, mock_repository, test_organization):
        """Test getting organization by API key."""
        api_key = "test-api-key"
        mock_repository.get_by_api_key.return_value = test_organization
        
        result = await organization_service.get_by_api_key(api_key)
        
        assert result == test_organization
        mock_repository.get_by_api_key.assert_called_once_with(api_key)
    
    @pytest.mark.asyncio
    async def test_activate_organization(self, organization_service, mock_repository, test_organization):
        """Test activating an organization."""
        test_organization.is_active = False
        activated_org = test_organization.model_copy(update={'is_active': True})
        
        mock_repository.get.return_value = test_organization
        mock_repository.update.return_value = activated_org
        
        result = await organization_service.activate_organization(test_organization.organization_id)
        
        assert result.is_active is True
    
    @pytest.mark.asyncio
    async def test_deactivate_organization(self, organization_service, mock_repository, test_organization):
        """Test deactivating an organization."""
        test_organization.is_active = True
        deactivated_org = test_organization.model_copy(update={'is_active': False})
        
        mock_repository.get.return_value = test_organization
        mock_repository.update.return_value = deactivated_org
        
        result = await organization_service.deactivate_organization(test_organization.organization_id)
        
        assert result.is_active is False
    
    @pytest.mark.asyncio
    async def test_update_plan(self, organization_service, mock_repository, test_organization):
        """Test updating organization plan."""
        new_plan = 'enterprise'
        updated_org = test_organization.model_copy(update={'plan_type': new_plan})
        
        mock_repository.get.return_value = test_organization
        mock_repository.update.return_value = updated_org
        
        result = await organization_service.update_plan(test_organization.organization_id, new_plan)
        
        assert result.plan_type == 'enterprise'
    
    @pytest.mark.asyncio
    async def test_validate_organization_data(self, organization_service):
        """Test organization data validation."""
        # Valid data
        valid_data = {
            'name': 'Valid Org',
            'contact_email': 'valid@example.com'
        }
        
        is_valid = organization_service.validate_organization_data(valid_data)
        assert is_valid is True
        
        # Invalid email
        invalid_data = {
            'name': 'Invalid Org',
            'contact_email': 'invalid-email'
        }
        
        with pytest.raises(ValueError, match="Invalid email"):
            organization_service.validate_organization_data(invalid_data)
        
        # Missing name
        invalid_data = {'contact_email': 'test@example.com'}
        
        with pytest.raises(ValueError, match="Organization name is required"):
            organization_service.validate_organization_data(invalid_data)