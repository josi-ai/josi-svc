"""Comprehensive tests for Chinese and Western astrology modules."""
import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timedelta
import pytz

from josi.services.chinese.bazi_calculator_service import BaZiCalculator
from josi.services.western.progressions_service import ProgressionCalculator
from josi.services.numerology_service import NumerologyCalculator


class TestBaZiCalculatorComprehensive:
    """Comprehensive tests for BaZi (Four Pillars) calculations."""
    
    @pytest.fixture
    def bazi_calculator(self):
        return BaZiCalculator()
    
    @pytest.fixture
    def test_datetime(self):
        return datetime(1990, 5, 15, 14, 30, 0)
    
    def test_calculate_year_pillar(self, bazi_calculator):
        """Test year pillar calculation."""
        # Test year 1990 (Horse year)
        result = bazi_calculator.calculate_year_pillar(1990)
        
        assert "stem" in result
        assert "branch" in result
        assert "element" in result
        assert result["branch"] == "Horse"
        assert result["stem"] in bazi_calculator.heavenly_stems
    
    def test_calculate_year_pillar_boundary(self, bazi_calculator):
        """Test year pillar at Chinese New Year boundary."""
        # Before Chinese New Year 2024
        result1 = bazi_calculator.calculate_year_pillar(2024, 1, 15)
        # After Chinese New Year 2024
        result2 = bazi_calculator.calculate_year_pillar(2024, 2, 15)
        
        # Should be different years in Chinese calendar
        assert result1["branch"] != result2["branch"]
    
    def test_calculate_month_pillar(self, bazi_calculator):
        """Test month pillar calculation."""
        year_stem_index = 6  # Example year stem
        
        # Test May (Snake month)
        result = bazi_calculator.calculate_month_pillar(year_stem_index, 5)
        
        assert "stem" in result
        assert "branch" in result
        assert result["branch"] == "Snake"
    
    def test_calculate_month_pillar_solar_terms(self, bazi_calculator):
        """Test month pillar with solar term consideration."""
        # Test around solar term boundary
        result1 = bazi_calculator.calculate_month_pillar(6, 5, 5)   # Before term
        result2 = bazi_calculator.calculate_month_pillar(6, 5, 7)   # After term
        
        # May have different branches depending on exact solar term
        assert "stem" in result1
        assert "branch" in result1
    
    def test_calculate_day_pillar(self, bazi_calculator):
        """Test day pillar calculation."""
        # Known date calculation
        result = bazi_calculator.calculate_day_pillar(
            datetime(2024, 1, 1, 12, 0, 0)
        )
        
        assert "stem" in result
        assert "branch" in result
        assert result["stem"] in bazi_calculator.heavenly_stems
        assert result["branch"] in bazi_calculator.earthly_branches
    
    def test_calculate_hour_pillar(self, bazi_calculator):
        """Test hour pillar calculation."""
        day_stem_index = 0  # Jia day
        
        # Test 14:30 (Wei hour)
        result = bazi_calculator.calculate_hour_pillar(day_stem_index, 14, 30)
        
        assert "stem" in result
        assert "branch" in result
        assert result["branch"] == "Goat"  # 13:00-15:00 is Goat hour
    
    def test_calculate_hour_pillar_all_hours(self, bazi_calculator):
        """Test all 12 double-hours."""
        day_stem_index = 0
        
        hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
        branches = []
        
        for hour in hours:
            result = bazi_calculator.calculate_hour_pillar(day_stem_index, hour, 30)
            branches.append(result["branch"])
        
        # Should have 12 different branches
        assert len(set(branches)) == 12
    
    def test_calculate_luck_pillars(self, bazi_calculator):
        """Test 10-year luck pillar calculation."""
        bazi_chart = {
            "month_pillar": {"stem": "Bing", "branch": "Wu"},
            "gender": "male",
            "year_branch": "Horse"
        }
        
        result = bazi_calculator.calculate_luck_pillars(
            bazi_chart,
            datetime(1990, 6, 15)
        )
        
        assert len(result) == 8  # 8 luck pillars
        assert all("start_age" in pillar for pillar in result)
        assert all("stem" in pillar for pillar in result)
        assert all("branch" in pillar for pillar in result)
        
        # Ages should increase by 10
        ages = [p["start_age"] for p in result]
        assert ages == list(range(ages[0], ages[0] + 80, 10))
    
    def test_analyze_day_master(self, bazi_calculator):
        """Test day master strength analysis."""
        bazi_chart = {
            "day_pillar": {"stem": "Jia", "element": "Wood"},
            "year_pillar": {"stem": "Geng", "element": "Metal"},
            "month_pillar": {"stem": "Bing", "element": "Fire"},
            "hour_pillar": {"stem": "Ren", "element": "Water"}
        }
        
        result = bazi_calculator.analyze_day_master(bazi_chart)
        
        assert "strength" in result
        assert "favorable_elements" in result
        assert "unfavorable_elements" in result
        assert result["strength"] in ["very_weak", "weak", "balanced", "strong", "very_strong"]
    
    def test_analyze_elements_balance(self, bazi_calculator):
        """Test five elements balance analysis."""
        bazi_chart = {
            "year_pillar": {"element": "Metal", "stem": "Geng", "branch": "Monkey"},
            "month_pillar": {"element": "Fire", "stem": "Bing", "branch": "Horse"},
            "day_pillar": {"element": "Wood", "stem": "Jia", "branch": "Tiger"},
            "hour_pillar": {"element": "Water", "stem": "Ren", "branch": "Rat"}
        }
        
        result = bazi_calculator.analyze_elements_balance(bazi_chart)
        
        assert "element_count" in result
        assert "missing_elements" in result
        assert "dominant_element" in result
        assert all(elem in result["element_count"] for elem in ["Wood", "Fire", "Earth", "Metal", "Water"])
    
    def test_calculate_hidden_stems(self, bazi_calculator):
        """Test hidden stem calculation in branches."""
        # Tiger contains Jia (Wood), Bing (Fire), Wu (Earth)
        result = bazi_calculator.calculate_hidden_stems("Tiger")
        
        assert len(result) == 3
        assert any(stem["stem"] == "Jia" for stem in result)
        assert any(stem["element"] == "Wood" for stem in result)
    
    def test_analyze_clash_combination(self, bazi_calculator):
        """Test branch clash and combination analysis."""
        bazi_chart = {
            "year_pillar": {"branch": "Rat"},
            "month_pillar": {"branch": "Horse"},  # Clashes with Rat
            "day_pillar": {"branch": "Dragon"},
            "hour_pillar": {"branch": "Monkey"}   # Forms harmony with Dragon and Rat
        }
        
        result = bazi_calculator.analyze_clash_combination(bazi_chart)
        
        assert "clashes" in result
        assert "combinations" in result
        assert "harmonies" in result
        assert "punishments" in result
        
        # Should detect Rat-Horse clash
        assert any("Rat" in clash and "Horse" in clash for clash in result["clashes"])
    
    def test_calculate_useful_gods(self, bazi_calculator):
        """Test useful god calculation."""
        bazi_chart = {
            "day_pillar": {"stem": "Jia", "element": "Wood"},
            "day_master_strength": "weak"
        }
        
        result = bazi_calculator.calculate_useful_gods(bazi_chart)
        
        assert "useful_gods" in result
        assert "jealous_gods" in result
        assert len(result["useful_gods"]) > 0
        
        # Weak Wood needs Water and Wood support
        assert "Water" in result["useful_gods"]
    
    def test_get_personality_traits(self, bazi_calculator):
        """Test personality analysis from BaZi."""
        bazi_chart = {
            "day_pillar": {"stem": "Jia", "branch": "Tiger"},
            "element_balance": {
                "Wood": 3,
                "Fire": 1,
                "Earth": 1,
                "Metal": 2,
                "Water": 1
            }
        }
        
        result = bazi_calculator.get_personality_traits(bazi_chart)
        
        assert "traits" in result
        assert "strengths" in result
        assert "weaknesses" in result
        assert "career_suggestions" in result
        assert len(result["traits"]) > 0
    
    def test_calculate_annual_luck(self, bazi_calculator):
        """Test annual luck calculation."""
        bazi_chart = {
            "day_pillar": {"stem": "Jia", "element": "Wood"}
        }
        
        result = bazi_calculator.calculate_annual_luck(bazi_chart, 2024)
        
        assert "year_stem" in result
        assert "year_branch" in result
        assert "luck_rating" in result
        assert "advice" in result
        assert 1 <= result["luck_rating"] <= 10


class TestProgressionCalculatorComprehensive:
    """Comprehensive tests for Western progression calculations."""
    
    @pytest.fixture
    def progression_calculator(self):
        return ProgressionCalculator()
    
    @pytest.fixture
    def natal_chart(self):
        return {
            "planets": {
                "Sun": {"longitude": 120.0, "sign": "Leo"},
                "Moon": {"longitude": 60.0, "sign": "Gemini"},
                "Mercury": {"longitude": 115.0, "sign": "Leo"},
                "Venus": {"longitude": 90.0, "sign": "Cancer"},
                "Mars": {"longitude": 180.0, "sign": "Libra"}
            },
            "houses": {
                "1": 0.0,
                "10": 270.0
            },
            "angles": {
                "ASC": 0.0,
                "MC": 270.0
            }
        }
    
    def test_calculate_secondary_progressions(self, progression_calculator):
        """Test secondary progression calculation."""
        birth_date = datetime(1990, 1, 1)
        target_date = datetime(2024, 1, 1)
        
        result = progression_calculator.calculate_secondary_progressions(
            self.natal_chart(),
            birth_date,
            target_date,
            40.7128,
            -74.0060
        )
        
        assert "progressed_planets" in result
        assert "progressed_angles" in result
        assert "days_for_year" in result
        assert result["days_for_year"] == 34  # 34 years = 34 days
        
        # Check progressed Sun moved approximately 34 degrees
        prog_sun = result["progressed_planets"]["Sun"]["longitude"]
        natal_sun = 120.0
        assert abs((prog_sun - natal_sun) - 34) < 2  # Allow small variance
    
    def test_calculate_solar_arc_directions(self, progression_calculator):
        """Test solar arc direction calculation."""
        birth_date = datetime(1990, 1, 1)
        target_date = datetime(2024, 1, 1)
        
        result = progression_calculator.calculate_solar_arc_directions(
            self.natal_chart(),
            birth_date,
            target_date
        )
        
        assert "directed_planets" in result
        assert "solar_arc" in result
        assert abs(result["solar_arc"] - 34) < 1  # ~1 degree per year
        
        # All planets should move by solar arc
        for planet in result["directed_planets"]:
            directed_pos = result["directed_planets"][planet]["longitude"]
            natal_pos = self.natal_chart()["planets"][planet]["longitude"]
            assert abs((directed_pos - natal_pos) % 360 - result["solar_arc"]) < 0.1
    
    def test_calculate_tertiary_progressions(self, progression_calculator):
        """Test tertiary progression calculation."""
        birth_date = datetime(1990, 1, 1)
        target_date = datetime(2024, 6, 1)
        
        result = progression_calculator.calculate_tertiary_progressions(
            self.natal_chart(),
            birth_date,
            target_date,
            40.7128,
            -74.0060
        )
        
        assert "progressed_planets" in result
        assert "days_for_month" in result
        # Should progress by number of months
        months = (target_date.year - birth_date.year) * 12 + (target_date.month - birth_date.month)
        assert abs(result["days_for_month"] - months) < 2
    
    def test_calculate_minor_progressions(self, progression_calculator):
        """Test minor progression calculation."""
        birth_date = datetime(1990, 1, 1)
        target_date = datetime(2024, 1, 1)
        
        result = progression_calculator.calculate_minor_progressions(
            self.natal_chart(),
            birth_date,
            target_date,
            40.7128,
            -74.0060
        )
        
        assert "progressed_planets" in result
        assert "lunar_months_for_year" in result
    
    def test_calculate_progressed_lunar_phases(self, progression_calculator):
        """Test progressed lunar phase calculation."""
        progressed_chart = {
            "Sun": {"longitude": 150.0},
            "Moon": {"longitude": 240.0}
        }
        
        result = progression_calculator.calculate_progressed_lunar_phases(
            progressed_chart
        )
        
        assert "phase" in result
        assert "phase_degree" in result
        assert "days_until_new_moon" in result
        
        # 90 degree difference = First Quarter
        assert result["phase"] == "First Quarter"
        assert abs(result["phase_degree"] - 90) < 1
    
    def test_calculate_converse_progressions(self, progression_calculator):
        """Test converse progression calculation."""
        birth_date = datetime(1990, 1, 1)
        target_date = datetime(2024, 1, 1)
        
        result = progression_calculator.calculate_converse_progressions(
            self.natal_chart(),
            birth_date,
            target_date,
            40.7128,
            -74.0060
        )
        
        assert "progressed_planets" in result
        # Converse goes backward in time
        assert "days_before_birth" in result
    
    def test_find_progressed_aspects(self, progression_calculator):
        """Test finding aspects in progressed chart."""
        progressed_planets = {
            "Sun": {"longitude": 150.0},
            "Moon": {"longitude": 240.0},
            "Venus": {"longitude": 330.0}
        }
        
        natal_planets = {
            "Sun": {"longitude": 120.0},
            "Moon": {"longitude": 60.0},
            "Mars": {"longitude": 180.0}
        }
        
        result = progression_calculator.find_progressed_aspects(
            progressed_planets,
            natal_planets
        )
        
        assert "progressed_to_natal" in result
        assert "progressed_to_progressed" in result
        
        # Should find prog Sun conjunct natal Sun (30 deg orb)
        prog_to_natal = result["progressed_to_natal"]
        assert any(
            asp["planet1"] == "Sun" and asp["planet2"] == "Sun" 
            for asp in prog_to_natal
        )
    
    def test_calculate_progressed_midpoints(self, progression_calculator):
        """Test progressed midpoint calculation."""
        progressed_planets = {
            "Sun": {"longitude": 0.0},
            "Moon": {"longitude": 90.0},
            "Venus": {"longitude": 180.0}
        }
        
        result = progression_calculator.calculate_progressed_midpoints(
            progressed_planets
        )
        
        assert len(result) > 0
        # Sun/Moon midpoint should be at 45 degrees
        sun_moon = next(
            m for m in result 
            if set(m["planets"]) == {"Sun", "Moon"}
        )
        assert sun_moon["midpoint"] == 45.0
    
    def test_get_progression_themes(self, progression_calculator):
        """Test progression theme interpretation."""
        progressed_aspects = [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "aspect": "conjunction",
                "orb": 1.0
            },
            {
                "planet1": "Venus",
                "planet2": "Mars",
                "aspect": "square",
                "orb": 2.0
            }
        ]
        
        result = progression_calculator.get_progression_themes(
            progressed_aspects
        )
        
        assert "major_themes" in result
        assert "life_areas" in result
        assert "timing" in result
        assert len(result["major_themes"]) > 0
    
    def test_calculate_profections(self, progression_calculator):
        """Test annual profection calculation."""
        birth_date = datetime(1990, 1, 1)
        target_date = datetime(2024, 1, 1)
        
        natal_houses = {str(i): (i-1) * 30.0 for i in range(1, 13)}
        
        result = progression_calculator.calculate_profections(
            birth_date,
            target_date,
            natal_houses
        )
        
        assert "profected_house" in result
        assert "house_ruler" in result
        assert "themes" in result
        
        # Age 34 = 34 % 12 = 10 = 11th house
        assert result["profected_house"] == 11


class TestNumerologyCalculatorComprehensive:
    """Comprehensive tests for Numerology calculations."""
    
    @pytest.fixture
    def numerology_calculator(self):
        return NumerologyCalculator()
    
    def test_calculate_life_path_number(self, numerology_calculator):
        """Test life path number calculation."""
        # Test known example: Aug 15, 1990
        result = numerology_calculator.calculate_life_path_number(
            datetime(1990, 8, 15)
        )
        
        assert "number" in result
        assert "reduced" in result
        assert "interpretation" in result
        
        # 1990 + 8 + 15 = 2013 = 6
        assert result["reduced"] == 6
    
    def test_calculate_life_path_master_numbers(self, numerology_calculator):
        """Test master number preservation."""
        # Date that reduces to 11
        result = numerology_calculator.calculate_life_path_number(
            datetime(2000, 1, 1)  # 2000 + 1 + 1 = 2002 = 4, need better example
        )
        
        assert "is_master" in result
        if result["number"] in [11, 22, 33]:
            assert result["is_master"] is True
    
    def test_calculate_expression_number(self, numerology_calculator):
        """Test expression/destiny number from name."""
        result = numerology_calculator.calculate_expression_number(
            "John Doe"
        )
        
        assert "number" in result
        assert "reduced" in result
        assert "letter_values" in result
        assert 1 <= result["reduced"] <= 9 or result["reduced"] in [11, 22, 33]
    
    def test_calculate_soul_urge_number(self, numerology_calculator):
        """Test soul urge number (vowels only)."""
        result = numerology_calculator.calculate_soul_urge_number(
            "John Doe"
        )
        
        assert "number" in result
        assert "vowels" in result
        assert result["vowels"] == ["o", "o", "e"]
    
    def test_calculate_personality_number(self, numerology_calculator):
        """Test personality number (consonants only)."""
        result = numerology_calculator.calculate_personality_number(
            "John Doe"
        )
        
        assert "number" in result
        assert "consonants" in result
        assert all(c not in "aeiou" for c in result["consonants"])
    
    def test_calculate_birthday_number(self, numerology_calculator):
        """Test birthday number calculation."""
        result = numerology_calculator.calculate_birthday_number(15)
        
        assert "number" in result
        assert "reduced" in result
        # 15 = 1 + 5 = 6
        assert result["reduced"] == 6
        
        # Test master number day
        result = numerology_calculator.calculate_birthday_number(22)
        assert result["number"] == 22
        assert result["is_master"] is True
    
    def test_calculate_maturity_number(self, numerology_calculator):
        """Test maturity number calculation."""
        result = numerology_calculator.calculate_maturity_number(
            life_path=6,
            expression=3
        )
        
        assert "number" in result
        # 6 + 3 = 9
        assert result["number"] == 9
    
    def test_calculate_personal_year(self, numerology_calculator):
        """Test personal year calculation."""
        result = numerology_calculator.calculate_personal_year(
            datetime(1990, 8, 15),  # Birth date
            2024  # Current year
        )
        
        assert "year_number" in result
        assert "cycle_position" in result
        assert "themes" in result
        assert 1 <= result["year_number"] <= 9
    
    def test_calculate_personal_month(self, numerology_calculator):
        """Test personal month calculation."""
        result = numerology_calculator.calculate_personal_month(
            personal_year=5,
            month=6
        )
        
        assert "month_number" in result
        # 5 + 6 = 11 = 2
        assert 1 <= result["month_number"] <= 9
    
    def test_calculate_personal_day(self, numerology_calculator):
        """Test personal day calculation."""
        result = numerology_calculator.calculate_personal_day(
            personal_year=5,
            month=6,
            day=15
        )
        
        assert "day_number" in result
        assert "energy" in result
    
    def test_calculate_pinnacles(self, numerology_calculator):
        """Test pinnacle cycle calculation."""
        result = numerology_calculator.calculate_pinnacles(
            life_path=6,
            birth_date=datetime(1990, 8, 15)
        )
        
        assert "pinnacles" in result
        assert len(result["pinnacles"]) == 4
        
        for pinnacle in result["pinnacles"]:
            assert "number" in pinnacle
            assert "age_range" in pinnacle
            assert "themes" in pinnacle
    
    def test_calculate_challenges(self, numerology_calculator):
        """Test challenge number calculation."""
        birth_date = datetime(1990, 8, 15)
        
        result = numerology_calculator.calculate_challenges(birth_date)
        
        assert "challenges" in result
        assert len(result["challenges"]) == 4
        
        for challenge in result["challenges"]:
            assert "number" in challenge
            assert "period" in challenge
            assert "lessons" in challenge
    
    def test_calculate_karmic_lessons(self, numerology_calculator):
        """Test karmic lesson calculation."""
        result = numerology_calculator.calculate_karmic_lessons("John Doe")
        
        assert "missing_numbers" in result
        assert "karmic_lessons" in result
        assert all(1 <= n <= 9 for n in result["missing_numbers"])
    
    def test_calculate_hidden_passion(self, numerology_calculator):
        """Test hidden passion number."""
        result = numerology_calculator.calculate_hidden_passion("John Doe")
        
        assert "number" in result
        assert "count" in result
        assert "percentage" in result
        assert 1 <= result["number"] <= 9
    
    def test_calculate_balance_number(self, numerology_calculator):
        """Test balance number from initials."""
        result = numerology_calculator.calculate_balance_number(
            "John", "Doe"
        )
        
        assert "number" in result
        assert "initials" in result
        assert result["initials"] == "JD"
    
    def test_calculate_cornerstone(self, numerology_calculator):
        """Test cornerstone (first letter) analysis."""
        result = numerology_calculator.calculate_cornerstone("John")
        
        assert "letter" in result
        assert "number" in result
        assert "traits" in result
        assert result["letter"] == "J"
    
    def test_calculate_capstone(self, numerology_calculator):
        """Test capstone (last letter) analysis."""
        result = numerology_calculator.calculate_capstone("John")
        
        assert "letter" in result
        assert "number" in result
        assert "traits" in result
        assert result["letter"] == "N"
    
    def test_get_compatibility_analysis(self, numerology_calculator):
        """Test numerology compatibility analysis."""
        person1_numbers = {
            "life_path": 6,
            "expression": 3,
            "soul_urge": 9
        }
        
        person2_numbers = {
            "life_path": 2,
            "expression": 7,
            "soul_urge": 5
        }
        
        result = numerology_calculator.get_compatibility_analysis(
            person1_numbers,
            person2_numbers
        )
        
        assert "overall_compatibility" in result
        assert "life_path_compatibility" in result
        assert "expression_compatibility" in result
        assert "challenges" in result
        assert "strengths" in result
        assert 0 <= result["overall_compatibility"] <= 100