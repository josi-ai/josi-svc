"""
Unit tests for Geocoding service.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import pytz

from josi.services.geocoding_service import GeocodingService


class TestGeocodingService:
    """Test geocoding service functionality."""
    
    @pytest.fixture
    def geocoding_service(self):
        """Create geocoding service instance."""
        return GeocodingService()
    
    def test_get_coordinates_and_timezone_success(self, geocoding_service):
        """Test successful geocoding with coordinates and timezone."""
        # Mock the geolocator response
        mock_location = Mock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        
        with patch.object(geocoding_service.geolocator, 'geocode', return_value=mock_location):
            with patch.object(geocoding_service.tf, 'timezone_at', return_value='America/New_York'):
                lat, lon, tz = geocoding_service.get_coordinates_and_timezone(
                    city="New York",
                    state="NY",
                    country="USA"
                )
                
                assert lat == 40.7128
                assert lon == -74.0060
                assert tz == "America/New_York"
    
    def test_get_coordinates_and_timezone_location_not_found(self, geocoding_service):
        """Test geocoding when location is not found."""
        with patch.object(geocoding_service.geolocator, 'geocode', return_value=None):
            with pytest.raises(ValueError, match="Could not find location"):
                geocoding_service.get_coordinates_and_timezone(
                    city="Nonexistent City",
                    country="Nowhere"
                )
    
    def test_get_coordinates_and_timezone_no_timezone(self, geocoding_service):
        """Test geocoding when timezone cannot be determined."""
        mock_location = Mock()
        mock_location.latitude = 0.0
        mock_location.longitude = 0.0
        
        with patch.object(geocoding_service.geolocator, 'geocode', return_value=mock_location):
            with patch.object(geocoding_service.tf, 'timezone_at', return_value=None):
                with pytest.raises(ValueError, match="Could not determine timezone"):
                    geocoding_service.get_coordinates_and_timezone(
                        city="Ocean Point",
                        country="International Waters"
                    )
    
    def test_get_coordinates_and_timezone_without_state(self, geocoding_service):
        """Test geocoding without state parameter."""
        mock_location = Mock()
        mock_location.latitude = 51.5074
        mock_location.longitude = -0.1278
        
        with patch.object(geocoding_service.geolocator, 'geocode', return_value=mock_location):
            with patch.object(geocoding_service.tf, 'timezone_at', return_value='Europe/London'):
                lat, lon, tz = geocoding_service.get_coordinates_and_timezone(
                    city="London",
                    country="UK"
                )
                
                assert lat == 51.5074
                assert lon == -0.1278
                assert tz == "Europe/London"
                
                # Verify the location string was built correctly
                geocoding_service.geolocator.geocode.assert_called_with("London, UK")
    
    def test_get_timezone_valid(self, geocoding_service):
        """Test getting timezone object from valid timezone name."""
        tz = geocoding_service.get_timezone("America/New_York")
        assert isinstance(tz, pytz.tzinfo.BaseTzInfo)
        assert str(tz) == "America/New_York"
    
    def test_get_timezone_invalid(self, geocoding_service):
        """Test getting timezone object from invalid timezone name."""
        with pytest.raises(pytz.exceptions.UnknownTimeZoneError):
            geocoding_service.get_timezone("Invalid/Timezone")
    
    def test_location_string_formatting(self, geocoding_service):
        """Test location string formatting with different inputs."""
        mock_location = Mock()
        mock_location.latitude = 35.6762
        mock_location.longitude = 139.6503
        
        with patch.object(geocoding_service.geolocator, 'geocode', return_value=mock_location) as mock_geocode:
            with patch.object(geocoding_service.tf, 'timezone_at', return_value='Asia/Tokyo'):
                # With all parameters
                geocoding_service.get_coordinates_and_timezone(
                    city="Tokyo",
                    state="Tokyo Prefecture",
                    country="Japan"
                )
                mock_geocode.assert_called_with("Tokyo, Tokyo Prefecture, Japan")
                
                # Without state
                geocoding_service.get_coordinates_and_timezone(
                    city="Paris",
                    country="France"
                )
                mock_geocode.assert_called_with("Paris, France")
    
    def test_various_timezones(self, geocoding_service):
        """Test timezone detection for various global locations."""
        test_cases = [
            # (lat, lon, expected_timezone)
            (40.7128, -74.0060, "America/New_York"),
            (51.5074, -0.1278, "Europe/London"),
            (35.6762, 139.6503, "Asia/Tokyo"),
            (-33.8688, 151.2093, "Australia/Sydney"),
            (55.7558, 37.6173, "Europe/Moscow"),
            (-23.5505, -46.6333, "America/Sao_Paulo"),
        ]
        
        for lat, lon, expected_tz in test_cases:
            mock_location = Mock()
            mock_location.latitude = lat
            mock_location.longitude = lon
            
            with patch.object(geocoding_service.geolocator, 'geocode', return_value=mock_location):
                with patch.object(geocoding_service.tf, 'timezone_at', return_value=expected_tz):
                    _, _, tz = geocoding_service.get_coordinates_and_timezone(
                        city="Test City",
                        country="Test Country"
                    )
                    assert tz == expected_tz
    
    def test_edge_case_coordinates(self, geocoding_service):
        """Test edge case coordinates like poles."""
        # North Pole
        mock_location = Mock()
        mock_location.latitude = 90.0
        mock_location.longitude = 0.0
        
        with patch.object(geocoding_service.geolocator, 'geocode', return_value=mock_location):
            # TimezoneFinder might return None for poles, or UTC
            with patch.object(geocoding_service.tf, 'timezone_at', return_value='UTC'):
                lat, lon, tz = geocoding_service.get_coordinates_and_timezone(
                    city="North Pole",
                    country="Arctic"
                )
                assert lat == 90.0
                assert lon == 0.0
                assert tz == "UTC"
    
    def test_geolocator_user_agent(self, geocoding_service):
        """Test that geolocator is initialized with correct user agent."""
        assert geocoding_service.geolocator.user_agent == "josi"