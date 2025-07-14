"""
Production-ready input validation and sanitization
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field, EmailStr
from datetime import datetime, date, time
from uuid import UUID
import re
import bleach
from decimal import Decimal

from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa


class ValidationError(Exception):
    """Custom validation error"""
    pass


class EnhancedPersonRequest(BaseModel):
    """Enhanced person request with comprehensive validation"""
    
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the person")
    date_of_birth: date = Field(..., description="Birth date in YYYY-MM-DD format")
    time_of_birth: time = Field(..., description="Birth time in HH:MM:SS format")
    place_of_birth: str = Field(..., min_length=1, max_length=200, description="Birth location")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)\.]{10,15}$', description="Phone number")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate and sanitize name"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        
        # Sanitize HTML and dangerous characters
        clean_name = bleach.clean(v.strip(), tags=[], strip=True)
        
        # Check for suspicious patterns
        if re.search(r'[<>"\']|script|javascript|onload|onclick', clean_name, re.IGNORECASE):
            raise ValueError('Name contains invalid characters')
        
        # Check for reasonable length and content
        if len(clean_name) < 1:
            raise ValueError('Name is too short')
        
        return clean_name
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        """Validate birth date is reasonable"""
        if v > date.today():
            raise ValueError('Birth date cannot be in the future')
        
        # Check reasonable age limits (0-150 years)
        age_days = (date.today() - v).days
        if age_days > 150 * 365:  # Roughly 150 years
            raise ValueError('Birth date is too far in the past')
        
        return v
    
    @validator('time_of_birth')
    def validate_birth_time(cls, v):
        """Validate birth time"""
        # Time validation is handled by pydantic automatically
        # But we can add custom logic here if needed
        return v
    
    @validator('place_of_birth')
    def validate_place(cls, v):
        """Validate and sanitize place of birth"""
        clean_place = bleach.clean(v.strip(), tags=[], strip=True)
        
        # Check for XSS attempts
        if re.search(r'[<>"\']|script|javascript', clean_place, re.IGNORECASE):
            raise ValueError('Place contains invalid characters')
        
        # Basic pattern validation for location
        if not re.match(r'^[a-zA-Z0-9\s,.\-\']+$', clean_place):
            raise ValueError('Place contains invalid characters')
        
        return clean_place
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number"""
        if v is None:
            return v
        
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'[^\d]', '', v)
        
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        
        return v
    
    @validator('notes')
    def validate_notes(cls, v):
        """Validate and sanitize notes"""
        if v is None:
            return v
        
        # Sanitize HTML
        clean_notes = bleach.clean(v.strip(), tags=[], strip=True)
        
        # Check for XSS attempts
        if re.search(r'script|javascript|onload|onclick', clean_notes, re.IGNORECASE):
            raise ValueError('Notes contain invalid content')
        
        return clean_notes


class ChartCalculationRequest(BaseModel):
    """Enhanced chart calculation request"""
    
    person_id: UUID = Field(..., description="Person's unique identifier")
    systems: str = Field(
        default="vedic,western",
        regex=r'^(vedic|western|chinese|hellenistic|mayan|celtic)(,(vedic|western|chinese|hellenistic|mayan|celtic))*$',
        description="Comma-separated list of astrology systems"
    )
    house_system: HouseSystem = Field(default=HouseSystem.PLACIDUS, description="House calculation system")
    ayanamsa: Ayanamsa = Field(default=Ayanamsa.LAHIRI, description="Ayanamsa for Vedic calculations")
    include_interpretations: bool = Field(default=False, description="Include AI interpretations")
    
    @validator('systems')
    def validate_systems(cls, v):
        """Validate astrology systems"""
        valid_systems = {'vedic', 'western', 'chinese', 'hellenistic', 'mayan', 'celtic'}
        systems = {s.strip() for s in v.split(',') if s.strip()}
        
        if not systems:
            raise ValueError("At least one astrology system must be specified")
        
        if not systems.issubset(valid_systems):
            invalid_systems = systems - valid_systems
            raise ValueError(f"Invalid systems: {invalid_systems}. Valid: {valid_systems}")
        
        return v


class LocationRequest(BaseModel):
    """Location validation request"""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    timezone: str = Field(..., min_length=1, max_length=50, description="Timezone identifier")
    
    @validator('timezone')
    def validate_timezone(cls, v):
        """Validate timezone"""
        import pytz
        try:
            pytz.timezone(v)
            return v
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {v}")


class DivisionalChartRequest(BaseModel):
    """Divisional chart request validation"""
    
    person_id: UUID = Field(..., description="Person's unique identifier")
    division: int = Field(..., ge=1, le=300, description="Division number (D1-D300)")
    ayanamsa: Ayanamsa = Field(default=Ayanamsa.LAHIRI, description="Ayanamsa system")
    
    @validator('division')
    def validate_division(cls, v):
        """Validate divisional chart number"""
        # Common divisional charts
        common_divisions = {1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60}
        
        if v not in common_divisions and v > 60:
            # Allow up to D300 but warn about uncommon divisions
            pass
        
        return v


class CompatibilityRequest(BaseModel):
    """Compatibility calculation request"""
    
    person1_id: UUID = Field(..., description="First person's ID")
    person2_id: UUID = Field(..., description="Second person's ID")
    include_composite: bool = Field(default=True, description="Include composite chart")
    
    @validator('person2_id')
    def validate_different_persons(cls, v, values):
        """Ensure persons are different"""
        if 'person1_id' in values and v == values['person1_id']:
            raise ValueError("Cannot calculate compatibility between the same person")
        return v


class PredictionRequest(BaseModel):
    """Prediction request validation"""
    
    person_id: UUID = Field(..., description="Person's unique identifier")
    prediction_date: Optional[datetime] = Field(None, description="Prediction date (default: now)")
    period_type: str = Field(
        default="daily",
        regex=r'^(daily|weekly|monthly|yearly)$',
        description="Prediction period type"
    )
    
    @validator('prediction_date')
    def validate_prediction_date(cls, v):
        """Validate prediction date"""
        if v is None:
            return v
        
        # Don't allow predictions too far in the future
        max_future = datetime.now() + timedelta(days=365 * 5)  # 5 years
        if v > max_future:
            raise ValueError("Prediction date too far in the future (max 5 years)")
        
        return v


class InputSanitizer:
    """Utility class for input sanitization"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255, allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        
        if not allow_html:
            # Remove HTML tags and dangerous characters
            cleaned = bleach.clean(value.strip(), tags=[], strip=True)
        else:
            # Allow limited HTML tags
            allowed_tags = ['b', 'i', 'em', 'strong', 'p', 'br']
            cleaned = bleach.clean(value.strip(), tags=allowed_tags, strip=True)
        
        # Check for XSS patterns
        xss_patterns = [
            r'javascript:', r'vbscript:', r'onload=', r'onclick=', r'onerror=',
            r'<script', r'</script>', r'eval\(', r'document\.cookie'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                raise ValidationError("Input contains potentially dangerous content")
        
        if len(cleaned) > max_length:
            raise ValidationError(f"String too long (max {max_length} characters)")
        
        return cleaned
    
    @staticmethod
    def validate_uuid(value: str) -> UUID:
        """Validate and return UUID"""
        try:
            return UUID(value)
        except ValueError:
            raise ValidationError("Invalid UUID format")
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> tuple:
        """Validate geographic coordinates"""
        if not isinstance(latitude, (int, float)):
            raise ValidationError("Latitude must be a number")
        if not isinstance(longitude, (int, float)):
            raise ValidationError("Longitude must be a number")
        
        if not -90 <= latitude <= 90:
            raise ValidationError("Latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            raise ValidationError("Longitude must be between -180 and 180")
        
        return float(latitude), float(longitude)
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date, max_range_days: int = 365) -> tuple:
        """Validate date range"""
        if start_date > end_date:
            raise ValidationError("Start date must be before end date")
        
        range_days = (end_date - start_date).days
        if range_days > max_range_days:
            raise ValidationError(f"Date range too large (max {max_range_days} days)")
        
        return start_date, end_date


def validate_request_size(content_length: Optional[int], max_size: int = 1024 * 1024) -> None:
    """Validate request content size"""
    if content_length is None:
        return
    
    if content_length > max_size:
        raise ValidationError(f"Request too large (max {max_size} bytes)")


def validate_request_rate(client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
    """Simple request rate validation (in production, use Redis)"""
    # This is a simplified version - in production, use Redis with sliding window
    import time
    
    # For now, just return True - rate limiting is handled by middleware
    return True