from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


class PlaceOfBirth(BaseModel):
    city: str
    state: Optional[str] = None
    country: str = "USA"


class PersonCreate(BaseModel):
    name: str
    date_of_birth: datetime
    place_of_birth: PlaceOfBirth
    time_of_birth: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "date_of_birth": "1990-01-15T00:00:00",
                "place_of_birth": {
                    "city": "New York",
                    "state": "NY",
                    "country": "USA"
                },
                "time_of_birth": "1990-01-15T14:30:00"
            }
        }


class PlanetPositionResponse(BaseModel):
    planet_name: str
    longitude: float
    latitude: float
    speed: Optional[float]
    house: Optional[int]
    sign: Optional[str]
    nakshatra: Optional[str]
    pada: Optional[int]


class AstrologyChartResponse(BaseModel):
    id: int
    person_id: int
    chart_type: str
    chart_data: Dict[str, Any]
    calculated_at: datetime
    planets: List[PlanetPositionResponse]
    
    @validator('chart_data', pre=True)
    def parse_chart_data(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        from_attributes = True


class PersonResponse(BaseModel):
    id: int
    name: str
    date_of_birth: datetime
    place_of_birth_city: str
    place_of_birth_state: Optional[str]
    place_of_birth_country: str
    latitude: float
    longitude: float
    time_of_birth: datetime
    timezone: str
    charts: List[AstrologyChartResponse]
    
    class Config:
        from_attributes = True