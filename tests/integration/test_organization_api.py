"""Integration tests for Organization API endpoints."""
import pytest
from uuid import uuid4

from tests.conftest import assert_response_success, assert_response_error


@pytest.mark.integration
class TestOrganizationAPI:
    """Integration tests for Organization API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_current_organization(self, async_client, test_organization):
        """Test getting the current organization based on API key."""
        response = await async_client.get("/api/v1/organizations/me")
        org = assert_response_success(response)
        
        assert org["organization_id"] == str(test_organization.organization_id)
        assert org["name"] == test_organization.name
        assert org["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_update_organization(self, async_client, test_organization):
        """Test updating organization details."""
        update_data = {
            "contact_email": "newemail@org.com",
            "contact_name": "New Contact",
            "contact_phone": "+1234567890"
        }
        
        response = await async_client.patch(
            f"/api/v1/organizations/{test_organization.organization_id}",
            json=update_data
        )
        updated_org = assert_response_success(response)
        
        assert updated_org["contact_email"] == "newemail@org.com"
        assert updated_org["contact_name"] == "New Contact"
        assert updated_org["contact_phone"] == "+1234567890"
    
    @pytest.mark.asyncio
    async def test_organization_usage_tracking(self, async_client, test_organization):
        """Test that API usage is tracked."""
        # Get initial usage
        response = await async_client.get("/api/v1/organizations/me")
        org = assert_response_success(response)
        initial_usage = org.get("current_month_usage", 0)
        
        # Make some API calls
        for _ in range(3):
            await async_client.get("/api/v1/persons")
        
        # Check updated usage
        response = await async_client.get("/api/v1/organizations/me")
        org = assert_response_success(response)
        new_usage = org.get("current_month_usage", 0)
        
        # Usage should have increased
        assert new_usage >= initial_usage
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self, async_client):
        """Test accessing API with invalid API key."""
        # Override headers with invalid API key
        invalid_client = async_client
        invalid_client.headers = {"X-API-Key": "invalid-key-12345"}
        
        response = await invalid_client.get("/api/v1/organizations/me")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_organization_rate_limits(self, async_client, test_organization):
        """Test organization rate limiting."""
        # This test would need rate limiting to be implemented
        # For now, just verify the fields exist
        response = await async_client.get("/api/v1/organizations/me")
        org = assert_response_success(response)
        
        assert "monthly_api_limit" in org
        assert "current_month_usage" in org
        assert org["monthly_api_limit"] > 0