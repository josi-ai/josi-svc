"""Comprehensive unit tests for Panchang service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import math

from josi.services.vedic.panchang_service import PanchangCalculator


class TestPanchangCalculator:
    """Comprehensive test coverage for PanchangCalculator."""
    
    @pytest.fixture
    def panchang_calculator(self):
        """Create a PanchangCalculator instance."""
        return PanchangCalculator()
    
    @pytest.fixture
    def test_datetime(self):
        """Test datetime for calculations."""
        return datetime(2024, 1, 15, 6, 30, 0)
    
    @pytest.fixture
    def test_location(self):
        """Test location coordinates."""
        return {
            'latitude': 28.6139,  # Delhi
            'longitude': 77.2090,
            'timezone': 'Asia/Kolkata'
        }
    
    def test_initialization(self, panchang_calculator):
        """Test PanchangCalculator initialization."""
        assert hasattr(panchang_calculator, 'calculate_panchang')
        assert hasattr(panchang_calculator, 'TITHIS')
        assert hasattr(panchang_calculator, 'NAKSHATRAS')
        assert hasattr(panchang_calculator, 'YOGAS')
        assert hasattr(panchang_calculator, 'KARANAS')
        
        # Check data structures
        assert len(panchang_calculator.TITHIS) == 30
        assert len(panchang_calculator.NAKSHATRAS) == 27
        assert len(panchang_calculator.YOGAS) == 27
        assert len(panchang_calculator.KARANAS) == 60
    
    def test_calculate_panchang_complete(self, panchang_calculator, test_datetime, test_location):
        """Test complete panchang calculation."""
        result = panchang_calculator.calculate_panchang(
            dt=test_datetime,
            location=test_location
        )
        
        assert 'tithi' in result
        assert 'nakshatra' in result
        assert 'yoga' in result
        assert 'karana' in result
        assert 'vara' in result
        assert 'sunrise' in result
        assert 'sunset' in result
        assert 'moonrise' in result
        assert 'moonset' in result
        assert 'rahu_kala' in result
        assert 'gulika_kala' in result
        assert 'yamaghanta' in result
    
    def test_calculate_tithi(self, panchang_calculator):
        """Test tithi calculation."""
        with patch.object(panchang_calculator, '_get_sun_moon_positions') as mock_pos:
            # Sun at 100°, Moon at 130° = 30° difference = Tritiya (3rd tithi)
            mock_pos.return_value = (100.0, 130.0)
            
            tithi = panchang_calculator._calculate_tithi(test_datetime, test_location)
            
            assert 'name' in tithi
            assert 'number' in tithi
            assert 'phase' in tithi
            assert 'percent_complete' in tithi
            assert 'ending_time' in tithi
            
            # 30° difference = 2.5 tithis, so 3rd tithi
            assert tithi['number'] == 3
            assert tithi['name'] == 'Tritiya'
    
    def test_calculate_nakshatra(self, panchang_calculator):
        """Test nakshatra calculation."""
        with patch.object(panchang_calculator, '_get_moon_position') as mock_moon:
            # Moon at 45° = Rohini nakshatra
            mock_moon.return_value = 45.0
            
            nakshatra = panchang_calculator._calculate_nakshatra(test_datetime, test_location)
            
            assert 'name' in nakshatra
            assert 'number' in nakshatra
            assert 'lord' in nakshatra
            assert 'pada' in nakshatra
            assert 'percent_complete' in nakshatra
            assert 'ending_time' in nakshatra
            
            # 45° / 13.333 = 3.375, so 4th nakshatra (0-indexed = 3)
            assert nakshatra['number'] == 3
            assert nakshatra['name'] == 'Rohini'
            assert nakshatra['lord'] == 'Moon'
    
    def test_calculate_yoga(self, panchang_calculator):
        """Test yoga calculation."""
        with patch.object(panchang_calculator, '_get_sun_moon_positions') as mock_pos:
            # Sun at 100°, Moon at 150°, combined = 250°
            mock_pos.return_value = (100.0, 150.0)
            
            yoga = panchang_calculator._calculate_yoga(test_datetime, test_location)
            
            assert 'name' in yoga
            assert 'number' in yoga
            assert 'deity' in yoga
            assert 'percent_complete' in yoga
            assert 'ending_time' in yoga
            
            # (100 + 150) / 13.333 = 18.75, so 19th yoga
            assert yoga['number'] == 19
    
    def test_calculate_karana(self, panchang_calculator):
        """Test karana calculation."""
        with patch.object(panchang_calculator, '_calculate_tithi') as mock_tithi:
            mock_tithi.return_value = {
                'number': 5,
                'percent_complete': 0.5
            }
            
            karana = panchang_calculator._calculate_karana(test_datetime, test_location)
            
            assert 'name' in karana
            assert 'number' in karana
            assert 'type' in karana  # Chara or Sthira
            assert 'percent_complete' in karana
            
            # 5th tithi, 50% complete = 9th karana
            assert karana['number'] == 9
    
    def test_calculate_vara(self, panchang_calculator, test_datetime):
        """Test weekday (vara) calculation."""
        vara = panchang_calculator._calculate_vara(test_datetime)
        
        assert 'name' in vara
        assert 'number' in vara
        assert 'lord' in vara
        
        # January 15, 2024 is Monday
        assert vara['number'] == 1
        assert vara['name'] == 'Somavara'
        assert vara['lord'] == 'Moon'
    
    def test_calculate_sunrise_sunset(self, panchang_calculator, test_datetime, test_location):
        """Test sunrise and sunset calculation."""
        with patch('ephem.Observer') as mock_observer:
            mock_obs_instance = MagicMock()
            mock_observer.return_value = mock_obs_instance
            
            # Mock sun calculations
            mock_sun = MagicMock()
            mock_obs_instance.next_rising.return_value = 2460324.75  # Julian day
            mock_obs_instance.next_setting.return_value = 2460325.25
            
            with patch('ephem.Sun') as mock_sun_class:
                mock_sun_class.return_value = mock_sun
                
                sunrise, sunset = panchang_calculator._calculate_sunrise_sunset(
                    test_datetime, test_location
                )
                
                assert isinstance(sunrise, datetime)
                assert isinstance(sunset, datetime)
                assert sunrise < sunset
    
    def test_calculate_moonrise_moonset(self, panchang_calculator, test_datetime, test_location):
        """Test moonrise and moonset calculation."""
        with patch('ephem.Observer') as mock_observer:
            mock_obs_instance = MagicMock()
            mock_observer.return_value = mock_obs_instance
            
            # Mock moon calculations
            mock_moon = MagicMock()
            mock_obs_instance.next_rising.return_value = 2460324.85
            mock_obs_instance.next_setting.return_value = 2460325.35
            
            with patch('ephem.Moon') as mock_moon_class:
                mock_moon_class.return_value = mock_moon
                
                moonrise, moonset = panchang_calculator._calculate_moonrise_moonset(
                    test_datetime, test_location
                )
                
                assert isinstance(moonrise, datetime)
                assert isinstance(moonset, datetime)
    
    def test_calculate_rahu_kala(self, panchang_calculator, test_datetime, test_location):
        """Test Rahu Kala calculation."""
        with patch.object(panchang_calculator, '_calculate_sunrise_sunset') as mock_sun:
            sunrise = test_datetime.replace(hour=6, minute=0)
            sunset = test_datetime.replace(hour=18, minute=0)
            mock_sun.return_value = (sunrise, sunset)
            
            rahu_kala = panchang_calculator._calculate_rahu_kala(
                test_datetime, test_location
            )
            
            assert 'start' in rahu_kala
            assert 'end' in rahu_kala
            assert isinstance(rahu_kala['start'], datetime)
            assert isinstance(rahu_kala['end'], datetime)
            assert rahu_kala['start'] < rahu_kala['end']
            
            # Rahu Kala should be 1.5 hours (1/8 of day)
            duration = rahu_kala['end'] - rahu_kala['start']
            assert duration == timedelta(hours=1.5)
    
    def test_calculate_gulika_kala(self, panchang_calculator, test_datetime, test_location):
        """Test Gulika Kala calculation."""
        with patch.object(panchang_calculator, '_calculate_sunrise_sunset') as mock_sun:
            sunrise = test_datetime.replace(hour=6, minute=0)
            sunset = test_datetime.replace(hour=18, minute=0)
            mock_sun.return_value = (sunrise, sunset)
            
            gulika_kala = panchang_calculator._calculate_gulika_kala(
                test_datetime, test_location
            )
            
            assert 'start' in gulika_kala
            assert 'end' in gulika_kala
            assert gulika_kala['start'] < gulika_kala['end']
    
    def test_calculate_yamaghanta(self, panchang_calculator, test_datetime, test_location):
        """Test Yamaghanta calculation."""
        with patch.object(panchang_calculator, '_calculate_sunrise_sunset') as mock_sun:
            sunrise = test_datetime.replace(hour=6, minute=0)
            sunset = test_datetime.replace(hour=18, minute=0)
            mock_sun.return_value = (sunrise, sunset)
            
            yamaghanta = panchang_calculator._calculate_yamaghanta(
                test_datetime, test_location
            )
            
            assert 'start' in yamaghanta
            assert 'end' in yamaghanta
            assert yamaghanta['start'] < yamaghanta['end']
    
    def test_tithi_transitions(self, panchang_calculator):
        """Test tithi transition detection."""
        # Test Krishna Paksha to Shukla Paksha transition
        with patch.object(panchang_calculator, '_get_sun_moon_positions') as mock_pos:
            # New moon (Sun-Moon conjunction)
            mock_pos.return_value = (100.0, 100.0)
            
            tithi = panchang_calculator._calculate_tithi(test_datetime, test_location)
            assert tithi['phase'] == 'Shukla'  # Bright fortnight begins
    
    def test_special_tithis(self, panchang_calculator):
        """Test special tithi identification."""
        special_tithis = {
            4: 'Chaturthi',  # Ganesh Chaturthi
            8: 'Ashtami',    # Durga Ashtami
            11: 'Ekadashi',  # Fasting day
            14: 'Chaturdashi',  # Day before new/full moon
            15: 'Purnima',   # Full moon
            30: 'Amavasya'   # New moon
        }
        
        for tithi_num, expected_name in special_tithis.items():
            assert panchang_calculator.TITHIS[tithi_num - 1] == expected_name
    
    def test_nakshatra_transition_time(self, panchang_calculator):
        """Test nakshatra transition time calculation."""
        current_longitude = 40.0  # In Rohini
        moon_speed = 13.0  # Degrees per day
        
        # Next nakshatra starts at 53.333 degrees
        time_to_next = panchang_calculator._calculate_transition_time(
            current_longitude, 53.333, moon_speed
        )
        
        assert isinstance(time_to_next, timedelta)
        # Should be about 24.6 hours
        hours = time_to_next.total_seconds() / 3600
        assert 24 < hours < 25
    
    def test_yoga_quality(self, panchang_calculator):
        """Test yoga quality classification."""
        # Some yogas are auspicious, some are inauspicious
        auspicious_yogas = ['Siddha', 'Sadhya', 'Shubha', 'Shukla']
        inauspicious_yogas = ['Vyatipata', 'Vaidhriti', 'Parigha', 'Vishkumbha']
        
        for yoga_name in auspicious_yogas:
            quality = panchang_calculator._get_yoga_quality(yoga_name)
            assert quality == 'auspicious'
        
        for yoga_name in inauspicious_yogas:
            quality = panchang_calculator._get_yoga_quality(yoga_name)
            assert quality == 'inauspicious'
    
    def test_karana_types(self, panchang_calculator):
        """Test karana type classification."""
        # First 7 karanas are Chara (movable), repeat
        # Last 4 karanas are Sthira (fixed), occur once per lunar month
        
        for i in range(7):
            karana_type = panchang_calculator._get_karana_type(i)
            assert karana_type == 'Chara'
        
        for i in range(56, 60):
            karana_type = panchang_calculator._get_karana_type(i)
            assert karana_type == 'Sthira'
    
    def test_festival_determination(self, panchang_calculator, test_datetime, test_location):
        """Test festival and special day determination."""
        # Mock a full moon day
        with patch.object(panchang_calculator, '_calculate_tithi') as mock_tithi:
            mock_tithi.return_value = {
                'number': 15,
                'name': 'Purnima',
                'phase': 'Shukla'
            }
            
            festivals = panchang_calculator.get_festivals(test_datetime, test_location)
            
            assert isinstance(festivals, list)
            # Should identify it as a full moon day
    
    def test_samvatsara_calculation(self, panchang_calculator):
        """Test 60-year Samvatsara cycle calculation."""
        # 2024 is Krodhi samvatsara (24th in cycle)
        year = 2024
        
        samvatsara = panchang_calculator._calculate_samvatsara(year)
        
        assert 'number' in samvatsara
        assert 'name' in samvatsara
        assert samvatsara['number'] >= 1 and samvatsara['number'] <= 60
    
    def test_masa_calculation(self, panchang_calculator, test_datetime):
        """Test lunar month (masa) calculation."""
        with patch.object(panchang_calculator, '_get_sun_position') as mock_sun:
            # Sun in Capricorn (270-300 degrees)
            mock_sun.return_value = 285.0
            
            masa = panchang_calculator._calculate_masa(test_datetime)
            
            assert 'name' in masa
            assert 'solar_month' in masa
            assert masa['name'] == 'Magha'  # When sun is in Capricorn
    
    def test_paksha_determination(self, panchang_calculator):
        """Test lunar fortnight (paksha) determination."""
        # Shukla Paksha (waxing moon)
        for tithi in range(1, 16):
            paksha = panchang_calculator._get_paksha(tithi)
            assert paksha == 'Shukla'
        
        # Krishna Paksha (waning moon)
        for tithi in range(16, 31):
            paksha = panchang_calculator._get_paksha(tithi)
            assert paksha == 'Krishna'
    
    def test_abhijit_muhurta(self, panchang_calculator, test_datetime, test_location):
        """Test Abhijit Muhurta calculation."""
        with patch.object(panchang_calculator, '_calculate_sunrise_sunset') as mock_sun:
            sunrise = test_datetime.replace(hour=6, minute=0)
            sunset = test_datetime.replace(hour=18, minute=0)
            mock_sun.return_value = (sunrise, sunset)
            
            abhijit = panchang_calculator._calculate_abhijit_muhurta(
                test_datetime.date(), test_location
            )
            
            assert 'start' in abhijit
            assert 'end' in abhijit
            # Abhijit is around midday
            assert 11 <= abhijit['start'].hour <= 13
    
    def test_durmuhurta_calculation(self, panchang_calculator, test_datetime, test_location):
        """Test Durmuhurta (inauspicious time) calculation."""
        durmuhurtas = panchang_calculator._calculate_durmuhurtas(
            test_datetime.date(), test_location
        )
        
        assert isinstance(durmuhurtas, list)
        assert len(durmuhurtas) == 2  # Two per day
        
        for dm in durmuhurtas:
            assert 'start' in dm
            assert 'end' in dm
            assert dm['start'] < dm['end']
    
    def test_choghadiya_calculation(self, panchang_calculator, test_datetime, test_location):
        """Test Choghadiya calculation."""
        with patch.object(panchang_calculator, '_calculate_sunrise_sunset') as mock_sun:
            sunrise = test_datetime.replace(hour=6, minute=0)
            sunset = test_datetime.replace(hour=18, minute=0)
            mock_sun.return_value = (sunrise, sunset)
            
            choghadiyas = panchang_calculator.calculate_choghadiya(
                test_datetime.date(), test_location
            )
            
            assert 'day' in choghadiyas
            assert 'night' in choghadiyas
            
            # 8 periods each for day and night
            assert len(choghadiyas['day']) == 8
            assert len(choghadiyas['night']) == 8
    
    def test_planetary_hora(self, panchang_calculator, test_datetime, test_location):
        """Test planetary hora calculation."""
        hora = panchang_calculator.calculate_planetary_hora(
            test_datetime, test_location
        )
        
        assert 'planet' in hora
        assert 'quality' in hora
        assert 'start' in hora
        assert 'end' in hora
        
        assert hora['planet'] in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    def test_json_serialization(self, panchang_calculator, test_datetime, test_location):
        """Test JSON serialization of panchang data."""
        panchang = panchang_calculator.calculate_panchang(test_datetime, test_location)
        
        # Should be JSON serializable
        import json
        json_str = json.dumps(panchang, default=str)
        assert isinstance(json_str, str)
        
        # Should be able to deserialize
        deserialized = json.loads(json_str)
        assert 'tithi' in deserialized