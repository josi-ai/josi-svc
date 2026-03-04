"""Request DTO for stateless chart calculation."""
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from josi.models.chart_model import HouseSystem, Ayanamsa
from josi.api.v1.dto.validators import parse_birth_time


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
    house_system: HouseSystem = Field(default=HouseSystem.PORPHYRY)
    ayanamsa: Ayanamsa = Field(default=Ayanamsa.LAHIRI)

    @field_validator("time_of_birth")
    @classmethod
    def validate_time(cls, v: str) -> str:
        parse_birth_time(v)  # raises ValueError if format is invalid
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
        return self

    @property
    def parsed_time(self) -> time:
        """Parse time_of_birth on access (already validated by field_validator)."""
        return parse_birth_time(self.time_of_birth)
