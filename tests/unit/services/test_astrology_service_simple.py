"""Simple unit tests for Astrology service."""
import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
import sys

# Mock swisseph module
sys.modules['swisseph'] = Mock()

from josi.services.astrology_service import AstrologyCalculator


class TestAstrologyServiceSimple:
    """Simple test coverage for AstrologyCalculator."""
    
    @pytest.fixture
    def astrology_calculator(self):
        """Create an AstrologyCalculator instance."""
        with patch('josi.services.astrology_service.swe.set_ephe_path'):
            return AstrologyCalculator()
    
    @pytest.fixture
    def test_datetime(self):
        """Test datetime for calculations."""
        return datetime(1990, 1, 1, 12, 0, 0)
    
    def test_initialization(self):
        """Test AstrologyCalculator initialization."""
        with patch('josi.services.astrology_service.swe.set_ephe_path') as mock_set_path:
            calculator = AstrologyCalculator()
            
            mock_set_path.assert_called_once_with('')
            assert hasattr(calculator, 'PLANETS')
            assert hasattr(calculator, 'NAKSHATRAS')
            assert hasattr(calculator, 'SIGNS')
            assert len(calculator.PLANETS) == 9
            assert len(calculator.NAKSHATRAS) == 27
            assert len(calculator.SIGNS) == 12
    
    def test_datetime_to_julian(self, astrology_calculator, test_datetime):
        """Test datetime to Julian day conversion."""
        with patch('josi.services.astrology_service.swe.julday') as mock_julday:
            mock_julday.return_value = 2447892.0
            
            result = astrology_calculator._datetime_to_julian(test_datetime)
            
            assert result == 2447892.0
            mock_julday.assert_called_once_with(1990, 1, 1, 12.0)
    
    def test_get_ayanamsa(self, astrology_calculator):
        """Test ayanamsa calculation."""
        julian_day = 2447892.0
        
        with patch('josi.services.astrology_service.swe.set_sid_mode') as mock_set_sid:
            with patch('josi.services.astrology_service.swe.get_ayanamsa') as mock_get_ayanamsa:
                mock_get_ayanamsa.return_value = 23.456
                
                result = astrology_calculator._get_ayanamsa(julian_day, 'lahiri')
                
                assert result == 23.456
                mock_set_sid.assert_called_once_with(1)  # SIDM_LAHIRI
                mock_get_ayanamsa.assert_called_once_with(julian_day)
    
    def test_calculate_houses(self, astrology_calculator):
        """Test house calculation."""
        julian_day = 2447892.0
        latitude = 40.7128
        longitude = -74.0060
        
        with patch('josi.services.astrology_service.swe.houses') as mock_houses:
            mock_houses.return_value = (
                [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
                [0.0, 270.0]
            )
            
            result = astrology_calculator._calculate_houses(julian_day, latitude, longitude)
            
            assert len(result) == 12
            assert result[0] == 0.0
            assert result[11] == 330.0
    
    def test_get_nakshatra_pada(self, astrology_calculator):
        """Test nakshatra and pada calculation."""
        # 45 degrees = Rohini nakshatra, pada 1
        nakshatra, pada = astrology_calculator._get_nakshatra_pada(45.0)
        
        assert nakshatra == "Rohini"
        assert pada == 1
        
        # 0 degrees = Ashwini, pada 1
        nakshatra, pada = astrology_calculator._get_nakshatra_pada(0.0)
        assert nakshatra == "Ashwini"
        assert pada == 1
    
    def test_get_sign(self, astrology_calculator):
        """Test zodiac sign calculation."""
        assert astrology_calculator._get_sign(0.0) == "Aries"
        assert astrology_calculator._get_sign(30.0) == "Taurus"
        assert astrology_calculator._get_sign(120.0) == "Leo"
        assert astrology_calculator._get_sign(359.0) == "Pisces"
    
    @patch('josi.services.astrology_service.swe.calc')
    @patch('josi.services.astrology_service.swe.houses')
    @patch('josi.services.astrology_service.swe.get_ayanamsa')
    @patch('josi.services.astrology_service.swe.julday')
    def test_calculate_vedic_chart(self, mock_julday, mock_get_ayanamsa, mock_houses, mock_calc, 
                                  astrology_calculator, test_datetime):
        """Test Vedic chart calculation."""
        # Setup mocks
        mock_julday.return_value = 2447892.0
        mock_get_ayanamsa.return_value = 23.456
        mock_houses.return_value = (
            [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
            [0.0, 270.0]
        )
        
        # Mock planet calculations
        planet_results = {
            0: ((120.5, 0.1, 1.0, 0.98, 0.0, 0.0), 0),  # Sun
            1: ((45.2, -0.5, 1.0, 12.5, 0.0, 0.0), 0),  # Moon
            10: ((120.0, 0.0, 1.0, 0.1, 0.0, 0.0), 0),  # Rahu
        }
        
        mock_calc.side_effect = lambda jd, planet_id: planet_results.get(planet_id, ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0))
        
        result = astrology_calculator.calculate_vedic_chart(
            test_datetime,
            latitude=40.7128,
            longitude=-74.0060
        )
        
        assert result['chart_type'] == 'vedic'
        assert result['ayanamsa'] == 23.456
        assert 'ascendant' in result
        assert 'houses' in result
        assert 'planets' in result
        assert 'Sun' in result['planets']
        assert 'Moon' in result['planets']
        assert 'Rahu' in result['planets']
        assert 'Ketu' in result['planets']
    
    def test_calculate_south_indian_chart(self, astrology_calculator, test_datetime):
        """Test South Indian chart calculation."""
        with patch.object(astrology_calculator, 'calculate_vedic_chart') as mock_vedic:
            mock_vedic.return_value = {
                'chart_type': 'vedic',
                'ayanamsa': 23.456,
                'ascendant': {'longitude': 0.0},
                'houses': [0.0] * 12,
                'planets': {}
            }
            
            result = astrology_calculator.calculate_south_indian_chart(
                test_datetime,
                latitude=40.0,
                longitude=-74.0
            )
            
            assert result['chart_type'] == 'south_indian'
            mock_vedic.assert_called_once()
    
    @patch('josi.services.astrology_service.swe.calc')
    @patch('josi.services.astrology_service.swe.houses')
    @patch('josi.services.astrology_service.swe.julday')
    def test_calculate_western_chart(self, mock_julday, mock_houses, mock_calc,
                                   astrology_calculator, test_datetime):
        """Test Western chart calculation."""
        # Setup mocks
        mock_julday.return_value = 2447892.0
        mock_houses.return_value = (
            [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
            [0.0, 270.0]
        )
        
        # Mock planet calculations
        planet_results = {
            0: ((120.5, 0.1, 1.0, 0.98, 0.0, 0.0), 0),  # Sun
            1: ((45.2, -0.5, 1.0, 12.5, 0.0, 0.0), 0),  # Moon
        }
        
        mock_calc.side_effect = lambda jd, planet_id: planet_results.get(planet_id, ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0))
        
        result = astrology_calculator.calculate_western_chart(
            test_datetime,
            latitude=40.0,
            longitude=-74.0
        )
        
        assert result['chart_type'] == 'western'
        assert 'ascendant' in result
        assert 'houses' in result
        assert 'planets' in result
        assert 'ayanamsa' not in result  # Western doesn't use ayanamsa
        assert 'Ketu' not in result['planets']  # Western doesn't use Ketu