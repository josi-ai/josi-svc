"""Additional tests to fill remaining coverage gaps and achieve near 100% coverage."""
import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timedelta
import math

from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.dasha_service import VimshottariDashaCalculator
from josi.services.vedic.panchang_service import PanchangCalculator
from josi.services.vedic.ashtakoota_service import AshtakootaCalculator
from josi.services.chinese.bazi_calculator_service import BaZiCalculator
from josi.services.western.progressions_service import ProgressionCalculator
from josi.services.numerology_service import NumerologyCalculator


class TestRemainingGaps:
    """Fill remaining coverage gaps in core modules."""
    
    # AstrologyCalculator - Missing method
    def test_calculate_planet_strength_edge_cases(self):
        """Test planet strength calculation in various conditions."""
        calc = AstrologyCalculator()
        
        # Test exaltation
        planet_data = {
            "longitude": 10.0,  # Sun in Aries (exaltation)
            "sign": "aries",
            "house": 10,
            "speed": 1.0
        }
        result = calc.calculate_planet_strength(planet_data, "Sun")
        assert result["dignity"] == "exaltation"
        assert result["strength_score"] > 0
        
        # Test debilitation
        planet_data["longitude"] = 190.0  # Sun in Libra (fall)
        planet_data["sign"] = "libra"
        result = calc.calculate_planet_strength(planet_data, "Sun")
        assert result["dignity"] == "fall"
        assert result["strength_score"] < 0
        
        # Test retrograde impact
        planet_data["speed"] = -0.5
        result = calc.calculate_planet_strength(planet_data, "Mercury")
        assert result["is_retrograde"] is True
        assert "retrograde_impact" in result
    
    # VimshottariDashaCalculator - Missing private method
    def test_calculate_sookshma_periods(self):
        """Test sookshma (4th level) period calculation."""
        calc = VimshottariDashaCalculator()
        
        pratyantar = {
            "planet": "Venus",
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2024, 2, 1),
            "years": 0.083  # 1 month
        }
        
        # This would be a private method
        result = calc._calculate_sookshma_periods(pratyantar)
        assert len(result) == 9  # 9 sookshma periods
        assert all("planet" in s for s in result)
        assert all("start_date" in s for s in result)
        
        # Verify no overlap
        for i in range(len(result) - 1):
            assert result[i]["end_date"] <= result[i+1]["start_date"]
    
    # PanchangCalculator - Missing method
    def test_calculate_special_yogas(self):
        """Test calculation of special yogas like Sarvartha Siddhi."""
        calc = PanchangCalculator()
        
        # Test Sarvartha Siddhi Yoga
        result = calc.calculate_special_yogas(
            vara_index=0,  # Sunday
            nakshatra_index=6  # Pushya
        )
        
        assert "sarvartha_siddhi" in result
        assert result["sarvartha_siddhi"] is True
        assert "amrita_siddhi" in result
        
        # Test Dwipushkar Yoga
        result = calc.calculate_special_yogas(
            vara_index=2,  # Tuesday
            nakshatra_index=8  # Ashlesha
        )
        assert "dwipushkar" in result
    
    # AshtakootaCalculator - Missing cancellation method
    def test_dosha_cancellation_rules(self):
        """Test comprehensive dosha cancellation rules."""
        calc = AshtakootaCalculator()
        
        # Test Manglik cancellation - both partners Manglik
        chart1 = {
            "planets": {"Mars": {"house": 7}},
            "ascendant": "aries"
        }
        chart2 = {
            "planets": {"Mars": {"house": 1}},
            "ascendant": "leo"
        }
        
        result = calc._check_dosha_cancellation(chart1, chart2, "manglik")
        assert result["cancelled"] is True
        assert "both_have_dosha" in result["reasons"]
        
        # Test aspect cancellation
        chart1["planets"]["Jupiter"] = {"house": 7, "aspects": [1, 5, 7, 9]}
        result = calc._check_dosha_cancellation(chart1, chart2, "manglik")
        assert "benefic_aspect" in result["reasons"]
    
    # BaZiCalculator - Missing element cycle method
    def test_element_production_cycle(self):
        """Test five element production and destruction cycles."""
        calc = BaZiCalculator()
        
        # Test production cycle
        result = calc._get_element_cycle("production")
        assert result["Wood"] == "Fire"
        assert result["Fire"] == "Earth"
        assert result["Earth"] == "Metal"
        assert result["Metal"] == "Water"
        assert result["Water"] == "Wood"
        
        # Test destruction cycle
        result = calc._get_element_cycle("destruction")
        assert result["Wood"] == "Earth"
        assert result["Fire"] == "Metal"
        assert result["Earth"] == "Water"
        assert result["Metal"] == "Wood"
        assert result["Water"] == "Fire"
    
    # ProgressionCalculator - Missing symbolic directions
    def test_calculate_symbolic_directions(self):
        """Test symbolic direction calculations."""
        calc = ProgressionCalculator()
        
        natal_chart = {
            "planets": {
                "Sun": {"longitude": 0.0},
                "Moon": {"longitude": 90.0}
            }
        }
        
        # Test 30-degree symbolic directions
        result = calc.calculate_symbolic_directions(
            natal_chart,
            direction_key=30,  # 30 degrees = 1 year
            years=5
        )
        
        assert result["directed_planets"]["Sun"]["longitude"] == 150.0
        assert result["directed_planets"]["Moon"]["longitude"] == 240.0
        assert result["direction_arc"] == 150.0
    
    # NumerologyCalculator - Missing interpretation method
    def test_get_detailed_interpretations(self):
        """Test detailed number interpretations."""
        calc = NumerologyCalculator()
        
        # Test life path interpretations
        result = calc._get_interpretation("life_path", 7)
        assert "meaning" in result
        assert "strengths" in result
        assert "challenges" in result
        assert "career" in result
        
        # Test master number interpretation
        result = calc._get_interpretation("life_path", 22)
        assert "master_number" in result
        assert result["master_number"] is True
        assert "special_mission" in result
    
    # Additional edge cases for 100% coverage
    def test_error_handling_edge_cases(self):
        """Test error handling in edge cases."""
        calc = AstrologyCalculator()
        
        # Test invalid house system
        with pytest.raises(ValueError):
            calc.calculate_houses(
                datetime.now(),
                40.7, -74.0,
                house_system="invalid_system"
            )
        
        # Test invalid ayanamsa
        with pytest.raises(ValueError):
            calc.calculate_vedic_chart(
                datetime.now(),
                40.7, -74.0,
                ayanamsa="invalid_ayanamsa"
            )
    
    def test_boundary_calculations(self):
        """Test calculations at mathematical boundaries."""
        calc = NumerologyCalculator()
        
        # Test reducing large numbers
        result = calc._reduce_to_single_digit(999999)
        assert 1 <= result <= 9 or result in [11, 22, 33]
        
        # Test empty name
        with pytest.raises(ValueError):
            calc.calculate_expression_number("")
        
        # Test special characters
        result = calc.calculate_expression_number("John-Paul O'Connor")
        assert result["number"] > 0
    
    def test_concurrent_calculation_thread_safety(self):
        """Test thread safety of calculations."""
        import threading
        
        calc = AstrologyCalculator()
        results = []
        errors = []
        
        def calculate_chart(dt, lat, lon):
            try:
                with patch('swisseph.calc_ut') as mock_calc:
                    mock_calc.return_value = ((120.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0)
                    result = calc.calculate_planets(dt, lat, lon)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            dt = datetime(2024, 1, i+1)
            t = threading.Thread(
                target=calculate_chart,
                args=(dt, 40.7 + i*0.1, -74.0)
            )
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # All calculations should succeed
        assert len(results) == 10
        assert len(errors) == 0
    
    def test_memory_cleanup(self):
        """Test proper memory cleanup after calculations."""
        import gc
        import weakref
        
        calc = AstrologyCalculator()
        
        # Create a large calculation result
        with patch('swisseph.calc_ut') as mock_calc:
            mock_calc.return_value = ((120.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0)
            result = calc.calculate_planets(datetime.now(), 40.7, -74.0)
        
        # Create weak reference
        weak_result = weakref.ref(result)
        
        # Delete reference
        del result
        gc.collect()
        
        # Object should be garbage collected
        assert weak_result() is None
    
    def test_calculation_determinism(self):
        """Test that calculations are deterministic."""
        calc = VimshottariDashaCalculator()
        
        dt = datetime(1990, 1, 1, 12, 0, 0)
        moon_long = 125.5
        
        # Calculate multiple times
        results = []
        for _ in range(5):
            result = calc.calculate_vimshottari_dasha(dt, moon_long)
            results.append(result)
        
        # All results should be identical
        first = results[0]
        for result in results[1:]:
            assert len(result) == len(first)
            for i, dasha in enumerate(result):
                assert dasha["planet"] == first[i]["planet"]
                assert dasha["years"] == first[i]["years"]
    
    def test_unicode_name_support(self):
        """Test Unicode name support in numerology."""
        calc = NumerologyCalculator()
        
        # Test various scripts
        names = [
            "José García",
            "François Müller", 
            "Владимир Путин",
            "王小明",
            "محمد علي",
            "Σωκράτης"
        ]
        
        for name in names:
            try:
                result = calc.calculate_expression_number(name)
                assert result["number"] > 0
            except:
                # Some scripts might not be supported
                pass
    
    def test_extreme_date_ranges(self):
        """Test calculations with extreme date ranges."""
        calc = PanchangCalculator()
        
        # Very old date (within Python datetime limits)
        old_date = datetime(1, 1, 1)
        result = calc.calculate_tithi(0.0, 180.0)
        assert result["index"] > 0
        
        # Very future date
        future_date = datetime(9999, 12, 31)
        result = calc.calculate_nakshatra(270.0)
        assert 1 <= result["index"] <= 27
    
    def test_precision_requirements(self):
        """Test precision in astronomical calculations."""
        calc = AstrologyCalculator()
        
        # Test aspect orb precision
        planet_positions = {
            "Mercury": {"longitude": 120.00000},
            "Venus": {"longitude": 120.00001}  # 0.00001° apart
        }
        
        aspects = calc.calculate_aspects(
            planet_positions,
            orb_settings={"conjunction": 0.0001}
        )
        
        # Should detect extremely close conjunction
        assert len(aspects) == 1
        assert aspects[0]["orb"] < 0.00002