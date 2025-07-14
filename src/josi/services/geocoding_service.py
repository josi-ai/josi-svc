from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from typing import Tuple, Optional


class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="josi")
        self.tf = TimezoneFinder()
    
    def get_coordinates_and_timezone(
        self, 
        city: str, 
        state: Optional[str] = None, 
        country: str = "USA"
    ) -> Tuple[float, float, str]:
        """
        Get latitude, longitude, and timezone for a given location.
        
        Args:
            city: City name
            state: State/Province name (optional)
            country: Country name
            
        Returns:
            Tuple of (latitude, longitude, timezone_name)
        """
        location_parts = [city]
        if state:
            location_parts.append(state)
        location_parts.append(country)
        
        location_string = ", ".join(location_parts)
        
        location = self.geolocator.geocode(location_string)
        if not location:
            raise ValueError(f"Could not find location: {location_string}")
        
        latitude = location.latitude
        longitude = location.longitude
        
        timezone_name = self.tf.timezone_at(lat=latitude, lng=longitude)
        if not timezone_name:
            raise ValueError(f"Could not determine timezone for coordinates: {latitude}, {longitude}")
        
        return latitude, longitude, timezone_name
    
    def get_timezone(self, timezone_name: str):
        """Get pytz timezone object from timezone name."""
        try:
            return pytz.timezone(timezone_name)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {timezone_name}")
    
    def get_timezone_from_coordinates(self, latitude: float, longitude: float) -> str:
        """Get timezone name from coordinates."""
        timezone_name = self.tf.timezone_at(lat=latitude, lng=longitude)
        if not timezone_name:
            raise ValueError(f"Could not determine timezone for coordinates: {latitude}, {longitude}")
        return timezone_name