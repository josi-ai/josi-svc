"""Unit tests for base repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.sql import select
from sqlmodel import SQLModel, Field

from josi.repositories.base_repository import BaseRepository
from josi.models.base import SQLBaseModel, TenantBaseModel


# Test models
class MockTestModel(SQLBaseModel, table=True):
    __tablename__ = "test_model"
    test_id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str
    value: int = 0


class MockTenantTestModel(TenantBaseModel, table=True):
    __tablename__ = "tenant_test_model"
    test_id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str
    value: int = 0


class TestBaseRepository:
    """Test BaseRepository functionality."""
    
    @pytest.fixture
    def base_repository(self, mock_db_session):
        """Create a BaseRepository instance."""
        return BaseRepository(MockTestModel, mock_db_session)
    
    @pytest.mark.asyncio
    async def test_create(self, base_repository, mock_db_session):
        """Test create method."""
        test_data = {"name": "Test Item", "value": 42}
        created_item = TestModel(**test_data, test_id=uuid4())
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        mock_db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'created_at', datetime.now()))
        
        result = await base_repository.create(test_data)
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Verify the created object
        assert result.name == "Test Item"
        assert result.value == 42
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, base_repository, mock_db_session):
        """Test get_by_id method."""
        test_id = uuid4()
        test_item = TestModel(test_id=test_id, name="Test Item", value=42)
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_item
        
        result = await base_repository.get_by_id(test_id)
        
        assert result == test_item
        assert result.test_id == test_id
        assert result.name == "Test Item"
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, base_repository, mock_db_session):
        """Test get_by_id when item not found."""
        test_id = uuid4()
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = await base_repository.get_by_id(test_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_id_soft_deleted(self, base_repository, mock_db_session):
        """Test get_by_id excludes soft deleted items."""
        test_id = uuid4()
        deleted_item = TestModel(
            test_id=test_id,
            name="Deleted Item",
            value=42,
            is_deleted=True,
            deleted_at=datetime.now()
        )
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = await base_repository.get_by_id(test_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update(self, base_repository, mock_db_session):
        """Test update method."""
        test_id = uuid4()
        existing_item = TestModel(test_id=test_id, name="Old Name", value=42)
        update_data = {"name": "New Name", "value": 100}
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = existing_item
        mock_db_session.refresh = AsyncMock()
        
        result = await base_repository.update(test_id, update_data)
        
        assert result.name == "New Name"
        assert result.value == 100
        mock_db_session.add.assert_called_once_with(existing_item)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(existing_item)
    
    @pytest.mark.asyncio
    async def test_delete_soft(self, base_repository, mock_db_session):
        """Test soft delete method."""
        test_id = uuid4()
        existing_item = TestModel(test_id=test_id, name="Test Item", value=42)
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = existing_item
        mock_db_session.refresh = AsyncMock()
        
        # Mock datetime.now() for consistent testing
        with patch('josi.repositories.base.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
            result = await base_repository.delete(test_id, soft=True)
        
        assert result is True
        assert existing_item.is_deleted is True
        assert existing_item.deleted_at == datetime(2024, 1, 1, 12, 0, 0)
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_hard(self, base_repository, mock_db_session):
        """Test hard delete method."""
        test_id = uuid4()
        existing_item = TestModel(test_id=test_id, name="Test Item", value=42)
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = existing_item
        
        result = await base_repository.delete(test_id, soft=False)
        
        assert result is True
        mock_db_session.delete.assert_called_once_with(existing_item)
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_with_filters(self, base_repository, mock_db_session):
        """Test list method with filters."""
        items = [
            TestModel(test_id=uuid4(), name="Item 1", value=10),
            TestModel(test_id=uuid4(), name="Item 2", value=20),
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = items
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.list(filters={"value": 10})
        
        assert len(result) == 2
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count(self, base_repository, mock_db_session):
        """Test count method."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_db_session.execute.return_value = mock_result
        
        result = await base_repository.count(filters={"value": 10})
        
        assert result == 5
        mock_db_session.execute.assert_called_once()


class TestTenantRepository:
    """Test TenantRepository functionality."""
    
    @pytest.fixture
    def tenant_repository(self, mock_db_session, mock_redis):
        """Create a TenantRepository instance."""
        org_id = uuid4()
        return TenantRepository(TenantTestModel, mock_db_session, mock_redis, org_id)
    
    @pytest.mark.asyncio
    async def test_create_with_organization(self, tenant_repository, mock_db_session):
        """Test create method adds organization_id."""
        test_data = {"name": "Test Item", "value": 42}
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        mock_db_session.refresh = AsyncMock()
        
        result = await tenant_repository.create(test_data)
        
        # Verify organization_id is set
        assert result.organization_id == tenant_repository.organization_id
        assert result.name == "Test Item"
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_with_organization_filter(self, tenant_repository, mock_db_session):
        """Test get_by_id filters by organization."""
        test_id = uuid4()
        test_item = TenantTestModel(
            test_id=test_id,
            name="Test Item",
            value=42,
            organization_id=tenant_repository.organization_id
        )
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_item
        
        result = await tenant_repository.get_by_id(test_id)
        
        assert result == test_item
        # Verify the query includes organization filter
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_with_organization_filter(self, tenant_repository, mock_db_session):
        """Test list method filters by organization."""
        items = [
            TenantTestModel(
                test_id=uuid4(),
                name="Item 1",
                value=10,
                organization_id=tenant_repository.organization_id
            ),
            TenantTestModel(
                test_id=uuid4(),
                name="Item 2",
                value=20,
                organization_id=tenant_repository.organization_id
            ),
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = items
        mock_db_session.execute.return_value = mock_result
        
        result = await tenant_repository.list()
        
        assert len(result) == 2
        # All items should belong to the same organization
        for item in result:
            assert item.organization_id == tenant_repository.organization_id