"""
Astronomical accuracy verification tests.
These tests verify calculations against known correct values.
"""
import pytest
from datetime import datetime
import math

# Import without mocking to test real calculations
from josi.services.astrology_service import AstrologyCalculator


class TestAstronomicalAccuracy:
    """Verify astronomical calculations against known correct values."""
    
    @pytest.fixture
    def calculator(self):
        """Real calculator without mocking."""
        return AstrologyCalculator()
    
    def test_sun_position_j2000(self, calculator):
        """Test Sun position at J2000 epoch."""
        # J2000.0 = January 1, 2000, 12:00 TT
        # Expected Sun longitude: 280.46° (from astronomical tables)
        j2000 = datetime(2000, 1, 1, 12, 0, 0)
        
        result = calculator.calculate_planets(j2000, 0, 0)
        sun_longitude = result['Sun']['longitude']
        
        # Should be within 0.01 degrees
        expected = 280.46
        assert abs(sun_longitude - expected) < 0.01, \
            f"Sun longitude {sun_longitude} differs from expected {expected}"
    
    def test_moon_position_known_full_moon(self, calculator):
        """Test Moon position at known full moon."""
        # Full Moon on July 13, 2022, 18:37 UTC
        # Moon should be ~180° from Sun (opposition)
        full_moon_time = datetime(2022, 7, 13, 18, 37, 0)
        
        result = calculator.calculate_planets(full_moon_time, 0, 0)
        sun_long = result['Sun']['longitude']
        moon_long = result['Moon']['longitude']
        
        # Calculate angular separation
        diff = abs(moon_long - sun_long)
        if diff > 180:
            diff = 360 - diff
        
        # Should be very close to 180° at full moon
        assert abs(diff - 180) < 1.0, \
            f"Sun-Moon separation {diff} not close to 180° at full moon"
    
    def test_spring_equinox_2024(self, calculator):
        """Test Sun position at Spring Equinox 2024."""
        # Spring Equinox 2024: March 20, 03:06 UTC
        # Sun should be at 0° Aries (0° longitude)
        equinox = datetime(2024, 3, 20, 3, 6, 0)
        
        result = calculator.calculate_planets(equinox, 0, 0)
        sun_longitude = result['Sun']['longitude']
        
        # Should be very close to 0°
        assert abs(sun_longitude) < 0.1 or abs(sun_longitude - 360) < 0.1, \
            f"Sun not at 0° Aries during spring equinox: {sun_longitude}"
    
    def test_mercury_retrograde_2024(self, calculator):
        """Test Mercury retrograde detection."""
        # Mercury retrograde period in 2024
        # April 1-25, 2024 (one of the periods)
        
        # Before retrograde
        before = datetime(2024, 3, 28, 0, 0, 0)
        is_retro_before = calculator.is_planet_retrograde("Mercury", before)
        assert not is_retro_before, "Mercury should be direct before retrograde"
        
        # During retrograde
        during = datetime(2024, 4, 10, 0, 0, 0)
        is_retro_during = calculator.is_planet_retrograde("Mercury", during)
        assert is_retro_during, "Mercury should be retrograde on April 10, 2024"
        
        # After retrograde
        after = datetime(2024, 4, 28, 0, 0, 0)
        is_retro_after = calculator.is_planet_retrograde("Mercury", after)
        assert not is_retro_after, "Mercury should be direct after retrograde"
    
    def test_ascendant_calculation_known_case(self, calculator):
        """Test Ascendant calculation for known case."""
        # New York City, Jan 1, 2000, 00:00 EST
        # Expected ASC: approximately 3° Libra (183°)
        nyc_lat = 40.7128
        nyc_lon = -74.0060
        dt = datetime(2000, 1, 1, 0, 0, 0)  # Midnight
        
        houses = calculator.calculate_houses(dt, nyc_lat, nyc_lon, "placidus")
        asc = houses.get("1", houses.get("ASC", 0))
        
        # Should be in Libra (180-210°)
        assert 180 <= asc <= 210, \
            f"Ascendant {asc} not in expected range for NYC midnight"
    
    def test_mc_calculation_noon(self, calculator):
        """Test MC calculation at noon."""
        # At solar noon, Sun should be near MC
        # London, June 21, 2024, 12:00 (summer solstice)
        london_lat = 51.5074
        london_lon = -0.1278
        dt = datetime(2024, 6, 21, 12, 0, 0)
        
        planets = calculator.calculate_planets(dt, london_lat, london_lon)
        houses = calculator.calculate_houses(dt, london_lat, london_lon)
        
        sun_long = planets['Sun']['longitude']
        mc = houses.get("10", houses.get("MC", 0))
        
        # Sun should be within 30° of MC at noon
        diff = abs(sun_long - mc)
        if diff > 180:
            diff = 360 - diff
        
        assert diff < 30, \
            f"Sun {sun_long} too far from MC {mc} at noon"
    
    def test_house_system_consistency(self, calculator):
        """Test that house systems are internally consistent."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        lat, lon = 40.7128, -74.0060
        
        # Equal houses should all be 30° apart
        equal_houses = calculator.calculate_houses(dt, lat, lon, "equal")
        for i in range(1, 12):
            current = equal_houses.get(str(i), 0)
            next_house = equal_houses.get(str(i + 1), 0)
            diff = (next_house - current) % 360
            assert abs(diff - 30) < 0.1, \
                f"Equal houses {i} and {i+1} not 30° apart"
        
        # Whole sign houses should align with signs
        whole_houses = calculator.calculate_houses(dt, lat, lon, "whole_sign")
        asc = whole_houses.get("1", 0)
        first_house_start = int(asc / 30) * 30
        
        for i in range(1, 13):
            expected = (first_house_start + (i - 1) * 30) % 360
            actual = whole_houses.get(str(i), 0)
            assert abs(actual - expected) < 0.1, \
                f"Whole sign house {i} not aligned with signs"


class TestVedicCalculations:
    """Verify Vedic astrology calculations."""
    
    def test_ayanamsa_values(self):
        """Test Lahiri ayanamsa for known dates."""
        calculator = AstrologyCalculator()
        
        # Known Lahiri ayanamsa values
        test_cases = [
            (datetime(1900, 1, 1), 22.46),
            (datetime(1950, 1, 1), 23.09),
            (datetime(2000, 1, 1), 23.85),
            (datetime(2024, 1, 1), 24.16),
        ]
        
        for dt, expected in test_cases:
            actual = calculator.get_ayanamsa_value(dt, "lahiri")
            # Should be within 0.05 degrees
            assert abs(actual - expected) < 0.05, \
                f"Ayanamsa for {dt.year} is {actual}, expected ~{expected}"
    
    def test_nakshatra_calculation(self):
        """Test nakshatra calculation from longitude."""
        from josi.services.vedic.panchang_service import PanchangCalculator
        calc = PanchangCalculator()
        
        # Each nakshatra is 13°20' (13.333°)
        test_cases = [
            (0.0, 1, "Ashwini"),      # 0° = Ashwini
            (13.333, 2, "Bharani"),   # 13°20' = Bharani
            (26.666, 3, "Krittika"),  # 26°40' = Krittika
            (120.0, 10, "Magha"),     # 120° = Magha
        ]
        
        for longitude, expected_index, expected_name in test_cases:
            result = calc.calculate_nakshatra(longitude)
            assert result["index"] == expected_index, \
                f"Longitude {longitude} should be nakshatra {expected_index}"
            assert result["name"] == expected_name, \
                f"Nakshatra name mismatch for {longitude}"
    
    def test_tithi_calculation(self):
        """Test tithi calculation."""
        from josi.services.vedic.panchang_service import PanchangCalculator
        calc = PanchangCalculator()
        
        # Tithi = (Moon - Sun) / 12
        test_cases = [
            (0, 0, 1, "Shukla Pratipada"),      # New Moon
            (0, 180, 15, "Purnima"),            # Full Moon
            (0, 90, 8, "Shukla Ashtami"),       # First Quarter
            (0, 270, 23, "Krishna Ashtami"),    # Last Quarter
        ]
        
        for sun_long, moon_long, expected_index, expected_name in test_cases:
            result = calc.calculate_tithi(sun_long, moon_long)
            assert result["index"] == expected_index, \
                f"Tithi calculation wrong for Sun={sun_long}, Moon={moon_long}"


class TestChineseAstrology:
    """Verify Chinese astrology calculations."""
    
    def test_chinese_zodiac_years(self):
        """Test Chinese zodiac animal years."""
        from josi.services.chinese.bazi_calculator_service import BaZiCalculator
        calc = BaZiCalculator()
        
        # Known zodiac years
        test_cases = [
            (2024, "Dragon"),
            (2023, "Rabbit"),
            (2022, "Tiger"),
            (2021, "Ox"),
            (2020, "Rat"),
            (1990, "Horse"),
            (1984, "Rat"),  # Rat repeats every 12 years
        ]
        
        for year, expected_animal in test_cases:
            result = calc.calculate_year_pillar(year, 6, 15)  # Mid-year date
            assert result["branch"] == expected_animal, \
                f"Year {year} should be {expected_animal}, got {result['branch']}"


class TestNumerology:
    """Verify numerology calculations."""
    
    def test_life_path_calculation(self):
        """Test life path number calculation."""
        from josi.services.numerology_service import NumerologyCalculator
        calc = NumerologyCalculator()
        
        # Known examples
        test_cases = [
            # Date format: YYYY-MM-DD
            (datetime(1990, 8, 15), 6),  # 1+9+9+0+8+1+5 = 33 = 6
            (datetime(2000, 1, 1), 4),   # 2+0+0+0+1+1 = 4
            (datetime(1955, 10, 28), 4), # 1+9+5+5+1+0+2+8 = 31 = 4
        ]
        
        for birth_date, expected in test_cases:
            result = calc.calculate_life_path_number(birth_date)
            assert result["reduced"] == expected, \
                f"Life path for {birth_date} should be {expected}"
    
    def test_expression_number(self):
        """Test expression number from name."""
        from josi.services.numerology_service import NumerologyCalculator
        calc = NumerologyCalculator()
        
        # Using Pythagorean system
        # A=1, B=2, C=3... I=9, J=1, K=2...
        result = calc.calculate_expression_number("JOHN")
        # J=1, O=6, H=8, N=5 = 20 = 2
        assert result["reduced"] == 2, "JOHN should reduce to 2"


class TestAccuracyMetrics:
    """Overall accuracy metrics and benchmarks."""
    
    def test_calculation_precision(self):
        """Test that calculations maintain sufficient precision."""
        calc = AstrologyCalculator()
        dt = datetime(2024, 1, 1, 12, 0, 0)
        
        # Run same calculation multiple times
        results = []
        for _ in range(5):
            result = calc.calculate_planets(dt, 40.7128, -74.0060)
            results.append(result['Sun']['longitude'])
        
        # All results should be identical
        assert all(r == results[0] for r in results), \
            "Calculations not deterministic"
        
        # Should have reasonable precision (not rounded to integers)
        sun_pos = results[0]
        assert sun_pos != int(sun_pos), \
            "Calculation precision too low"
        
    def test_performance_benchmarks(self):
        """Test that calculations complete in reasonable time."""
        import time
        calc = AstrologyCalculator()
        
        # Single chart calculation
        start = time.time()
        calc.calculate_western_chart(
            datetime.now(), 40.7128, -74.0060
        )
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Chart calculation too slow: {elapsed}s"


def run_verification_suite():
    """Run all verification tests and generate report."""
    print("Running Astronomical Accuracy Verification Suite...")
    print("=" * 60)
    
    # This would run all tests and generate detailed report
    # showing accuracy metrics and any failures
    
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_verification_suite()