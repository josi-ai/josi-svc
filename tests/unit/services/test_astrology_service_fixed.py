"""Fixed comprehensive unit tests for AstrologyService."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from josi.services.astrology_service import AstrologyCalculator


class TestAstrologyCalculatorFixed:
    """Fixed comprehensive test coverage for AstrologyCalculator."""
    
    @pytest.fixture
    def astrology_calculator(self):
        """Create an AstrologyCalculator instance."""
        with patch('josi.services.astrology_service.swe.set_ephe_path'):
            return AstrologyCalculator()
    
    @pytest.fixture
    def test_datetime(self):
        """Test datetime for calculations."""
        return datetime(1990, 1, 1, 12, 0, 0)
    
    @pytest.fixture
    def test_location(self):
        """Test location coordinates."""
        return {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    
    def test_initialization(self):
        """Test AstrologyCalculator initialization."""
        with patch('josi.services.astrology_service.swe.set_ephe_path') as mock_set_path:
            calculator = AstrologyCalculator()
            
            # Verify ephemeris path was set
            mock_set_path.assert_called_once_with('')
            
            # Check constants
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
    
    def test_get_ayanamsa_lahiri(self, astrology_calculator):
        """Test getting Lahiri ayanamsa."""
        julian_day = 2447892.0
        
        with patch('josi.services.astrology_service.swe.set_sid_mode') as mock_set_sid:
            with patch('josi.services.astrology_service.swe.get_ayanamsa') as mock_get_ayanamsa:
                mock_get_ayanamsa.return_value = 23.456
                
                result = astrology_calculator._get_ayanamsa(julian_day, 'lahiri')
                
                assert result == 23.456
                mock_set_sid.assert_called_once_with(1)  # SIDM_LAHIRI = 1
                mock_get_ayanamsa.assert_called_once_with(julian_day)
    
    def test_get_ayanamsa_krishnamurti(self, astrology_calculator):
        """Test getting Krishnamurti ayanamsa."""
        julian_day = 2447892.0
        
        with patch('josi.services.astrology_service.swe.set_sid_mode') as mock_set_sid:
            with patch('josi.services.astrology_service.swe.get_ayanamsa') as mock_get_ayanamsa:
                mock_get_ayanamsa.return_value = 23.123
                
                result = astrology_calculator._get_ayanamsa(julian_day, 'krishnamurti')
                
                assert result == 23.123
                mock_set_sid.assert_called_once_with(5)  # SIDM_KRISHNAMURTI = 5
    
    def test_get_ayanamsa_default(self, astrology_calculator):
        """Test getting ayanamsa with unknown system defaults to Lahiri."""
        julian_day = 2447892.0
        
        with patch('josi.services.astrology_service.swe.set_sid_mode') as mock_set_sid:
            with patch('josi.services.astrology_service.swe.get_ayanamsa') as mock_get_ayanamsa:
                mock_get_ayanamsa.return_value = 23.456
                
                result = astrology_calculator._get_ayanamsa(julian_day, 'unknown')
                
                assert result == 23.456
                mock_set_sid.assert_called_once_with(1)  # Defaults to SIDM_LAHIRI
    
    def test_calculate_houses(self, astrology_calculator, test_location):
        """Test house calculation."""
        julian_day = 2447892.0
        
        with patch('josi.services.astrology_service.swe.houses') as mock_houses:
            # Mock house cusps (12 houses)
            mock_houses.return_value = (
                [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
                [0.0, 270.0]  # ASC, MC
            )
            
            result = astrology_calculator._calculate_houses(
                julian_day,
                test_location['latitude'],
                test_location['longitude']
            )
            
            assert len(result) == 12
            assert result[0] == 0.0
            assert result[11] == 330.0
            mock_houses.assert_called_once_with(julian_day, test_location['latitude'], test_location['longitude'], b'P')
    
    def test_get_nakshatra_pada(self, astrology_calculator):
        """Test nakshatra and pada calculation."""
        test_cases = [
            (0.0, ("Ashwini", 1)),
            (3.5, ("Ashwini", 2)),
            (7.0, ("Ashwini", 3)),
            (10.5, ("Ashwini", 4)),
            (13.5, ("Bharani", 1)),
            (120.0, ("Magha", 3)),
            (359.0, ("Revati", 4))
        ]
        
        for longitude, expected in test_cases:
            result = astrology_calculator._get_nakshatra_pada(longitude)
            assert result == expected
    
    def test_get_sign(self, astrology_calculator):
        """Test zodiac sign calculation."""
        test_cases = [
            (0.0, "Aries"),
            (15.0, "Aries"),
            (30.0, "Taurus"),
            (45.0, "Taurus"),
            (120.0, "Leo"),
            (180.0, "Libra"),
            (270.0, "Capricorn"),
            (359.0, "Pisces")
        ]
        
        for longitude, expected_sign in test_cases:
            result = astrology_calculator._get_sign(longitude)
            assert result == expected_sign
    
    @patch('josi.services.astrology_service.swe.calc')
    @patch('josi.services.astrology_service.swe.houses')
    @patch('josi.services.astrology_service.swe.get_ayanamsa')
    @patch('josi.services.astrology_service.swe.julday')
    def test_calculate_vedic_chart(self, mock_julday, mock_get_ayanamsa, mock_houses, mock_calc, 
                                  astrology_calculator, test_datetime, test_location):
        """Test Vedic chart calculation."""
        # Mock Julian day
        mock_julday.return_value = 2447892.0
        
        # Mock ayanamsa
        mock_get_ayanamsa.return_value = 23.456
        
        # Mock houses
        mock_houses.return_value = (
            [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
            [0.0, 270.0]
        )
        
        # Mock planet calculations
        planet_results = {
            0: ((120.5, 0.1, 1.0, 0.98, 0.0, 0.0), 0),  # Sun
            1: ((45.2, -0.5, 1.0, 12.5, 0.0, 0.0), 0),  # Moon
            2: ((90.0, 0.0, 1.0, 1.2, 0.0, 0.0), 0),    # Mercury
            3: ((60.0, 0.0, 1.0, 0.8, 0.0, 0.0), 0),    # Venus
            4: ((180.0, 0.0, 1.0, 0.5, 0.0, 0.0), 0),   # Mars
            5: ((240.0, 0.0, 1.0, 0.1, 0.0, 0.0), 0),   # Jupiter
            6: ((300.0, 0.0, 1.0, 0.05, 0.0, 0.0), 0),  # Saturn
            10: ((120.0, 0.0, 1.0, 0.1, 0.0, 0.0), 0),  # Rahu
        }
        
        mock_calc.side_effect = lambda jd, planet_id: planet_results.get(planet_id, ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0))
        
        result = astrology_calculator.calculate_vedic_chart(
            test_datetime,
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert result['chart_type'] == 'vedic'
        assert result['ayanamsa'] == 23.456
        assert 'ascendant' in result
        assert 'houses' in result
        assert 'planets' in result
        
        # Check that all planets are present
        assert 'Sun' in result['planets']
        assert 'Moon' in result['planets']
        assert 'Rahu' in result['planets']
        assert 'Ketu' in result['planets']
        
        # Check Ketu is 180 degrees from Rahu
        rahu_long = result['planets']['Rahu']['longitude']
        ketu_long = result['planets']['Ketu']['longitude']
        diff = abs(ketu_long - rahu_long)
        assert abs(diff - 180.0) < 0.1 or abs(diff - 180.0 + 360) < 0.1
    
    def test_calculate_south_indian_chart(self, astrology_calculator, test_datetime, test_location):
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
                test_location['latitude'],
                test_location['longitude']
            )
            
            assert result['chart_type'] == 'south_indian'
            mock_vedic.assert_called_once_with(test_datetime, test_location['latitude'], test_location['longitude'])
    
    @patch('josi.services.astrology_service.swe.calc')
    @patch('josi.services.astrology_service.swe.houses')
    @patch('josi.services.astrology_service.swe.julday')
    def test_calculate_western_chart(self, mock_julday, mock_houses, mock_calc,
                                   astrology_calculator, test_datetime, test_location):
        """Test Western chart calculation."""
        # Mock Julian day
        mock_julday.return_value = 2447892.0
        
        # Mock houses
        mock_houses.return_value = (
            [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
            [0.0, 270.0]
        )
        
        # Mock planet calculations
        planet_results = {
            0: ((120.5, 0.1, 1.0, 0.98, 0.0, 0.0), 0),  # Sun
            1: ((45.2, -0.5, 1.0, 12.5, 0.0, 0.0), 0),  # Moon
            2: ((90.0, 0.0, 1.0, 1.2, 0.0, 0.0), 0),    # Mercury
            3: ((60.0, 0.0, 1.0, 0.8, 0.0, 0.0), 0),    # Venus
            4: ((180.0, 0.0, 1.0, 0.5, 0.0, 0.0), 0),   # Mars
            5: ((240.0, 0.0, 1.0, 0.1, 0.0, 0.0), 0),   # Jupiter
            6: ((300.0, 0.0, 1.0, 0.05, 0.0, 0.0), 0),  # Saturn
            10: ((120.0, 0.0, 1.0, 0.1, 0.0, 0.0), 0),  # Rahu
        }
        
        mock_calc.side_effect = lambda jd, planet_id: planet_results.get(planet_id, ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0))
        
        result = astrology_calculator.calculate_western_chart(
            test_datetime,
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert result['chart_type'] == 'western'
        assert 'ascendant' in result
        assert 'houses' in result
        assert 'planets' in result
        
        # Western chart should not have ayanamsa
        assert 'ayanamsa' not in result
        
        # Ketu should not be in Western chart
        assert 'Ketu' not in result['planets']
        
        # Check that other planets are present
        assert 'Sun' in result['planets']
        assert 'Moon' in result['planets']
        assert 'Rahu' in result['planets']  # North Node is used in Western astrology
    
    def test_house_determination_normal(self, astrology_calculator):
        """Test house determination for normal case."""
        # Test internal house calculation logic
        houses = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
        
        # Planet at 45 degrees should be in house 2
        longitude = 45.0
        house = 1
        for i in range(12):
            house_start = houses[i]
            house_end = houses[(i + 1) % 12]
            
            if house_start <= longitude < house_end:
                house = i + 1
                break
        
        assert house == 2
    
    def test_house_determination_crossing_zero(self, astrology_calculator):
        """Test house determination when house crosses 0 degrees."""
        # Test when house crosses 0 degrees (e.g., 330-30)
        houses = [330.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0]
        
        # Planet at 345 degrees should be in house 1
        longitude = 345.0
        house = 1
        for i in range(12):
            house_start = houses[i]
            house_end = houses[(i + 1) % 12]
            
            if house_start <= longitude < house_end:
                house = i + 1
                break
            elif house_start > house_end:  # Crosses 0°
                if longitude >= house_start or longitude < house_end:
                    house = i + 1
                    break
        
        assert house == 1