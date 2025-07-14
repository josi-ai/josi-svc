"""
Integration tests for complete API workflow.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime
import json
from uuid import uuid4

from josi.main import app
from josi.models.organization_model import Organization
from josi.core.database import get_session
from sqlmodel import Session, select


@pytest.mark.asyncio
class TestCompleteWorkflow:
    """Test complete user workflows through the API."""
    
    async def test_person_and_chart_creation_workflow(self, async_client: AsyncClient, test_organization: Organization):
        """Test creating a person and generating multiple charts."""
        # Step 1: Create a person
        person_data = {
            "name": "Workflow Test User",
            "email": "workflow@test.com",
            "date_of_birth": "1990-05-15",
            "time_of_birth": "14:30:00",
            "place_of_birth": "Los Angeles, CA, USA",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "timezone": "America/Los_Angeles"
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=person_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 201
        person_result = response.json()
        assert person_result["success"] is True
        person_id = person_result["data"]["person_id"]
        
        # Step 2: Create a Vedic chart
        vedic_chart_data = {
            "chart_type": "vedic",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri"
        }
        
        response = await async_client.post(
            f"/api/v1/persons/{person_id}/charts",
            json=vedic_chart_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 201
        vedic_result = response.json()
        assert vedic_result["success"] is True
        assert vedic_result["data"]["chart_type"] == "vedic"
        assert "planet_positions" in vedic_result["data"]["chart_data"]
        
        # Step 3: Create a Western chart
        western_chart_data = {
            "chart_type": "western",
            "house_system": "placidus"
        }
        
        response = await async_client.post(
            f"/api/v1/persons/{person_id}/charts",
            json=western_chart_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 201
        western_result = response.json()
        assert western_result["success"] is True
        assert western_result["data"]["chart_type"] == "western"
        
        # Step 4: Get all charts for the person
        response = await async_client.get(
            f"/api/v1/persons/{person_id}/charts",
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 200
        charts_result = response.json()
        assert charts_result["success"] is True
        assert len(charts_result["data"]) >= 2
        
        # Step 5: Get specific chart details
        vedic_chart_id = vedic_result["data"]["chart_id"]
        response = await async_client.get(
            f"/api/v1/charts/{vedic_chart_id}",
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 200
        chart_detail = response.json()
        assert chart_detail["success"] is True
        assert chart_detail["data"]["chart_id"] == vedic_chart_id
    
    async def test_multi_tenant_isolation(self, async_client: AsyncClient, test_organization: Organization):
        """Test that data is properly isolated between organizations."""
        # Create a second organization
        with next(get_session()) as session:
            org2 = Organization(
                name="Second Organization",
                slug=f"second-org-{uuid4().hex[:8]}",
                api_key=f"test-key-{uuid4().hex}",
                is_active=True,
                plan_type="free",
                monthly_api_limit=1000,
                current_month_usage=0,
                is_deleted=False
            )
            session.add(org2)
            session.commit()
            session.refresh(org2)
        
        # Create person in first organization
        person_data = {
            "name": "Org1 User",
            "email": "org1@test.com",
            "date_of_birth": "1985-03-20",
            "time_of_birth": "09:15:00",
            "place_of_birth": "New York, NY, USA",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York"
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=person_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 201
        org1_person = response.json()["data"]
        
        # Try to access org1's person with org2's API key
        response = await async_client.get(
            f"/api/v1/persons/{org1_person['person_id']}",
            headers={"X-API-Key": org2.api_key}
        )
        assert response.status_code == 404
        
        # Create person in second organization
        person_data["email"] = "org2@test.com"
        response = await async_client.post(
            "/api/v1/persons",
            json=person_data,
            headers={"X-API-Key": org2.api_key}
        )
        assert response.status_code == 201
        
        # List persons for each organization
        response1 = await async_client.get(
            "/api/v1/persons",
            headers={"X-API-Key": test_organization.api_key}
        )
        response2 = await async_client.get(
            "/api/v1/persons",
            headers={"X-API-Key": org2.api_key}
        )
        
        # Each org should only see their own data
        org1_persons = response1.json()["data"]
        org2_persons = response2.json()["data"]
        
        org1_ids = {p["person_id"] for p in org1_persons}
        org2_ids = {p["person_id"] for p in org2_persons}
        
        # No overlap between organizations
        assert len(org1_ids.intersection(org2_ids)) == 0
    
    async def test_error_handling_workflow(self, async_client: AsyncClient, test_organization: Organization):
        """Test API error handling for various scenarios."""
        # Test 1: Invalid birth date (future date)
        invalid_person = {
            "name": "Future Person",
            "date_of_birth": "2030-01-01",
            "time_of_birth": "12:00:00",
            "place_of_birth": "London, UK",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "Europe/London"
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=invalid_person,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 422
        
        # Test 2: Invalid coordinates
        invalid_coords = {
            "name": "Invalid Coords",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00:00",
            "place_of_birth": "Invalid Place",
            "latitude": 200.0,  # Invalid latitude
            "longitude": -180.0,
            "timezone": "UTC"
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=invalid_coords,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 422
        
        # Test 3: Missing required fields
        incomplete_person = {
            "name": "Incomplete Person"
            # Missing required fields
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=incomplete_person,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 422
        
        # Test 4: Invalid API key
        response = await async_client.get(
            "/api/v1/persons",
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401
        
        # Test 5: Non-existent resource
        fake_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/persons/{fake_id}",
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 404
    
    async def test_pagination_workflow(self, async_client: AsyncClient, test_organization: Organization):
        """Test pagination for listing endpoints."""
        # Create multiple persons
        for i in range(15):
            person_data = {
                "name": f"Test User {i}",
                "email": f"user{i}@test.com",
                "date_of_birth": "1990-01-01",
                "time_of_birth": "12:00:00",
                "place_of_birth": "Test City",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC"
            }
            
            response = await async_client.post(
                "/api/v1/persons",
                json=person_data,
                headers={"X-API-Key": test_organization.api_key}
            )
            assert response.status_code == 201
        
        # Test pagination
        response = await async_client.get(
            "/api/v1/persons?skip=0&limit=5",
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) <= 5
        
        # Get next page
        response = await async_client.get(
            "/api/v1/persons?skip=5&limit=5",
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) <= 5
    
    async def test_update_workflow(self, async_client: AsyncClient, test_organization: Organization):
        """Test updating resources."""
        # Create a person
        person_data = {
            "name": "Original Name",
            "email": "original@test.com",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00:00",
            "place_of_birth": "Original City",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC"
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=person_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 201
        person = response.json()["data"]
        person_id = person["person_id"]
        
        # Update the person
        update_data = {
            "name": "Updated Name",
            "email": "updated@test.com",
            "notes": "Updated via API test"
        }
        
        response = await async_client.patch(
            f"/api/v1/persons/{person_id}",
            json=update_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 200
        updated = response.json()["data"]
        assert updated["name"] == "Updated Name"
        assert updated["email"] == "updated@test.com"
        assert updated["notes"] == "Updated via API test"
        
        # Verify the update persisted
        response = await async_client.get(
            f"/api/v1/persons/{person_id}",
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 200
        fetched = response.json()["data"]
        assert fetched["name"] == "Updated Name"
    
    async def test_delete_workflow(self, async_client: AsyncClient, test_organization: Organization):
        """Test soft delete functionality."""
        # Create a person
        person_data = {
            "name": "To Be Deleted",
            "email": "delete@test.com",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "12:00:00",
            "place_of_birth": "Delete City",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC"
        }
        
        response = await async_client.post(
            "/api/v1/persons",
            json=person_data,
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 201
        person_id = response.json()["data"]["person_id"]
        
        # Delete the person
        response = await async_client.delete(
            f"/api/v1/persons/{person_id}",
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 204
        
        # Try to get the deleted person
        response = await async_client.get(
            f"/api/v1/persons/{person_id}",
            headers={"X-API-Key": test_organization.api_key}
        )
        assert response.status_code == 404
        
        # Verify it doesn't appear in list
        response = await async_client.get(
            "/api/v1/persons",
            headers={"X-API-Key": test_organization.api_key}
        )
        persons = response.json()["data"]
        person_ids = [p["person_id"] for p in persons]
        assert person_id not in person_ids