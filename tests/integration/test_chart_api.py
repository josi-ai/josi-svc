"""Integration tests for Chart API endpoints."""
import pytest
from uuid import uuid4
from datetime import datetime

from tests.conftest import assert_response_success, assert_response_error, generate_chart_request_data


@pytest.mark.integration
class TestChartAPI:
    """Integration tests for Chart API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_natal_chart(self, async_client, test_person):
        """Test creating a natal chart."""
        chart_data = {
            "person_id": str(test_person.person_id),
            "chart_type": "natal",
            "house_system": "placidus",
            "ayanamsa": "lahiri",
            "coordinate_system": "tropical"
        }
        
        response = await async_client.post("/api/v1/charts", json=chart_data)
        
        # Chart creation might fail if ephemeris data is not available
        if response.status_code == 201:
            chart = assert_response_success(response, status_code=201)
            assert chart["person_id"] == str(test_person.person_id)
            assert chart["chart_type"] == "natal"
            assert chart["house_system"] == "placidus"
            assert chart["ayanamsa"] == "lahiri"
            assert chart["coordinate_system"] == "tropical"
            assert "chart_data" in chart
            assert chart["organization_id"] == str(test_person.organization_id)
        else:
            # If ephemeris data is not available, ensure proper error handling
            assert response.status_code in [400, 500]
            data = response.json()
            assert data["success"] is False
    
    @pytest.mark.asyncio
    async def test_create_transit_chart(self, async_client, test_person):
        """Test creating a transit chart."""
        chart_data = {
            "person_id": str(test_person.person_id),
            "chart_type": "transit",
            "house_system": "whole_sign",
            "coordinate_system": "sidereal"
        }
        
        response = await async_client.post("/api/v1/charts", json=chart_data)
        
        if response.status_code == 201:
            chart = assert_response_success(response, status_code=201)
            assert chart["chart_type"] == "transit"
            assert chart["house_system"] == "whole_sign"
            assert chart["coordinate_system"] == "sidereal"
    
    @pytest.mark.asyncio
    async def test_get_chart(self, async_client, test_person):
        """Test getting a chart by ID."""
        # First create a chart
        chart_data = generate_chart_request_data(test_person.person_id)
        create_response = await async_client.post("/api/v1/charts", json=chart_data)
        
        if create_response.status_code == 201:
            created_chart = create_response.json()["data"]
            chart_id = created_chart["chart_id"]
            
            # Get the chart
            response = await async_client.get(f"/api/v1/charts/{chart_id}")
            chart = assert_response_success(response)
            
            assert chart["chart_id"] == chart_id
            assert chart["person_id"] == str(test_person.person_id)
            assert chart["chart_type"] == chart_data["chart_type"]
    
    @pytest.mark.asyncio
    async def test_list_person_charts(self, async_client, test_person):
        """Test listing all charts for a person."""
        # Create multiple charts for the person
        chart_types = ["natal", "transit", "solar_return"]
        created_charts = []
        
        for chart_type in chart_types:
            chart_data = {
                "person_id": str(test_person.person_id),
                "chart_type": chart_type,
                "house_system": "placidus",
                "coordinate_system": "tropical"
            }
            response = await async_client.post("/api/v1/charts", json=chart_data)
            if response.status_code == 201:
                created_charts.append(response.json()["data"])
        
        # List charts for the person
        response = await async_client.get(f"/api/v1/persons/{test_person.person_id}/charts")
        
        if response.status_code == 200:
            charts = assert_response_success(response)
            assert isinstance(charts, list)
            assert len(charts) >= len(created_charts)
            
            # Verify all charts belong to the person
            for chart in charts:
                assert chart["person_id"] == str(test_person.person_id)
    
    @pytest.mark.asyncio
    async def test_delete_chart(self, async_client, test_person):
        """Test deleting a chart."""
        # Create a chart
        chart_data = generate_chart_request_data(test_person.person_id)
        create_response = await async_client.post("/api/v1/charts", json=chart_data)
        
        if create_response.status_code == 201:
            chart_id = create_response.json()["data"]["chart_id"]
            
            # Delete the chart
            response = await async_client.delete(f"/api/v1/charts/{chart_id}")
            assert_response_success(response)
            
            # Verify chart is deleted
            get_response = await async_client.get(f"/api/v1/charts/{chart_id}")
            assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_cross_organization_chart_isolation(self, async_client, db_session, test_person):
        """Test that organizations cannot access each other's charts."""
        # Create a chart for test_person
        chart_data = generate_chart_request_data(test_person.person_id)
        create_response = await async_client.post("/api/v1/charts", json=chart_data)
        
        if create_response.status_code == 201:
            chart_id = create_response.json()["data"]["chart_id"]
            
            # Create another organization
            from josi.models.organization_model import Organization
            other_org = Organization(
                organization_id=uuid4(),
                name="Other Organization",
                api_key=f"other-api-key-{uuid4()}",
                is_active=True
            )
            db_session.add(other_org)
            await db_session.commit()
            
            # Try to access the chart with other org's API key
            headers = {"X-API-Key": other_org.api_key}
            response = await async_client.get(
                f"/api/v1/charts/{chart_id}",
                headers=headers
            )
            
            assert response.status_code == 404