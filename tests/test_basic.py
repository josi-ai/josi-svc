"""Basic smoke test to verify the application can start."""
import pytest


def test_basic_import():
    """Test that we can import basic modules."""
    from josi.models.base import SQLBaseModel, TenantBaseModel
    from josi.models.person_model import Person
    from josi.models.organization_model import Organization
    
    assert SQLBaseModel is not None
    assert TenantBaseModel is not None
    assert Person is not None
    assert Organization is not None


def test_config_import():
    """Test that configuration can be imported."""
    from josi.core.config import settings
    
    assert settings is not None
    assert settings.app_name is not None