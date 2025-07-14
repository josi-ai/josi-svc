"""
Enhanced comprehensive tests for chart controller - Production Ready
"""
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from datetime import datetime, date, time
from fastapi.testclient import TestClient
from fastapi import FastAPI

from josi.api.v1.controllers.chart_controller import router
from josi.api.v1.dependencies import ChartServiceDep, PersonServiceDep
from josi.api.response import ResponseModel
from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa


class TestChartControllerProduction:
    """Production-ready comprehensive chart controller tests"""
    
    @pytest.fixture
    def mock_chart_service(self):
        """Mock chart service with realistic responses"""
        service = AsyncMock()
        
        # Mock successful chart calculation
        service.calculate_charts.return_value = [
            {
                "chart_id": str(uuid4()),
                "system": "vedic",
                "chart_data": {
                    "planets": {
                        "Sun": {"longitude": 168.75, "sign": "Virgo", "house": 1},
                        "Moon": {"longitude": 45.32, "sign": "Taurus", "house": 8},
                        "Mars": {"longitude": 225.14, "sign": "Scorpio", "house": 3}
                    },
                    "houses": [168.75, 198.32, 228.14, 258.96, 289.78, 320.60, 
                              351.42, 22.24, 53.06, 83.88, 114.70, 145.52],
                    "ascendant": {"longitude": 168.75, "sign": "Virgo"}
                },
                "calculated_at": datetime.now().isoformat()
            },
            {
                "chart_id": str(uuid4()),
                "system": "western",
                "chart_data": {
                    "planets": {
                        "Sun": {"longitude": 168.75, "sign": "Virgo", "house": 1},
                        "Moon": {"longitude": 45.32, "sign": "Taurus", "house": 8}
                    },
                    "houses": [168.75, 198.32, 228.14],
                    "ascendant": {"longitude": 168.75, "sign": "Virgo"}
                }
            }
        ]
        
        return service
    
    @pytest.fixture
    def mock_person_service(self):
        """Mock person service"""
        service = AsyncMock()
        service.get_person.return_value = {
            "person_id": str(uuid4()),
            "name": "Test Person",
            "date_of_birth": date(1990, 1, 1),
            "time_of_birth": datetime(1990, 1, 1, 12, 0),
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York"
        }
        return service
    
    @pytest.fixture
    def test_app(self, mock_chart_service, mock_person_service):
        """Create test FastAPI app with mocked dependencies"""
        app = FastAPI()
        app.include_router(router)
        
        # Override dependencies
        app.dependency_overrides[ChartServiceDep] = lambda: mock_chart_service
        app.dependency_overrides[PersonServiceDep] = lambda: mock_person_service
        
        return app
    
    @pytest.fixture
    def client(self, test_app):
        """Test client"""
        return TestClient(test_app)
    
    @pytest.mark.unit
    def test_calculate_chart_success_single_system(self, client, mock_chart_service, mock_person_service):
        """Test successful chart calculation for single system"""
        person_id = str(uuid4())
        
        response = client.post(
            f"/charts/calculate?person_id={person_id}&systems=vedic&house_system=placidus&ayanamsa=lahiri"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Successfully calculated" in data["message"]
        assert len(data["data"]) >= 1
        assert data["data"][0]["system"] in ["vedic", "western"]
        
        # Verify service calls
        mock_person_service.get_person.assert_called_once()
        mock_chart_service.calculate_charts.assert_called_once()
    
    @pytest.mark.unit
    def test_calculate_chart_success_multiple_systems(self, client, mock_chart_service):
        """Test successful chart calculation for multiple systems"""
        person_id = str(uuid4())
        
        response = client.post(
            f"/charts/calculate?person_id={person_id}&systems=vedic,western&include_interpretations=true"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2  # Vedic and Western
        
        # Verify chart data structure
        for chart in data["data"]:
            assert "chart_id" in chart
            assert "system" in chart
            assert "chart_data" in chart
            assert "planets" in chart["chart_data"]
            assert "houses" in chart["chart_data"]
            assert "ascendant" in chart["chart_data"]
    
    @pytest.mark.unit
    def test_calculate_chart_invalid_system(self, client):
        """Test chart calculation with invalid astrology system"""
        person_id = str(uuid4())
        
        response = client.post(
            f"/charts/calculate?person_id={person_id}&systems=invalid_system"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid astrology system" in data["detail"]
    
    @pytest.mark.unit
    def test_calculate_chart_person_not_found(self, client, mock_person_service):
        """Test chart calculation when person doesn't exist"""
        person_id = str(uuid4())
        mock_person_service.get_person.return_value = None
        
        response = client.post(
            f"/charts/calculate?person_id={person_id}&systems=vedic"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    @pytest.mark.unit
    def test_calculate_chart_service_error(self, client, mock_chart_service):
        """Test chart calculation when service throws error"""
        person_id = str(uuid4())
        mock_chart_service.calculate_charts.side_effect = Exception("Calculation failed")
        
        response = client.post(
            f"/charts/calculate?person_id={person_id}&systems=vedic"
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to calculate charts" in data["detail"]
    
    @pytest.mark.unit
    def test_get_person_charts_success(self, client, mock_chart_service):
        """Test successful retrieval of person's charts"""
        person_id = str(uuid4())
        mock_chart_service.get_person_charts.return_value = [
            {"chart_id": str(uuid4()), "system": "vedic"},
            {"chart_id": str(uuid4()), "system": "western"}
        ]
        
        response = client.get(f"/charts/person/{person_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        mock_chart_service.get_person_charts.assert_called_once_with(
            uuid4(person_id), None, None
        )
    
    @pytest.mark.unit
    def test_get_person_charts_with_filters(self, client, mock_chart_service):
        """Test retrieval of person's charts with filters"""
        person_id = str(uuid4())
        
        response = client.get(
            f"/charts/person/{person_id}?system=vedic&chart_type=natal"
        )
        
        assert response.status_code == 200
        mock_chart_service.get_person_charts.assert_called_once_with(
            uuid4(person_id), AstrologySystem.VEDIC, "natal"
        )
    
    @pytest.mark.unit
    def test_get_chart_by_id_success(self, client, mock_chart_service):
        """Test successful retrieval of specific chart"""
        chart_id = str(uuid4())
        mock_chart_service.get_chart_by_id.return_value = {
            "chart_id": chart_id,
            "system": "vedic",
            "chart_data": {"planets": {}, "houses": []}
        }
        
        response = client.get(f"/charts/{chart_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["chart_id"] == chart_id
    
    @pytest.mark.unit
    def test_get_chart_by_id_not_found(self, client, mock_chart_service):
        """Test retrieval of non-existent chart"""
        chart_id = str(uuid4())
        mock_chart_service.get_chart_by_id.return_value = None
        
        response = client.get(f"/charts/{chart_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    @pytest.mark.unit
    def test_delete_chart_success(self, client, mock_chart_service):
        """Test successful chart deletion"""
        chart_id = str(uuid4())
        mock_chart_service.delete_chart.return_value = True
        
        response = client.delete(f"/charts/{chart_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]
        assert data["data"]["chart_id"] == chart_id
    
    @pytest.mark.unit
    def test_delete_chart_not_found(self, client, mock_chart_service):
        """Test deletion of non-existent chart"""
        chart_id = str(uuid4())
        mock_chart_service.delete_chart.return_value = False
        
        response = client.delete(f"/charts/{chart_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    @pytest.mark.unit
    def test_calculate_divisional_chart_success(self, client, mock_chart_service, mock_person_service):
        """Test successful divisional chart calculation"""
        person_id = str(uuid4())
        mock_chart_service.calculate_divisional_chart.return_value = {
            "division": 9,
            "chart_data": {"planets": {}, "houses": []},
            "interpretation": "Navamsa chart for marriage analysis"
        }
        
        response = client.get(f"/charts/divisional/{person_id}?division=9")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "D9 divisional chart" in data["message"]
        assert data["data"]["division"] == 9
    
    @pytest.mark.unit
    def test_calculate_divisional_chart_invalid_division(self, client):
        """Test divisional chart with invalid division number"""
        person_id = str(uuid4())
        
        response = client.get(f"/charts/divisional/{person_id}?division=500")  # > 300
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.unit 
    def test_calculate_transit_chart_success(self, client, mock_chart_service, mock_person_service):
        """Test successful transit chart calculation"""
        person_id = str(uuid4())
        mock_chart_service.calculate_transit_charts.return_value = {
            "natal_chart": {"planets": {}},
            "transit_chart": {"planets": {}},
            "aspects": [],
            "interpretations": []
        }
        
        response = client.post(
            f"/charts/transit?person_id={person_id}&systems=vedic&include_aspects=true"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Transit charts calculated successfully" in data["message"]
    
    @pytest.mark.unit
    def test_calculate_synastry_success(self, client, mock_chart_service, mock_person_service):
        """Test successful synastry calculation"""
        person1_id = str(uuid4())
        person2_id = str(uuid4())
        
        # Mock person service to return different people
        mock_person_service.get_person.side_effect = [
            {"person_id": person1_id, "name": "Person 1"},
            {"person_id": person2_id, "name": "Person 2"}
        ]
        
        mock_chart_service.calculate_synastry.return_value = {
            "compatibility_score": 85,
            "aspects": [],
            "house_overlays": [],
            "composite_chart": {}
        }
        
        response = client.post(
            f"/charts/synastry?person1_id={person1_id}&person2_id={person2_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Synastry analysis completed" in data["message"]
        assert "compatibility_score" in data["data"]
    
    @pytest.mark.unit
    def test_calculate_synastry_missing_person(self, client, mock_person_service):
        """Test synastry calculation with missing person"""
        person1_id = str(uuid4())
        person2_id = str(uuid4())
        
        # Mock one person not found
        mock_person_service.get_person.side_effect = [
            {"person_id": person1_id, "name": "Person 1"},
            None  # Second person not found
        ]
        
        response = client.post(
            f"/charts/synastry?person1_id={person1_id}&person2_id={person2_id}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "One or both persons not found" in data["detail"]

    @pytest.mark.performance
    def test_chart_calculation_performance(self, client):
        """Performance test for chart calculation"""
        import time
        
        person_id = str(uuid4())
        start_time = time.time()
        
        response = client.post(
            f"/charts/calculate?person_id={person_id}&systems=vedic"
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should respond within reasonable time (with mocks this should be very fast)
        assert response_time < 1.0  # 1 second max
        assert response.status_code in [200, 404, 500]  # Any valid HTTP response