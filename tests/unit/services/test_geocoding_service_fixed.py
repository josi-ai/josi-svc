"""Fixed comprehensive unit tests for GeocodingService."""
import pytest
from unittest.mock import MagicMock, patch

from josi.services.geocoding_service import GeocodingService


class TestGeocodingServiceFixed:
    """Fixed comprehensive test coverage for GeocodingService."""
    
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
                
                # Verify geolocator and timezone finder were created
                mock_nominatim.assert_called_once_with(user_agent="josi")
                mock_tf.assert_called_once()
                
                assert hasattr(service, 'geolocator')
                assert hasattr(service, 'tf')
    
    def test_get_coordinates_and_timezone_success(self, geocoding_service):
        """Test successful geocoding with coordinates and timezone."""
        # Mock location result
        mock_location = MagicMock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        geocoding_service.geolocator.geocode.return_value = mock_location
        
        # Mock timezone finder
        geocoding_service.tf.timezone_at.return_value = "America/New_York"
        
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(
            city="New York",
            state="NY",
            country="USA"
        )
        
        assert lat == 40.7128
        assert lon == -74.0060
        assert tz == "America/New_York"
        
        # Verify geocode was called with full address
        geocoding_service.geolocator.geocode.assert_called_once_with("New York, NY, USA")
        geocoding_service.tf.timezone_at.assert_called_once_with(lat=40.7128, lng=-74.0060)
    
    def test_get_coordinates_and_timezone_city_only(self, geocoding_service):
        """Test geocoding with city only (defaults to USA)."""
        mock_location = MagicMock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = "America/New_York"
        
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(city="New York")
        
        assert lat == 40.7128
        assert lon == -74.0060
        assert tz == "America/New_York"
        
        # Should geocode with city and default country USA
        geocoding_service.geolocator.geocode.assert_called_once_with("New York, USA")
    
    def test_get_coordinates_and_timezone_city_state(self, geocoding_service):
        """Test geocoding with city and state."""
        mock_location = MagicMock()
        mock_location.latitude = 34.0522
        mock_location.longitude = -118.2437
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = "America/Los_Angeles"
        
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(
            city="Los Angeles",
            state="California"
        )
        
        assert lat == 34.0522
        assert lon == -118.2437
        assert tz == "America/Los_Angeles"
        
        # Defaults to USA as country
        geocoding_service.geolocator.geocode.assert_called_once_with("Los Angeles, California, USA")
    
    def test_get_coordinates_and_timezone_custom_country(self, geocoding_service):
        """Test geocoding with custom country."""
        mock_location = MagicMock()
        mock_location.latitude = 51.5074
        mock_location.longitude = -0.1278
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = "Europe/London"
        
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(
            city="London",
            country="UK"
        )
        
        assert lat == 51.5074
        assert lon == -0.1278
        assert tz == "Europe/London"
        
        geocoding_service.geolocator.geocode.assert_called_once_with("London, UK")
    
    def test_get_coordinates_and_timezone_not_found(self, geocoding_service):
        """Test geocoding when location not found."""
        geocoding_service.geolocator.geocode.return_value = None
        
        with pytest.raises(ValueError, match="Could not find location: NonexistentCity, USA"):
            geocoding_service.get_coordinates_and_timezone(city="NonexistentCity")
    
    def test_get_coordinates_and_timezone_no_timezone(self, geocoding_service):
        """Test geocoding when timezone cannot be determined."""
        mock_location = MagicMock()
        mock_location.latitude = 0.0
        mock_location.longitude = 0.0
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = None
        
        with pytest.raises(ValueError, match="Could not determine timezone for coordinates: 0.0, 0.0"):
            geocoding_service.get_coordinates_and_timezone(city="Middle of Ocean")
    
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
        with patch('josi.services.geocoding_service.pytz.timezone') as mock_timezone:
            mock_timezone.side_effect = Exception("Unknown timezone")
            
            with pytest.raises(Exception, match="Unknown timezone"):
                geocoding_service.get_timezone("Invalid/Timezone")
    
    def test_get_timezone_unknown_timezone_error(self, geocoding_service):
        """Test getting timezone with UnknownTimeZoneError."""
        import pytz
        with patch('josi.services.geocoding_service.pytz.timezone') as mock_timezone:
            mock_timezone.side_effect = pytz.exceptions.UnknownTimeZoneError("Invalid/Timezone")
            
            with pytest.raises(ValueError, match="Unknown timezone: Invalid/Timezone"):
                geocoding_service.get_timezone("Invalid/Timezone")
    
    def test_full_geocoding_flow(self, geocoding_service):
        """Test full geocoding flow from city to timezone object."""
        # Mock location
        mock_location = MagicMock()
        mock_location.latitude = 35.6762
        mock_location.longitude = 139.6503
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = "Asia/Tokyo"
        
        # Get coordinates and timezone name
        lat, lon, tz_name = geocoding_service.get_coordinates_and_timezone(
            city="Tokyo",
            country="Japan"
        )
        
        assert lat == 35.6762
        assert lon == 139.6503
        assert tz_name == "Asia/Tokyo"
        
        # Get timezone object
        with patch('josi.services.geocoding_service.pytz.timezone') as mock_timezone:
            mock_tz_object = MagicMock()
            mock_timezone.return_value = mock_tz_object
            
            tz_object = geocoding_service.get_timezone(tz_name)
            
            assert tz_object == mock_tz_object
            mock_timezone.assert_called_once_with("Asia/Tokyo")
    
    def test_geocoding_with_none_state(self, geocoding_service):
        """Test geocoding with None state parameter."""
        mock_location = MagicMock()
        mock_location.latitude = 48.8566
        mock_location.longitude = 2.3522
        geocoding_service.geolocator.geocode.return_value = mock_location
        geocoding_service.tf.timezone_at.return_value = "Europe/Paris"
        
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(
            city="Paris",
            state=None,
            country="France"
        )
        
        assert lat == 48.8566
        assert lon == 2.3522
        assert tz == "Europe/Paris"
        
        # Should not include None in location string
        geocoding_service.geolocator.geocode.assert_called_once_with("Paris, France")