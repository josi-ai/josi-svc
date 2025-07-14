"""Comprehensive unit tests for Vedic Remedies service."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from josi.services.vedic.remedies_service import RemediesCalculator


class TestRemediesCalculator:
    """Comprehensive test coverage for RemediesCalculator."""
    
    @pytest.fixture
    def remedies_calculator(self):
        """Create a RemediesCalculator instance."""
        return RemediesCalculator()
    
    @pytest.fixture
    def sample_chart_data(self):
        """Sample chart data for testing."""
        return {
            'planets': {
                'Sun': {'sign': 'Leo', 'house': 10, 'is_debilitated': False, 'is_exalted': False},
                'Moon': {'sign': 'Cancer', 'house': 9, 'is_debilitated': False, 'is_exalted': False},
                'Mars': {'sign': 'Capricorn', 'house': 3, 'is_debilitated': False, 'is_exalted': True},
                'Mercury': {'sign': 'Pisces', 'house': 5, 'is_debilitated': True, 'is_exalted': False},
                'Jupiter': {'sign': 'Sagittarius', 'house': 2, 'is_debilitated': False, 'is_exalted': False},
                'Venus': {'sign': 'Virgo', 'house': 11, 'is_debilitated': True, 'is_exalted': False},
                'Saturn': {'sign': 'Aquarius', 'house': 4, 'is_debilitated': False, 'is_exalted': False},
                'Rahu': {'sign': 'Gemini', 'house': 8, 'is_debilitated': False, 'is_exalted': False},
                'Ketu': {'sign': 'Sagittarius', 'house': 2, 'is_debilitated': False, 'is_exalted': False}
            },
            'houses': {
                1: {'sign': 'Scorpio', 'planets': []},
                2: {'sign': 'Sagittarius', 'planets': ['Jupiter', 'Ketu']},
                3: {'sign': 'Capricorn', 'planets': ['Mars']},
                4: {'sign': 'Aquarius', 'planets': ['Saturn']},
                5: {'sign': 'Pisces', 'planets': ['Mercury']},
                6: {'sign': 'Aries', 'planets': []},
                7: {'sign': 'Taurus', 'planets': []},
                8: {'sign': 'Gemini', 'planets': ['Rahu']},
                9: {'sign': 'Cancer', 'planets': ['Moon']},
                10: {'sign': 'Leo', 'planets': ['Sun']},
                11: {'sign': 'Virgo', 'planets': ['Venus']},
                12: {'sign': 'Libra', 'planets': []}
            },
            'ascendant': 'Scorpio',
            'moon_sign': 'Cancer',
            'doshas': ['Mangal Dosha', 'Kaal Sarp Dosha']
        }
    
    def test_initialization(self, remedies_calculator):
        """Test RemediesCalculator initialization."""
        assert hasattr(remedies_calculator, 'calculate_remedies')
        assert hasattr(remedies_calculator, 'GEMSTONES')
        assert hasattr(remedies_calculator, 'MANTRAS')
        assert hasattr(remedies_calculator, 'YANTRAS')
        assert hasattr(remedies_calculator, 'PUJAS')
        assert hasattr(remedies_calculator, 'DONATIONS')
    
    def test_calculate_remedies_comprehensive(self, remedies_calculator, sample_chart_data):
        """Test comprehensive remedy calculation."""
        result = remedies_calculator.calculate_remedies(
            chart_data=sample_chart_data,
            concern_areas=['career', 'health', 'relationships']
        )
        
        assert 'gemstone_remedies' in result
        assert 'mantra_remedies' in result
        assert 'yantra_remedies' in result
        assert 'puja_remedies' in result
        assert 'donation_remedies' in result
        assert 'lifestyle_remedies' in result
        assert 'dosha_remedies' in result
    
    def test_calculate_gemstone_remedies(self, remedies_calculator, sample_chart_data):
        """Test gemstone remedy recommendations."""
        gemstones = remedies_calculator._calculate_gemstone_remedies(sample_chart_data)
        
        assert isinstance(gemstones, list)
        assert len(gemstones) > 0
        
        for gem in gemstones:
            assert 'gemstone' in gem
            assert 'planet' in gem
            assert 'finger' in gem
            assert 'metal' in gem
            assert 'weight' in gem
            assert 'day_to_wear' in gem
            assert 'purpose' in gem
    
    def test_weak_planet_gemstone(self, remedies_calculator):
        """Test gemstone for weak/debilitated planet."""
        # Mercury is debilitated in Pisces
        weak_planet = {
            'planet': 'Mercury',
            'sign': 'Pisces',
            'is_debilitated': True
        }
        
        gemstone = remedies_calculator._get_gemstone_for_planet('Mercury', weak_planet)
        
        assert gemstone['gemstone'] == 'Emerald'
        assert gemstone['substitute'] == 'Green Tourmaline'
        assert 'weak' in gemstone['purpose'].lower() or 'debilitated' in gemstone['purpose'].lower()
    
    def test_calculate_mantra_remedies(self, remedies_calculator, sample_chart_data):
        """Test mantra remedy recommendations."""
        mantras = remedies_calculator._calculate_mantra_remedies(sample_chart_data)
        
        assert isinstance(mantras, list)
        assert len(mantras) > 0
        
        for mantra in mantras:
            assert 'mantra' in mantra
            assert 'planet' in mantra
            assert 'count' in mantra
            assert 'mala' in mantra
            assert 'best_time' in mantra
            assert 'duration' in mantra
    
    def test_beeja_mantras(self, remedies_calculator):
        """Test beeja (seed) mantra recommendations."""
        planet = 'Sun'
        
        beeja_mantra = remedies_calculator._get_beeja_mantra(planet)
        
        assert 'Om Hraam Hreem Hraum Sah Suryaya Namah' in beeja_mantra
    
    def test_calculate_yantra_remedies(self, remedies_calculator, sample_chart_data):
        """Test yantra remedy recommendations."""
        yantras = remedies_calculator._calculate_yantra_remedies(sample_chart_data)
        
        assert isinstance(yantras, list)
        
        for yantra in yantras:
            assert 'yantra' in yantra
            assert 'planet' in yantra
            assert 'material' in yantra
            assert 'installation_day' in yantra
            assert 'placement' in yantra
            assert 'activation_mantra' in yantra
    
    def test_calculate_puja_remedies(self, remedies_calculator, sample_chart_data):
        """Test puja remedy recommendations."""
        pujas = remedies_calculator._calculate_puja_remedies(sample_chart_data)
        
        assert isinstance(pujas, list)
        
        for puja in pujas:
            assert 'puja_name' in puja
            assert 'deity' in puja
            assert 'purpose' in puja
            assert 'frequency' in puja
            assert 'best_days' in puja
            assert 'offerings' in puja
    
    def test_calculate_donation_remedies(self, remedies_calculator, sample_chart_data):
        """Test donation remedy recommendations."""
        donations = remedies_calculator._calculate_donation_remedies(sample_chart_data)
        
        assert isinstance(donations, list)
        
        for donation in donations:
            assert 'items' in donation
            assert 'planet' in donation
            assert 'day' in donation
            assert 'recipients' in donation
            assert 'quantity' in donation
    
    def test_planet_specific_donations(self, remedies_calculator):
        """Test planet-specific donation items."""
        # Sun donations
        sun_donations = remedies_calculator._get_donation_items('Sun')
        assert 'wheat' in sun_donations
        assert 'jaggery' in sun_donations
        assert 'red cloth' in sun_donations
        
        # Saturn donations
        saturn_donations = remedies_calculator._get_donation_items('Saturn')
        assert 'black sesame' in saturn_donations
        assert 'iron' in saturn_donations
        assert 'oil' in saturn_donations
    
    def test_calculate_lifestyle_remedies(self, remedies_calculator, sample_chart_data):
        """Test lifestyle remedy recommendations."""
        lifestyle = remedies_calculator._calculate_lifestyle_remedies(sample_chart_data)
        
        assert isinstance(lifestyle, list)
        
        for remedy in lifestyle:
            assert 'category' in remedy
            assert 'recommendations' in remedy
            assert 'planet' in remedy
            assert 'timing' in remedy
    
    def test_dosha_specific_remedies(self, remedies_calculator, sample_chart_data):
        """Test dosha-specific remedy recommendations."""
        # Chart has Mangal Dosha and Kaal Sarp Dosha
        dosha_remedies = remedies_calculator._calculate_dosha_remedies(
            sample_chart_data['doshas']
        )
        
        assert isinstance(dosha_remedies, dict)
        assert 'Mangal Dosha' in dosha_remedies
        assert 'Kaal Sarp Dosha' in dosha_remedies
        
        # Mangal Dosha remedies
        mangal_remedies = dosha_remedies['Mangal Dosha']
        assert 'pujas' in mangal_remedies
        assert 'mantras' in mangal_remedies
        assert 'fasting' in mangal_remedies
    
    def test_career_specific_remedies(self, remedies_calculator, sample_chart_data):
        """Test career-specific remedies."""
        career_remedies = remedies_calculator._get_career_remedies(sample_chart_data)
        
        assert isinstance(career_remedies, list)
        # Sun in 10th house is good for career
        # Should focus on maintaining Sun's strength
    
    def test_health_specific_remedies(self, remedies_calculator, sample_chart_data):
        """Test health-specific remedies."""
        health_remedies = remedies_calculator._get_health_remedies(sample_chart_data)
        
        assert isinstance(health_remedies, list)
        # Should recommend remedies based on 6th house and its lord
    
    def test_relationship_specific_remedies(self, remedies_calculator, sample_chart_data):
        """Test relationship-specific remedies."""
        relationship_remedies = remedies_calculator._get_relationship_remedies(sample_chart_data)
        
        assert isinstance(relationship_remedies, list)
        # Venus is debilitated, should recommend Venus remedies
        venus_remedy_found = any(
            'Venus' in str(remedy) for remedy in relationship_remedies
        )
        assert venus_remedy_found
    
    def test_remedy_compatibility(self, remedies_calculator):
        """Test remedy compatibility checking."""
        existing_remedies = ['Ruby', 'Pearl']
        new_remedy = 'Emerald'
        
        is_compatible = remedies_calculator._check_remedy_compatibility(
            existing_remedies, new_remedy
        )
        
        assert isinstance(is_compatible, bool)
    
    def test_remedy_timing(self, remedies_calculator):
        """Test remedy timing recommendations."""
        planet = 'Jupiter'
        
        timing = remedies_calculator._get_remedy_timing(planet)
        
        assert 'best_day' in timing
        assert 'best_hora' in timing
        assert 'nakshatra' in timing
        assert timing['best_day'] == 'Thursday'
    
    def test_emergency_remedies(self, remedies_calculator):
        """Test emergency/immediate remedies."""
        crisis_type = 'acute_health'
        
        emergency_remedies = remedies_calculator._get_emergency_remedies(crisis_type)
        
        assert isinstance(emergency_remedies, list)
        assert len(emergency_remedies) > 0
        # Should include quick-acting remedies
    
    def test_remedy_strength_levels(self, remedies_calculator):
        """Test different strength levels of remedies."""
        planet = 'Mars'
        severity = 'severe'
        
        strong_remedies = remedies_calculator._get_remedies_by_strength(planet, severity)
        
        assert 'primary' in strong_remedies
        assert 'secondary' in strong_remedies
        assert 'supportive' in strong_remedies
    
    def test_combination_remedies(self, remedies_calculator):
        """Test combination remedy recommendations."""
        planets = ['Saturn', 'Rahu']  # Challenging combination
        
        combo_remedies = remedies_calculator._get_combination_remedies(planets)
        
        assert isinstance(combo_remedies, dict)
        # Should include remedies that work for both planets
    
    def test_seasonal_remedy_adjustments(self, remedies_calculator):
        """Test seasonal adjustments for remedies."""
        base_remedy = {
            'planet': 'Sun',
            'type': 'mantra',
            'practice': 'Surya mantra'
        }
        season = 'winter'
        
        adjusted = remedies_calculator._adjust_for_season(base_remedy, season)
        
        assert 'timing_adjustment' in adjusted
        assert 'additional_practices' in adjusted
    
    def test_remedy_progress_tracking(self, remedies_calculator):
        """Test remedy progress tracking suggestions."""
        remedy_plan = {
            'duration': 40,  # days
            'practices': ['mantra', 'gemstone', 'donation']
        }
        
        tracking = remedies_calculator._create_progress_tracker(remedy_plan)
        
        assert 'milestones' in tracking
        assert 'evaluation_points' in tracking
        assert 'signs_of_progress' in tracking
    
    def test_contraindications(self, remedies_calculator):
        """Test remedy contraindications."""
        person_conditions = ['pregnancy', 'heart_condition']
        remedy = {'type': 'fasting', 'intensity': 'strict'}
        
        is_safe = remedies_calculator._check_contraindications(
            remedy, person_conditions
        )
        
        assert is_safe is False  # Strict fasting not safe during pregnancy
    
    def test_remedy_combinations_to_avoid(self, remedies_calculator):
        """Test remedy combinations that should be avoided."""
        avoid_combos = remedies_calculator.AVOID_COMBINATIONS
        
        assert isinstance(avoid_combos, list)
        # Example: Ruby and Blue Sapphire (Sun and Saturn) conflict
        assert any(
            'Ruby' in combo and 'Blue Sapphire' in combo
            for combo in avoid_combos
        )
    
    def test_custom_remedy_generation(self, remedies_calculator, sample_chart_data):
        """Test custom remedy generation based on unique chart patterns."""
        custom_concern = 'spiritual_growth'
        
        custom_remedies = remedies_calculator.generate_custom_remedies(
            sample_chart_data,
            custom_concern
        )
        
        assert isinstance(custom_remedies, dict)
        assert 'practices' in custom_remedies
        assert 'duration' in custom_remedies
        assert 'expected_results' in custom_remedies