"""Integration tests for all API endpoints."""
import pytest
import requests
from uuid import UUID

BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key-12345"
HEADERS = {"X-API-Key": API_KEY}
PERSON_ID = "f2303d9c-0bc9-4b18-b17e-9cf4b7bd5f9f"


class TestAPIEndpoints:
    """Test all API endpoints for functionality."""
    
    def test_chart_calculation_western(self):
        """Test Western chart calculation."""
        response = requests.post(
            f"{BASE_URL}/api/v1/charts/calculate",
            headers=HEADERS,
            params={"person_id": PERSON_ID, "systems": "western", "house_system": "placidus"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_chart_calculation_vedic(self):
        """Test Vedic chart calculation."""
        response = requests.post(
            f"{BASE_URL}/api/v1/charts/calculate",
            headers=HEADERS,
            params={"person_id": PERSON_ID, "systems": "vedic", "house_system": "whole_sign"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_chart_calculation_multiple_systems(self):
        """Test multiple system chart calculation."""
        response = requests.post(
            f"{BASE_URL}/api/v1/charts/calculate",
            headers=HEADERS,
            params={"person_id": PERSON_ID, "systems": "western,vedic", "house_system": "placidus"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_person_charts(self):
        """Test getting person's charts."""
        response = requests.get(
            f"{BASE_URL}/api/v1/charts/person/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_divisional_charts(self):
        """Test divisional chart calculation."""
        response = requests.get(
            f"{BASE_URL}/api/v1/charts/divisional/{PERSON_ID}",
            headers=HEADERS,
            params={"division": 9}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_person_by_id(self):
        """Test getting person by ID."""
        response = requests.get(
            f"{BASE_URL}/api/v1/persons/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_list_persons(self):
        """Test listing all persons."""
        response = requests.get(
            f"{BASE_URL}/api/v1/persons/",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_panchang(self):
        """Test panchang calculation."""
        response = requests.get(
            f"{BASE_URL}/api/v1/panchang/",
            headers=HEADERS,
            params={
                "date": "1961-08-04T19:24:00",
                "latitude": 21.304547,
                "longitude": -157.8581,
                "timezone": "Pacific/Honolulu"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_muhurta(self):
        """Test muhurta calculation."""
        response = requests.post(
            f"{BASE_URL}/api/v1/panchang/muhurta",
            headers=HEADERS,
            params={
                "purpose": "marriage",
                "start_date": "2025-01-01T00:00:00",
                "end_date": "2025-12-31T23:59:59",
                "latitude": 21.304547,
                "longitude": -157.8581,
                "timezone": "Pacific/Honolulu"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_vimshottari_dasha(self):
        """Test Vimshottari dasha calculation."""
        response = requests.get(
            f"{BASE_URL}/api/v1/dasha/vimshottari/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_yogini_dasha(self):
        """Test Yogini dasha calculation."""
        response = requests.get(
            f"{BASE_URL}/api/v1/dasha/yogini/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_chara_dasha(self):
        """Test Chara dasha calculation."""
        response = requests.get(
            f"{BASE_URL}/api/v1/dasha/chara/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_current_transits(self):
        """Test current transits."""
        response = requests.get(
            f"{BASE_URL}/api/v1/transits/current/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_transit_forecast(self):
        """Test transit forecast."""
        response = requests.get(
            f"{BASE_URL}/api/v1/transits/forecast/{PERSON_ID}",
            headers=HEADERS,
            params={"days": 30}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_compatibility_calculate(self):
        """Test compatibility calculation."""
        response = requests.post(
            f"{BASE_URL}/api/v1/compatibility/calculate",
            headers=HEADERS,
            params={
                "person1_id": PERSON_ID,
                "person2_id": PERSON_ID
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_synastry(self):
        """Test synastry calculation."""
        response = requests.post(
            f"{BASE_URL}/api/v1/compatibility/synastry",
            headers=HEADERS,
            params={
                "person1_id": PERSON_ID,
                "person2_id": PERSON_ID
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_daily_predictions(self):
        """Test daily predictions."""
        response = requests.get(
            f"{BASE_URL}/api/v1/predictions/daily/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_monthly_predictions(self):
        """Test monthly predictions."""
        response = requests.get(
            f"{BASE_URL}/api/v1/predictions/monthly/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_yearly_predictions(self):
        """Test yearly predictions."""
        response = requests.get(
            f"{BASE_URL}/api/v1/predictions/yearly/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_remedies(self):
        """Test remedies for person."""
        response = requests.get(
            f"{BASE_URL}/api/v1/remedies/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_gemstone_recommendations(self):
        """Test gemstone recommendations."""
        response = requests.get(
            f"{BASE_URL}/api/v1/remedies/gemstones/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_numerology(self):
        """Test numerology analysis."""
        response = requests.post(
            f"{BASE_URL}/api/v1/remedies/numerology",
            headers=HEADERS,
            params={"name": "Barack Obama", "date_of_birth": "1961-08-04T00:00:00"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_color_therapy(self):
        """Test color therapy recommendations."""
        response = requests.post(
            f"{BASE_URL}/api/v1/remedies/color-therapy/{PERSON_ID}",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_location_search(self):
        """Test location search."""
        response = requests.get(
            f"{BASE_URL}/api/v1/location/search",
            headers=HEADERS,
            params={"query": "New York"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_location_coordinates(self):
        """Test getting coordinates."""
        response = requests.post(
            f"{BASE_URL}/api/v1/location/coordinates",
            headers=HEADERS,
            params={"city": "New York", "state": "NY", "country": "USA"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_location_timezone(self):
        """Test timezone from coordinates."""
        response = requests.get(
            f"{BASE_URL}/api/v1/location/timezone",
            headers=HEADERS,
            params={"latitude": 40.7128, "longitude": -74.0060}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = requests.get(f"{BASE_URL}/", headers=HEADERS)
        assert response.status_code == 200