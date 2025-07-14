"""Fixed comprehensive unit tests for BaseRepository and TenantRepository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from uuid import uuid4
from datetime import datetime
from typing import Optional

from josi.repositories.base_repository import BaseRepository
from josi.models.base import SQLBaseModel, TenantBaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field


# Test models that match the actual implementation
class TestModel(SQLBaseModel, table=True):
    """Test model for BaseRepository testing."""
    __tablename__ = "test_model_fixed"
    
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    value: int = 0


class TestTenantModel(TenantBaseModel, table=True):
    """Test tenant model for TenantRepository testing."""
    __tablename__ = "test_tenant_model_fixed"
    
    test_tenant_model_id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    value: int = 0


class TestBaseRepositoryFixed:
    """Fixed comprehensive test coverage for BaseRepository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def base_repository(self, mock_db_session):
        """Create a BaseRepository instance."""
        return BaseRepository(TestModel, mock_db_session)
    
    @pytest.fixture
    def test_model_id(self):
        """Test model ID."""
        return str(uuid4())
    
    @pytest.fixture
    def test_model_data(self, test_model_id):
        """Test model data."""
        return {
            "id": test_model_id,
            "name": "Test Model",
            "description": "Test description",
            "value": 42
        }
    
    @pytest.fixture
    def test_model_instance(self, test_model_data):
        """Create a test model instance."""
        instance = TestModel(**test_model_data)
        instance.is_deleted = False
        instance.created_at = datetime.now()
        instance.updated_at = datetime.now()
        return instance
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self, base_repository, mock_db_session, test_model_id, test_model_instance):
        """Test getting record by ID with 'id' field."""
        # Mock the query execution
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = test_model_instance
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get(test_model_id)
        
        assert result == test_model_instance
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, base_repository, mock_db_session, test_model_id):
        """Test getting non-existent record."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get(test_model_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_success(self, base_repository, mock_db_session, test_model_instance):
        """Test getting multiple records."""
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [test_model_instance]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get_multi(skip=0, limit=10)
        
        assert result == [test_model_instance]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_with_filters(self, base_repository, mock_db_session, test_model_instance):
        """Test getting multiple records with filters."""
        filters = {"name": "Test Model", "value": 42}
        
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [test_model_instance]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.get_multi(skip=0, limit=10, filters=filters)
        
        assert result == [test_model_instance]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_success(self, base_repository, mock_db_session, test_model_data):
        """Test creating a new record."""
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        result = await base_repository.create(test_model_data)
        
        # Verify the instance was created and added
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Check the created instance
        created_instance = mock_db_session.add.call_args[0][0]
        assert created_instance.name == "Test Model"
        assert created_instance.value == 42
    
    @pytest.mark.asyncio
    async def test_update_success(self, base_repository, mock_db_session, test_model_id, test_model_instance):
        """Test updating a record."""
        update_data = {"name": "Updated Name", "value": 100}
        
        # Mock get method to return the instance
        with patch.object(base_repository, 'get', return_value=test_model_instance) as mock_get:
            mock_db_session.flush = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            result = await base_repository.update(test_model_id, update_data)
            
            # Verify get was called
            mock_get.assert_called_once_with(test_model_id)
            
            # Verify fields were updated
            assert result.name == "Updated Name"
            assert result.value == 100
            
            # Verify database operations
            mock_db_session.flush.assert_called_once()
            mock_db_session.refresh.assert_called_once_with(result)
    
    @pytest.mark.asyncio
    async def test_update_not_found(self, base_repository, test_model_id):
        """Test updating non-existent record."""
        update_data = {"name": "Updated Name"}
        
        with patch.object(base_repository, 'get', return_value=None):
            result = await base_repository.update(test_model_id, update_data)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_soft_delete(self, base_repository, mock_db_session, test_model_id, test_model_instance):
        """Test soft delete when model supports it."""
        test_model_instance.is_deleted = False
        test_model_instance.deleted_at = None
        
        with patch.object(base_repository, 'get', return_value=test_model_instance):
            mock_db_session.flush = AsyncMock()
            
            result = await base_repository.delete(test_model_id)
            
            assert result is True
            assert test_model_instance.is_deleted is True
            assert test_model_instance.deleted_at is not None
            mock_db_session.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_not_found(self, base_repository, test_model_id):
        """Test deleting non-existent record."""
        with patch.object(base_repository, 'get', return_value=None):
            result = await base_repository.delete(test_model_id)
            
            assert result is False


class TestTenantRepositoryFixed:
    """Fixed comprehensive test coverage for TenantRepository."""
    
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
        return TenantRepository(TestTenantModel, mock_db_session, test_organization_id)
    
    @pytest.fixture
    def test_tenant_model_id(self):
        """Test tenant model ID."""
        return str(uuid4())
    
    @pytest.fixture
    def test_tenant_model_data(self, test_tenant_model_id, test_organization_id):
        """Test tenant model data."""
        return {
            "test_tenant_model_id": test_tenant_model_id,
            "organization_id": test_organization_id,
            "name": "Test Tenant Model",
            "description": "Test tenant description",
            "value": 42
        }
    
    @pytest.fixture
    def test_tenant_model_instance(self, test_tenant_model_data):
        """Create a test tenant model instance."""
        instance = TestTenantModel(**test_tenant_model_data)
        instance.is_deleted = False
        instance.created_at = datetime.now()
        instance.updated_at = datetime.now()
        return instance
    
    @pytest.mark.asyncio
    async def test_get_within_tenant(self, tenant_repository, mock_db_session, test_tenant_model_id, test_tenant_model_instance):
        """Test getting record within tenant."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = test_tenant_model_instance
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get(test_tenant_model_id)
        
        assert result == test_tenant_model_instance
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_multi_within_tenant(self, tenant_repository, mock_db_session, test_tenant_model_instance):
        """Test getting multiple records within tenant."""
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [test_tenant_model_instance]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.get_multi(skip=0, limit=10)
        
        assert result == [test_tenant_model_instance]
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_within_tenant(self, tenant_repository, mock_db_session, test_organization_id):
        """Test creating record within tenant."""
        create_data = {"name": "New Tenant Model", "description": "New description"}
        
        mock_db_session.add = MagicMock()
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        result = await tenant_repository.create(create_data)
        
        # Verify organization_id was added
        created_instance = mock_db_session.add.call_args[0][0]
        assert created_instance.organization_id == test_organization_id
        assert created_instance.name == "New Tenant Model"
        
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_within_tenant(self, tenant_repository, mock_db_session, test_tenant_model_id, test_tenant_model_instance):
        """Test updating record within tenant."""
        update_data = {"name": "Updated Tenant Name", "value": 200}
        
        with patch.object(tenant_repository, 'get', return_value=test_tenant_model_instance):
            mock_db_session.flush = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            result = await tenant_repository.update(test_tenant_model_id, update_data)
            
            assert result.name == "Updated Tenant Name"
            assert result.value == 200
            mock_db_session.flush.assert_called_once()
            mock_db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_within_tenant(self, tenant_repository, mock_db_session, test_tenant_model_id, test_tenant_model_instance):
        """Test deleting record within tenant."""
        test_tenant_model_instance.is_deleted = False
        test_tenant_model_instance.deleted_at = None
        
        with patch.object(tenant_repository, 'get', return_value=test_tenant_model_instance):
            mock_db_session.flush = AsyncMock()
            
            result = await tenant_repository.delete(test_tenant_model_id)
            
            assert result is True
            assert test_tenant_model_instance.is_deleted is True
            assert test_tenant_model_instance.deleted_at is not None
            mock_db_session.flush.assert_called_once()
    
    def test_add_tenant_filter(self, tenant_repository):
        """Test _add_tenant_filter method."""
        mock_query = MagicMock()
        mock_query.where.return_value = "filtered_query"
        
        result = tenant_repository._add_tenant_filter(mock_query)
        
        assert result == "filtered_query"
        mock_query.where.assert_called_once()