"""Comprehensive unit tests for Muhurta (electional astrology) service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from josi.services.vedic.muhurta_service import MuhurtaCalculator


class TestMuhurtaCalculator:
    """Comprehensive test coverage for MuhurtaCalculator."""
    
    @pytest.fixture
    def muhurta_calculator(self):
        """Create a MuhurtaCalculator instance."""
        return MuhurtaCalculator()
    
    @pytest.fixture
    def test_location(self):
        """Test location coordinates."""
        return {
            'latitude': 28.6139,  # Delhi
            'longitude': 77.2090,
            'timezone': 'Asia/Kolkata'
        }
    
    @pytest.fixture
    def test_datetime(self):
        """Test datetime."""
        return datetime(2024, 1, 15, 10, 0, 0)
    
    def test_initialization(self, muhurta_calculator):
        """Test MuhurtaCalculator initialization."""
        assert hasattr(muhurta_calculator, 'find_auspicious_times')
        assert hasattr(muhurta_calculator, 'check_muhurta_quality')
        assert hasattr(muhurta_calculator, 'get_panchanga')
    
    def test_find_auspicious_times_basic(self, muhurta_calculator, test_datetime, test_location):
        """Test finding auspicious times for an activity."""
        result = muhurta_calculator.find_auspicious_times(
            activity_type='marriage',
            start_date=test_datetime,
            end_date=test_datetime + timedelta(days=7),
            location=test_location,
            preferences={}
        )
        
        assert 'recommended_times' in result
        assert 'avoided_times' in result
        assert isinstance(result['recommended_times'], list)
        assert isinstance(result['avoided_times'], list)
    
    def test_check_muhurta_quality(self, muhurta_calculator, test_datetime, test_location):
        """Test checking quality of a specific muhurta."""
        result = muhurta_calculator.check_muhurta_quality(
            datetime_to_check=test_datetime,
            activity_type='business',
            location=test_location
        )
        
        assert 'quality_score' in result
        assert 'factors' in result
        assert 'recommendations' in result
        assert 0 <= result['quality_score'] <= 100
    
    def test_get_panchanga(self, muhurta_calculator, test_datetime, test_location):
        """Test panchanga calculation."""
        result = muhurta_calculator.get_panchanga(
            dt=test_datetime,
            location=test_location
        )
        
        assert 'tithi' in result
        assert 'nakshatra' in result
        assert 'yoga' in result
        assert 'karana' in result
        assert 'vara' in result  # Weekday
    
    def test_calculate_tithi(self, muhurta_calculator, test_datetime, test_location):
        """Test tithi (lunar day) calculation."""
        with patch.object(muhurta_calculator, '_get_sun_moon_positions') as mock_pos:
            mock_pos.return_value = (120.0, 150.0)  # Sun at 120°, Moon at 150°
            
            tithi = muhurta_calculator._calculate_tithi(test_datetime, test_location)
            
            assert 'name' in tithi
            assert 'phase' in tithi
            assert 'percent' in tithi
            assert tithi['number'] >= 1 and tithi['number'] <= 30
    
    def test_calculate_nakshatra(self, muhurta_calculator, test_datetime, test_location):
        """Test nakshatra calculation."""
        with patch.object(muhurta_calculator, '_get_moon_position') as mock_moon:
            mock_moon.return_value = 45.0  # Moon in Rohini
            
            nakshatra = muhurta_calculator._calculate_nakshatra(test_datetime, test_location)
            
            assert 'name' in nakshatra
            assert 'lord' in nakshatra
            assert 'pada' in nakshatra
            assert nakshatra['number'] >= 0 and nakshatra['number'] < 27
    
    def test_calculate_yoga(self, muhurta_calculator, test_datetime, test_location):
        """Test yoga calculation."""
        with patch.object(muhurta_calculator, '_get_sun_moon_positions') as mock_pos:
            mock_pos.return_value = (100.0, 200.0)
            
            yoga = muhurta_calculator._calculate_yoga(test_datetime, test_location)
            
            assert 'name' in yoga
            assert 'number' in yoga
            assert yoga['number'] >= 0 and yoga['number'] < 27
    
    def test_calculate_karana(self, muhurta_calculator, test_datetime, test_location):
        """Test karana calculation."""
        with patch.object(muhurta_calculator, '_calculate_tithi') as mock_tithi:
            mock_tithi.return_value = {'number': 5, 'percent': 0.5}
            
            karana = muhurta_calculator._calculate_karana(test_datetime, test_location)
            
            assert 'name' in karana
            assert 'number' in karana
            assert karana['number'] >= 0 and karana['number'] < 60
    
    def test_activity_specific_rules_marriage(self, muhurta_calculator):
        """Test marriage-specific muhurta rules."""
        rules = muhurta_calculator._get_activity_rules('marriage')
        
        assert 'favorable_tithis' in rules
        assert 'unfavorable_tithis' in rules
        assert 'favorable_nakshatras' in rules
        assert 'unfavorable_nakshatras' in rules
        assert 'favorable_days' in rules
        assert 'avoid_months' in rules
    
    def test_activity_specific_rules_travel(self, muhurta_calculator):
        """Test travel-specific muhurta rules."""
        rules = muhurta_calculator._get_activity_rules('travel')
        
        assert 'favorable_tithis' in rules
        assert 'direction_rules' in rules  # Travel direction considerations
    
    def test_activity_specific_rules_business(self, muhurta_calculator):
        """Test business-specific muhurta rules."""
        rules = muhurta_calculator._get_activity_rules('business')
        
        assert 'favorable_tithis' in rules
        assert 'wealth_nakshatras' in rules
    
    def test_check_abhijit_muhurta(self, muhurta_calculator, test_location):
        """Test Abhijit muhurta calculation (most auspicious time of day)."""
        date = datetime(2024, 1, 15)
        
        abhijit = muhurta_calculator._get_abhijit_muhurta(date, test_location)
        
        assert isinstance(abhijit, dict)
        assert 'start' in abhijit
        assert 'end' in abhijit
        # Abhijit is around midday
        assert abhijit['start'].hour >= 11 and abhijit['start'].hour <= 13
    
    def test_check_rahu_kala(self, muhurta_calculator, test_datetime, test_location):
        """Test Rahu Kala (inauspicious period) calculation."""
        rahu_kala = muhurta_calculator._get_rahu_kala(test_datetime.date(), test_location)
        
        assert isinstance(rahu_kala, dict)
        assert 'start' in rahu_kala
        assert 'end' in rahu_kala
        assert rahu_kala['start'] < rahu_kala['end']
    
    def test_check_gulika_kala(self, muhurta_calculator, test_datetime, test_location):
        """Test Gulika Kala calculation."""
        gulika_kala = muhurta_calculator._get_gulika_kala(test_datetime.date(), test_location)
        
        assert isinstance(gulika_kala, dict)
        assert 'start' in gulika_kala
        assert 'end' in gulika_kala
    
    def test_check_yamaghanta(self, muhurta_calculator, test_datetime, test_location):
        """Test Yamaghanta (death time) calculation."""
        yamaghanta = muhurta_calculator._get_yamaghanta(test_datetime.date(), test_location)
        
        assert isinstance(yamaghanta, dict)
        assert 'start' in yamaghanta
        assert 'end' in yamaghanta
    
    def test_check_durmuhurta(self, muhurta_calculator, test_datetime, test_location):
        """Test Durmuhurta (inauspicious muhurtas) calculation."""
        durmuhurtas = muhurta_calculator._get_durmuhurtas(test_datetime.date(), test_location)
        
        assert isinstance(durmuhurtas, list)
        assert len(durmuhurtas) == 2  # Two durmuhurtas per day
        for dm in durmuhurtas:
            assert 'start' in dm
            assert 'end' in dm
    
    def test_check_amrita_kala(self, muhurta_calculator, test_datetime, test_location):
        """Test Amrita Kala (nectar time) calculation."""
        amrita_kala = muhurta_calculator._get_amrita_kala(test_datetime.date(), test_location)
        
        assert isinstance(amrita_kala, dict)
        assert 'start' in amrita_kala
        assert 'end' in amrita_kala
    
    def test_lunar_month_considerations(self, muhurta_calculator):
        """Test lunar month-based considerations."""
        # Adhika masa (extra month)
        is_adhika = muhurta_calculator._is_adhika_masa(datetime(2024, 7, 1))
        assert isinstance(is_adhika, bool)
        
        # Kshaya masa (lost month)
        is_kshaya = muhurta_calculator._is_kshaya_masa(datetime(2024, 1, 1))
        assert isinstance(is_kshaya, bool)
    
    def test_special_yoga_detection(self, muhurta_calculator, test_datetime, test_location):
        """Test detection of special yogas."""
        special_yogas = muhurta_calculator._check_special_yogas(test_datetime, test_location)
        
        assert isinstance(special_yogas, list)
        # Could include Sarvartha Siddhi Yoga, Amrita Siddhi Yoga, etc.
    
    def test_eclipse_checking(self, muhurta_calculator, test_datetime, test_location):
        """Test eclipse period checking."""
        is_eclipse = muhurta_calculator._is_eclipse_period(test_datetime, test_location)
        
        assert isinstance(is_eclipse, bool)
    
    def test_gandanta_checking(self, muhurta_calculator, test_datetime, test_location):
        """Test Gandanta (junction point) checking."""
        with patch.object(muhurta_calculator, '_get_moon_position') as mock_moon:
            # Moon at junction of water-fire signs (29°59' Pisces)
            mock_moon.return_value = 359.99
            
            is_gandanta = muhurta_calculator._is_gandanta(test_datetime, test_location)
            
            assert is_gandanta is True
    
    def test_mrityubhaga_checking(self, muhurta_calculator, test_datetime, test_location):
        """Test Mrityubhaga (death-inflicting degree) checking."""
        with patch.object(muhurta_calculator, '_get_moon_position') as mock_moon:
            mock_moon.return_value = 120.0  # Specific degree in Leo
            
            is_mrityubhaga = muhurta_calculator._is_mrityubhaga(test_datetime, test_location)
            
            assert isinstance(is_mrityubhaga, bool)
    
    def test_hora_calculation(self, muhurta_calculator, test_datetime, test_location):
        """Test planetary hora (hour) calculation."""
        hora = muhurta_calculator._get_current_hora(test_datetime, test_location)
        
        assert 'planet' in hora
        assert 'quality' in hora
        assert hora['planet'] in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    def test_choghadiya_calculation(self, muhurta_calculator, test_datetime, test_location):
        """Test Choghadiya (Gujarati time division) calculation."""
        choghadiya = muhurta_calculator._get_choghadiya(test_datetime, test_location)
        
        assert 'name' in choghadiya
        assert 'quality' in choghadiya
        assert choghadiya['quality'] in ['good', 'neutral', 'bad']
    
    def test_tarabala_calculation(self, muhurta_calculator, test_datetime, test_location):
        """Test Tarabala (star strength) calculation."""
        birth_nakshatra = 4  # Rohini
        current_nakshatra = 10  # Magha
        
        tarabala = muhurta_calculator._calculate_tarabala(birth_nakshatra, current_nakshatra)
        
        assert 'strength' in tarabala
        assert 'category' in tarabala
        assert tarabala['strength'] >= 0
    
    def test_chandrabala_calculation(self, muhurta_calculator, test_datetime, test_location):
        """Test Chandrabala (moon strength) calculation."""
        birth_sign = 3  # Cancer
        current_moon_sign = 8  # Sagittarius
        
        chandrabala = muhurta_calculator._calculate_chandrabala(birth_sign, current_moon_sign)
        
        assert 'strength' in chandrabala
        assert 'favorable' in chandrabala
    
    def test_find_next_good_muhurta(self, muhurta_calculator, test_datetime, test_location):
        """Test finding next good muhurta from given time."""
        result = muhurta_calculator.find_next_good_muhurta(
            start_time=test_datetime,
            activity='general',
            location=test_location,
            max_days=7
        )
        
        assert isinstance(result, datetime)
        assert result >= test_datetime
        assert result <= test_datetime + timedelta(days=7)
    
    def test_custom_preferences(self, muhurta_calculator, test_datetime, test_location):
        """Test muhurta calculation with custom preferences."""
        preferences = {
            'avoid_rahu_kala': True,
            'prefer_abhijit': True,
            'required_nakshatra': ['Rohini', 'Pushya'],
            'avoid_tithi': [4, 9, 14]  # Chaturthi, Navami, Chaturdashi
        }
        
        result = muhurta_calculator.find_auspicious_times(
            activity_type='custom',
            start_date=test_datetime,
            end_date=test_datetime + timedelta(days=3),
            location=test_location,
            preferences=preferences
        )
        
        # Should respect preferences
        for time_slot in result['recommended_times']:
            assert time_slot['factors']['rahu_kala'] is False
    
    def test_batch_muhurta_checking(self, muhurta_calculator, test_datetime, test_location):
        """Test checking multiple datetimes for muhurta quality."""
        datetimes = [
            test_datetime,
            test_datetime + timedelta(hours=3),
            test_datetime + timedelta(days=1),
            test_datetime + timedelta(days=2, hours=14)
        ]
        
        results = muhurta_calculator.check_multiple_muhurtas(
            datetimes=datetimes,
            activity_type='meeting',
            location=test_location
        )
        
        assert len(results) == len(datetimes)
        for result in results:
            assert 'datetime' in result
            assert 'quality_score' in result
            assert 'suitable' in result