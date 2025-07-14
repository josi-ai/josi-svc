"""Comprehensive unit tests for Chinese Bazi calculator service."""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from josi.services.chinese.bazi_calculator_service import BaZiCalculator


class TestBaZiCalculator:
    """Comprehensive test coverage for BaZiCalculator."""
    
    @pytest.fixture
    def bazi_calculator(self):
        """Create a BaZiCalculator instance."""
        return BaZiCalculator()
    
    @pytest.fixture
    def test_datetime(self):
        """Test datetime for calculations."""
        return datetime(1990, 5, 15, 14, 30, 0)
    
    @pytest.fixture
    def test_location(self):
        """Test location for calculations."""
        return {
            'latitude': 39.9042,  # Beijing
            'longitude': 116.4074,
            'timezone': 'Asia/Shanghai'
        }
    
    def test_initialization(self, bazi_calculator):
        """Test BaZiCalculator initialization."""
        assert hasattr(bazi_calculator, 'calculate_bazi_chart')
        assert hasattr(bazi_calculator, 'HEAVENLY_STEMS')
        assert hasattr(bazi_calculator, 'EARTHLY_BRANCHES')
        assert hasattr(bazi_calculator, 'FIVE_ELEMENTS')
        
        # Check data structures
        assert len(bazi_calculator.HEAVENLY_STEMS) == 10
        assert len(bazi_calculator.EARTHLY_BRANCHES) == 12
        assert len(bazi_calculator.FIVE_ELEMENTS) == 5
    
    def test_calculate_bazi_chart_basic(self, bazi_calculator, test_datetime, test_location):
        """Test basic Bazi chart calculation."""
        result = bazi_calculator.calculate_bazi_chart(
            birth_datetime=test_datetime,
            location=test_location,
            gender='male'
        )
        
        assert 'four_pillars' in result
        assert 'year_pillar' in result['four_pillars']
        assert 'month_pillar' in result['four_pillars']
        assert 'day_pillar' in result['four_pillars']
        assert 'hour_pillar' in result['four_pillars']
        assert 'elements_balance' in result
        assert 'day_master' in result
        assert 'luck_pillars' in result
    
    def test_pillar_structure(self, bazi_calculator, test_datetime, test_location):
        """Test structure of each pillar."""
        result = bazi_calculator.calculate_bazi_chart(test_datetime, test_location, 'female')
        
        for pillar_name in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']:
            pillar = result['four_pillars'][pillar_name]
            assert 'stem' in pillar
            assert 'branch' in pillar
            assert 'stem_element' in pillar
            assert 'branch_element' in pillar
            assert 'hidden_stems' in pillar
            assert pillar['stem'] in bazi_calculator.HEAVENLY_STEMS
            assert pillar['branch'] in bazi_calculator.EARTHLY_BRANCHES
    
    def test_calculate_chinese_year(self, bazi_calculator):
        """Test Chinese year calculation."""
        # Test known years
        test_cases = [
            (datetime(2020, 2, 5), 2020),  # After Chinese New Year
            (datetime(2020, 1, 20), 2019),  # Before Chinese New Year
            (datetime(1990, 1, 27), 1990),  # After CNY (Jan 27, 1990)
            (datetime(1990, 1, 26), 1989),  # Before CNY
        ]
        
        for dt, expected_year in test_cases:
            chinese_year = bazi_calculator._get_chinese_year(dt)
            assert chinese_year == expected_year
    
    def test_calculate_year_pillar(self, bazi_calculator):
        """Test year pillar calculation."""
        # 1990 is Horse year (Geng Wu)
        dt = datetime(1990, 5, 15)
        stem, branch = bazi_calculator._calculate_year_pillar(dt)
        
        assert stem in bazi_calculator.HEAVENLY_STEMS
        assert branch in bazi_calculator.EARTHLY_BRANCHES
        assert branch == "Wu"  # Horse
    
    def test_calculate_month_pillar(self, bazi_calculator):
        """Test month pillar calculation."""
        # May is typically Snake month
        dt = datetime(1990, 5, 15)
        year_stem = "Geng"
        
        stem, branch = bazi_calculator._calculate_month_pillar(dt, year_stem)
        
        assert stem in bazi_calculator.HEAVENLY_STEMS
        assert branch in bazi_calculator.EARTHLY_BRANCHES
    
    def test_calculate_day_pillar(self, bazi_calculator):
        """Test day pillar calculation."""
        dt = datetime(1990, 5, 15)
        
        stem, branch = bazi_calculator._calculate_day_pillar(dt)
        
        assert stem in bazi_calculator.HEAVENLY_STEMS
        assert branch in bazi_calculator.EARTHLY_BRANCHES
    
    def test_calculate_hour_pillar(self, bazi_calculator):
        """Test hour pillar calculation."""
        # 14:30 is Wei hour (13:00-15:00)
        dt = datetime(1990, 5, 15, 14, 30)
        day_stem = "Bing"
        
        stem, branch = bazi_calculator._calculate_hour_pillar(dt, day_stem)
        
        assert stem in bazi_calculator.HEAVENLY_STEMS
        assert branch in bazi_calculator.EARTHLY_BRANCHES
        assert branch == "Wei"  # Goat hour
    
    def test_get_element_from_stem(self, bazi_calculator):
        """Test element determination from heavenly stem."""
        test_cases = [
            ("Jia", "Wood"), ("Yi", "Wood"),
            ("Bing", "Fire"), ("Ding", "Fire"),
            ("Wu", "Earth"), ("Ji", "Earth"),
            ("Geng", "Metal"), ("Xin", "Metal"),
            ("Ren", "Water"), ("Gui", "Water")
        ]
        
        for stem, expected_element in test_cases:
            element = bazi_calculator._get_element_from_stem(stem)
            assert element == expected_element
    
    def test_get_element_from_branch(self, bazi_calculator):
        """Test element determination from earthly branch."""
        test_cases = [
            ("Zi", "Water"), ("Chou", "Earth"),
            ("Yin", "Wood"), ("Mao", "Wood"),
            ("Chen", "Earth"), ("Si", "Fire"),
            ("Wu", "Fire"), ("Wei", "Earth"),
            ("Shen", "Metal"), ("You", "Metal"),
            ("Xu", "Earth"), ("Hai", "Water")
        ]
        
        for branch, expected_element in test_cases:
            element = bazi_calculator._get_element_from_branch(branch)
            assert element == expected_element
    
    def test_get_hidden_stems(self, bazi_calculator):
        """Test hidden stems calculation for earthly branches."""
        # Each branch contains hidden heavenly stems
        result = bazi_calculator._get_hidden_stems("Zi")
        
        assert isinstance(result, list)
        assert len(result) > 0
        for stem in result:
            assert stem in bazi_calculator.HEAVENLY_STEMS
    
    def test_calculate_element_balance(self, bazi_calculator):
        """Test five elements balance calculation."""
        four_pillars = {
            'year_pillar': {'stem': 'Geng', 'branch': 'Wu'},
            'month_pillar': {'stem': 'Xin', 'branch': 'Si'},
            'day_pillar': {'stem': 'Bing', 'branch': 'Yin'},
            'hour_pillar': {'stem': 'Yi', 'branch': 'Wei'}
        }
        
        balance = bazi_calculator._calculate_element_balance(four_pillars)
        
        assert len(balance) == 5
        assert all(element in balance for element in bazi_calculator.FIVE_ELEMENTS)
        assert all(isinstance(count, int) and count >= 0 for count in balance.values())
    
    def test_determine_day_master_strength(self, bazi_calculator):
        """Test day master strength determination."""
        day_master_element = "Fire"
        element_balance = {
            "Wood": 2, "Fire": 3, "Earth": 1, "Metal": 1, "Water": 1
        }
        birth_month = 5  # Summer, Fire season
        
        strength = bazi_calculator._determine_day_master_strength(
            day_master_element, element_balance, birth_month
        )
        
        assert strength in ['very_strong', 'strong', 'balanced', 'weak', 'very_weak']
    
    def test_calculate_luck_pillars_male(self, bazi_calculator, test_datetime):
        """Test luck pillar calculation for male."""
        year_pillar = {'stem': 'Geng', 'branch': 'Wu'}
        month_pillar = {'stem': 'Xin', 'branch': 'Si'}
        
        luck_pillars = bazi_calculator._calculate_luck_pillars(
            test_datetime, year_pillar, month_pillar, 'male'
        )
        
        assert isinstance(luck_pillars, list)
        assert len(luck_pillars) > 0
        
        for pillar in luck_pillars:
            assert 'stem' in pillar
            assert 'branch' in pillar
            assert 'start_age' in pillar
            assert 'start_year' in pillar
    
    def test_calculate_luck_pillars_female(self, bazi_calculator, test_datetime):
        """Test luck pillar calculation for female."""
        year_pillar = {'stem': 'Geng', 'branch': 'Wu'}
        month_pillar = {'stem': 'Xin', 'branch': 'Si'}
        
        luck_pillars = bazi_calculator._calculate_luck_pillars(
            test_datetime, year_pillar, month_pillar, 'female'
        )
        
        assert isinstance(luck_pillars, list)
        # Female luck pillars may run in reverse order for certain years
    
    def test_element_interactions(self, bazi_calculator):
        """Test five element interaction cycles."""
        # Generating cycle
        assert bazi_calculator._generates("Wood", "Fire") is True
        assert bazi_calculator._generates("Fire", "Earth") is True
        assert bazi_calculator._generates("Earth", "Metal") is True
        assert bazi_calculator._generates("Metal", "Water") is True
        assert bazi_calculator._generates("Water", "Wood") is True
        
        # Controlling cycle
        assert bazi_calculator._controls("Wood", "Earth") is True
        assert bazi_calculator._controls("Earth", "Water") is True
        assert bazi_calculator._controls("Water", "Fire") is True
        assert bazi_calculator._controls("Fire", "Metal") is True
        assert bazi_calculator._controls("Metal", "Wood") is True
    
    def test_branch_relationships(self, bazi_calculator):
        """Test earthly branch relationships."""
        # Harmony groups
        harmony = bazi_calculator._get_branch_harmony("Zi")
        assert isinstance(harmony, list)
        
        # Clash relationships
        clash = bazi_calculator._get_branch_clash("Zi")
        assert clash == "Wu"  # Rat clashes with Horse
        
        # Punishment relationships
        punishment = bazi_calculator._get_branch_punishment("Zi")
        assert isinstance(punishment, (str, type(None)))
    
    def test_get_favorable_elements(self, bazi_calculator):
        """Test favorable element determination."""
        day_master = "Fire"
        day_master_strength = "strong"
        
        favorable = bazi_calculator._get_favorable_elements(day_master, day_master_strength)
        
        assert isinstance(favorable, list)
        assert all(elem in bazi_calculator.FIVE_ELEMENTS for elem in favorable)
        # Strong Fire needs controlling elements
        assert "Water" in favorable or "Metal" in favorable
    
    def test_special_chart_patterns(self, bazi_calculator):
        """Test special chart pattern detection."""
        four_pillars = {
            'year_pillar': {'stem': 'Jia', 'branch': 'Zi'},
            'month_pillar': {'stem': 'Jia', 'branch': 'Zi'},
            'day_pillar': {'stem': 'Jia', 'branch': 'Zi'},
            'hour_pillar': {'stem': 'Jia', 'branch': 'Zi'}
        }
        
        patterns = bazi_calculator._detect_special_patterns(four_pillars)
        
        assert isinstance(patterns, list)
        # Should detect extreme imbalance or special formations
    
    def test_timezone_handling(self, bazi_calculator):
        """Test proper timezone handling."""
        # Test with UTC
        dt_utc = datetime(1990, 5, 15, 6, 30, 0, tzinfo=timezone.utc)
        location_utc = {'latitude': 0, 'longitude': 0, 'timezone': 'UTC'}
        
        result = bazi_calculator.calculate_bazi_chart(dt_utc, location_utc, 'male')
        
        assert 'four_pillars' in result
        # Hour pillar should reflect UTC time
    
    def test_solar_term_boundaries(self, bazi_calculator):
        """Test handling of solar term boundaries."""
        # Test date near solar term change (e.g., around Feb 4)
        dt = datetime(1990, 2, 4, 12, 0)
        
        month_stem, month_branch = bazi_calculator._calculate_month_pillar(dt, "Geng")
        
        assert month_stem in bazi_calculator.HEAVENLY_STEMS
        assert month_branch in bazi_calculator.EARTHLY_BRANCHES
    
    def test_gender_differences(self, bazi_calculator, test_datetime, test_location):
        """Test gender-specific calculations."""
        male_chart = bazi_calculator.calculate_bazi_chart(test_datetime, test_location, 'male')
        female_chart = bazi_calculator.calculate_bazi_chart(test_datetime, test_location, 'female')
        
        # Four pillars should be the same
        assert male_chart['four_pillars'] == female_chart['four_pillars']
        
        # Luck pillars may differ
        assert 'luck_pillars' in male_chart
        assert 'luck_pillars' in female_chart
    
    def test_interpretation_generation(self, bazi_calculator, test_datetime, test_location):
        """Test interpretation text generation."""
        result = bazi_calculator.calculate_bazi_chart(test_datetime, test_location, 'male')
        
        interpretation = bazi_calculator.generate_interpretation(result)
        
        assert isinstance(interpretation, dict)
        assert 'personality' in interpretation
        assert 'career' in interpretation
        assert 'relationships' in interpretation
        assert 'health' in interpretation
        assert 'wealth' in interpretation
    
    def test_annual_luck(self, bazi_calculator):
        """Test annual luck calculation."""
        bazi_chart = {
            'day_master': 'Fire',
            'favorable_elements': ['Water', 'Metal']
        }
        current_year = 2024  # Dragon year
        
        annual_luck = bazi_calculator.calculate_annual_luck(bazi_chart, current_year)
        
        assert 'year_stem' in annual_luck
        assert 'year_branch' in annual_luck
        assert 'favorability' in annual_luck
        assert 'themes' in annual_luck
    
    def test_edge_cases(self, bazi_calculator):
        """Test edge cases in Bazi calculation."""
        # Midnight birth
        midnight = datetime(1990, 1, 1, 0, 0, 0)
        location = {'latitude': 0, 'longitude': 0, 'timezone': 'UTC'}
        
        result = bazi_calculator.calculate_bazi_chart(midnight, location, 'male')
        assert result['four_pillars']['hour_pillar']['branch'] == 'Zi'  # Rat hour
        
        # Leap year
        leap_date = datetime(2000, 2, 29, 12, 0)
        result = bazi_calculator.calculate_bazi_chart(leap_date, location, 'female')
        assert 'four_pillars' in result