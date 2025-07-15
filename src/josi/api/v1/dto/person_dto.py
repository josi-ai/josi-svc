"""
Data Transfer Objects for Person API.
"""
from datetime import datetime, date, time
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal
import re


class CreatePersonRequest(BaseModel):
    """Request model for creating a person with flexible time input."""
    
    # Basic Information
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Birth Information
    date_of_birth: date
    time_of_birth: Union[str, time] = Field(
        description="Birth time in format: HH:MM, HH:MM:SS, HH:MM AM/PM, or time object"
    )
    place_of_birth: str
    
    # Location coordinates (optional - will be geocoded if not provided)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    timezone: Optional[str] = None
    
    # Additional Information
    gender: Optional[str] = None
    birth_certificate_id: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator('time_of_birth', mode='before')
    @classmethod
    def parse_time_of_birth(cls, v):
        """Parse various time formats into a time object."""
        if isinstance(v, time):
            return v
            
        if isinstance(v, str):
            # Remove extra whitespace
            v = v.strip()
            
            # Try parsing AM/PM format (e.g., "2:30 PM", "02:30 PM")
            am_pm_pattern = r'^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)$'
            match = re.match(am_pm_pattern, v)
            if match:
                hour, minute, second, period = match.groups()
                hour = int(hour)
                minute = int(minute)
                second = int(second) if second else 0
                
                # Convert to 24-hour format
                if period.upper() == 'PM' and hour != 12:
                    hour += 12
                elif period.upper() == 'AM' and hour == 12:
                    hour = 0
                    
                return time(hour, minute, second)
            
            # Try parsing 24-hour format (e.g., "14:30", "14:30:00")
            time_24h_pattern = r'^(\d{1,2}):(\d{2})(?::(\d{2}))?$'
            match = re.match(time_24h_pattern, v)
            if match:
                hour, minute, second = match.groups()
                hour = int(hour)
                minute = int(minute)
                second = int(second) if second else 0
                
                if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                    return time(hour, minute, second)
            
            raise ValueError(f"Invalid time format: {v}. Use HH:MM, HH:MM:SS, or HH:MM AM/PM")
        
        raise ValueError(f"time_of_birth must be a string or time object, got {type(v)}")
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if v is not None:
            lat_val = float(v)
            if not -90 <= lat_val <= 90:
                raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if v is not None:
            lon_val = float(v)
            if not -180 <= lon_val <= 180:
                raise ValueError('Longitude must be between -180 and 180')
        return v
    
    def to_person_entity(self):
        """Convert to PersonEntity with combined datetime."""
        from josi.models.person_model import PersonEntity
        
        # Combine date and time into datetime
        time_obj = self.time_of_birth if isinstance(self.time_of_birth, time) else time.fromisoformat(self.time_of_birth)
        combined_datetime = datetime.combine(self.date_of_birth, time_obj)
        
        return PersonEntity(
            name=self.name,
            email=self.email,
            phone=self.phone,
            date_of_birth=self.date_of_birth,
            time_of_birth=combined_datetime,
            place_of_birth=self.place_of_birth,
            latitude=self.latitude or Decimal('0'),  # Will be geocoded
            longitude=self.longitude or Decimal('0'),  # Will be geocoded
            timezone=self.timezone or 'UTC',  # Will be determined
            gender=self.gender,
            birth_certificate_id=self.birth_certificate_id,
            notes=self.notes
        )