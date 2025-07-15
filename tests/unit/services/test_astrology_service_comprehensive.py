"""Comprehensive unit tests for AstrologyService to achieve 90% coverage."""
import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
from decimal import Decimal
import math

from josi.services.astrology_service import AstrologyCalculator


class TestAstrologyCalculatorComprehensive:
    """Comprehensive test coverage for all AstrologyCalculator methods."""
    
    @pytest.fixture
    def astrology_calculator(self):
        """Create an AstrologyCalculator instance."""
        return AstrologyCalculator()
    
    @pytest.fixture
    def test_datetime(self):
        """Standard test datetime."""
        return datetime(1990, 1, 1, 12, 0, 0)
    
    @pytest.fixture
    def test_location(self):
        """Standard test location (New York)."""
        return {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    
    # Test initialization and setup
    def test_ephemeris_path_setup(self):
        """Test that ephemeris path is properly set."""
        with patch('swisseph.set_ephe_path') as mock_set_path:
            calc = AstrologyCalculator()
            mock_set_path.assert_called_once()
    
    # Test calculate_divisional_chart
    def test_calculate_divisional_chart_navamsa(self, astrology_calculator, test_datetime, test_location):
        """Test Navamsa (D9) divisional chart calculation."""
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            mock_planets.return_value = {
                "Sun": {"longitude": 120.0},
                "Moon": {"longitude": 60.0},
                "Mars": {"longitude": 180.0}
            }
            
            result = astrology_calculator.calculate_divisional_chart(
                test_datetime,
                test_location['latitude'],
                test_location['longitude'],
                division=9
            )
            
            assert isinstance(result, dict)
            assert "planets" in result
            assert "division" in result
            assert result["division"] == 9
            
            # Check that planetary positions were adjusted for D9
            sun_d9 = result["planets"]["Sun"]["longitude"]
            # D9 calculation: (120 * 9) % 360 = 0
            assert sun_d9 == 0.0
    
    def test_calculate_divisional_chart_dashamsa(self, astrology_calculator, test_datetime, test_location):
        """Test Dashamsa (D10) career chart calculation."""
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            mock_planets.return_value = {
                "Sun": {"longitude": 45.0},
                "Moon": {"longitude": 90.0}
            }
            
            result = astrology_calculator.calculate_divisional_chart(
                test_datetime,
                test_location['latitude'],
                test_location['longitude'],
                division=10
            )
            
            assert result["division"] == 10
            # D10 calculation: (45 * 10) % 360 = 90
            assert result["planets"]["Sun"]["longitude"] == 90.0
    
    def test_calculate_divisional_chart_hora(self, astrology_calculator, test_datetime, test_location):
        """Test Hora (D2) wealth chart calculation."""
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            mock_planets.return_value = {
                "Sun": {"longitude": 25.0},  # In first half of sign
                "Moon": {"longitude": 45.0}   # In second half of sign
            }
            
            result = astrology_calculator.calculate_divisional_chart(
                test_datetime,
                test_location['latitude'],
                test_location['longitude'],
                division=2
            )
            
            assert result["division"] == 2
            # D2 special calculation for Sun/Moon rulership
            assert "special_calculation" in result or "planets" in result
    
    # Test calculate_synastry
    def test_calculate_synastry_basic(self, astrology_calculator):
        """Test synastry calculation between two charts."""
        chart1 = {
            "planets": {
                "Sun": {"longitude": 120.0},
                "Moon": {"longitude": 60.0},
                "Venus": {"longitude": 90.0}
            }
        }
        
        chart2 = {
            "planets": {
                "Sun": {"longitude": 180.0},
                "Moon": {"longitude": 240.0},
                "Venus": {"longitude": 270.0}
            }
        }
        
        result = astrology_calculator.calculate_synastry(chart1, chart2)
        
        assert isinstance(result, dict)
        assert "aspects" in result
        assert "composite" in result
        assert len(result["aspects"]) > 0
        
        # Check for specific aspects
        # Sun1 (120) to Sun2 (180) = 60 degrees = sextile
        has_sun_aspect = any(
            a for a in result["aspects"] 
            if a["planet1"] == "Sun" and a["planet2"] == "Sun"
        )
        assert has_sun_aspect
    
    def test_calculate_synastry_with_orbs(self, astrology_calculator):
        """Test synastry with custom orb settings."""
        chart1 = {
            "planets": {
                "Sun": {"longitude": 0.0},
                "Moon": {"longitude": 89.0}  # Almost square to Moon2
            }
        }
        
        chart2 = {
            "planets": {
                "Sun": {"longitude": 180.0},  # Opposition to Sun1
                "Moon": {"longitude": 0.0}
            }
        }
        
        result = astrology_calculator.calculate_synastry(
            chart1, chart2, 
            orb_settings={"opposition": 10, "square": 8}
        )
        
        # Should find Sun1-Sun2 opposition
        opposition = next(
            (a for a in result["aspects"] 
             if a["aspect"] == "opposition"), 
            None
        )
        assert opposition is not None
        assert opposition["orb"] == 0.0
    
    # Test composite chart calculation
    def test_calculate_composite_chart(self, astrology_calculator):
        """Test composite chart calculation."""
        chart1 = {
            "planets": {
                "Sun": {"longitude": 0.0},
                "Moon": {"longitude": 90.0},
                "Mercury": {"longitude": 45.0}
            },
            "houses": {"1": 0.0, "10": 270.0}
        }
        
        chart2 = {
            "planets": {
                "Sun": {"longitude": 180.0},
                "Moon": {"longitude": 270.0},
                "Mercury": {"longitude": 315.0}
            },
            "houses": {"1": 30.0, "10": 300.0}
        }
        
        result = astrology_calculator.calculate_composite_chart(chart1, chart2)
        
        assert isinstance(result, dict)
        assert "planets" in result
        assert "houses" in result
        
        # Composite Sun should be midpoint of 0 and 180 = 90
        assert result["planets"]["Sun"]["longitude"] == 90.0
        
        # Composite Moon: midpoint of 90 and 270 = 180
        assert result["planets"]["Moon"]["longitude"] == 180.0
        
        # Composite Mercury: midpoint of 45 and 315
        # Shorter arc: 45 to 315 = 180 degrees, midpoint = 180
        assert "Mercury" in result["planets"]
    
    # Test transit calculations
    def test_calculate_transits(self, astrology_calculator, test_datetime):
        """Test transit calculations."""
        natal_chart = {
            "planets": {
                "Sun": {"longitude": 120.0},
                "Moon": {"longitude": 60.0},
                "Mars": {"longitude": 180.0}
            }
        }
        
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            # Mock current planetary positions
            mock_planets.return_value = {
                "Sun": {"longitude": 150.0},  # 30 degrees from natal = semi-sextile
                "Moon": {"longitude": 240.0},  # 180 from natal = opposition
                "Mars": {"longitude": 270.0}   # 90 from natal = square
            }
            
            result = astrology_calculator.calculate_transits(
                natal_chart,
                test_datetime,
                40.7128,
                -74.0060
            )
            
            assert isinstance(result, dict)
            assert "transiting_planets" in result
            assert "aspects" in result
            
            # Should find Moon opposition
            moon_opp = next(
                (a for a in result["aspects"] 
                 if a["planet1"] == "Moon" and a["aspect"] == "opposition"),
                None
            )
            assert moon_opp is not None
    
    # Test solar return
    def test_calculate_solar_return(self, astrology_calculator):
        """Test solar return chart calculation."""
        birth_datetime = datetime(1990, 8, 15, 14, 30, 0)
        year = 2024
        
        with patch('swisseph.calc_ut') as mock_calc:
            with patch('swisseph.julday') as mock_julday:
                # Mock Julian day calculation
                mock_julday.return_value = 2460000.0
                
                # Mock Sun position for birth and return
                mock_calc.side_effect = [
                    ((142.5, 0.0, 1.0, 0.0, 0.0, 0.0), 0),  # Birth Sun
                    ((142.5, 0.0, 1.0, 0.0, 0.0, 0.0), 0),  # Return Sun (same degree)
                ]
                
                result = astrology_calculator.calculate_solar_return(
                    birth_datetime,
                    year,
                    40.7128,
                    -74.0060
                )
                
                assert isinstance(result, dict)
                assert "return_datetime" in result
                assert "chart" in result
                assert result["year"] == year
    
    # Test lunar return
    def test_calculate_lunar_return(self, astrology_calculator):
        """Test lunar return chart calculation."""
        birth_datetime = datetime(1990, 8, 15, 14, 30, 0)
        
        with patch('swisseph.calc_ut') as mock_calc:
            with patch('swisseph.julday') as mock_julday:
                mock_julday.return_value = 2460000.0
                
                # Mock Moon positions
                mock_calc.side_effect = [
                    ((45.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0),  # Birth Moon
                    ((45.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0),  # Return Moon
                ]
                
                result = astrology_calculator.calculate_lunar_return(
                    birth_datetime,
                    datetime(2024, 1, 1),
                    40.7128,
                    -74.0060
                )
                
                assert isinstance(result, dict)
                assert "return_datetime" in result
                assert "chart" in result
    
    # Test progressions
    def test_calculate_secondary_progressions(self, astrology_calculator):
        """Test secondary progression calculation."""
        birth_datetime = datetime(1990, 1, 1, 12, 0, 0)
        target_date = datetime(2024, 1, 1)
        
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            mock_planets.return_value = {
                "Sun": {"longitude": 134.0},  # Progressed ~34 degrees
                "Moon": {"longitude": 180.0}
            }
            
            result = astrology_calculator.calculate_secondary_progressions(
                birth_datetime,
                target_date,
                40.7128,
                -74.0060
            )
            
            assert isinstance(result, dict)
            assert "progressed_planets" in result
            assert "progression_date" in result
            assert "years_progressed" in result
            assert result["years_progressed"] == 34  # 2024 - 1990
    
    # Test midpoints
    def test_calculate_midpoints(self, astrology_calculator):
        """Test midpoint calculation."""
        planet_positions = {
            "Sun": {"longitude": 0.0},
            "Moon": {"longitude": 90.0},
            "Mercury": {"longitude": 180.0},
            "Venus": {"longitude": 270.0}
        }
        
        result = astrology_calculator.calculate_midpoints(planet_positions)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Find Sun/Moon midpoint
        sun_moon = next(
            (m for m in result 
             if set(m["planets"]) == {"Sun", "Moon"}),
            None
        )
        assert sun_moon is not None
        assert sun_moon["midpoint"] == 45.0  # Midpoint of 0 and 90
    
    # Test Arabic parts
    def test_calculate_arabic_parts(self, astrology_calculator):
        """Test Arabic parts/Lots calculation."""
        chart_data = {
            "planets": {
                "Sun": {"longitude": 120.0},
                "Moon": {"longitude": 60.0},
                "Mercury": {"longitude": 90.0},
                "Venus": {"longitude": 150.0},
                "Mars": {"longitude": 180.0},
                "Jupiter": {"longitude": 210.0},
                "Saturn": {"longitude": 240.0}
            },
            "houses": {
                "1": 0.0,  # Ascendant
                "7": 180.0  # Descendant
            }
        }
        
        result = astrology_calculator.calculate_arabic_parts(chart_data)
        
        assert isinstance(result, dict)
        assert "part_of_fortune" in result
        
        # Part of Fortune = ASC + Moon - Sun
        # = 0 + 60 - 120 = -60 = 300
        expected_pof = (0.0 + 60.0 - 120.0) % 360
        assert result["part_of_fortune"]["longitude"] == expected_pof
    
    # Test fixed stars
    def test_calculate_fixed_stars(self, astrology_calculator):
        """Test fixed star positions and conjunctions."""
        with patch('swisseph.fixstar_ut') as mock_fixstar:
            # Mock some fixed star positions
            mock_fixstar.side_effect = [
                ("Aldebaran", (45.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0),
                ("Regulus", (150.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0),
                ("Spica", (203.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0),
            ]
            
            planet_positions = {
                "Sun": {"longitude": 45.5},  # Conjunct Aldebaran
                "Moon": {"longitude": 150.2}  # Conjunct Regulus
            }
            
            result = astrology_calculator.calculate_fixed_stars(
                datetime(2024, 1, 1),
                planet_positions
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Check for Aldebaran conjunction
            aldebaran = next(
                (s for s in result if s["name"] == "Aldebaran"),
                None
            )
            assert aldebaran is not None
            assert "conjunctions" in aldebaran
    
    # Test retrograde detection
    def test_is_planet_retrograde(self, astrology_calculator):
        """Test retrograde motion detection."""
        with patch('swisseph.calc_ut') as mock_calc:
            # Mock planet with negative speed (retrograde)
            mock_calc.return_value = ((120.0, 0.0, 1.0, -0.5, 0.0, 0.0), 0)
            
            result = astrology_calculator.is_planet_retrograde(
                "Mercury",
                datetime(2024, 1, 1)
            )
            
            assert result is True
            
            # Mock planet with positive speed (direct)
            mock_calc.return_value = ((120.0, 0.0, 1.0, 0.5, 0.0, 0.0), 0)
            
            result = astrology_calculator.is_planet_retrograde(
                "Mercury",
                datetime(2024, 1, 1)
            )
            
            assert result is False
    
    # Test eclipse calculations
    def test_find_eclipses(self, astrology_calculator):
        """Test eclipse finder."""
        with patch('swisseph.sol_eclipse_when_glob') as mock_sol_eclipse:
            with patch('swisseph.lun_eclipse_when') as mock_lun_eclipse:
                # Mock solar eclipse
                mock_sol_eclipse.return_value = (2460000.0, 0)
                # Mock lunar eclipse
                mock_lun_eclipse.return_value = (2460030.0, 0)
                
                result = astrology_calculator.find_eclipses(
                    datetime(2024, 1, 1),
                    datetime(2024, 12, 31)
                )
                
                assert isinstance(result, dict)
                assert "solar_eclipses" in result
                assert "lunar_eclipses" in result
                assert len(result["solar_eclipses"]) > 0
                assert len(result["lunar_eclipses"]) > 0
    
    # Test void of course Moon
    def test_calculate_void_of_course(self, astrology_calculator):
        """Test void of course Moon calculation."""
        result = astrology_calculator.calculate_void_of_course(
            datetime(2024, 1, 1),
            datetime(2024, 1, 7),
            timezone="UTC"
        )
        
        assert isinstance(result, list)
        # Should return void of course periods
    
    # Test planetary hours
    def test_calculate_planetary_hours(self, astrology_calculator):
        """Test planetary hour calculation."""
        result = astrology_calculator.calculate_planetary_hours(
            datetime(2024, 1, 1),
            40.7128,
            -74.0060,
            timezone="America/New_York"
        )
        
        assert isinstance(result, dict)
        assert "day_hours" in result
        assert "night_hours" in result
        assert len(result["day_hours"]) == 12
        assert len(result["night_hours"]) == 12
        
        # First hour should be ruled by day's planet
        assert "ruler" in result["day_hours"][0]
    
    # Test dignity and debility
    def test_calculate_essential_dignities(self, astrology_calculator):
        """Test essential dignity calculation."""
        # Sun in Leo (domicile)
        result = astrology_calculator.calculate_essential_dignities(
            "Sun", 
            125.0  # 5 degrees Leo
        )
        
        assert isinstance(result, dict)
        assert result["dignity"] == "domicile"
        assert result["score"] > 0
        
        # Moon in Capricorn (detriment)
        result = astrology_calculator.calculate_essential_dignities(
            "Moon",
            280.0  # 10 degrees Capricorn
        )
        
        assert result["dignity"] == "detriment"
        assert result["score"] < 0
    
    # Test aspect patterns
    def test_find_aspect_patterns(self, astrology_calculator):
        """Test aspect pattern detection (T-square, Grand Trine, etc)."""
        planet_positions = {
            "Sun": {"longitude": 0.0},
            "Moon": {"longitude": 120.0},
            "Venus": {"longitude": 240.0},  # Grand Trine
            "Mars": {"longitude": 90.0},
            "Jupiter": {"longitude": 180.0},
            "Saturn": {"longitude": 270.0}  # T-Square with Sun-Jupiter
        }
        
        aspects = astrology_calculator.calculate_aspects(planet_positions)
        patterns = astrology_calculator.find_aspect_patterns(aspects, planet_positions)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        # Should find Grand Trine
        grand_trine = next(
            (p for p in patterns if p["type"] == "grand_trine"),
            None
        )
        assert grand_trine is not None
        assert set(grand_trine["planets"]) == {"Sun", "Moon", "Venus"}
    
    # Test harmonic charts
    def test_calculate_harmonic_chart(self, astrology_calculator):
        """Test harmonic chart calculation."""
        planet_positions = {
            "Sun": {"longitude": 30.0},
            "Moon": {"longitude": 90.0},
            "Mercury": {"longitude": 120.0}
        }
        
        # Calculate 5th harmonic
        result = astrology_calculator.calculate_harmonic_chart(
            planet_positions,
            harmonic=5
        )
        
        assert isinstance(result, dict)
        # Sun at 30° * 5 = 150°
        assert result["Sun"]["longitude"] == 150.0
        # Moon at 90° * 5 = 450° = 90°
        assert result["Moon"]["longitude"] == 90.0
    
    # Test relocation chart
    def test_calculate_relocated_chart(self, astrology_calculator):
        """Test relocation chart calculation."""
        birth_datetime = datetime(1990, 1, 1, 12, 0, 0)
        birth_lat, birth_lon = 40.7128, -74.0060  # New York
        new_lat, new_lon = 51.5074, -0.1278  # London
        
        with patch.object(astrology_calculator, 'calculate_houses') as mock_houses:
            mock_houses.return_value = {
                "1": 15.0,  # New ASC
                "10": 280.0  # New MC
            }
            
            result = astrology_calculator.calculate_relocated_chart(
                birth_datetime,
                birth_lat, birth_lon,
                new_lat, new_lon
            )
            
            assert isinstance(result, dict)
            assert "houses" in result
            assert "location" in result
            assert result["location"]["latitude"] == new_lat
            assert result["location"]["longitude"] == new_lon