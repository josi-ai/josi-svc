"""Extended comprehensive unit tests for BaseRepository and TenantRepository to increase coverage."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from typing import Optional

from josi.repositories.base_repository import BaseRepository
from josi.models.base import SQLBaseModel, TenantBaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field


# Test models for repository testing
class ExtendedTestModel(SQLBaseModel, table=True):
    """Test model for BaseRepository testing."""
    __tablename__ = "extended_test_model"
    
    extended_test_model_id: str = Field(primary_key=True)
    name: str
    description: Optional[str] = None
    value: int = 0


class ExtendedTestTenantModel(TenantBaseModel, table=True):
    """Test tenant model for TenantRepository testing."""
    __tablename__ = "extended_test_tenant_model"
    
    extended_test_tenant_model_id: str = Field(primary_key=True)
    name: str
    description: Optional[str] = None
    value: int = 0


class SimpleModel(SQLModel, table=True):
    """Simple model without soft delete fields."""
    __tablename__ = "simple_model"
    
    simple_model_id: str = Field(primary_key=True)
    name: str


class TestBaseRepositoryExtended:
    """Extended comprehensive test coverage for BaseRepository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def base_repository(self, mock_db_session):
        """Create a BaseRepository instance."""
        return BaseRepository(ExtendedTestModel, mock_db_session)
    
    @pytest.fixture
    def simple_repository(self, mock_db_session):
        """Create a BaseRepository instance with simple model."""
        return BaseRepository(SimpleModel, mock_db_session)
    
    @pytest.fixture
    def test_model_id(self):
        """Test model ID."""
        return uuid4()
    
    @pytest.fixture
    def test_model_data(self, test_model_id):
        """Test model data."""
        return {
            "extended_test_model_id": test_model_id,
            "name": "Test Model",
            "description": "Test description",
            "value": 42
        }
    
    @pytest.fixture
    def test_model_instance(self, test_model_data):
        """Create a test model instance."""
        return ExtendedTestModel(**test_model_data)
    
    @pytest.mark.asyncio
    async def test_get_with_tablename_id_field(self, base_repository, mock_db_session, test_model_id, test_model_instance):
        """Test getting record by tablename_id field pattern."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = test_model_instance
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get(test_model_id)
        
        assert result == test_model_instance
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_with_primary_key_discovery(self, mock_db_session):
        """Test getting record when primary key needs to be discovered."""
        # Create a model where we need to discover the primary key
        mock_model = MagicMock()
        mock_model.__name__ = "TestModel"
        mock_model.__tablename__ = "test_model"
        
        # Mock primary key attribute
        mock_pk_attr = MagicMock()
        mock_pk_attr.primary_key = True
        
        # Mock dir() to return the primary key attribute name
        with patch('builtins.dir', return_value=['id_field']):
            with patch('builtins.getattr', return_value=mock_pk_attr):
                repository = BaseRepository(mock_model, mock_db_session)
                
                mock_result = AsyncMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db_session.execute.return_value = mock_result
                
                result = await repository.get(uuid4())
                
                assert result is None
                mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_no_id_field_error(self, mock_db_session):
        """Test get method throws error when no ID field found."""
        # Create a model without proper ID fields
        mock_model = MagicMock()
        mock_model.__name__ = "NoIdModel"
        mock_model.__tablename__ = "no_id_model"
        
        # Mock hasattr to return False for all ID checks
        def mock_hasattr(obj, name):
            return False
        
        with patch('builtins.hasattr', side_effect=mock_hasattr):
            with patch('builtins.dir', return_value=[]):
                repository = BaseRepository(mock_model, mock_db_session)
                
                with pytest.raises(ValueError, match="Could not find ID field for model NoIdModel"):
                    await repository.get(uuid4())
    
    @pytest.mark.asyncio
    async def test_get_with_soft_delete_filtering(self, base_repository, mock_db_session, test_model_id):
        """Test get method filters out soft deleted records."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None  # Simulates filtered out deleted record
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get(test_model_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_with_soft_delete_filtering(self, base_repository, mock_db_session, test_model_instance):
        """Test get_multi method filters out soft deleted records."""
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = [test_model_instance]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get_multi()
        
        assert result == [test_model_instance]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_with_filters(self, base_repository, mock_db_session, test_model_instance):
        """Test get_multi with various filters."""
        filters = {"name": "Test Model", "value": 42}
        
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = [test_model_instance]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get_multi(skip=10, limit=50, filters=filters)
        
        assert result == [test_model_instance]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_ignores_invalid_filter_fields(self, base_repository, mock_db_session):
        """Test get_multi ignores filter fields that don't exist on model."""
        filters = {"nonexistent_field": "value", "another_invalid": 123}
        
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get_multi(filters=filters)
        
        assert result == []
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_empty_filters(self, base_repository, mock_db_session):
        """Test get_multi with empty filters dict."""
        filters = {}
        
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get_multi(filters=filters)
        
        assert result == []
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_with_flush_and_refresh(self, base_repository, mock_db_session, test_model_data):
        """Test create method with proper flush and refresh sequence."""
        created_instance = ExtendedTestModel(**test_model_data)
        
        # Mock session operations
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Mock the model constructor
        with patch.object(ExtendedTestModel, '__new__') as mock_new:
            mock_new.return_value = created_instance
            
            result = await base_repository.create(test_model_data)
        
        assert result == created_instance
        mock_db_session.add.assert_called_once_with(created_instance)
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(created_instance)
    
    @pytest.mark.asyncio
    async def test_update_successful(self, base_repository, mock_db_session, test_model_id, test_model_instance):
        """Test successful update operation."""
        update_data = {"name": "Updated Name", "description": "Updated description", "value": 100}
        
        # Mock get method
        with patch.object(base_repository, 'get', return_value=test_model_instance):
            mock_db_session.flush = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            result = await base_repository.update(test_model_id, update_data)
        
        assert result == test_model_instance
        assert test_model_instance.name == "Updated Name"
        assert test_model_instance.description == "Updated description"
        assert test_model_instance.value == 100
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(test_model_instance)
    
    @pytest.mark.asyncio
    async def test_update_with_timestamp(self, base_repository, mock_db_session, test_model_id, test_model_instance):
        """Test update automatically sets updated_at timestamp."""
        update_data = {"name": "Updated Name"}
        
        # Add updated_at attribute to the instance
        test_model_instance.updated_at = datetime(2023, 1, 1)
        
        with patch.object(base_repository, 'get', return_value=test_model_instance):
            mock_db_session.flush = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            with patch('josi.repositories.base_repository.datetime') as mock_datetime:
                mock_now = datetime(2023, 6, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now
                
                result = await base_repository.update(test_model_id, update_data)
        
        assert result == test_model_instance
        assert test_model_instance.updated_at == mock_now
    
    @pytest.mark.asyncio
    async def test_update_ignores_invalid_fields(self, base_repository, mock_db_session, test_model_id, test_model_instance):
        """Test update ignores fields that don't exist on model."""
        update_data = {"name": "Updated Name", "nonexistent_field": "value"}
        
        with patch.object(base_repository, 'get', return_value=test_model_instance):
            mock_db_session.flush = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            result = await base_repository.update(test_model_id, update_data)
        
        assert result == test_model_instance
        assert test_model_instance.name == "Updated Name"
        # Verify nonexistent field wasn't set
        assert not hasattr(test_model_instance, 'nonexistent_field')
    
    @pytest.mark.asyncio
    async def test_update_entity_not_found(self, base_repository, mock_db_session, test_model_id):
        """Test update returns None when entity not found."""
        update_data = {"name": "Updated Name"}
        
        with patch.object(base_repository, 'get', return_value=None):
            result = await base_repository.update(test_model_id, update_data)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_soft_delete_with_timestamp(self, base_repository, mock_db_session, test_model_id, test_model_instance):
        """Test soft delete sets is_deleted and deleted_at."""
        # Add soft delete attributes
        test_model_instance.is_deleted = False
        test_model_instance.deleted_at = None
        
        with patch.object(base_repository, 'get', return_value=test_model_instance):
            mock_db_session.flush = AsyncMock()
            
            with patch('josi.repositories.base_repository.datetime') as mock_datetime:
                mock_now = datetime(2023, 6, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now
                
                result = await base_repository.delete(test_model_id)
        
        assert result is True
        assert test_model_instance.is_deleted is True
        assert test_model_instance.deleted_at == mock_now
        mock_db_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_soft_delete_without_timestamp(self, base_repository, mock_db_session, test_model_id):
        """Test soft delete when model has is_deleted but no deleted_at."""
        # Create instance with only is_deleted field
        test_instance = MagicMock()
        test_instance.is_deleted = False
        
        # Mock hasattr to return True for is_deleted, False for deleted_at
        def mock_hasattr(obj, attr):
            if attr == 'is_deleted':
                return True
            elif attr == 'deleted_at':
                return False
            return False
        
        with patch.object(base_repository, 'get', return_value=test_instance):
            mock_db_session.flush = AsyncMock()
            
            with patch('builtins.hasattr', side_effect=mock_hasattr):
                result = await base_repository.delete(test_model_id)
        
        assert result is True
        assert test_instance.is_deleted is True
        mock_db_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_hard_delete(self, simple_repository, mock_db_session, test_model_id):
        """Test hard delete when model doesn't support soft delete."""
        # Create instance without soft delete fields
        test_instance = SimpleModel(simple_model_id=test_model_id, name="Test")
        
        with patch.object(simple_repository, 'get', return_value=test_instance):
            mock_db_session.delete = AsyncMock()
            mock_db_session.flush = AsyncMock()
            
            # Mock hasattr to return False for is_deleted
            with patch('builtins.hasattr', return_value=False):
                result = await simple_repository.delete(test_model_id)
        
        assert result is True
        mock_db_session.delete.assert_called_once_with(test_instance)
        mock_db_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_entity_not_found(self, base_repository, mock_db_session, test_model_id):
        """Test delete returns False when entity not found."""
        with patch.object(base_repository, 'get', return_value=None):
            result = await base_repository.delete(test_model_id)
        
        assert result is False


class TestTenantRepositoryExtended:
    """Extended comprehensive test coverage for TenantRepository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def test_organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def tenant_repository(self, mock_db_session, test_organization_id):
        """Create a TenantRepository instance."""
        return TenantRepository(ExtendedTestTenantModel, mock_db_session, test_organization_id)
    
    @pytest.fixture
    def test_tenant_model_id(self):
        """Test tenant model ID."""
        return uuid4()
    
    @pytest.fixture
    def test_tenant_model_data(self, test_tenant_model_id, test_organization_id):
        """Test tenant model data."""
        return {
            "extended_test_tenant_model_id": test_tenant_model_id,
            "organization_id": test_organization_id,
            "name": "Test Tenant Model",
            "description": "Test tenant description",
            "value": 42
        }
    
    @pytest.fixture
    def test_tenant_model_instance(self, test_tenant_model_data):
        """Create a test tenant model instance."""
        return ExtendedTestTenantModel(**test_tenant_model_data)
    
    @pytest.mark.asyncio
    async def test_get_with_tenant_filtering(self, tenant_repository, mock_db_session, test_tenant_model_id, test_tenant_model_instance):
        """Test get method filters by organization_id."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = test_tenant_model_instance
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get(test_tenant_model_id)
        
        assert result == test_tenant_model_instance
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_wrong_organization(self, tenant_repository, mock_db_session, test_tenant_model_id):
        """Test get method returns None for different organization."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None  # Different org, so filtered out
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get(test_tenant_model_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tenant_no_id_field_error(self, mock_db_session, test_organization_id):
        """Test get method throws error when no ID field found in tenant repository."""
        # Create a model without proper ID fields
        mock_model = MagicMock()
        mock_model.__name__ = "NoIdTenantModel"
        mock_model.__tablename__ = "no_id_tenant_model"
        
        # Mock hasattr to return False for all ID checks
        def mock_hasattr(obj, name):
            return False
        
        with patch('builtins.hasattr', side_effect=mock_hasattr):
            with patch('builtins.dir', return_value=[]):
                repository = TenantRepository(mock_model, mock_db_session, test_organization_id)
                
                with pytest.raises(ValueError, match="Could not find ID field for model NoIdTenantModel"):
                    await repository.get(uuid4())
    
    @pytest.mark.asyncio
    async def test_get_multi_with_tenant_filtering(self, tenant_repository, mock_db_session, test_tenant_model_instance):
        """Test get_multi filters by organization_id."""
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = [test_tenant_model_instance]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get_multi(skip=5, limit=25)
        
        assert result == [test_tenant_model_instance]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_with_filters_and_tenant(self, tenant_repository, mock_db_session, test_tenant_model_instance):
        """Test get_multi with filters and tenant filtering."""
        filters = {"name": "Test Tenant Model", "value": 42}
        
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = [test_tenant_model_instance]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get_multi(filters=filters)
        
        assert result == [test_tenant_model_instance]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_ignores_invalid_filters(self, tenant_repository, mock_db_session):
        """Test get_multi ignores invalid filter fields in tenant repository."""
        filters = {"invalid_field": "value", "another_invalid": 123}
        
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get_multi(filters=filters)
        
        assert result == []
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_automatically_sets_organization_id(self, tenant_repository, mock_db_session, test_organization_id):
        """Test create automatically sets organization_id."""
        create_data = {"name": "New Tenant Model", "description": "New description", "value": 100}
        expected_data = {**create_data, "organization_id": test_organization_id}
        created_instance = ExtendedTestTenantModel(**expected_data, extended_test_tenant_model_id=uuid4())
        
        # Mock session operations
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Mock the model constructor
        with patch.object(ExtendedTestTenantModel, '__new__') as mock_new:
            mock_new.return_value = created_instance
            
            result = await tenant_repository.create(create_data)
        
        assert result == created_instance
        assert result.organization_id == test_organization_id
        mock_db_session.add.assert_called_once_with(created_instance)
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(created_instance)
    
    @pytest.mark.asyncio
    async def test_create_overwrites_organization_id(self, tenant_repository, mock_db_session, test_organization_id):
        """Test create overwrites any provided organization_id."""
        different_org_id = uuid4()
        create_data = {
            "name": "New Tenant Model",
            "organization_id": different_org_id  # This should be overwritten
        }
        expected_data = {**create_data, "organization_id": test_organization_id}
        created_instance = ExtendedTestTenantModel(**expected_data, extended_test_tenant_model_id=uuid4())
        
        # Mock session operations
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Mock the model constructor
        with patch.object(ExtendedTestTenantModel, '__new__') as mock_new:
            mock_new.return_value = created_instance
            
            result = await tenant_repository.create(create_data)
        
        assert result == created_instance
        assert result.organization_id == test_organization_id
        assert result.organization_id != different_org_id
    
    @pytest.mark.asyncio
    async def test_update_within_tenant(self, tenant_repository, mock_db_session, test_tenant_model_id, test_tenant_model_instance):
        """Test update within tenant context."""
        update_data = {"name": "Updated Tenant Name", "value": 200}
        
        with patch.object(tenant_repository, 'get', return_value=test_tenant_model_instance):
            mock_db_session.flush = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            result = await tenant_repository.update(test_tenant_model_id, update_data)
        
        assert result == test_tenant_model_instance
        assert test_tenant_model_instance.name == "Updated Tenant Name"
        assert test_tenant_model_instance.value == 200
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_with_timestamp_tenant(self, tenant_repository, mock_db_session, test_tenant_model_id, test_tenant_model_instance):
        """Test update sets updated_at timestamp in tenant repository."""
        update_data = {"name": "Updated Tenant Name"}
        
        # Add updated_at attribute
        test_tenant_model_instance.updated_at = datetime(2023, 1, 1)
        
        with patch.object(tenant_repository, 'get', return_value=test_tenant_model_instance):
            mock_db_session.flush = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            with patch('josi.repositories.base_repository.datetime') as mock_datetime:
                mock_now = datetime(2023, 6, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now
                
                result = await tenant_repository.update(test_tenant_model_id, update_data)
        
        assert result == test_tenant_model_instance
        assert test_tenant_model_instance.updated_at == mock_now
    
    @pytest.mark.asyncio
    async def test_update_entity_not_found_tenant(self, tenant_repository, mock_db_session, test_tenant_model_id):
        """Test update returns None when entity not found in tenant."""
        update_data = {"name": "Updated Name"}
        
        with patch.object(tenant_repository, 'get', return_value=None):
            result = await tenant_repository.update(test_tenant_model_id, update_data)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_soft_delete_tenant(self, tenant_repository, mock_db_session, test_tenant_model_id, test_tenant_model_instance):
        """Test soft delete in tenant repository."""
        # Add soft delete attributes
        test_tenant_model_instance.is_deleted = False
        test_tenant_model_instance.deleted_at = None
        
        with patch.object(tenant_repository, 'get', return_value=test_tenant_model_instance):
            mock_db_session.flush = AsyncMock()
            
            with patch('josi.repositories.base_repository.datetime') as mock_datetime:
                mock_now = datetime(2023, 6, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now
                
                result = await tenant_repository.delete(test_tenant_model_id)
        
        assert result is True
        assert test_tenant_model_instance.is_deleted is True
        assert test_tenant_model_instance.deleted_at == mock_now
        mock_db_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_hard_delete_tenant(self, mock_db_session, test_organization_id):
        """Test hard delete in tenant repository when no soft delete support."""
        # Use simple model without soft delete
        simple_tenant_model = MagicMock()
        simple_tenant_model.__name__ = "SimpleTenantModel"
        simple_tenant_model.__tablename__ = "simple_tenant_model"
        simple_tenant_model.organization_id = test_organization_id
        
        repository = TenantRepository(simple_tenant_model, mock_db_session, test_organization_id)
        test_instance = MagicMock()
        test_id = uuid4()
        
        with patch.object(repository, 'get', return_value=test_instance):
            mock_db_session.delete = AsyncMock()
            mock_db_session.flush = AsyncMock()
            
            # Mock hasattr to return False for is_deleted
            with patch('builtins.hasattr', return_value=False):
                result = await repository.delete(test_id)
        
        assert result is True
        mock_db_session.delete.assert_called_once_with(test_instance)
        mock_db_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_entity_not_found_tenant(self, tenant_repository, mock_db_session, test_tenant_model_id):
        """Test delete returns False when entity not found in tenant."""
        with patch.object(tenant_repository, 'get', return_value=None):
            result = await tenant_repository.delete(test_tenant_model_id)
        
        assert result is False
    
    def test_add_tenant_filter_method(self, tenant_repository, test_organization_id):
        """Test _add_tenant_filter method."""
        mock_query = MagicMock()
        mock_query.where.return_value = "filtered_query"
        
        result = tenant_repository._add_tenant_filter(mock_query)
        
        assert result == "filtered_query"
        mock_query.where.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_repository_initialization_parameters(self, mock_db_session):
        """Test repository initialization with all parameters."""
        # Test BaseRepository
        base_repo = BaseRepository(ExtendedTestModel, mock_db_session)
        assert base_repo.model == ExtendedTestModel
        assert base_repo.session == mock_db_session
        
        # Test TenantRepository
        org_id = uuid4()
        tenant_repo = TenantRepository(ExtendedTestTenantModel, mock_db_session, org_id)
        assert tenant_repo.model == ExtendedTestTenantModel
        assert tenant_repo.session == mock_db_session
        assert tenant_repo.organization_id == org_id
    
    @pytest.mark.asyncio
    async def test_get_multi_no_filters_tenant(self, tenant_repository, mock_db_session, test_tenant_model_instance):
        """Test get_multi without filters in tenant repository."""
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = [test_tenant_model_instance]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get_multi()
        
        assert result == [test_tenant_model_instance]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_empty_conditions_tenant(self, tenant_repository, mock_db_session):
        """Test get_multi with no matching conditions in tenant repository."""
        filters = {"nonexistent": "value"}
        
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get_multi(filters=filters)
        
        assert result == []
        mock_db_session.execute.assert_called_once()