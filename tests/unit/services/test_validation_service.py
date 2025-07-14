"""Comprehensive unit tests for validation service."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import math

from josi.services.validation_service import AstrologyValidator, AccuracyImprover


class TestAstrologyValidator:
    """Comprehensive test coverage for AstrologyValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create AstrologyValidator instance."""
        return AstrologyValidator()
    
    @pytest.fixture
    def sample_calculated_position(self):
        """Sample calculated planet position."""
        return {
            'longitude': 123.456,
            'latitude': 1.234,
            'speed': 0.987
        }
    
    @pytest.fixture
    def sample_reference_position(self):
        """Sample reference planet position."""
        return {
            'longitude': 123.460,
            'latitude': 1.235,
            'speed': 0.988
        }
    
    def test_initialization(self, validator):
        """Test AstrologyValidator initialization."""
        assert hasattr(validator, 'tolerance')
        assert validator.tolerance['longitude'] == 0.01
        assert validator.tolerance['latitude'] == 0.01
        assert validator.tolerance['speed'] == 0.001
    
    def test_validate_with_horizons(self, validator):
        """Test validate_with_horizons placeholder method."""
        # This method is currently a placeholder
        result = validator.validate_with_horizons(
            planet="Mars",
            dt=datetime(2024, 1, 1),
            latitude=40.0,
            longitude=-74.0
        )
        assert result is None  # Currently returns None (pass statement)
    
    def test_validate_planet_position_within_tolerance(self, validator, sample_calculated_position, sample_reference_position):
        """Test planet position validation within tolerance."""
        result = validator.validate_planet_position(
            calculated=sample_calculated_position,
            reference=sample_reference_position
        )
        
        assert result['valid'] is True
        assert len(result['warnings']) == 1  # Speed warning expected
        assert 'longitude' in result['differences']
        assert result['differences']['longitude'] == pytest.approx(0.004, abs=1e-6)
        assert result['differences']['latitude'] == pytest.approx(0.001, abs=1e-6)
        assert result['differences']['speed'] == pytest.approx(0.001, abs=1e-6)
    
    def test_validate_planet_position_longitude_exceeds_tolerance(self, validator):
        """Test validation when longitude difference exceeds tolerance."""
        calculated = {'longitude': 123.456, 'latitude': 1.234, 'speed': 0.987}
        reference = {'longitude': 123.500, 'latitude': 1.234, 'speed': 0.987}
        
        result = validator.validate_planet_position(calculated, reference)
        
        assert result['valid'] is False
        assert len(result['warnings']) == 1
        assert "Longitude difference" in result['warnings'][0]
        assert result['differences']['longitude'] == pytest.approx(0.044, abs=1e-6)
    
    def test_validate_planet_position_latitude_exceeds_tolerance(self, validator):
        """Test validation when latitude difference exceeds tolerance."""
        calculated = {'longitude': 123.456, 'latitude': 1.234, 'speed': 0.987}
        reference = {'longitude': 123.456, 'latitude': 1.250, 'speed': 0.987}
        
        result = validator.validate_planet_position(calculated, reference)
        
        assert result['valid'] is False
        assert len(result['warnings']) == 1
        assert "Latitude difference" in result['warnings'][0]
        assert result['differences']['latitude'] == pytest.approx(0.016, abs=1e-6)
    
    def test_validate_planet_position_speed_exceeds_tolerance(self, validator):
        """Test validation when speed difference exceeds tolerance."""
        calculated = {'longitude': 123.456, 'latitude': 1.234, 'speed': 0.987}
        reference = {'longitude': 123.456, 'latitude': 1.234, 'speed': 0.990}
        
        result = validator.validate_planet_position(calculated, reference)
        
        assert result['valid'] is True  # Speed only generates warnings
        assert len(result['warnings']) == 1
        assert "Speed difference" in result['warnings'][0]
        assert result['differences']['speed'] == pytest.approx(0.003, abs=1e-6)
    
    def test_validate_planet_position_wrap_around(self, validator):
        """Test validation with 360-degree wrap-around."""
        calculated = {'longitude': 359.5, 'latitude': 1.234, 'speed': 0.987}
        reference = {'longitude': 0.5, 'latitude': 1.234, 'speed': 0.987}
        
        result = validator.validate_planet_position(calculated, reference)
        
        assert result['valid'] is False  # 1 degree still exceeds 0.01 tolerance
        assert result['differences']['longitude'] == pytest.approx(1.0, abs=1e-6)
    
    def test_validate_planet_position_no_latitude_in_reference(self, validator):
        """Test validation when reference has no latitude."""
        calculated = {'longitude': 123.456, 'latitude': 1.234, 'speed': 0.987}
        reference = {'longitude': 123.456}
        
        result = validator.validate_planet_position(calculated, reference)
        
        assert result['valid'] is True
        assert 'latitude' not in result['differences']
    
    def test_validate_planet_position_no_speed(self, validator):
        """Test validation when speed is missing."""
        calculated = {'longitude': 123.456, 'latitude': 1.234}
        reference = {'longitude': 123.456, 'latitude': 1.234}
        
        result = validator.validate_planet_position(calculated, reference)
        
        assert result['valid'] is True
        assert 'speed' not in result['differences']
    
    def test_validate_ayanamsa_lahiri(self, validator):
        """Test ayanamsa validation for Lahiri system."""
        dt = datetime(2024, 1, 1)
        calculated = 24.12  # Approximate value for 2024
        
        result = validator.validate_ayanamsa(calculated, 'lahiri', dt)
        
        assert isinstance(result['valid'], bool)
        assert 'expected' in result
        assert 'calculated' in result
        assert 'difference' in result
        assert result['difference'] < 0.2  # Should be reasonably close
    
    def test_validate_ayanamsa_krishnamurti(self, validator):
        """Test ayanamsa validation for Krishnamurti system."""
        dt = datetime(2000, 1, 1)
        calculated = 23.73
        
        result = validator.validate_ayanamsa(calculated, 'krishnamurti', dt)
        
        assert result['valid'] is True
        assert result['difference'] < 0.1
    
    def test_validate_ayanamsa_raman(self, validator):
        """Test ayanamsa validation for Raman system."""
        dt = datetime(2010, 6, 15)
        calculated = 22.50  # Approximate value
        
        result = validator.validate_ayanamsa(calculated, 'raman', dt)
        
        assert 'expected' in result
        assert 'calculated' in result
        assert result['calculated'] == calculated
    
    def test_validate_ayanamsa_fagan_bradley(self, validator):
        """Test ayanamsa validation for Fagan-Bradley system."""
        dt = datetime(2020, 12, 31)
        calculated = 25.02  # Approximate value
        
        result = validator.validate_ayanamsa(calculated, 'fagan_bradley', dt)
        
        assert isinstance(result['valid'], bool)
        assert result['expected'] > 24.74  # Should be greater than 2000 value
    
    def test_validate_ayanamsa_unknown_system(self, validator):
        """Test ayanamsa validation with unknown system."""
        dt = datetime(2024, 1, 1)
        calculated = 24.0
        
        result = validator.validate_ayanamsa(calculated, 'unknown_system', dt)
        
        # Should default to Lahiri
        assert 'expected' in result
        assert result['expected'] > 23.85
    
    def test_validate_ayanamsa_edge_dates(self, validator):
        """Test ayanamsa validation with various dates."""
        # Past date
        dt_past = datetime(1950, 1, 1)
        result_past = validator.validate_ayanamsa(22.0, 'lahiri', dt_past)
        assert result_past['expected'] < 23.85  # Should be less than 2000 value
        
        # Future date
        dt_future = datetime(2050, 1, 1)
        result_future = validator.validate_ayanamsa(25.0, 'lahiri', dt_future)
        assert result_future['expected'] > 23.85  # Should be greater than 2000 value


class TestAccuracyImprover:
    """Comprehensive test coverage for AccuracyImprover."""
    
    def test_apply_aberration_correction(self):
        """Test aberration of light correction."""
        longitude = 123.456
        speed = 1.0
        
        corrected = AccuracyImprover.apply_aberration_correction(longitude, speed)
        
        # Check that correction was applied
        assert corrected != longitude
        assert corrected < longitude  # Correction should subtract
        
        # Test with different speeds
        corrected_slow = AccuracyImprover.apply_aberration_correction(longitude, 0.1)
        corrected_fast = AccuracyImprover.apply_aberration_correction(longitude, 2.0)
        
        assert corrected_slow != corrected_fast
    
    def test_apply_aberration_correction_zero_speed(self):
        """Test aberration correction with zero speed."""
        longitude = 180.0
        speed = 0.0
        
        corrected = AccuracyImprover.apply_aberration_correction(longitude, speed)
        
        # With zero speed, correction should still apply base aberration
        assert corrected != longitude
        aberration_degrees = 20.49552 / 3600
        expected = longitude - aberration_degrees
        assert corrected == pytest.approx(expected, abs=1e-6)
    
    def test_apply_nutation_correction(self):
        """Test nutation correction."""
        longitude = 100.0
        obliquity = 23.45
        nutation_long = 0.005
        nutation_obl = 0.002
        
        corrected = AccuracyImprover.apply_nutation_correction(
            longitude, obliquity, nutation_long, nutation_obl
        )
        
        # Simple implementation just adds nutation in longitude
        assert corrected == longitude + nutation_long
    
    def test_apply_nutation_correction_negative(self):
        """Test nutation correction with negative values."""
        longitude = 200.0
        obliquity = 23.45
        nutation_long = -0.008
        nutation_obl = -0.003
        
        corrected = AccuracyImprover.apply_nutation_correction(
            longitude, obliquity, nutation_long, nutation_obl
        )
        
        assert corrected == longitude + nutation_long
        assert corrected < longitude
    
    def test_calculate_topocentric_position_without_distance(self):
        """Test topocentric calculation without distance."""
        geocentric_pos = {
            'longitude': 123.456,
            'latitude': 5.678,
            'speed': 0.987
        }
        observer_lat = 40.0
        observer_lon = -74.0
        
        topocentric = AccuracyImprover.calculate_topocentric_position(
            geocentric_pos, observer_lat, observer_lon
        )
        
        # Without distance, no parallax correction applied
        assert topocentric['longitude'] == geocentric_pos['longitude']
        assert topocentric['latitude'] == geocentric_pos['latitude']
        assert topocentric['speed'] == geocentric_pos['speed']
    
    def test_calculate_topocentric_position_with_distance(self):
        """Test topocentric calculation with distance (Moon case)."""
        geocentric_pos = {
            'longitude': 123.456,
            'latitude': 5.678,
            'speed': 13.2,
            'distance': 384400  # Moon's average distance in km
        }
        observer_lat = 40.0
        observer_lon = -74.0
        
        topocentric = AccuracyImprover.calculate_topocentric_position(
            geocentric_pos, observer_lat, observer_lon
        )
        
        # With distance, parallax correction should be applied
        assert topocentric['longitude'] != geocentric_pos['longitude']
        assert topocentric['longitude'] < geocentric_pos['longitude']
        
        # Other values should be preserved
        assert topocentric['latitude'] == geocentric_pos['latitude']
        assert topocentric['speed'] == geocentric_pos['speed']
        assert topocentric['distance'] == geocentric_pos['distance']
    
    def test_calculate_topocentric_position_with_elevation(self):
        """Test topocentric calculation with observer elevation."""
        geocentric_pos = {
            'longitude': 90.0,
            'latitude': 0.0,
            'distance': 150000  # Close object for larger parallax
        }
        observer_lat = 0.0  # Equator
        observer_lon = 0.0
        observer_elevation = 1000  # 1km elevation
        
        topocentric = AccuracyImprover.calculate_topocentric_position(
            geocentric_pos, observer_lat, observer_lon, observer_elevation
        )
        
        # Should apply parallax correction
        assert topocentric['longitude'] != geocentric_pos['longitude']
    
    def test_calculate_topocentric_position_high_latitude(self):
        """Test topocentric calculation at high latitude."""
        geocentric_pos = {
            'longitude': 180.0,
            'latitude': 10.0,
            'distance': 400000
        }
        observer_lat = 89.0  # Near North Pole
        observer_lon = 0.0
        
        topocentric = AccuracyImprover.calculate_topocentric_position(
            geocentric_pos, observer_lat, observer_lon
        )
        
        # At high latitudes, parallax correction should be minimal
        parallax = abs(topocentric['longitude'] - geocentric_pos['longitude'])
        assert parallax < 0.1  # Small correction expected
    
    def test_calculate_topocentric_position_preserves_extra_fields(self):
        """Test that topocentric calculation preserves extra fields."""
        geocentric_pos = {
            'longitude': 45.0,
            'latitude': 15.0,
            'distance': 500000,
            'magnitude': 2.5,
            'name': 'TestObject',
            'extra_data': {'color': 'red'}
        }
        
        topocentric = AccuracyImprover.calculate_topocentric_position(
            geocentric_pos, 30.0, 45.0
        )
        
        # All extra fields should be preserved
        assert 'magnitude' in topocentric
        assert topocentric['magnitude'] == 2.5
        assert topocentric['name'] == 'TestObject'
        assert topocentric['extra_data'] == {'color': 'red'}