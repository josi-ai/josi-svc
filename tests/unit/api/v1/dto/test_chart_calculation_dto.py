"""Tests for CalculateChartRequest DTO."""
import pytest
from datetime import date, time


class TestCalculateChartRequest:

    def test_valid_request_with_lat_lng(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        req = CalculateChartRequest(
            date_of_birth="1990-06-15",
            time_of_birth="14:30",
            latitude=13.0827,
            longitude=80.2707,
            timezone="Asia/Kolkata",
        )
        assert req.date_of_birth == date(1990, 6, 15)
        assert req.parsed_time == time(14, 30)
        assert req.latitude == 13.0827
        assert req.longitude == 80.2707

    def test_valid_request_with_place(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        req = CalculateChartRequest(
            date_of_birth="1990-06-15",
            time_of_birth="2:30 PM",
            place_of_birth="Chennai, India",
        )
        assert req.place_of_birth == "Chennai, India"
        assert req.parsed_time == time(14, 30)

    def test_time_parsing_24h(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        req = CalculateChartRequest(
            date_of_birth="2000-01-01",
            time_of_birth="23:45:30",
            latitude=0.0,
            longitude=0.0,
        )
        assert req.parsed_time == time(23, 45, 30)

    def test_time_parsing_12h_am(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        req = CalculateChartRequest(
            date_of_birth="2000-01-01",
            time_of_birth="12:00 AM",
            latitude=0.0,
            longitude=0.0,
        )
        assert req.parsed_time == time(0, 0)

    def test_rejects_no_location(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        with pytest.raises(ValueError, match="place_of_birth.*latitude.*longitude"):
            CalculateChartRequest(
                date_of_birth="1990-06-15",
                time_of_birth="14:30",
            )

    def test_rejects_partial_lat_lng(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        with pytest.raises(ValueError, match="both latitude and longitude"):
            CalculateChartRequest(
                date_of_birth="1990-06-15",
                time_of_birth="14:30",
                latitude=13.0,
            )

    def test_rejects_invalid_latitude(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        with pytest.raises(ValueError, match="between -90 and 90"):
            CalculateChartRequest(
                date_of_birth="1990-06-15",
                time_of_birth="14:30",
                latitude=100.0,
                longitude=80.0,
            )

    def test_rejects_invalid_time(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        with pytest.raises(ValueError, match="Invalid time format"):
            CalculateChartRequest(
                date_of_birth="1990-06-15",
                time_of_birth="not-a-time",
                latitude=13.0,
                longitude=80.0,
            )

    def test_defaults(self):
        from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
        req = CalculateChartRequest(
            date_of_birth="1990-06-15",
            time_of_birth="14:30",
            latitude=13.0,
            longitude=80.0,
        )
        assert req.house_system == "porphyry"
        assert req.ayanamsa == "lahiri"
