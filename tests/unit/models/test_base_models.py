"""Unit tests for base models."""
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field

from josi.models.base import SQLBaseModel, TenantBaseModel


# Define test models at module level to avoid redefinition
class MockModelForBase(SQLBaseModel, table=True):
    __tablename__ = "test_model_base"
    test_id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str


class MockModelForTenant(TenantBaseModel, table=True):
    __tablename__ = "test_model_tenant"
    test_id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str


class TestSQLBaseModel:
    """Test SQLBaseModel functionality."""
    
    def test_sqlbase_model_fields(self):
        """Test that SQLBaseModel has required fields."""
        model = SQLBaseModel()
        
        # Check timestamp fields exist
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        assert hasattr(model, 'is_deleted')
        assert hasattr(model, 'deleted_at')
        
        # Check default values
        assert model.is_deleted is False
        assert model.deleted_at is None
    
    def test_sqlbase_model_creation(self):
        """Test SQLBaseModel instance creation."""
        model = MockModelForBase(name="Test")
        assert model.name == "Test"
        assert model.is_deleted is False
        assert model.deleted_at is None
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')


class TestTenantBaseModel:
    """Test TenantBaseModel functionality."""
    
    def test_tenant_base_model_fields(self):
        """Test that TenantBaseModel has required fields."""
        org_id = uuid4()
        model = TenantBaseModel(organization_id=org_id)
        
        # Check all base fields exist
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        assert hasattr(model, 'is_deleted')
        assert hasattr(model, 'deleted_at')
        assert hasattr(model, 'organization_id')
        
        # Check default values
        assert model.is_deleted is False
        assert model.deleted_at is None
        assert model.organization_id == org_id
    
    def test_tenant_base_model_creation(self):
        """Test TenantBaseModel instance creation."""
        org_id = uuid4()
        model = MockModelForTenant(name="Test", organization_id=org_id)
        
        assert model.name == "Test"
        assert model.organization_id == org_id
        assert model.is_deleted is False
        assert model.deleted_at is None
    
    def test_tenant_base_model_inheritance(self):
        """Test that TenantBaseModel inherits from SQLBaseModel."""
        assert issubclass(TenantBaseModel, SQLBaseModel)