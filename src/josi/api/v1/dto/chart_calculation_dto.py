"""Request DTO for stateless chart calculation."""
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re


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

    parsed_time: Optional[time] = Field(default=None, exclude=True)

    @field_validator("time_of_birth")
    @classmethod
    def validate_time(cls, v: str) -> str:
        cls._parse_time(v)
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
        has_place = self.place_of_birth is not None
        has_lat = self.latitude is not None
        has_lng = self.longitude is not None

        if has_lat != has_lng:
            raise ValueError("Must provide both latitude and longitude, not just one")
        if not has_place and not has_lat:
            raise ValueError(
                "Must provide place_of_birth or latitude + longitude"
            )

        self.parsed_time = self._parse_time(self.time_of_birth)
        return self

    @staticmethod
    def _parse_time(v: str) -> time:
        v = v.strip()

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
