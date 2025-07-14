"""
Test suite for Vedic Chart Calculations
Tests: POST /api/v1/charts/calculate with vedic system
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
import pytz
import os

# Test data for a known person
TEST_PERSON_DATA = {
    "name": "Test Vedic Chart",
    "date_of_birth": "1990-01-15",
    "time_of_birth": "10:30:00",
    "place_of_birth": "New Delhi, India"
}

class TestVedicChartAPI:
    """Test cases for Vedic chart calculations."""
    
    @pytest.fixture
    async def api_client(self):
        """Create API client with authentication."""
        return AsyncClient(
            base_url="http://localhost:8000",
            headers={"X-API-Key": os.getenv("API_KEY", "test-api-key")}
        )
    
    @pytest.fixture
    async def test_person(self, api_client):
        """Create a test person for chart calculations."""
        response = await api_client.post(
            "/api/v1/persons/",
            json=TEST_PERSON_DATA
        )
        assert response.status_code == 200
        person_data = response.json()
        yield person_data["data"]
        
        # Cleanup
        await api_client.delete(f"/api/v1/persons/{person_data['data']['person_id']}")
    
    @pytest.mark.asyncio
    async def test_vedic_chart_calculation_success(self, api_client, test_person):
        """Test successful Vedic chart calculation."""
        # Arrange
        params = {
            "person_id": test_person["person_id"],
            "systems": ["vedic"],
            "ayanamsa": "lahiri",
            "house_system": "whole_sign"
        }
        
        # Act
        response = await api_client.post(
            "/api/v1/charts/calculate",
            params=params
        )
        
        # Assert
        assert response.status_code == 200, f"Failed with: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        chart_data = data["data"]["charts"]["vedic"]["chart_data"]
        
        # Verify Vedic chart structure
        assert chart_data["chart_type"] == "vedic"
        assert "ayanamsa" in chart_data
        assert "ascendant" in chart_data
        assert "planets" in chart_data
        assert "houses" in chart_data
        
        # Verify Vedic-specific elements
        ascendant = chart_data["ascendant"]
        assert "nakshatra" in ascendant
        assert "pada" in ascendant
        
        # Check planets have Vedic attributes
        for planet_name, planet_data in chart_data["planets"].items():
            if planet_name != "Ketu":  # Ketu is calculated differently
                assert "nakshatra" in planet_data
                assert "pada" in planet_data
                assert "sign" in planet_data
                assert "house" in planet_data
    
    @pytest.mark.asyncio
    async def test_vedic_chart_with_different_ayanamsa(self, api_client, test_person):
        """Test Vedic chart with different ayanamsa systems."""
        ayanamsa_systems = ["lahiri", "krishnamurti", "raman", "yukteshwar"]
        
        for ayanamsa in ayanamsa_systems:
            # Arrange
            params = {
                "person_id": test_person["person_id"],
                "systems": ["vedic"],
                "ayanamsa": ayanamsa,
                "house_system": "whole_sign"
            }
            
            # Act
            response = await api_client.post(
                "/api/v1/charts/calculate",
                params=params
            )
            
            # Assert
            assert response.status_code == 200, f"Failed for {ayanamsa}: {response.text}"
            
            data = response.json()
            chart_data = data["data"]["charts"]["vedic"]["chart_data"]
            
            # Verify correct ayanamsa value is present
            assert "ayanamsa" in chart_data
            assert isinstance(chart_data["ayanamsa"], (int, float))
    
    @pytest.mark.asyncio
    async def test_vedic_chart_south_indian_style(self, api_client, test_person):
        """Test South Indian chart style calculation."""
        # Arrange
        params = {
            "person_id": test_person["person_id"],
            "systems": ["south_indian"],
            "ayanamsa": "lahiri",
            "house_system": "whole_sign"
        }
        
        # Act
        response = await api_client.post(
            "/api/v1/charts/calculate",
            params=params
        )
        
        # Assert
        assert response.status_code == 200, f"Failed with: {response.text}"
        
        data = response.json()
        chart_data = data["data"]["charts"]["south_indian"]["chart_data"]
        
        assert chart_data["chart_type"] == "south_indian"
        # South Indian chart should have same data as Vedic, just different display format
        assert "planets" in chart_data
        assert "houses" in chart_data
    
    @pytest.mark.asyncio
    async def test_vedic_chart_with_dasha(self, api_client, test_person):
        """Test that Vedic chart includes Dasha periods."""
        # Arrange
        params = {
            "person_id": test_person["person_id"],
            "systems": ["vedic"],
            "ayanamsa": "lahiri"
        }
        
        # Act
        response = await api_client.post(
            "/api/v1/charts/calculate",
            params=params
        )
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        chart_data = data["data"]["charts"]["vedic"]["chart_data"]
        
        # Verify Dasha is included
        assert "dasha" in chart_data
        dasha_data = chart_data["dasha"]
        
        assert "current_dasha" in dasha_data
        assert "dasha_periods" in dasha_data
        assert len(dasha_data["dasha_periods"]) > 0
    
    @pytest.mark.asyncio
    async def test_vedic_chart_with_panchang(self, api_client, test_person):
        """Test that Vedic chart includes Panchang data."""
        # Arrange
        params = {
            "person_id": test_person["person_id"],
            "systems": ["vedic"],
            "ayanamsa": "lahiri"
        }
        
        # Act
        response = await api_client.post(
            "/api/v1/charts/calculate",
            params=params
        )
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        chart_data = data["data"]["charts"]["vedic"]["chart_data"]
        
        # Verify Panchang is included
        assert "panchang" in chart_data
        panchang = chart_data["panchang"]
        
        assert "tithi" in panchang
        assert "nakshatra" in panchang
        assert "yoga" in panchang
        assert "karana" in panchang
        assert "vara" in panchang
    
    @pytest.mark.asyncio 
    async def test_vedic_calculation_error_handling(self, api_client):
        """Test error handling for invalid Vedic chart requests."""
        # Test with invalid person_id
        params = {
            "person_id": "00000000-0000-0000-0000-000000000000",
            "systems": ["vedic"]
        }
        
        response = await api_client.post(
            "/api/v1/charts/calculate",
            params=params
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])