"""
Real-world chart calculation tests using actual birth data.

Tests chart calculations using real birth data from famous personalities
with known accurate astrological information for verification.
"""
import pytest
from datetime import datetime, date, time
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient
from fastapi import status

from tests.conftest import assert_response_success, assert_response_error


class TestRealBirthDataCharts:
    """Test chart calculations with real birth data."""
    
    # Famous personalities with well-documented birth data
    CELEBRITY_BIRTH_DATA = {
        "barack_obama": {
            "name": "Barack Obama",
            "date_of_birth": "1961-08-04",
            "time_of_birth": "1961-08-04T19:24:00",  # 7:24 PM
            "place_of_birth": "Honolulu, Hawaii, USA",
            "latitude": "21.3099",
            "longitude": "-157.8581",
            "timezone": "Pacific/Honolulu",
            "email": "barack.obama@test.com",
            # Known astrological facts for verification
            "expected_vedic": {
                "sun_sign": "Cancer",  # Vedic system
                "moon_sign": "Gemini",
                "ascendant": "Capricorn",
                "birth_nakshatra": "Punarvasu"
            },
            "expected_western": {
                "sun_sign": "Leo",  # Western tropical
                "moon_sign": "Gemini",
                "ascendant": "Aquarius"
            }
        },
        "oprah_winfrey": {
            "name": "Oprah Winfrey",
            "date_of_birth": "1954-01-29",
            "time_of_birth": "1954-01-29T16:30:00",  # 4:30 PM
            "place_of_birth": "Kosciusko, Mississippi, USA",
            "latitude": "33.0573",
            "longitude": "-89.5867",
            "timezone": "America/Chicago",
            "email": "oprah.winfrey@test.com",
            "expected_vedic": {
                "sun_sign": "Capricorn",
                "moon_sign": "Sagittarius",
                "ascendant": "Gemini"
            },
            "expected_western": {
                "sun_sign": "Aquarius",
                "moon_sign": "Sagittarius",
                "ascendant": "Cancer"
            }
        },
        "steve_jobs": {
            "name": "Steve Jobs",
            "date_of_birth": "1955-02-24",
            "time_of_birth": "1955-02-24T19:15:00",  # 7:15 PM
            "place_of_birth": "San Francisco, California, USA",
            "latitude": "37.7749",
            "longitude": "-122.4194",
            "timezone": "America/Los_Angeles",
            "email": "steve.jobs@test.com",
            "expected_vedic": {
                "sun_sign": "Aquarius",
                "moon_sign": "Aries",
                "ascendant": "Virgo"
            },
            "expected_western": {
                "sun_sign": "Pisces",
                "moon_sign": "Aries",
                "ascendant": "Virgo"
            }
        },
        "albert_einstein": {
            "name": "Albert Einstein",
            "date_of_birth": "1879-03-14",
            "time_of_birth": "1879-03-14T11:30:00",  # 11:30 AM
            "place_of_birth": "Ulm, Germany",
            "latitude": "48.3984",
            "longitude": "9.9915",
            "timezone": "Europe/Berlin",
            "email": "albert.einstein@test.com",
            "expected_vedic": {
                "sun_sign": "Aquarius",
                "moon_sign": "Sagittarius",
                "ascendant": "Gemini"
            },
            "expected_western": {
                "sun_sign": "Pisces",
                "moon_sign": "Sagittarius",
                "ascendant": "Gemini"
            }
        }
    }
    
    @pytest.mark.asyncio
    async def test_barack_obama_vedic_chart(self, async_client: AsyncClient, db_session):
        """Test Barack Obama's Vedic chart calculation."""
        person_data = self.CELEBRITY_BIRTH_DATA["barack_obama"]
        
        # Create person
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        # Calculate Vedic chart
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        
        # Verify chart structure
        assert "chart_id" in chart_data
        assert chart_data["chart_type"] == "natal"
        assert chart_data["coordinate_system"] == "sidereal"
        assert "planets" in chart_data["chart_data"]
        assert "houses" in chart_data["chart_data"]
        assert "aspects" in chart_data["chart_data"]
        
        # Verify key planetary positions
        planets = chart_data["chart_data"]["planets"]
        
        # Check Sun position (should be in Cancer in Vedic system)
        assert "Sun" in planets
        sun_sign = self._get_vedic_sign(planets["Sun"]["longitude"])
        assert sun_sign == person_data["expected_vedic"]["sun_sign"], \
            f"Expected Sun in {person_data['expected_vedic']['sun_sign']}, got {sun_sign}"
        
        # Check Moon position
        assert "Moon" in planets
        moon_sign = self._get_vedic_sign(planets["Moon"]["longitude"])
        assert moon_sign == person_data["expected_vedic"]["moon_sign"], \
            f"Expected Moon in {person_data['expected_vedic']['moon_sign']}, got {moon_sign}"
        
        # Check Ascendant
        houses = chart_data["chart_data"]["houses"]
        ascendant_sign = self._get_vedic_sign(houses[0]["sign_longitude"])
        assert ascendant_sign == person_data["expected_vedic"]["ascendant"], \
            f"Expected Ascendant in {person_data['expected_vedic']['ascendant']}, got {ascendant_sign}"
    
    @pytest.mark.asyncio
    async def test_barack_obama_western_chart(self, async_client: AsyncClient, db_session):
        """Test Barack Obama's Western chart calculation."""
        person_data = self.CELEBRITY_BIRTH_DATA["barack_obama"]
        
        # Create person
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        # Calculate Western chart
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        
        # Verify key planetary positions
        planets = chart_data["chart_data"]["planets"]
        
        # Check Sun position (should be in Leo in Western system)
        sun_sign = self._get_western_sign(planets["Sun"]["longitude"])
        assert sun_sign == person_data["expected_western"]["sun_sign"], \
            f"Expected Sun in {person_data['expected_western']['sun_sign']}, got {sun_sign}"
        
        # Check Moon position
        moon_sign = self._get_western_sign(planets["Moon"]["longitude"])
        assert moon_sign == person_data["expected_western"]["moon_sign"], \
            f"Expected Moon in {person_data['expected_western']['moon_sign']}, got {moon_sign}"
    
    @pytest.mark.asyncio
    async def test_multiple_celebrities_vedic_accuracy(self, async_client: AsyncClient, db_session):
        """Test Vedic chart accuracy for multiple celebrities."""
        for celebrity_key, person_data in self.CELEBRITY_BIRTH_DATA.items():
            # Create person
            person_response = await async_client.post("/api/v1/persons/", json=person_data)
            person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
            person_id = person_result["person_id"]
            
            # Calculate Vedic chart
            chart_request = {
                "person_id": person_id,
                "chart_type": "natal",
                "house_system": "whole_sign",
                "ayanamsa": "lahiri",
                "coordinate_system": "sidereal"
            }
            
            chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
            chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
            
            planets = chart_data["chart_data"]["planets"]
            houses = chart_data["chart_data"]["houses"]
            
            # Verify Sun sign
            sun_sign = self._get_vedic_sign(planets["Sun"]["longitude"])
            expected_sun = person_data["expected_vedic"]["sun_sign"]
            assert sun_sign == expected_sun, \
                f"{celebrity_key}: Expected Sun in {expected_sun}, got {sun_sign}"
            
            # Verify Moon sign
            moon_sign = self._get_vedic_sign(planets["Moon"]["longitude"])
            expected_moon = person_data["expected_vedic"]["moon_sign"]
            assert moon_sign == expected_moon, \
                f"{celebrity_key}: Expected Moon in {expected_moon}, got {moon_sign}"
            
            # Verify Ascendant
            ascendant_sign = self._get_vedic_sign(houses[0]["sign_longitude"])
            expected_asc = person_data["expected_vedic"]["ascendant"]
            assert ascendant_sign == expected_asc, \
                f"{celebrity_key}: Expected Ascendant in {expected_asc}, got {ascendant_sign}"
    
    @pytest.mark.asyncio
    async def test_chart_consistency_across_calculations(self, async_client: AsyncClient, db_session):
        """Test that the same birth data produces consistent chart results."""
        person_data = self.CELEBRITY_BIRTH_DATA["steve_jobs"]
        
        # Create person once
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "whole_sign",
            "ayanamsa": "lahiri",
            "coordinate_system": "sidereal"
        }
        
        # Calculate same chart multiple times
        charts = []
        for i in range(3):
            chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
            chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
            charts.append(chart_data)
        
        # Verify all calculations are identical
        for i in range(1, len(charts)):
            self._assert_charts_identical(charts[0], charts[i], f"Chart {i+1}")
    
    @pytest.mark.asyncio
    async def test_house_systems_accuracy(self, async_client: AsyncClient, db_session):
        """Test accuracy of different house systems."""
        person_data = self.CELEBRITY_BIRTH_DATA["oprah_winfrey"]
        
        # Create person
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        house_systems = ["placidus", "koch", "equal", "whole_sign", "campanus"]
        charts = {}
        
        for house_system in house_systems:
            chart_request = {
                "person_id": person_id,
                "chart_type": "natal",
                "house_system": house_system,
                "coordinate_system": "tropical"
            }
            
            chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
            chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
            charts[house_system] = chart_data
        
        # Verify planetary positions are the same across house systems
        for system1 in house_systems:
            for system2 in house_systems:
                if system1 != system2:
                    planets1 = charts[system1]["chart_data"]["planets"]
                    planets2 = charts[system2]["chart_data"]["planets"]
                    
                    for planet in planets1:
                        assert abs(planets1[planet]["longitude"] - planets2[planet]["longitude"]) < 0.01, \
                            f"Planet {planet} longitude differs between {system1} and {system2}"
        
        # Verify house positions differ appropriately between systems
        placidus_houses = charts["placidus"]["chart_data"]["houses"]
        whole_sign_houses = charts["whole_sign"]["chart_data"]["houses"]
        
        # House cusps should be different between Placidus and Whole Sign
        # (except possibly for the 1st house)
        different_cusps = 0
        for i in range(1, 12):  # Houses 2-12
            placidus_cusp = placidus_houses[i]["cusp_longitude"]
            whole_sign_cusp = whole_sign_houses[i]["cusp_longitude"]
            if abs(placidus_cusp - whole_sign_cusp) > 1.0:  # More than 1 degree difference
                different_cusps += 1
        
        assert different_cusps >= 6, "House systems should produce different house cusps"
    
    @pytest.mark.asyncio
    async def test_ayanamsa_variations(self, async_client: AsyncClient, db_session):
        """Test different Ayanamsa calculations."""
        person_data = self.CELEBRITY_BIRTH_DATA["albert_einstein"]
        
        # Create person
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        ayanamsas = ["lahiri", "raman", "krishnamurti", "yukteshwar"]
        charts = {}
        
        for ayanamsa in ayanamsas:
            chart_request = {
                "person_id": person_id,
                "chart_type": "natal",
                "house_system": "whole_sign",
                "ayanamsa": ayanamsa,
                "coordinate_system": "sidereal"
            }
            
            chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
            chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
            charts[ayanamsa] = chart_data
        
        # Verify that different ayanamsas produce different sidereal positions
        lahiri_sun = charts["lahiri"]["chart_data"]["planets"]["Sun"]["longitude"]
        raman_sun = charts["raman"]["chart_data"]["planets"]["Sun"]["longitude"]
        
        # Should be slightly different (typically less than 1 degree)
        assert abs(lahiri_sun - raman_sun) > 0.1, \
            "Different ayanamsas should produce different planetary positions"
        assert abs(lahiri_sun - raman_sun) < 2.0, \
            "Ayanamsa differences should be reasonable (< 2 degrees)"
    
    @pytest.mark.asyncio
    async def test_chart_aspects_calculation(self, async_client: AsyncClient, db_session):
        """Test planetary aspects calculation accuracy."""
        person_data = self.CELEBRITY_BIRTH_DATA["barack_obama"]
        
        # Create person
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        # Calculate chart
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        
        aspects = chart_data["chart_data"]["aspects"]
        planets = chart_data["chart_data"]["planets"]
        
        # Verify aspects structure
        assert isinstance(aspects, list)
        assert len(aspects) > 0, "Chart should have planetary aspects"
        
        # Verify each aspect has required fields
        for aspect in aspects:
            assert "planet1" in aspect
            assert "planet2" in aspect
            assert "aspect" in aspect
            assert "orb" in aspect
            assert aspect["planet1"] in planets
            assert aspect["planet2"] in planets
            
            # Verify orb is reasonable (typically < 10 degrees)
            assert 0 <= aspect["orb"] <= 10, f"Aspect orb {aspect['orb']} seems unreasonable"
        
        # Verify major aspects are present
        aspect_types = [aspect["aspect"] for aspect in aspects]
        major_aspects = ["conjunction", "opposition", "square", "trine", "sextile"]
        
        found_major_aspects = [asp for asp in aspect_types if asp in major_aspects]
        assert len(found_major_aspects) > 0, "Chart should have at least some major aspects"
    
    def _get_vedic_sign(self, longitude: float) -> str:
        """Convert longitude to Vedic sign name."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign_index = int(longitude / 30)
        return signs[sign_index % 12]
    
    def _get_western_sign(self, longitude: float) -> str:
        """Convert longitude to Western sign name (same as Vedic for calculation)."""
        return self._get_vedic_sign(longitude)
    
    def _assert_charts_identical(self, chart1: dict, chart2: dict, chart2_name: str):
        """Assert that two charts are identical."""
        planets1 = chart1["chart_data"]["planets"]
        planets2 = chart2["chart_data"]["planets"]
        
        for planet in planets1:
            assert planet in planets2, f"{chart2_name}: Missing planet {planet}"
            
            long1 = planets1[planet]["longitude"]
            long2 = planets2[planet]["longitude"]
            assert abs(long1 - long2) < 0.001, \
                f"{chart2_name}: Planet {planet} longitude differs: {long1} vs {long2}"


class TestChartValidation:
    """Test chart calculation validation and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_person_id_chart_calculation(self, async_client: AsyncClient):
        """Test chart calculation with invalid person ID."""
        chart_request = {
            "person_id": str(uuid4()),  # Non-existent person
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_invalid_chart_parameters(self, async_client: AsyncClient, db_session):
        """Test chart calculation with invalid parameters."""
        # Create a valid person first
        person_data = {
            "name": "Test Person",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "1990-01-01T12:00:00",
            "place_of_birth": "New York, NY, USA",
            "latitude": "40.7128",
            "longitude": "-74.0060",
            "timezone": "America/New_York",
            "email": "test@example.com"
        }
        
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        # Test invalid house system
        invalid_chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "invalid_system",
            "coordinate_system": "tropical"
        }
        
        response = await async_client.post("/api/v1/charts/calculate", json=invalid_chart_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test invalid coordinate system
        invalid_chart_request["house_system"] = "placidus"
        invalid_chart_request["coordinate_system"] = "invalid_system"
        
        response = await async_client.post("/api/v1/charts/calculate", json=invalid_chart_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_extreme_date_handling(self, async_client: AsyncClient, db_session):
        """Test chart calculation with extreme dates."""
        # Very old date
        old_person_data = {
            "name": "Ancient Person",
            "date_of_birth": "1000-01-01",
            "time_of_birth": "1000-01-01T12:00:00",
            "place_of_birth": "Rome, Italy",
            "latitude": "41.9028",
            "longitude": "12.4964",
            "timezone": "Europe/Rome",
            "email": "ancient@example.com"
        }
        
        person_response = await async_client.post("/api/v1/persons/", json=old_person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        # This might fail for very old dates due to ephemeris limitations
        response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # Expected for dates outside ephemeris range
            error_data = response.json()
            assert "ephemeris" in error_data["detail"].lower() or "date" in error_data["detail"].lower()
        else:
            # If it succeeds, verify the chart is valid
            chart_data = assert_response_success(response, status.HTTP_201_CREATED)
            assert "planets" in chart_data["chart_data"]
    
    @pytest.mark.asyncio
    async def test_high_latitude_locations(self, async_client: AsyncClient, db_session):
        """Test chart calculation for high latitude locations."""
        # Location in Alaska (high latitude)
        arctic_person_data = {
            "name": "Arctic Person",
            "date_of_birth": "1990-06-21",  # Summer solstice
            "time_of_birth": "1990-06-21T12:00:00",
            "place_of_birth": "Barrow, Alaska, USA",
            "latitude": "71.2906",
            "longitude": "-156.7889",
            "timezone": "America/Anchorage",
            "email": "arctic@example.com"
        }
        
        person_response = await async_client.post("/api/v1/persons/", json=arctic_person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        chart_request = {
            "person_id": person_id,
            "chart_type": "natal",
            "house_system": "placidus",
            "coordinate_system": "tropical"
        }
        
        chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
        chart_data = assert_response_success(chart_response, status.HTTP_201_CREATED)
        
        # Verify chart was calculated successfully despite high latitude
        assert "planets" in chart_data["chart_data"]
        assert "houses" in chart_data["chart_data"]
        
        # Verify all major planets are present
        planets = chart_data["chart_data"]["planets"]
        expected_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        
        for planet in expected_planets:
            assert planet in planets, f"Missing planet {planet} in high-latitude chart"
            assert 0 <= planets[planet]["longitude"] < 360, \
                f"Invalid longitude for {planet}: {planets[planet]['longitude']}"


class TestPerformanceWithRealData:
    """Test performance with real birth data calculations."""
    
    @pytest.mark.asyncio
    async def test_multiple_chart_calculation_performance(self, async_client: AsyncClient, db_session):
        """Test performance when calculating multiple charts."""
        import time
        
        # Create multiple persons
        person_ids = []
        for i, (key, person_data) in enumerate(list(TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA.items())[:3]):
            person_data = person_data.copy()
            person_data["email"] = f"perf_test_{i}@example.com"
            
            person_response = await async_client.post("/api/v1/persons/", json=person_data)
            person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
            person_ids.append(person_result["person_id"])
        
        # Time multiple chart calculations
        start_time = time.time()
        
        for person_id in person_ids:
            chart_request = {
                "person_id": person_id,
                "chart_type": "natal",
                "house_system": "placidus",
                "coordinate_system": "tropical"
            }
            
            chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
            assert_response_success(chart_response, status.HTTP_201_CREATED)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should calculate 3 charts in reasonable time (< 10 seconds)
        assert total_time < 10.0, f"Chart calculations took too long: {total_time:.2f} seconds"
        
        avg_time = total_time / len(person_ids)
        print(f"Average chart calculation time: {avg_time:.2f} seconds")
    
    @pytest.mark.asyncio
    async def test_concurrent_chart_calculations(self, async_client: AsyncClient, db_session):
        """Test concurrent chart calculations don't interfere."""
        import asyncio
        
        person_data = TestRealBirthDataCharts.CELEBRITY_BIRTH_DATA["barack_obama"].copy()
        person_data["email"] = "concurrent_test@example.com"
        
        person_response = await async_client.post("/api/v1/persons/", json=person_data)
        person_result = assert_response_success(person_response, status.HTTP_201_CREATED)
        person_id = person_result["person_id"]
        
        async def calculate_chart(chart_type, house_system):
            chart_request = {
                "person_id": person_id,
                "chart_type": chart_type,
                "house_system": house_system,
                "coordinate_system": "tropical"
            }
            
            chart_response = await async_client.post("/api/v1/charts/calculate", json=chart_request)
            return assert_response_success(chart_response, status.HTTP_201_CREATED)
        
        # Run multiple calculations concurrently
        tasks = [
            calculate_chart("natal", "placidus"),
            calculate_chart("natal", "koch"),
            calculate_chart("natal", "equal"),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all calculations succeeded
        assert len(results) == 3
        for result in results:
            assert "chart_id" in result
            assert "chart_data" in result
            assert "planets" in result["chart_data"]