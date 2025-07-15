"""
Integration tests for celebrity chart calculations.

This module tests the Josi API using real celebrity birth data with known
astrological positions to validate the accuracy of calculations.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
import asyncio
from typing import Dict, Any, List

from tests.fixtures.celebrity_birth_data import (
    get_celebrity_test_data,
    get_celebrities_by_rating,
    get_test_payload
)


class TestCelebrityCharts:
    """Test suite for celebrity chart calculations."""
    
    @pytest.fixture
    def api_headers(self) -> Dict[str, str]:
        """Get API headers with test organization key."""
        return {"X-API-Key": "test-api-key"}
    
    async def create_person(
        self, 
        client: AsyncClient, 
        celebrity_data: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create a person in the API."""
        payload = get_test_payload(celebrity_data)
        response = await client.post(
            "/api/v1/persons",
            json=payload,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        return data["data"]
    
    async def calculate_chart(
        self,
        client: AsyncClient,
        person_id: str,
        chart_type: str,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Calculate a chart for a person."""
        payload = {
            "person_id": person_id,
            "chart_type": chart_type,
            "house_system": "placidus" if chart_type == "western" else "whole_sign",
            "ayanamsa": "lahiri" if chart_type == "vedic" else None
        }
        
        response = await client.post(
            "/api/v1/charts",
            json=payload,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        return data["data"]
    
    @pytest.mark.asyncio
    async def test_celebrity_person_creation(self, client: AsyncClient, api_headers: Dict[str, str]):
        """Test creating persons for all celebrities in our catalog."""
        celebrities = get_celebrity_test_data()
        created_persons = []
        
        for celebrity in celebrities:
            person = await self.create_person(client, celebrity, api_headers)
            
            # Verify person data
            assert person["name"] == celebrity["name"]
            assert person["birth_date"] == celebrity["birth_date"]
            assert person["birth_time"] == celebrity["birth_time"]
            assert person["birth_place"] == celebrity["birth_place"]
            assert abs(person["latitude"] - celebrity["latitude"]) < 0.01
            assert abs(person["longitude"] - celebrity["longitude"]) < 0.01
            assert person["timezone"] == celebrity["timezone"]
            
            created_persons.append(person)
            print(f"✓ Created person: {celebrity['name']} (ID: {person['person_id']})")
        
        assert len(created_persons) == len(celebrities)
    
    @pytest.mark.asyncio
    async def test_western_chart_calculations(self, client: AsyncClient, api_headers: Dict[str, str]):
        """Test Western chart calculations for celebrities."""
        # Test with a subset of highly reliable (AA-rated) celebrities
        celebrities = get_celebrities_by_rating("AA")[:3]  # Test first 3 AA-rated
        
        for celebrity in celebrities:
            # Create person
            person = await self.create_person(client, celebrity, api_headers)
            
            # Calculate Western chart
            chart = await self.calculate_chart(
                client, 
                person["person_id"], 
                "western",
                api_headers
            )
            
            # Verify chart structure
            assert chart["chart_type"] == "western"
            assert chart["person_id"] == person["person_id"]
            assert chart["house_system"] == "placidus"
            assert "planet_positions" in chart["chart_data"]
            assert "house_cusps" in chart["chart_data"]
            assert "aspects" in chart["chart_data"]
            
            # Verify sun sign matches expected
            sun_position = chart["chart_data"]["planet_positions"]["sun"]
            assert sun_position["sign"] == celebrity["expected_sun_sign"].lower()
            
            print(f"✓ Western chart calculated for {celebrity['name']}")
            print(f"  Sun: {sun_position['sign']} at {sun_position['degree']:.2f}°")
    
    @pytest.mark.asyncio
    async def test_vedic_chart_calculations(self, client: AsyncClient, api_headers: Dict[str, str]):
        """Test Vedic chart calculations for celebrities."""
        celebrities = get_celebrities_by_rating("AA")[:3]
        
        for celebrity in celebrities:
            # Create person
            person = await self.create_person(client, celebrity, api_headers)
            
            # Calculate Vedic chart
            chart = await self.calculate_chart(
                client,
                person["person_id"],
                "vedic",
                api_headers
            )
            
            # Verify chart structure
            assert chart["chart_type"] == "vedic"
            assert chart["person_id"] == person["person_id"]
            assert chart["ayanamsa"] == "lahiri"
            assert "planet_positions" in chart["chart_data"]
            assert "house_cusps" in chart["chart_data"]
            
            # Check for Vedic-specific data
            assert "nakshatras" in chart["chart_data"]
            assert "yogas" in chart["chart_data"]
            
            print(f"✓ Vedic chart calculated for {celebrity['name']}")
            print(f"  Ayanamsa: {chart['ayanamsa']}")
    
    @pytest.mark.asyncio
    async def test_multiple_chart_types(self, client: AsyncClient, api_headers: Dict[str, str]):
        """Test calculating multiple chart types for the same person."""
        # Use Barack Obama as test case
        celebrity = next(c for c in get_celebrity_test_data() if c["name"] == "Barack Obama")
        person = await self.create_person(client, celebrity, api_headers)
        
        chart_types = ["western", "vedic", "chinese"]
        charts = {}
        
        for chart_type in chart_types:
            chart = await self.calculate_chart(
                client,
                person["person_id"],
                chart_type,
                api_headers
            )
            charts[chart_type] = chart
            print(f"✓ {chart_type.capitalize()} chart calculated for {celebrity['name']}")
        
        # Verify all charts reference the same person
        assert all(chart["person_id"] == person["person_id"] for chart in charts.values())
        
        # Verify each chart has unique data
        assert charts["western"]["chart_data"].get("house_cusps") is not None
        assert charts["vedic"]["chart_data"].get("nakshatras") is not None
        assert charts["chinese"]["chart_data"].get("elements") is not None
    
    @pytest.mark.asyncio
    async def test_chart_accuracy_validation(self, client: AsyncClient, api_headers: Dict[str, str]):
        """Test the accuracy of calculated positions against known values."""
        # Use Einstein as test case (well-documented positions)
        celebrity = next(c for c in get_celebrity_test_data() if c["name"] == "Albert Einstein")
        person = await self.create_person(client, celebrity, api_headers)
        
        # Calculate Western chart
        chart = await self.calculate_chart(
            client,
            person["person_id"],
            "western",
            api_headers
        )
        
        # Known positions for Einstein (approximate)
        # Sun: 23° Pisces
        # Moon: 14° Sagittarius  
        # Mercury: 3° Aries
        
        positions = chart["chart_data"]["planet_positions"]
        
        # Check Sun position
        sun = positions["sun"]
        assert sun["sign"] == "pisces"
        assert 20 <= sun["degree"] <= 26  # Allow some tolerance
        
        # Check Moon position
        moon = positions["moon"]
        assert moon["sign"] == "sagittarius"
        assert 10 <= moon["degree"] <= 18
        
        print(f"✓ Position accuracy validated for {celebrity['name']}")
        print(f"  Sun: {sun['sign']} {sun['degree']:.2f}°")
        print(f"  Moon: {moon['sign']} {moon['degree']:.2f}°")
    
    @pytest.mark.asyncio
    async def test_batch_celebrity_processing(self, client: AsyncClient, api_headers: Dict[str, str]):
        """Test processing multiple celebrities in parallel."""
        celebrities = get_celebrity_test_data()[:5]  # Test first 5
        
        # Create all persons in parallel
        person_tasks = [
            self.create_person(client, celebrity, api_headers)
            for celebrity in celebrities
        ]
        persons = await asyncio.gather(*person_tasks)
        
        # Calculate charts in parallel
        chart_tasks = [
            self.calculate_chart(client, person["person_id"], "western", api_headers)
            for person in persons
        ]
        charts = await asyncio.gather(*chart_tasks)
        
        # Verify results
        assert len(charts) == len(celebrities)
        for i, chart in enumerate(charts):
            assert chart["person_id"] == persons[i]["person_id"]
            print(f"✓ Batch processed: {celebrities[i]['name']}")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client: AsyncClient, api_headers: Dict[str, str]):
        """Test error handling with invalid data."""
        # Test with invalid birth time
        invalid_data = {
            "name": "Invalid Test",
            "birth_date": "2000-01-01",
            "birth_time": "25:00:00",  # Invalid time
            "birth_place": "London, England",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "Europe/London"
        }
        
        response = await client.post(
            "/api/v1/persons",
            json=invalid_data,
            headers=api_headers
        )
        
        assert response.status_code == 422  # Validation error
        
        print("✓ Error handling validated")
    
    @pytest.mark.asyncio
    async def test_timezone_handling(self, client: AsyncClient, api_headers: Dict[str, str]):
        """Test correct timezone handling for different locations."""
        # Test celebrities from different timezones
        timezone_tests = [
            ("Barack Obama", "Pacific/Honolulu"),  # Hawaii
            ("Princess Diana", "Europe/London"),    # UK
            ("Nelson Mandela", "Africa/Johannesburg")  # South Africa
        ]
        
        for name, expected_tz in timezone_tests:
            celebrity = next(c for c in get_celebrity_test_data() if c["name"] == name)
            person = await self.create_person(client, celebrity, api_headers)
            
            assert person["timezone"] == expected_tz
            print(f"✓ Timezone verified for {name}: {expected_tz}")


@pytest.mark.asyncio
async def test_celebrity_chart_summary(client: AsyncClient):
    """Generate a summary report of all celebrity chart tests."""
    test_suite = TestCelebrityCharts()
    headers = {"X-API-Key": "test-api-key"}
    
    print("\n" + "="*60)
    print("CELEBRITY CHART INTEGRATION TEST SUMMARY")
    print("="*60)
    
    celebrities = get_celebrity_test_data()
    print(f"\nTotal celebrities in catalog: {len(celebrities)}")
    print(f"AA-rated (birth certificate): {len(get_celebrities_by_rating('AA'))}")
    print(f"A-rated (from memory): {len(get_celebrities_by_rating('A'))}")
    
    print("\nCelebrity Catalog:")
    for celebrity in celebrities:
        print(f"  - {celebrity['name']} ({celebrity['birth_date']}) - Rating: {celebrity['rating']}")
    
    print("\n" + "="*60)