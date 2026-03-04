# Stateless Chart Calculation Endpoint — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `POST /api/v1/charts/calculate-chart` endpoint that accepts birth details in the request body and returns a Vedic chart without saving to DB.

**Architecture:** New Pydantic request DTO with flexible time parsing and location resolution (lat/lng or place name geocoding). New route on existing chart controller. Calls `AstrologyCalculator.calculate_vedic_chart()` directly — no new service layer.

**Tech Stack:** FastAPI, Pydantic v2, pyswisseph, geopy/Nominatim, timezonefinder, pytz

---

## Task 1: Create the request DTO

**Files:**
- Create: `src/josi/api/v1/dto/chart_calculation_dto.py`
- Test: `tests/unit/api/dto/test_chart_calculation_dto.py`

**Step 1: Write failing tests for the DTO**

Create `tests/unit/api/dto/test_chart_calculation_dto.py`:

```python
"""Tests for CalculateChartRequest DTO."""
import pytest
from datetime import date, time


class TestCalculateChartRequest:
    """Test the request body validation."""

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
        assert req.house_system == "placidus"
        assert req.ayanamsa == "lahiri"
```

**Step 2: Run tests to verify they fail**

Run: `poetry run pytest tests/unit/api/dto/test_chart_calculation_dto.py -v --no-cov`
Expected: FAIL — `ModuleNotFoundError: No module named 'josi.api.v1.dto.chart_calculation_dto'`

**Step 3: Implement the DTO**

Create `src/josi/api/v1/dto/chart_calculation_dto.py`:

```python
"""Request DTO for stateless chart calculation."""
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re

from josi.models.chart_model import HouseSystem, Ayanamsa


class CalculateChartRequest(BaseModel):
    """Request body for POST /api/v1/charts/calculate-chart."""

    date_of_birth: date
    time_of_birth: str = Field(
        description="Birth time: HH:MM, HH:MM:SS, or HH:MM AM/PM"
    )
    place_of_birth: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    house_system: str = Field(default="placidus")
    ayanamsa: str = Field(default="lahiri")

    # Populated by validator — not part of the JSON input
    parsed_time: Optional[time] = Field(default=None, exclude=True)

    @field_validator("time_of_birth")
    @classmethod
    def validate_time(cls, v: str) -> str:
        """Validate that time_of_birth is parseable."""
        cls._parse_time(v)  # raises ValueError if invalid
        return v

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @model_validator(mode="after")
    def validate_location(self):
        """Ensure either place_of_birth or lat/lng is provided."""
        has_place = self.place_of_birth is not None
        has_lat = self.latitude is not None
        has_lng = self.longitude is not None

        if has_lat != has_lng:
            raise ValueError("Must provide both latitude and longitude, not just one")
        if not has_place and not has_lat:
            raise ValueError(
                "Must provide place_of_birth or latitude + longitude"
            )

        # Parse and store the time object
        self.parsed_time = self._parse_time(self.time_of_birth)
        return self

    @staticmethod
    def _parse_time(v: str) -> time:
        """Parse flexible time string into a time object."""
        v = v.strip()

        # AM/PM format
        match = re.match(
            r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)$", v
        )
        if match:
            hour, minute, second, period = match.groups()
            hour, minute = int(hour), int(minute)
            second = int(second) if second else 0
            if period.upper() == "PM" and hour != 12:
                hour += 12
            elif period.upper() == "AM" and hour == 12:
                hour = 0
            return time(hour, minute, second)

        # 24-hour format
        match = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", v)
        if match:
            hour, minute, second = match.groups()
            hour, minute = int(hour), int(minute)
            second = int(second) if second else 0
            if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                return time(hour, minute, second)

        raise ValueError(
            f"Invalid time format: {v}. Use HH:MM, HH:MM:SS, or HH:MM AM/PM"
        )
```

**Step 4: Run tests to verify they pass**

Run: `poetry run pytest tests/unit/api/dto/test_chart_calculation_dto.py -v --no-cov`
Expected: All 9 tests PASS

**Step 5: Commit**

```bash
git add src/josi/api/v1/dto/chart_calculation_dto.py tests/unit/api/dto/test_chart_calculation_dto.py
git commit -m "feat: add CalculateChartRequest DTO with flexible time parsing"
```

---

## Task 2: Add the controller route

**Files:**
- Modify: `src/josi/api/v1/controllers/chart_controller.py` (add route after line 103)
- Test: `tests/unit/api/controllers/test_calculate_chart_endpoint.py`

**Step 1: Write failing test for the endpoint**

Create `tests/unit/api/controllers/test_calculate_chart_endpoint.py`:

```python
"""Tests for POST /api/v1/charts/calculate-chart endpoint."""
import pytest
from unittest.mock import patch, MagicMock


class TestCalculateChartEndpoint:
    """Test the stateless chart calculation endpoint."""

    @pytest.fixture
    def mock_chart_data(self):
        """Sample chart data returned by AstrologyCalculator."""
        return {
            "chart_type": "vedic",
            "ayanamsa": 24.15,
            "ayanamsa_name": "lahiri",
            "house_system": "placidus",
            "ascendant": {
                "longitude": 120.5,
                "sign": "Leo",
                "nakshatra": "Magha",
                "pada": 2,
            },
            "houses": [120.5] * 12,
            "planets": {
                "Sun": {
                    "longitude": 60.0,
                    "sign": "Gemini",
                    "nakshatra": "Mrigashira",
                    "pada": 1,
                }
            },
        }

    @pytest.mark.asyncio
    async def test_calculate_chart_with_lat_lng(self, async_client, mock_chart_data):
        """Test calculation with direct lat/lng."""
        with patch(
            "josi.services.astrology_service.AstrologyCalculator.calculate_vedic_chart",
            return_value=mock_chart_data,
        ):
            response = await async_client.post(
                "/api/v1/charts/calculate-chart",
                json={
                    "date_of_birth": "1990-06-15",
                    "time_of_birth": "14:30",
                    "latitude": 13.0827,
                    "longitude": 80.2707,
                    "timezone": "Asia/Kolkata",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["chart_type"] == "vedic"

    @pytest.mark.asyncio
    async def test_calculate_chart_with_place(self, async_client, mock_chart_data):
        """Test calculation with geocoded place name."""
        with (
            patch(
                "josi.services.astrology_service.AstrologyCalculator.calculate_vedic_chart",
                return_value=mock_chart_data,
            ),
            patch(
                "josi.services.geocoding_service.GeocodingService.get_coordinates_and_timezone",
                return_value=(13.0827, 80.2707, "Asia/Kolkata"),
            ),
        ):
            response = await async_client.post(
                "/api/v1/charts/calculate-chart",
                json={
                    "date_of_birth": "1990-06-15",
                    "time_of_birth": "2:30 PM",
                    "place_of_birth": "Chennai, India",
                },
            )
        assert response.status_code == 200
        assert response.json()["success"] is True

    @pytest.mark.asyncio
    async def test_calculate_chart_rejects_no_location(self, async_client):
        """Test 422 when no location provided."""
        response = await async_client.post(
            "/api/v1/charts/calculate-chart",
            json={
                "date_of_birth": "1990-06-15",
                "time_of_birth": "14:30",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_chart_lat_lng_priority(self, async_client, mock_chart_data):
        """When both place and lat/lng given, lat/lng takes priority (no geocoding)."""
        with patch(
            "josi.services.astrology_service.AstrologyCalculator.calculate_vedic_chart",
            return_value=mock_chart_data,
        ) as mock_calc:
            response = await async_client.post(
                "/api/v1/charts/calculate-chart",
                json={
                    "date_of_birth": "1990-06-15",
                    "time_of_birth": "14:30",
                    "place_of_birth": "Chennai, India",
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "timezone": "Asia/Kolkata",
                },
            )
        assert response.status_code == 200
        # Verify the calculator was called with the provided lat/lng, not geocoded
        call_args = mock_calc.call_args
        assert abs(call_args.kwargs.get("latitude", call_args[0][1]) - 28.6139) < 0.01
```

**Step 2: Run tests to verify they fail**

Run: `poetry run pytest tests/unit/api/controllers/test_calculate_chart_endpoint.py -v --no-cov`
Expected: FAIL — 404 (route doesn't exist yet)

**Step 3: Implement the controller route**

Add to `src/josi/api/v1/controllers/chart_controller.py` after the existing imports (line 4), add:

```python
from datetime import datetime
```

After the existing imports (line 8-10), add:

```python
from josi.api.v1.dependencies import (
    ChartServiceDep, PersonServiceDep,
    AstrologyCalculatorDep, GeocodingServiceDep
)
from josi.api.v1.dto.chart_calculation_dto import CalculateChartRequest
```

Replace the existing import of dependencies (line 8):
```python
from josi.api.v1.dependencies import ChartServiceDep, PersonServiceDep
```

Then add the new route after the existing `calculate_chart` function (after line 103):

```python
@router.post("/calculate-chart", response_model=ResponseModel)
async def calculate_chart_stateless(
    request: CalculateChartRequest,
    calculator: AstrologyCalculatorDep,
    geocoding: GeocodingServiceDep,
) -> ResponseModel:
    """
    Calculate a Vedic astrology chart from birth details (stateless).

    Accepts birth date, time, and location directly — no stored person required.
    Returns the full Vedic chart without saving to the database.

    Provide either place_of_birth (geocoded automatically) or latitude + longitude.
    If both are given, lat/lng takes priority.
    """
    # Resolve coordinates
    lat = request.latitude
    lng = request.longitude
    tz = request.timezone

    if lat is not None and lng is not None:
        # Use provided coordinates; resolve timezone if missing
        if not tz:
            try:
                tz = geocoding.get_timezone_from_coordinates(lat, lng)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
    else:
        # Geocode place name
        try:
            lat, lng, resolved_tz = geocoding.get_coordinates_and_timezone(
                city=request.place_of_birth
            )
            if not tz:
                tz = resolved_tz
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not geocode location: {str(e)}",
            )

    # Build timezone-aware datetime
    import pytz

    birth_dt = datetime.combine(request.date_of_birth, request.parsed_time)
    try:
        local_tz = pytz.timezone(tz)
        birth_dt = local_tz.localize(birth_dt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid timezone '{tz}': {str(e)}")

    # Calculate chart
    try:
        calculator.set_ayanamsa(request.ayanamsa)
        chart_data = calculator.calculate_vedic_chart(
            dt=birth_dt,
            latitude=float(lat),
            longitude=float(lng),
            timezone=tz,
            house_system=request.house_system,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Chart calculation failed: {str(e)}"
        )

    return ResponseModel(
        success=True,
        message="Vedic chart calculated successfully",
        data=chart_data,
    )
```

**Step 4: Run tests to verify they pass**

Run: `poetry run pytest tests/unit/api/controllers/test_calculate_chart_endpoint.py -v --no-cov`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add src/josi/api/v1/controllers/chart_controller.py tests/unit/api/controllers/test_calculate_chart_endpoint.py
git commit -m "feat: add stateless POST /charts/calculate-chart endpoint"
```

---

## Task 3: Manual smoke test via Docker

**Step 1: Rebuild and start**

Run: `josi redock up`

**Step 2: Test with lat/lng via curl**

```bash
curl -s -X POST http://localhost:1954/api/v1/charts/calculate-chart \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "date_of_birth": "1990-06-15",
    "time_of_birth": "2:30 PM",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": "Asia/Kolkata"
  }' | python -m json.tool | head -30
```

Expected: 200 with `{"success": true, "data": {"chart_type": "vedic", ...}}`

**Step 3: Test with place name**

```bash
curl -s -X POST http://localhost:1954/api/v1/charts/calculate-chart \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "date_of_birth": "1990-06-15",
    "time_of_birth": "14:30",
    "place_of_birth": "Chennai, India"
  }' | python -m json.tool | head -30
```

Expected: 200 with geocoded coordinates and chart data

**Step 4: Verify in Swagger UI**

Open http://localhost:1954/docs in browser. Confirm the new `POST /api/v1/charts/calculate-chart` endpoint appears under the "charts" tag with the request body schema.

**Step 5: Commit design doc**

```bash
git add docs/plans/2026-03-05-stateless-chart-endpoint-design.md
git commit -m "docs: add design doc for stateless chart endpoint"
```
