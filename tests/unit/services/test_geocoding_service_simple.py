"""Simple unit tests for Geocoding service."""
import pytest
from unittest.mock import MagicMock, patch, Mock
import sys

# Mock external dependencies
sys.modules['geopy'] = Mock()
sys.modules['geopy.geocoders'] = Mock()
sys.modules['timezonefinder'] = Mock()
sys.modules['pytz'] = Mock()

from josi.services.geocoding_service import GeocodingService


class TestGeocodingServiceSimple:
    """Simple test coverage for GeocodingService."""
    
    @pytest.fixture
    def geocoding_service(self):
        """Create a GeocodingService instance."""
        with patch('josi.services.geocoding_service.Nominatim'):
            with patch('josi.services.geocoding_service.TimezoneFinder'):
                return GeocodingService()
    
    def test_initialization(self):
        """Test GeocodingService initialization."""
        with patch('josi.services.geocoding_service.Nominatim') as mock_nominatim:
            with patch('josi.services.geocoding_service.TimezoneFinder') as mock_tf:
                service = GeocodingService()
                
                mock_nominatim.assert_called_once_with(user_agent="astrow")
                mock_tf.assert_called_once()
                assert hasattr(service, 'geolocator')
                assert hasattr(service, 'tf')
    
    def test_get_coordinates_and_timezone_success(self, geocoding_service):
        """Test successful geocoding."""
        mock_location = MagicMock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = "America/New_York"
        
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(
            city="New York",
            state="NY",
            country="USA"
        )
        
        assert lat == 40.7128
        assert lon == -74.0060
        assert tz == "America/New_York"
        
        geocoding_service.geolocator.geocode.assert_called_once_with("New York, NY, USA")
        geocoding_service.tf.timezone_at.assert_called_once_with(lat=40.7128, lng=-74.0060)
    
    def test_get_coordinates_and_timezone_not_found(self, geocoding_service):
        """Test geocoding when location not found."""
        geocoding_service.geolocator.geocode.return_value = None
        
        with pytest.raises(ValueError, match="Could not find location"):
            geocoding_service.get_coordinates_and_timezone(city="NonexistentCity")
    
    def test_get_coordinates_and_timezone_no_timezone(self, geocoding_service):
        """Test geocoding when timezone cannot be determined."""
        mock_location = MagicMock()
        mock_location.latitude = 0.0
        mock_location.longitude = 0.0
        
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = None
        
        with pytest.raises(ValueError, match="Could not determine timezone"):
            geocoding_service.get_coordinates_and_timezone(city="Middle of Ocean")
    
    def test_get_coordinates_and_timezone_city_only(self, geocoding_service):
        """Test geocoding with city only."""
        mock_location = MagicMock()
        mock_location.latitude = 51.5074
        mock_location.longitude = -0.1278
        
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = "Europe/London"
        
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(city="London")
        
        assert lat == 51.5074
        assert lon == -0.1278
        assert tz == "Europe/London"
        
        geocoding_service.geolocator.geocode.assert_called_once_with("London, USA")
    
    def test_get_timezone_valid(self, geocoding_service):
        """Test getting valid timezone object."""
        with patch('josi.services.geocoding_service.pytz.timezone') as mock_timezone:
            mock_tz = MagicMock()
            mock_timezone.return_value = mock_tz
            
            result = geocoding_service.get_timezone("America/New_York")
            
            assert result == mock_tz
            mock_timezone.assert_called_once_with("America/New_York")
    
    def test_get_timezone_invalid(self, geocoding_service):
        """Test getting invalid timezone."""
        import pytz
        with patch('josi.services.geocoding_service.pytz.timezone') as mock_timezone:
            mock_timezone.side_effect = pytz.exceptions.UnknownTimeZoneError("Invalid/Timezone")
            
            with pytest.raises(ValueError, match="Unknown timezone: Invalid/Timezone"):
                geocoding_service.get_timezone("Invalid/Timezone")