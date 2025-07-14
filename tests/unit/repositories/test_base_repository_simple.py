"""Simple unit tests for Base Repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock
from datetime import datetime
from uuid import uuid4
import sys

# Mock SQLAlchemy modules
sys.modules['sqlalchemy'] = Mock()
sys.modules['sqlalchemy.ext.asyncio'] = Mock()
sys.modules['sqlmodel'] = Mock()

from josi.repositories.base_repository import BaseRepository
from josi.models.base import SQLBaseModel, TenantBaseModel


class TestModel(SQLBaseModel):
    """Test model for repository testing."""
    __tablename__ = "test_model"
    
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    deleted_at: datetime = None


class TestTenantModel(TenantBaseModel):
    """Test tenant model for repository testing."""
    __tablename__ = "test_tenant_model"
    
    id: str
    name: str
    organization_id: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    deleted_at: datetime = None


class TestBaseRepositorySimple:
    """Simple test coverage for BaseRepository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock()
        # Mock execute result
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock()
        mock_result.scalars = AsyncMock()
        mock_result.unique = MagicMock(return_value=mock_result)
        mock_result.all = AsyncMock(return_value=[])
        session.execute = AsyncMock(return_value=mock_result)
        return session
    
    @pytest.fixture
    def base_repository(self, mock_db_session):
        """Create BaseRepository instance."""
        return BaseRepository(TestModel, mock_db_session)
    
    @pytest.fixture
    def test_instance(self):
        """Create test model instance."""
        return TestModel(
            id=str(uuid4()),
            name="Test Item",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_deleted=False
        )
    
    @pytest.mark.asyncio
    async def test_create(self, base_repository, mock_db_session, test_instance):
        """Test creating a record."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_instance
        
        result = await base_repository.create(test_instance)
        
        assert result == test_instance
        mock_db_session.add.assert_called_once_with(test_instance)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(test_instance)
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, base_repository, mock_db_session, test_instance):
        """Test getting record by ID."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_instance
        
        result = await base_repository.get(test_instance.id)
        
        assert result == test_instance
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_not_found(self, base_repository, mock_db_session):
        """Test getting non-existent record."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = await base_repository.get(str(uuid4()))
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update(self, base_repository, mock_db_session, test_instance):
        """Test updating a record."""
        update_data = {"name": "Updated Name"}
        updated_instance = test_instance
        updated_instance.name = "Updated Name"
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = updated_instance
        
        result = await base_repository.update(test_instance.id, update_data)
        
        assert result.name == "Updated Name"
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_soft_delete(self, base_repository, mock_db_session, test_instance):
        """Test soft deleting a record."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_instance
        
        result = await base_repository.soft_delete(test_instance.id)
        
        assert result is True
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_hard_delete(self, base_repository, mock_db_session, test_instance):
        """Test hard deleting a record."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_instance
        
        result = await base_repository.hard_delete(test_instance.id)
        
        assert result is True
        mock_db_session.delete.assert_called_once_with(test_instance)
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list(self, base_repository, mock_db_session, test_instance):
        """Test listing records."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [test_instance]
        
        result = await base_repository.list(skip=0, limit=10)
        
        assert len(result) == 1
        assert result[0] == test_instance
    
    @pytest.mark.asyncio
    async def test_list_with_filters(self, base_repository, mock_db_session, test_instance):
        """Test listing records with filters."""
        filters = {"name": "Test Item"}
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [test_instance]
        
        result = await base_repository.list(skip=0, limit=10, filters=filters)
        
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_count(self, base_repository, mock_db_session):
        """Test counting records."""
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 5
        mock_db_session.execute.return_value = mock_count_result
        
        result = await base_repository.count()
        
        assert result == 5
    
    @pytest.mark.asyncio
    async def test_exists(self, base_repository, mock_db_session):
        """Test checking if record exists."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = True
        
        result = await base_repository.exists(str(uuid4()))
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_bulk_create(self, base_repository, mock_db_session):
        """Test bulk creating records."""
        instances = [
            TestModel(id=str(uuid4()), name=f"Item {i}", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            for i in range(3)
        ]
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = instances
        
        result = await base_repository.bulk_create(instances)
        
        assert len(result) == 3
        assert mock_db_session.add_all.called
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_restore(self, base_repository, mock_db_session, test_instance):
        """Test restoring soft deleted record."""
        test_instance.is_deleted = True
        test_instance.deleted_at = datetime.utcnow()
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_instance
        
        result = await base_repository.restore(test_instance.id)
        
        assert result is True
        mock_db_session.commit.assert_called_once()


class TestTenantRepositorySimple:
    """Simple test coverage for TenantRepository."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock()
        mock_result.scalars = AsyncMock()
        mock_result.unique = MagicMock(return_value=mock_result)
        mock_result.all = AsyncMock(return_value=[])
        session.execute = AsyncMock(return_value=mock_result)
        return session
    
    @pytest.fixture
    def tenant_repository(self, mock_db_session):
        """Create TenantRepository instance."""
        org_id = str(uuid4())
        return TenantRepository(TestTenantModel, mock_db_session, org_id)
    
    @pytest.fixture
    def test_tenant_instance(self):
        """Create test tenant model instance."""
        return TestTenantModel(
            id=str(uuid4()),
            name="Test Tenant Item",
            organization_id=str(uuid4()),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_deleted=False
        )
    
    @pytest.mark.asyncio
    async def test_tenant_create(self, tenant_repository, mock_db_session, test_tenant_instance):
        """Test creating a tenant record."""
        test_tenant_instance.organization_id = tenant_repository.organization_id
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_tenant_instance
        
        result = await tenant_repository.create(test_tenant_instance)
        
        assert result.organization_id == tenant_repository.organization_id
        mock_db_session.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_tenant_list_filtered_by_org(self, tenant_repository, mock_db_session, test_tenant_instance):
        """Test listing tenant records filtered by organization."""
        test_tenant_instance.organization_id = tenant_repository.organization_id
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [test_tenant_instance]
        
        result = await tenant_repository.list()
        
        assert len(result) == 1
        assert result[0].organization_id == tenant_repository.organization_id
    
    @pytest.mark.asyncio
    async def test_tenant_get_wrong_org(self, tenant_repository, mock_db_session):
        """Test getting record from different organization returns None."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = await tenant_repository.get(str(uuid4()))
        
        assert result is None