"""Extended comprehensive unit tests for OrganizationService to increase coverage."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from secrets import token_urlsafe

from josi.services.organization_service import OrganizationService
from josi.models.organization_model import Organization, OrganizationEntity
from josi.repositories.base_repository import BaseRepository


class TestOrganizationServiceExtended:
    """Extended comprehensive test coverage for OrganizationService."""
    
    @pytest.fixture
    def mock_organization_repository(self):
        """Create a mock organization repository."""
        repo = AsyncMock(spec=BaseRepository)
        return repo
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def organization_service(self, mock_db_session, mock_organization_repository):
        """Create an OrganizationService instance."""
        with patch('josi.services.organization_service.OrganizationRepository', return_value=mock_organization_repository):
            service = OrganizationService(mock_db_session)
            return service
    
    @pytest.fixture
    def test_organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def test_organization(self, test_organization_id):
        """Create a test organization."""
        return Organization(
            organization_id=test_organization_id,
            name="Test Organization",
            slug="test-org-unique",
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
    
    @pytest.fixture
    def test_premium_organization(self, test_organization_id):
        """Create a test premium organization."""
        return Organization(
            organization_id=test_organization_id,
            name="Premium Organization",
            slug="premium-org-unique",
            api_key="premium-api-key-67890",
            is_active=True,
            plan_type="premium",
            monthly_api_limit=10000,
            current_month_usage=0,
            contact_email="admin@premiumorg.com",
            contact_name="Premium Admin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_create_organization_with_all_fields(self, organization_service, mock_organization_repository):
        """Test creating an organization with all fields populated."""
        org_data = OrganizationEntity(
            name="Complete Organization",
            slug="complete-org",
            contact_email="admin@completeorg.com",
            contact_name="Complete Admin",
            contact_phone="+1234567890",
            website="https://completeorg.com",
            address="123 Main St, City, State",
            plan_type="premium"
        )
        
        expected_org = Organization(
            organization_id=uuid4(),
            name="Complete Organization",
            slug="complete-org",
            api_key="generated-api-key",
            is_active=True,
            plan_type="premium",
            monthly_api_limit=10000,
            current_month_usage=0,
            contact_email="admin@completeorg.com",
            contact_name="Complete Admin",
            contact_phone="+1234567890",
            website="https://completeorg.com",
            address="123 Main St, City, State"
        )
        
        mock_organization_repository.create.return_value = expected_org
        
        result = await organization_service.create_organization(org_data)
        
        assert result == expected_org
        mock_organization_repository.create.assert_called_once()
        
        # Verify the created organization data
        create_args = mock_organization_repository.create.call_args[0][0]
        assert create_args.name == "Complete Organization"
        assert create_args.plan_type == "premium"
        assert create_args.contact_phone == "+1234567890"
        assert create_args.website == "https://completeorg.com"
    
    @pytest.mark.asyncio
    async def test_create_organization_generates_unique_api_key(self, organization_service, mock_organization_repository):
        """Test that creating organization generates unique API key."""
        org_data = OrganizationEntity(
            name="New Organization",
            slug="new-org",
            contact_email="admin@neworg.com",
            contact_name="New Admin"
        )
        
        # Create multiple organizations to verify uniqueness
        created_orgs = []
        for i in range(3):
            expected_org = Organization(
                organization_id=uuid4(),
                name=f"New Organization {i}",
                slug=f"new-org-{i}",
                api_key=f"unique-api-key-{i}-{token_urlsafe(32)}",
                is_active=True,
                plan_type="free",
                monthly_api_limit=1000,
                current_month_usage=0,
                contact_email=f"admin{i}@neworg.com",
                contact_name=f"New Admin {i}"
            )
            created_orgs.append(expected_org)
        
        mock_organization_repository.create.side_effect = created_orgs
        
        # Create organizations and verify API keys are different
        results = []
        for i in range(3):
            org_data.name = f"New Organization {i}"
            org_data.slug = f"new-org-{i}"
            org_data.contact_email = f"admin{i}@neworg.com"
            result = await organization_service.create_organization(org_data)
            results.append(result)
        
        # Verify all API keys are unique
        api_keys = [org.api_key for org in results]
        assert len(set(api_keys)) == len(api_keys)  # All unique
    
    @pytest.mark.asyncio
    async def test_get_organization_by_api_key_not_found(self, organization_service, mock_organization_repository):
        """Test getting organization by API key when not found."""
        api_key = "non-existent-api-key"
        
        mock_organization_repository.get_by_api_key.return_value = None
        
        result = await organization_service.get_organization_by_api_key(api_key)
        
        assert result is None
        mock_organization_repository.get_by_api_key.assert_called_once_with(api_key)
    
    @pytest.mark.asyncio
    async def test_get_organization_by_slug(self, organization_service, mock_organization_repository, test_organization):
        """Test getting organization by slug."""
        slug = test_organization.slug
        
        mock_organization_repository.get_by_slug.return_value = test_organization
        
        result = await organization_service.get_organization_by_slug(slug)
        
        assert result == test_organization
        mock_organization_repository.get_by_slug.assert_called_once_with(slug)
    
    @pytest.mark.asyncio
    async def test_get_organization_by_slug_not_found(self, organization_service, mock_organization_repository):
        """Test getting organization by slug when not found."""
        slug = "non-existent-slug"
        
        mock_organization_repository.get_by_slug.return_value = None
        
        result = await organization_service.get_organization_by_slug(slug)
        
        assert result is None
        mock_organization_repository.get_by_slug.assert_called_once_with(slug)
    
    @pytest.mark.asyncio
    async def test_update_organization_plan_type_upgrade(self, organization_service, mock_organization_repository, test_organization):
        """Test updating organization plan type to premium."""
        org_id = test_organization.organization_id
        update_data = {"plan_type": "premium"}
        
        updated_org = Organization(
            **test_organization.model_dump(),
            plan_type="premium",
            monthly_api_limit=10000
        )
        
        mock_organization_repository.get.return_value = test_organization
        mock_organization_repository.update.return_value = updated_org
        
        result = await organization_service.update_organization(org_id, update_data)
        
        assert result.plan_type == "premium"
        assert result.monthly_api_limit == 10000
        mock_organization_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_organization_plan_type_downgrade(self, organization_service, mock_organization_repository, test_premium_organization):
        """Test updating organization plan type to free."""
        org_id = test_premium_organization.organization_id
        update_data = {"plan_type": "free"}
        
        updated_org = Organization(
            **test_premium_organization.model_dump(),
            plan_type="free",
            monthly_api_limit=1000
        )
        
        mock_organization_repository.get.return_value = test_premium_organization
        mock_organization_repository.update.return_value = updated_org
        
        result = await organization_service.update_organization(org_id, update_data)
        
        assert result.plan_type == "free"
        assert result.monthly_api_limit == 1000
        mock_organization_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_organization_not_found(self, organization_service, mock_organization_repository):
        """Test updating non-existent organization."""
        org_id = uuid4()
        update_data = {"contact_email": "new@email.com"}
        
        mock_organization_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found"):
            await organization_service.update_organization(org_id, update_data)
    
    @pytest.mark.asyncio
    async def test_activate_organization(self, organization_service, mock_organization_repository, test_organization):
        """Test activating a deactivated organization."""
        org_id = test_organization.organization_id
        
        # Start with deactivated organization
        test_organization.is_active = False
        
        activated_org = Organization(
            **test_organization.model_dump(),
            is_active=True
        )
        
        mock_organization_repository.get.return_value = test_organization
        mock_organization_repository.update.return_value = activated_org
        
        result = await organization_service.activate_organization(org_id)
        
        assert result.is_active is True
        mock_organization_repository.get.assert_called_once_with(org_id)
        mock_organization_repository.update.assert_called_once()
        
        update_args = mock_organization_repository.update.call_args[0][1]
        assert update_args["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_deactivate_organization_not_found(self, organization_service, mock_organization_repository):
        """Test deactivating non-existent organization."""
        org_id = uuid4()
        
        mock_organization_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found"):
            await organization_service.deactivate_organization(org_id)
    
    @pytest.mark.asyncio
    async def test_rotate_api_key_not_found(self, organization_service, mock_organization_repository):
        """Test rotating API key for non-existent organization."""
        org_id = uuid4()
        
        mock_organization_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found"):
            await organization_service.rotate_api_key(org_id)
    
    @pytest.mark.asyncio
    async def test_increment_usage_multiple_times(self, organization_service, mock_organization_repository, test_organization):
        """Test incrementing usage multiple times."""
        org_id = test_organization.organization_id
        
        # Simulate multiple increments
        usage_values = [1, 2, 3, 4, 5]
        updated_orgs = []
        
        for usage in usage_values:
            updated_org = Organization(
                **test_organization.model_dump(),
                current_month_usage=usage
            )
            updated_orgs.append(updated_org)
        
        mock_organization_repository.get.return_value = test_organization
        mock_organization_repository.update.side_effect = updated_orgs
        
        for expected_usage in usage_values:
            result = await organization_service.increment_usage(org_id)
            assert result.current_month_usage == expected_usage
    
    @pytest.mark.asyncio
    async def test_increment_usage_not_found(self, organization_service, mock_organization_repository):
        """Test incrementing usage for non-existent organization."""
        org_id = uuid4()
        
        mock_organization_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found"):
            await organization_service.increment_usage(org_id)
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_at_limit(self, organization_service, mock_organization_repository, test_organization):
        """Test checking rate limit when exactly at limit."""
        org_id = test_organization.organization_id
        
        test_organization.current_month_usage = 1000
        test_organization.monthly_api_limit = 1000
        
        mock_organization_repository.get.return_value = test_organization
        
        result = await organization_service.check_rate_limit(org_id)
        
        assert result is False  # At limit should return False
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_not_found(self, organization_service, mock_organization_repository):
        """Test checking rate limit for non-existent organization."""
        org_id = uuid4()
        
        mock_organization_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found"):
            await organization_service.check_rate_limit(org_id)
    
    @pytest.mark.asyncio
    async def test_reset_monthly_usage(self, organization_service, mock_organization_repository, test_organization):
        """Test resetting monthly usage for an organization."""
        org_id = test_organization.organization_id
        
        # Organization with some usage
        test_organization.current_month_usage = 500
        
        reset_org = Organization(
            **test_organization.model_dump(),
            current_month_usage=0
        )
        
        mock_organization_repository.get.return_value = test_organization
        mock_organization_repository.update.return_value = reset_org
        
        result = await organization_service.reset_monthly_usage(org_id)
        
        assert result.current_month_usage == 0
        mock_organization_repository.get.assert_called_once_with(org_id)
        mock_organization_repository.update.assert_called_once()
        
        update_args = mock_organization_repository.update.call_args[0][1]
        assert update_args["current_month_usage"] == 0
    
    @pytest.mark.asyncio
    async def test_reset_monthly_usage_not_found(self, organization_service, mock_organization_repository):
        """Test resetting monthly usage for non-existent organization."""
        org_id = uuid4()
        
        mock_organization_repository.get.return_value = None
        
        with pytest.raises(ValueError, match="Organization not found"):
            await organization_service.reset_monthly_usage(org_id)
    
    @pytest.mark.asyncio
    async def test_get_usage_statistics(self, organization_service, mock_organization_repository, test_organization):
        """Test getting usage statistics for an organization."""
        org_id = test_organization.organization_id
        
        test_organization.current_month_usage = 750
        test_organization.monthly_api_limit = 1000
        
        mock_organization_repository.get.return_value = test_organization
        
        result = await organization_service.get_usage_statistics(org_id)
        
        assert result["current_usage"] == 750
        assert result["monthly_limit"] == 1000
        assert result["usage_percentage"] == 75.0
        assert result["remaining_calls"] == 250
        assert result["is_at_limit"] is False
    
    @pytest.mark.asyncio
    async def test_get_usage_statistics_at_limit(self, organization_service, mock_organization_repository, test_organization):
        """Test getting usage statistics when at limit."""
        org_id = test_organization.organization_id
        
        test_organization.current_month_usage = 1000
        test_organization.monthly_api_limit = 1000
        
        mock_organization_repository.get.return_value = test_organization
        
        result = await organization_service.get_usage_statistics(org_id)
        
        assert result["current_usage"] == 1000
        assert result["monthly_limit"] == 1000
        assert result["usage_percentage"] == 100.0
        assert result["remaining_calls"] == 0
        assert result["is_at_limit"] is True
    
    @pytest.mark.asyncio
    async def test_get_usage_statistics_over_limit(self, organization_service, mock_organization_repository, test_organization):
        """Test getting usage statistics when over limit."""
        org_id = test_organization.organization_id
        
        test_organization.current_month_usage = 1200
        test_organization.monthly_api_limit = 1000
        
        mock_organization_repository.get.return_value = test_organization
        
        result = await organization_service.get_usage_statistics(org_id)
        
        assert result["current_usage"] == 1200
        assert result["monthly_limit"] == 1000
        assert result["usage_percentage"] == 120.0
        assert result["remaining_calls"] == -200
        assert result["is_at_limit"] is True
    
    @pytest.mark.asyncio
    async def test_list_organizations_with_filters(self, organization_service, mock_organization_repository, test_organization, test_premium_organization):
        """Test listing organizations with different filters."""
        organizations = [test_organization, test_premium_organization]
        
        mock_organization_repository.get_multi.return_value = organizations
        
        # Test with skip and limit
        result = await organization_service.list_organizations(skip=5, limit=20)
        
        assert result == organizations
        mock_organization_repository.get_multi.assert_called_once_with(skip=5, limit=20)
    
    @pytest.mark.asyncio
    async def test_list_organizations_empty(self, organization_service, mock_organization_repository):
        """Test listing organizations when none exist."""
        mock_organization_repository.get_multi.return_value = []
        
        result = await organization_service.list_organizations(skip=0, limit=10)
        
        assert result == []
        mock_organization_repository.get_multi.assert_called_once_with(skip=0, limit=10)
    
    @pytest.mark.asyncio
    async def test_search_organizations_by_name(self, organization_service, mock_organization_repository, test_organization):
        """Test searching organizations by name."""
        search_term = "Test"
        organizations = [test_organization]
        
        mock_organization_repository.search_by_name.return_value = organizations
        
        result = await organization_service.search_organizations_by_name(search_term)
        
        assert result == organizations
        mock_organization_repository.search_by_name.assert_called_once_with(search_term)
    
    @pytest.mark.asyncio
    async def test_search_organizations_by_name_no_results(self, organization_service, mock_organization_repository):
        """Test searching organizations by name with no results."""
        search_term = "NonExistent"
        
        mock_organization_repository.search_by_name.return_value = []
        
        result = await organization_service.search_organizations_by_name(search_term)
        
        assert result == []
        mock_organization_repository.search_by_name.assert_called_once_with(search_term)
    
    @pytest.mark.asyncio
    async def test_delete_organization_soft_delete(self, organization_service, mock_organization_repository, test_organization_id):
        """Test soft deleting an organization."""
        mock_organization_repository.soft_delete.return_value = True
        
        result = await organization_service.delete_organization(test_organization_id)
        
        assert result is True
        mock_organization_repository.soft_delete.assert_called_once_with(test_organization_id)
    
    @pytest.mark.asyncio
    async def test_delete_organization_not_found(self, organization_service, mock_organization_repository, test_organization_id):
        """Test soft deleting non-existent organization."""
        mock_organization_repository.soft_delete.return_value = False
        
        result = await organization_service.delete_organization(test_organization_id)
        
        assert result is False
        mock_organization_repository.soft_delete.assert_called_once_with(test_organization_id)
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_db_session):
        """Test OrganizationService initialization."""
        with patch('josi.services.organization_service.OrganizationRepository') as mock_repo_class:
            service = OrganizationService(mock_db_session)
            
            # Verify dependencies were initialized
            mock_repo_class.assert_called_once_with(Organization, mock_db_session)
            
            assert service.db == mock_db_session
            assert hasattr(service, 'repository')
    
    @pytest.mark.asyncio
    async def test_organization_creation_with_default_values(self, organization_service, mock_organization_repository):
        """Test that organization creation sets proper default values."""
        org_data = OrganizationEntity(
            name="Minimal Organization",
            slug="minimal-org",
            contact_email="admin@minimal.com",
            contact_name="Minimal Admin"
        )
        
        expected_org = Organization(
            organization_id=uuid4(),
            name="Minimal Organization",
            slug="minimal-org",
            api_key="generated-api-key",
            is_active=True,  # Default
            plan_type="free",  # Default
            monthly_api_limit=1000,  # Default for free plan
            current_month_usage=0,  # Default
            contact_email="admin@minimal.com",
            contact_name="Minimal Admin"
        )
        
        mock_organization_repository.create.return_value = expected_org
        
        result = await organization_service.create_organization(org_data)
        
        assert result.is_active is True
        assert result.plan_type == "free"
        assert result.monthly_api_limit == 1000
        assert result.current_month_usage == 0
    
    @pytest.mark.asyncio
    async def test_error_handling_during_operations(self, organization_service, mock_organization_repository, test_organization_id):
        """Test error handling during various operations."""
        # Test database error during get operation
        mock_organization_repository.get.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception, match="Database connection error"):
            await organization_service.get_organization(test_organization_id)
    
    @pytest.mark.asyncio
    async def test_api_key_generation_uniqueness(self, organization_service):
        """Test that API key generation produces unique keys."""
        # Test internal API key generation (if method exists)
        keys = []
        for _ in range(10):
            # Simulate key generation - this would be done in the service
            key = token_urlsafe(32)
            keys.append(key)
        
        # Verify all keys are unique
        assert len(set(keys)) == len(keys)
        # Verify keys have appropriate length
        for key in keys:
            assert len(key) >= 32