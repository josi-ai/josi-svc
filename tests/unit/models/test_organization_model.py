"""
Unit tests for Organization model.
"""
import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from josi.models.organization_model import (
    Organization,
    OrganizationEntity,
    PlanType
)


class TestOrganizationModel:
    """Test Organization model validation and behavior."""
    
    def test_organization_creation_with_required_fields(self):
        """Test creating organization with required fields."""
        org = Organization(
            organization_id=uuid4(),
            name="Test Organization",
            slug="test-org",
            api_key="test-api-key-123",
            is_active=True,
            plan_type=PlanType.FREE,
            monthly_api_limit=1000,
            current_month_usage=0,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert org.name == "Test Organization"
        assert org.slug == "test-org"
        assert org.api_key == "test-api-key-123"
        assert org.is_active is True
        assert org.plan_type == PlanType.FREE
        assert org.monthly_api_limit == 1000
        assert org.current_month_usage == 0
    
    def test_organization_with_all_fields(self):
        """Test creating organization with all optional fields."""
        org_id = uuid4()
        settings = {"theme": "dark", "notifications": True}
        
        org = Organization(
            organization_id=org_id,
            name="Premium Organization",
            slug="premium-org",
            api_key="premium-api-key",
            is_active=True,
            settings=settings,
            plan_type=PlanType.PREMIUM,
            monthly_api_limit=10000,
            current_month_usage=500,
            contact_email="admin@example.com",
            contact_name="John Doe",
            contact_phone="+1234567890",
            address_line1="123 Main St",
            address_line2="Suite 100",
            city="New York",
            state="NY",
            country="USA",
            postal_code="10001",
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert org.organization_id == org_id
        assert org.contact_email == "admin@example.com"
        assert org.settings == settings
        assert org.plan_type == PlanType.PREMIUM
        assert org.postal_code == "10001"
    
    def test_plan_type_enum_values(self):
        """Test all plan type enum values."""
        assert PlanType.FREE == "free"
        assert PlanType.BASIC == "basic"
        assert PlanType.PREMIUM == "premium"
        assert PlanType.ENTERPRISE == "enterprise"
    
    def test_organization_slug_uniqueness(self):
        """Test that slug should be unique (validated at DB level)."""
        org = Organization(
            organization_id=uuid4(),
            name="Test Org",
            slug="unique-slug",
            api_key="api-key-1",
            is_active=True,
            plan_type=PlanType.FREE,
            monthly_api_limit=1000,
            current_month_usage=0,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create another org with same slug (would fail at DB level)
        org2 = Organization(
            organization_id=uuid4(),
            name="Another Org",
            slug="unique-slug",  # Same slug
            api_key="api-key-2",
            is_active=True,
            plan_type=PlanType.FREE,
            monthly_api_limit=1000,
            current_month_usage=0,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Both objects can be created in memory
        assert org.slug == org2.slug
        # But would fail on database insert due to unique constraint
    
    def test_api_key_generation(self):
        """Test that API keys should be secure and unique."""
        org = Organization(
            organization_id=uuid4(),
            name="Secure Org",
            slug="secure-org",
            api_key="sk_live_" + "x" * 32,  # Simulated secure key
            is_active=True,
            plan_type=PlanType.PREMIUM,
            monthly_api_limit=10000,
            current_month_usage=0,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert org.api_key.startswith("sk_live_")
        assert len(org.api_key) > 20  # Should be sufficiently long
    
    def test_usage_tracking(self):
        """Test API usage tracking fields."""
        org = Organization(
            organization_id=uuid4(),
            name="Limited Org",
            slug="limited-org",
            api_key="test-key",
            is_active=True,
            plan_type=PlanType.BASIC,
            monthly_api_limit=5000,
            current_month_usage=4999,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert org.current_month_usage < org.monthly_api_limit
        
        # Simulate reaching limit
        org.current_month_usage = 5000
        assert org.current_month_usage == org.monthly_api_limit
    
    def test_organization_deactivation(self):
        """Test organization active status."""
        org = Organization(
            organization_id=uuid4(),
            name="Inactive Org",
            slug="inactive-org",
            api_key="test-key",
            is_active=False,  # Deactivated
            plan_type=PlanType.FREE,
            monthly_api_limit=1000,
            current_month_usage=0,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert org.is_active is False
    
    def test_organization_settings_json(self):
        """Test organization settings as JSON field."""
        complex_settings = {
            "features": {
                "advanced_charts": True,
                "api_webhooks": False,
                "custom_branding": True
            },
            "limits": {
                "max_persons": 1000,
                "max_charts_per_person": 10
            },
            "preferences": {
                "default_house_system": "placidus",
                "default_ayanamsa": "lahiri"
            }
        }
        
        org = Organization(
            organization_id=uuid4(),
            name="Custom Org",
            slug="custom-org",
            api_key="test-key",
            is_active=True,
            settings=complex_settings,
            plan_type=PlanType.ENTERPRISE,
            monthly_api_limit=100000,
            current_month_usage=0,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert org.settings["features"]["advanced_charts"] is True
        assert org.settings["limits"]["max_persons"] == 1000
        assert org.settings["preferences"]["default_ayanamsa"] == "lahiri"
    
    def test_organization_contact_validation(self):
        """Test contact information fields."""
        org = Organization(
            organization_id=uuid4(),
            name="Contact Org",
            slug="contact-org",
            api_key="test-key",
            is_active=True,
            plan_type=PlanType.PREMIUM,
            monthly_api_limit=10000,
            current_month_usage=0,
            contact_email="invalid-email",  # Should ideally be validated
            contact_phone="123",  # Short phone number
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Model allows any string for email and phone
        # Validation would typically happen at service layer
        assert org.contact_email == "invalid-email"
        assert org.contact_phone == "123"
    
    def test_organization_soft_delete(self):
        """Test soft delete functionality."""
        org = Organization(
            organization_id=uuid4(),
            name="Deleted Org",
            slug="deleted-org",
            api_key="test-key",
            is_active=True,
            plan_type=PlanType.FREE,
            monthly_api_limit=1000,
            current_month_usage=0,
            is_deleted=True,
            deleted_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert org.is_deleted is True
        assert org.deleted_at is not None
    
    def test_organization_entity_fields(self):
        """Test OrganizationEntity base fields."""
        entity = OrganizationEntity(
            name="Entity Test",
            slug="entity-test",
            api_key="test-key",
            is_active=True,
            plan_type=PlanType.BASIC,
            monthly_api_limit=5000,
            current_month_usage=100
        )
        
        assert entity.name == "Entity Test"
        assert entity.slug == "entity-test"
        assert entity.settings is None  # Optional field