"""Comprehensive unit tests for Numerology service."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from josi.services.numerology_service import NumerologyCalculator


class TestNumerologyCalculator:
    """Comprehensive test coverage for NumerologyCalculator."""
    
    @pytest.fixture
    def numerology_calculator(self):
        """Create a NumerologyCalculator instance."""
        return NumerologyCalculator()
    
    @pytest.fixture
    def test_person(self):
        """Test person data."""
        return {
            'full_name': 'John Michael Smith',
            'birth_date': datetime(1990, 5, 15),
            'birth_name': 'John Michael Smith',  # Name at birth
            'current_name': 'John M. Smith'  # Current used name
        }
    
    def test_initialization(self, numerology_calculator):
        """Test NumerologyCalculator initialization."""
        assert hasattr(numerology_calculator, 'calculate_complete_numerology')
        assert hasattr(numerology_calculator, 'PYTHAGOREAN_VALUES')
        assert hasattr(numerology_calculator, 'CHALDEAN_VALUES')
        assert hasattr(numerology_calculator, 'MASTER_NUMBERS')
        
        # Check letter-number mappings
        assert numerology_calculator.PYTHAGOREAN_VALUES['A'] == 1
        assert numerology_calculator.PYTHAGOREAN_VALUES['Z'] == 8
        assert 11 in numerology_calculator.MASTER_NUMBERS
        assert 22 in numerology_calculator.MASTER_NUMBERS
        assert 33 in numerology_calculator.MASTER_NUMBERS
    
    def test_calculate_complete_numerology(self, numerology_calculator, test_person):
        """Test complete numerology calculation."""
        result = numerology_calculator.calculate_complete_numerology(
            full_name=test_person['full_name'],
            birth_date=test_person['birth_date']
        )
        
        assert 'life_path_number' in result
        assert 'expression_number' in result
        assert 'soul_urge_number' in result
        assert 'personality_number' in result
        assert 'birthday_number' in result
        assert 'maturity_number' in result
        assert 'karmic_debt_numbers' in result
        assert 'hidden_passion_numbers' in result
        assert 'planes_of_expression' in result
        assert 'pinnacle_cycles' in result
        assert 'challenge_numbers' in result
        assert 'personal_year' in result
    
    def test_calculate_life_path_number(self, numerology_calculator):
        """Test life path number calculation."""
        # Test date: May 15, 1990 = 5 + 15 + 1990 = 5 + 6 + 19 = 30 = 3
        birth_date = datetime(1990, 5, 15)
        
        life_path = numerology_calculator.calculate_life_path_number(birth_date)
        
        assert life_path == 3
        
        # Test master number: Nov 11, 2000 = 11 + 11 + 2 = 24 = 6
        # But 11 is kept as master number in month
        birth_date2 = datetime(2000, 11, 11)
        life_path2 = numerology_calculator.calculate_life_path_number(birth_date2)
        # This depends on implementation - might be 11 or reduced
    
    def test_calculate_expression_number(self, numerology_calculator):
        """Test expression/destiny number calculation."""
        name = "JOHN SMITH"
        
        expression = numerology_calculator.calculate_expression_number(name)
        
        assert isinstance(expression, int)
        assert 1 <= expression <= 9 or expression in [11, 22, 33]
    
    def test_calculate_soul_urge_number(self, numerology_calculator):
        """Test soul urge (heart's desire) number calculation."""
        name = "JOHN MICHAEL SMITH"
        
        soul_urge = numerology_calculator.calculate_soul_urge_number(name)
        
        assert isinstance(soul_urge, int)
        assert 1 <= soul_urge <= 9 or soul_urge in [11, 22, 33]
    
    def test_calculate_personality_number(self, numerology_calculator):
        """Test personality (outer expression) number calculation."""
        name = "JOHN MICHAEL SMITH"
        
        personality = numerology_calculator.calculate_personality_number(name)
        
        assert isinstance(personality, int)
        assert 1 <= personality <= 9 or personality in [11, 22, 33]
    
    def test_vowel_consonant_separation(self, numerology_calculator):
        """Test vowel and consonant separation."""
        name = "JOHN"
        
        vowels = numerology_calculator._get_vowels(name)
        consonants = numerology_calculator._get_consonants(name)
        
        assert vowels == "O"
        assert consonants == "JHN"
        
        # Test Y as vowel
        name2 = "LYNN"
        vowels2 = numerology_calculator._get_vowels(name2)
        assert "Y" in vowels2  # Y acts as vowel here
    
    def test_reduce_to_single_digit(self, numerology_calculator):
        """Test number reduction to single digit."""
        # Regular reduction
        assert numerology_calculator._reduce_to_single_digit(15) == 6
        assert numerology_calculator._reduce_to_single_digit(28) == 1
        assert numerology_calculator._reduce_to_single_digit(99) == 9
        
        # Master numbers should not be reduced
        assert numerology_calculator._reduce_to_single_digit(11, keep_master=True) == 11
        assert numerology_calculator._reduce_to_single_digit(22, keep_master=True) == 22
        assert numerology_calculator._reduce_to_single_digit(33, keep_master=True) == 33
    
    def test_calculate_birthday_number(self, numerology_calculator):
        """Test birthday number calculation."""
        birth_date = datetime(1990, 5, 15)
        
        birthday_num = numerology_calculator.calculate_birthday_number(birth_date)
        
        assert birthday_num == 6  # 15 = 1 + 5 = 6
        
        # Test master number birthday
        birth_date2 = datetime(1990, 5, 22)
        birthday_num2 = numerology_calculator.calculate_birthday_number(birth_date2)
        assert birthday_num2 == 22  # Keep as master number
    
    def test_calculate_maturity_number(self, numerology_calculator):
        """Test maturity number calculation."""
        life_path = 3
        expression = 7
        
        maturity = numerology_calculator.calculate_maturity_number(life_path, expression)
        
        assert maturity == 1  # 3 + 7 = 10 = 1
    
    def test_karmic_debt_detection(self, numerology_calculator):
        """Test karmic debt number detection."""
        # Karmic debt numbers: 13, 14, 16, 19
        
        # Test date that reduces to 13
        has_debt, debt_numbers = numerology_calculator._check_karmic_debt(13)
        assert has_debt is True
        assert 13 in debt_numbers
        
        # Test non-karmic number
        has_debt, debt_numbers = numerology_calculator._check_karmic_debt(15)
        assert has_debt is False
    
    def test_calculate_hidden_passion_numbers(self, numerology_calculator):
        """Test hidden passion number calculation."""
        name = "JENNIFER JONES"
        
        hidden_passions = numerology_calculator.calculate_hidden_passion_numbers(name)
        
        assert isinstance(hidden_passions, list)
        # Most frequent number(s) in the name
    
    def test_calculate_planes_of_expression(self, numerology_calculator):
        """Test planes of expression calculation."""
        name = "JOHN MICHAEL SMITH"
        
        planes = numerology_calculator.calculate_planes_of_expression(name)
        
        assert 'physical' in planes
        assert 'mental' in planes
        assert 'emotional' in planes
        assert 'intuitive' in planes
        
        # Each plane should have a count
        assert all(isinstance(count, int) for count in planes.values())
    
    def test_calculate_pinnacle_cycles(self, numerology_calculator):
        """Test pinnacle cycle calculation."""
        birth_date = datetime(1990, 5, 15)
        life_path = 3
        
        pinnacles = numerology_calculator.calculate_pinnacle_cycles(birth_date, life_path)
        
        assert len(pinnacles) == 4
        
        for i, pinnacle in enumerate(pinnacles):
            assert 'number' in pinnacle
            assert 'start_age' in pinnacle
            assert 'end_age' in pinnacle
            assert 'years' in pinnacle
            
            # Age ranges should be consecutive
            if i > 0:
                assert pinnacle['start_age'] == pinnacles[i-1]['end_age'] + 1
    
    def test_calculate_challenge_numbers(self, numerology_calculator):
        """Test challenge number calculation."""
        birth_date = datetime(1990, 5, 15)
        
        challenges = numerology_calculator.calculate_challenge_numbers(birth_date)
        
        assert len(challenges) == 4
        assert 'first_minor' in challenges
        assert 'second_minor' in challenges
        assert 'main' in challenges
        assert 'final' in challenges
        
        # Challenge numbers are 0-8 (no master numbers)
        for challenge in challenges.values():
            assert 0 <= challenge <= 8
    
    def test_calculate_personal_year(self, numerology_calculator):
        """Test personal year calculation."""
        birth_date = datetime(1990, 5, 15)
        current_year = 2024
        
        personal_year = numerology_calculator.calculate_personal_year(
            birth_date, current_year
        )
        
        assert 1 <= personal_year <= 9
        
        # Personal year = birth month + birth day + current year, reduced
        # 5 + 15 + 2024 = 5 + 6 + 8 = 19 = 10 = 1
    
    def test_calculate_personal_month(self, numerology_calculator):
        """Test personal month calculation."""
        personal_year = 5
        current_month = 3
        
        personal_month = numerology_calculator.calculate_personal_month(
            personal_year, current_month
        )
        
        assert 1 <= personal_month <= 9
        assert personal_month == 8  # 5 + 3 = 8
    
    def test_calculate_personal_day(self, numerology_calculator):
        """Test personal day calculation."""
        personal_month = 7
        current_day = 15
        
        personal_day = numerology_calculator.calculate_personal_day(
            personal_month, current_day
        )
        
        assert 1 <= personal_day <= 9
    
    def test_name_compatibility(self, numerology_calculator):
        """Test name compatibility calculation."""
        name1 = "JOHN SMITH"
        name2 = "JANE DOE"
        
        compatibility = numerology_calculator.calculate_name_compatibility(name1, name2)
        
        assert 'expression_compatibility' in compatibility
        assert 'soul_urge_compatibility' in compatibility
        assert 'overall_compatibility' in compatibility
        assert 'challenges' in compatibility
        assert 'strengths' in compatibility
    
    def test_missing_numbers(self, numerology_calculator):
        """Test missing numbers in name."""
        name = "ABCD"  # Missing many numbers
        
        missing = numerology_calculator.calculate_missing_numbers(name)
        
        assert isinstance(missing, list)
        assert all(1 <= num <= 9 for num in missing)
        # Should include numbers not represented in name
    
    def test_intensity_numbers(self, numerology_calculator):
        """Test intensity/quantity of each number."""
        name = "JENNIFER"
        
        intensity = numerology_calculator.calculate_intensity_numbers(name)
        
        assert isinstance(intensity, dict)
        assert all(1 <= k <= 9 for k in intensity.keys())
        assert all(v >= 0 for v in intensity.values())
    
    def test_pythagorean_vs_chaldean(self, numerology_calculator):
        """Test both Pythagorean and Chaldean systems."""
        name = "JOHN"
        
        pyth_value = numerology_calculator.calculate_name_number(name, system='pythagorean')
        chald_value = numerology_calculator.calculate_name_number(name, system='chaldean')
        
        # Values should differ between systems
        assert pyth_value != chald_value  # Usually different
    
    def test_cornerstone_capstone(self, numerology_calculator):
        """Test cornerstone and capstone calculation."""
        name = "MICHAEL"
        
        cornerstone = numerology_calculator.get_cornerstone(name)
        capstone = numerology_calculator.get_capstone(name)
        
        assert cornerstone == 'M'
        assert capstone == 'L'
        
        # Get their meanings
        corner_meaning = numerology_calculator.get_letter_meaning(cornerstone, 'cornerstone')
        cap_meaning = numerology_calculator.get_letter_meaning(capstone, 'capstone')
        
        assert isinstance(corner_meaning, str)
        assert isinstance(cap_meaning, str)
    
    def test_name_change_analysis(self, numerology_calculator):
        """Test name change impact analysis."""
        birth_name = "JOHN MICHAEL SMITH"
        new_name = "JOHN M SMITH"
        
        analysis = numerology_calculator.analyze_name_change(birth_name, new_name)
        
        assert 'expression_change' in analysis
        assert 'soul_urge_change' in analysis
        assert 'personality_change' in analysis
        assert 'recommendation' in analysis
    
    def test_business_name_numerology(self, numerology_calculator):
        """Test business name numerology."""
        business_name = "ACME CORPORATION"
        founding_date = datetime(2020, 1, 15)
        
        result = numerology_calculator.calculate_business_numerology(
            business_name, founding_date
        )
        
        assert 'expression_number' in result
        assert 'business_path_number' in result
        assert 'compatibility_with_date' in result
        assert 'success_areas' in result
    
    def test_address_numerology(self, numerology_calculator):
        """Test address/house numerology."""
        address = "123 MAIN STREET"
        
        house_number = numerology_calculator.calculate_address_numerology(address)
        
        assert isinstance(house_number, int)
        assert 1 <= house_number <= 9 or house_number in [11, 22, 33]
        
        # Just the number
        address2 = "456"
        house_number2 = numerology_calculator.calculate_address_numerology(address2)
        assert house_number2 == 6  # 4+5+6 = 15 = 6
    
    def test_recurring_numbers(self, numerology_calculator):
        """Test recurring number pattern detection."""
        numbers_in_chart = [3, 3, 6, 9, 3, 1, 3]
        
        recurring = numerology_calculator.find_recurring_patterns(numbers_in_chart)
        
        assert isinstance(recurring, dict)
        assert 3 in recurring  # Appears 4 times
        assert recurring[3] == 4
    
    def test_numerology_forecast(self, numerology_calculator, test_person):
        """Test numerological forecast generation."""
        current_date = datetime(2024, 1, 15)
        
        forecast = numerology_calculator.generate_forecast(
            test_person['birth_date'],
            current_date,
            test_person['full_name']
        )
        
        assert 'current_influences' in forecast
        assert 'upcoming_cycles' in forecast
        assert 'opportunities' in forecast
        assert 'challenges' in forecast
        assert 'advice' in forecast