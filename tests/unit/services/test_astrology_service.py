"""Comprehensive unit tests for AstrologyService."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from decimal import Decimal

from josi.services.astrology_service import AstrologyCalculator


class TestAstrologyCalculator:
    """Comprehensive test coverage for AstrologyCalculator."""
    
    @pytest.fixture
    def astrology_calculator(self):
        """Create an AstrologyCalculator instance."""
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
    
    def test_initialization(self, astrology_calculator):
        """Test AstrologyCalculator initialization."""
        assert hasattr(astrology_calculator, 'calculate_planets')
        assert hasattr(astrology_calculator, 'calculate_houses')
        assert hasattr(astrology_calculator, 'calculate_aspects')
        assert hasattr(astrology_calculator, 'calculate_vedic_chart')
        assert hasattr(astrology_calculator, 'calculate_western_chart')
    
    @patch('swisseph.set_ephe_path')
    def test_set_ephemeris_path(self, mock_set_ephe_path):
        """Test ephemeris path is set during initialization."""
        calculator = AstrologyCalculator()
        # Verify ephemeris path was set
        mock_set_ephe_path.assert_called()
    
    def test_calculate_planets_basic(self, astrology_calculator, test_datetime, test_location):
        """Test basic planet calculation."""
        with patch('swisseph.calc_ut') as mock_calc:
            # Mock planet position
            mock_calc.return_value = ((120.5, 0.0, 1.0, 0.0, 0.0, 0.0), 0)
            
            result = astrology_calculator.calculate_planets(
                test_datetime,
                test_location['latitude'],
                test_location['longitude']
            )
            
            assert isinstance(result, dict)
            # Should have called calc_ut for each planet
            assert mock_calc.call_count > 0
    
    def test_calculate_houses_placidus(self, astrology_calculator, test_datetime, test_location):
        """Test house calculation with Placidus system."""
        with patch('swisseph.houses') as mock_houses:
            # Mock house cusps (12 houses + ASC/MC)
            mock_houses.return_value = (
                [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
                [0.0, 270.0]  # ASC, MC
            )
            
            result = astrology_calculator.calculate_houses(
                test_datetime,
                test_location['latitude'],
                test_location['longitude'],
                house_system='placidus'
            )
            
            assert isinstance(result, dict)
            assert len(result) >= 12  # Should have at least 12 houses
    
    def test_calculate_houses_whole_sign(self, astrology_calculator, test_datetime, test_location):
        """Test house calculation with Whole Sign system."""
        with patch('swisseph.houses') as mock_houses:
            # For whole sign, first get ASC
            mock_houses.return_value = (
                [15.0] + [0.0] * 11,  # ASC at 15 degrees
                [0.0, 270.0]
            )
            
            result = astrology_calculator.calculate_houses(
                test_datetime,
                test_location['latitude'],
                test_location['longitude'],
                house_system='whole_sign'
            )
            
            assert isinstance(result, dict)
    
    def test_calculate_aspects(self, astrology_calculator):
        """Test aspect calculation between planets."""
        planet_positions = {
            "sun": {"longitude": 120.0},
            "moon": {"longitude": 240.0},
            "mars": {"longitude": 180.0}
        }
        
        result = astrology_calculator.calculate_aspects(planet_positions)
        
        assert isinstance(result, list)
        # Should find aspects between planets
        for aspect in result:
            assert "planet1" in aspect
            assert "planet2" in aspect
            assert "aspect" in aspect
            assert "orb" in aspect
    
    def test_calculate_aspects_conjunction(self, astrology_calculator):
        """Test conjunction aspect detection."""
        planet_positions = {
            "sun": {"longitude": 120.0},
            "moon": {"longitude": 122.0}  # 2 degree orb
        }
        
        result = astrology_calculator.calculate_aspects(planet_positions)
        
        # Should find conjunction between sun and moon
        conjunctions = [a for a in result if a["aspect"] == "conjunction"]
        assert len(conjunctions) > 0
        assert conjunctions[0]["orb"] <= 10.0  # Within orb
    
    def test_calculate_aspects_opposition(self, astrology_calculator):
        """Test opposition aspect detection."""
        planet_positions = {
            "sun": {"longitude": 0.0},
            "moon": {"longitude": 180.0}  # Exact opposition
        }
        
        result = astrology_calculator.calculate_aspects(planet_positions)
        
        # Should find opposition
        oppositions = [a for a in result if a["aspect"] == "opposition"]
        assert len(oppositions) > 0
        assert oppositions[0]["orb"] <= 10.0
    
    def test_calculate_aspects_trine(self, astrology_calculator):
        """Test trine aspect detection."""
        planet_positions = {
            "sun": {"longitude": 0.0},
            "moon": {"longitude": 120.0}  # Exact trine
        }
        
        result = astrology_calculator.calculate_aspects(planet_positions)
        
        # Should find trine
        trines = [a for a in result if a["aspect"] == "trine"]
        assert len(trines) > 0
        assert trines[0]["orb"] <= 8.0
    
    def test_calculate_aspects_square(self, astrology_calculator):
        """Test square aspect detection."""
        planet_positions = {
            "sun": {"longitude": 0.0},
            "moon": {"longitude": 90.0}  # Exact square
        }
        
        result = astrology_calculator.calculate_aspects(planet_positions)
        
        # Should find square
        squares = [a for a in result if a["aspect"] == "square"]
        assert len(squares) > 0
        assert squares[0]["orb"] <= 10.0
    
    def test_calculate_aspects_sextile(self, astrology_calculator):
        """Test sextile aspect detection."""
        planet_positions = {
            "sun": {"longitude": 0.0},
            "moon": {"longitude": 60.0}  # Exact sextile
        }
        
        result = astrology_calculator.calculate_aspects(planet_positions)
        
        # Should find sextile
        sextiles = [a for a in result if a["aspect"] == "sextile"]
        assert len(sextiles) > 0
        assert sextiles[0]["orb"] <= 6.0
    
    def test_calculate_vedic_chart(self, astrology_calculator, test_datetime, test_location):
        """Test Vedic chart calculation."""
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            with patch.object(astrology_calculator, 'calculate_houses') as mock_houses:
                with patch.object(astrology_calculator, 'calculate_aspects') as mock_aspects:
                    mock_planets.return_value = {"sun": {"longitude": 120.0}}
                    mock_houses.return_value = {"1": 0.0}
                    mock_aspects.return_value = []
                    
                    result = astrology_calculator.calculate_vedic_chart(
                        test_datetime,
                        test_location['latitude'],
                        test_location['longitude'],
                        ayanamsa='lahiri'
                    )
                    
                    assert isinstance(result, dict)
                    assert "planets" in result
                    assert "houses" in result
                    assert "aspects" in result
                    assert "ayanamsa" in result
                    
                    # Verify methods were called
                    mock_planets.assert_called_once()
                    mock_houses.assert_called_once()
                    mock_aspects.assert_called_once()
    
    def test_calculate_western_chart(self, astrology_calculator, test_datetime, test_location):
        """Test Western chart calculation."""
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            with patch.object(astrology_calculator, 'calculate_houses') as mock_houses:
                with patch.object(astrology_calculator, 'calculate_aspects') as mock_aspects:
                    mock_planets.return_value = {"sun": {"longitude": 120.0}}
                    mock_houses.return_value = {"1": 0.0}
                    mock_aspects.return_value = []
                    
                    result = astrology_calculator.calculate_western_chart(
                        test_datetime,
                        test_location['latitude'],
                        test_location['longitude'],
                        house_system='placidus'
                    )
                    
                    assert isinstance(result, dict)
                    assert "planets" in result
                    assert "houses" in result
                    assert "aspects" in result
                    
                    # Western chart should not have ayanamsa
                    assert "ayanamsa" not in result
    
    def test_calculate_chinese_chart(self, astrology_calculator, test_datetime):
        """Test Chinese chart calculation."""
        result = astrology_calculator.calculate_chinese_chart(test_datetime)
        
        assert isinstance(result, dict)
        # Should have Chinese astrology elements
        assert "year_pillar" in result or "chart_type" in result
    
    def test_calculate_divisional_chart(self, astrology_calculator, test_datetime, test_location):
        """Test divisional chart calculation."""
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            mock_planets.return_value = {"sun": {"longitude": 120.0}}
            
            # Test D9 (Navamsa) chart
            result = astrology_calculator.calculate_divisional_chart(
                test_datetime,
                test_location['latitude'],
                test_location['longitude'],
                division=9
            )
            
            assert isinstance(result, dict)
    
    def test_get_ayanamsa_value(self, astrology_calculator, test_datetime):
        """Test getting ayanamsa value."""
        with patch('swisseph.get_ayanamsa_ut') as mock_ayanamsa:
            mock_ayanamsa.return_value = 23.5
            
            # Convert datetime to julian day
            with patch('swisseph.julday') as mock_julday:
                mock_julday.return_value = 2447892.5
                
                result = astrology_calculator.get_ayanamsa_value(test_datetime, 'lahiri')
                
                assert isinstance(result, float)
                assert result == 23.5
    
    def test_convert_to_sidereal(self, astrology_calculator):
        """Test tropical to sidereal conversion."""
        tropical_longitude = 120.0
        ayanamsa = 23.0
        
        result = astrology_calculator.convert_to_sidereal(tropical_longitude, ayanamsa)
        
        assert result == tropical_longitude - ayanamsa
        assert result == 97.0
    
    def test_get_zodiac_sign(self, astrology_calculator):
        """Test zodiac sign calculation from longitude."""
        test_cases = [
            (15.0, "aries"),
            (45.0, "taurus"),
            (75.0, "gemini"),
            (105.0, "cancer"),
            (135.0, "leo"),
            (165.0, "virgo"),
            (195.0, "libra"),
            (225.0, "scorpio"),
            (255.0, "sagittarius"),
            (285.0, "capricorn"),
            (315.0, "aquarius"),
            (345.0, "pisces")
        ]
        
        for longitude, expected_sign in test_cases:
            result = astrology_calculator.get_zodiac_sign(longitude)
            assert result == expected_sign
    
    def test_get_house_position(self, astrology_calculator):
        """Test house position calculation."""
        planet_longitude = 45.0
        house_cusps = {
            "1": 0.0,
            "2": 30.0,
            "3": 60.0,
            "4": 90.0
        }
        
        result = astrology_calculator.get_house_position(planet_longitude, house_cusps)
        
        # Planet at 45 degrees should be in 2nd house
        assert result == 2
    
    def test_calculate_planet_strength(self, astrology_calculator):
        """Test planet strength calculation."""
        planet_data = {
            "longitude": 120.0,
            "sign": "leo",
            "house": 5
        }
        
        result = astrology_calculator.calculate_planet_strength(planet_data, "sun")
        
        assert isinstance(result, dict)
        # Sun in Leo (own sign) should have good strength
        assert "dignity" in result or "strength" in result