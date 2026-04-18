"""
Data Transfer Objects for Person API.
"""
from datetime import datetime, date, time
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal

from josi.api.v1.dto.validators import parse_birth_time


class CreatePersonRequest(BaseModel):
    """Request model for creating a person with flexible time input."""

    # Basic Information
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

    # Birth Information
    date_of_birth: date
    time_of_birth: Optional[Union[str, time]] = Field(
        default=None,
        description="Birth time in format: HH:MM, HH:MM:SS, HH:MM AM/PM, or time object"
    )
    place_of_birth: Optional[str] = None

    # Location coordinates (optional - will be geocoded if not provided)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    timezone: Optional[str] = None

    # Additional Information
    gender: Optional[str] = None
    birth_certificate_id: Optional[str] = None
    notes: Optional[str] = None
    is_default: Optional[bool] = False

    @field_validator('time_of_birth', mode='before')
    @classmethod
    def parse_time_of_birth(cls, v):
        """Parse various time formats into a time object."""
        if v is None:
            return None
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            return parse_birth_time(v)
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
        
        # Combine date and time into datetime (if time is provided)
        combined_datetime = None
        if self.time_of_birth is not None:
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
            notes=self.notes,
            is_default=self.is_default or False,
        )


class UpdatePersonRequest(BaseModel):
    """Request model for updating a person with flexible time input.
    
    All fields are optional - only provided fields will be updated.
    """

    # Basic Information
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    # Birth Information
    date_of_birth: Optional[date] = None
    time_of_birth: Optional[Union[str, time]] = Field(
        default=None,
        description="Birth time in format: HH:MM, HH:MM:SS, HH:MM AM/PM, or time object"
    )
    place_of_birth: Optional[str] = None

    # Location coordinates
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    timezone: Optional[str] = None

    # Additional Information
    gender: Optional[str] = None
    is_default: Optional[bool] = None
    birth_certificate_id: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('time_of_birth', mode='before')
    @classmethod
    def parse_time_of_birth(cls, v):
        """Parse various time formats into a time object."""
        if v is None:
            return None
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            return parse_birth_time(v)
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

    def to_update_dict(self, existing_date_of_birth: Optional[date] = None) -> dict:
        """Convert to a dict suitable for updating, combining date + time into datetime."""
        data = self.model_dump(exclude_unset=True)

        # If time_of_birth was provided, combine with date to produce a datetime
        if 'time_of_birth' in data and data['time_of_birth'] is not None:
            time_obj = data['time_of_birth']
            if isinstance(time_obj, str):
                time_obj = time.fromisoformat(time_obj)
            # Use newly provided date_of_birth, else fall back to existing
            dob = data.get('date_of_birth') or existing_date_of_birth
            if dob:
                data['time_of_birth'] = datetime.combine(dob, time_obj)
            else:
                # Store as a datetime on epoch date as a fallback
                data['time_of_birth'] = datetime.combine(date(1970, 1, 1), time_obj)

        return data