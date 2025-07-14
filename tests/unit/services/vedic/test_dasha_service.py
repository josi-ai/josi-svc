"""Comprehensive unit tests for Vimshottari Dasha service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from josi.services.vedic.dasha_service import VimshottariDashaCalculator


class TestVimshottariDashaCalculator:
    """Comprehensive test coverage for VimshottariDashaCalculator."""
    
    @pytest.fixture
    def dasha_calculator(self):
        """Create a VimshottariDashaCalculator instance."""
        return VimshottariDashaCalculator()
    
    @pytest.fixture
    def birth_datetime(self):
        """Sample birth datetime."""
        return datetime(1990, 1, 1, 12, 0, 0)
    
    def test_initialization(self, dasha_calculator):
        """Test VimshottariDashaCalculator initialization."""
        assert len(dasha_calculator.DASHA_ORDER) == 9
        assert dasha_calculator.TOTAL_YEARS == 120
        assert len(dasha_calculator.NAKSHATRA_RULERS) == 27
        
        # Verify total years add up to 120
        total = sum(years for _, years in dasha_calculator.DASHA_ORDER)
        assert total == 120
    
    def test_calculate_dasha_periods_basic(self, dasha_calculator, birth_datetime):
        """Test basic dasha period calculation."""
        moon_longitude = 45.0  # Rohini nakshatra (Moon ruled)
        
        result = dasha_calculator.calculate_dasha_periods(
            birth_datetime,
            moon_longitude,
            include_antardashas=False,
            include_pratyantardashas=False
        )
        
        assert 'mahadashas' in result
        assert 'birth_nakshatra' in result
        assert 'birth_nakshatra_lord' in result
        assert 'elapsed_in_birth_dasha' in result
        assert len(result['mahadashas']) == 9
    
    def test_calculate_dasha_periods_with_antardashas(self, dasha_calculator, birth_datetime):
        """Test dasha calculation with antardashas."""
        moon_longitude = 120.0  # Magha nakshatra (Ketu ruled)
        
        result = dasha_calculator.calculate_dasha_periods(
            birth_datetime,
            moon_longitude,
            include_antardashas=True,
            include_pratyantardashas=False
        )
        
        assert 'mahadashas' in result
        # Each mahadasha should have antardashas
        for mahadasha in result['mahadashas']:
            assert 'antardashas' in mahadasha
            assert len(mahadasha['antardashas']) == 9
    
    def test_calculate_dasha_periods_with_pratyantardashas(self, dasha_calculator, birth_datetime):
        """Test dasha calculation with pratyantardashas."""
        moon_longitude = 240.0  # Jyeshtha nakshatra (Mercury ruled)
        
        result = dasha_calculator.calculate_dasha_periods(
            birth_datetime,
            moon_longitude,
            include_antardashas=True,
            include_pratyantardashas=True
        )
        
        # Each antardasha should have pratyantardashas
        for mahadasha in result['mahadashas']:
            for antardasha in mahadasha['antardashas']:
                assert 'pratyantardashas' in antardasha
                assert len(antardasha['pratyantardashas']) == 9
    
    def test_get_nakshatra_details(self, dasha_calculator):
        """Test nakshatra detail calculation."""
        test_cases = [
            (0.0, 0, "Ashwini", "Ketu"),
            (13.5, 1, "Bharani", "Venus"),
            (30.0, 2, "Krittika", "Sun"),
            (120.0, 9, "Magha", "Ketu"),
            (359.0, 26, "Revati", "Mercury")
        ]
        
        for longitude, exp_index, exp_name, exp_lord in test_cases:
            index, name, lord = dasha_calculator._get_nakshatra_details(longitude)
            assert index == exp_index
            assert lord == exp_lord
    
    def test_calculate_elapsed_portion(self, dasha_calculator):
        """Test elapsed portion calculation in birth nakshatra."""
        # Moon at 5 degrees in Ashwini (0-13.33 degrees)
        longitude = 5.0
        elapsed = dasha_calculator._calculate_elapsed_portion(longitude)
        
        # Should be 5/13.333... = 0.375
        assert elapsed == pytest.approx(0.375, abs=0.001)
    
    def test_calculate_elapsed_portion_end_of_nakshatra(self, dasha_calculator):
        """Test elapsed portion at end of nakshatra."""
        # Moon at 13 degrees (near end of Ashwini)
        longitude = 13.0
        elapsed = dasha_calculator._calculate_elapsed_portion(longitude)
        
        # Should be close to 1.0
        assert elapsed == pytest.approx(0.975, abs=0.01)
    
    def test_calculate_remaining_dasha_period(self, dasha_calculator):
        """Test remaining dasha period calculation."""
        # Ketu dasha (7 years), 40% elapsed
        lord = "Ketu"
        elapsed_portion = 0.4
        
        remaining = dasha_calculator._calculate_remaining_dasha_period(lord, elapsed_portion)
        
        # Should be 60% of 7 years = 4.2 years
        assert remaining == pytest.approx(4.2, abs=0.01)
    
    def test_get_dasha_order_from_lord(self, dasha_calculator):
        """Test getting dasha order starting from specific lord."""
        order = dasha_calculator._get_dasha_order_from_lord("Mars")
        
        # Should start with Mars and continue in order
        assert order[0][0] == "Mars"
        assert order[1][0] == "Rahu"
        assert order[-1][0] == "Moon"
        assert len(order) == 9
    
    def test_calculate_mahadasha_dates(self, dasha_calculator, birth_datetime):
        """Test mahadasha date calculation."""
        dasha_order = dasha_calculator.DASHA_ORDER
        remaining_years = 5.0  # 5 years remaining in first dasha
        
        mahadashas = dasha_calculator._calculate_mahadasha_dates(
            birth_datetime,
            dasha_order,
            remaining_years
        )
        
        assert len(mahadashas) == 9
        
        # First dasha should start at birth
        assert mahadashas[0]['start_date'] == birth_datetime
        
        # Check continuity - each dasha should start when previous ends
        for i in range(1, len(mahadashas)):
            assert mahadashas[i]['start_date'] == mahadashas[i-1]['end_date']
    
    def test_calculate_antardasha_periods(self, dasha_calculator):
        """Test antardasha period calculation."""
        mahadasha_lord = "Venus"
        mahadasha_years = 20
        start_date = datetime(2000, 1, 1)
        
        antardashas = dasha_calculator._calculate_antardasha_periods(
            mahadasha_lord,
            mahadasha_years,
            start_date
        )
        
        assert len(antardashas) == 9
        
        # First antardasha should be of same lord
        assert antardashas[0]['lord'] == "Venus"
        
        # Check total duration equals mahadasha duration
        total_days = sum((ad['end_date'] - ad['start_date']).days for ad in antardashas)
        expected_days = mahadasha_years * 365.25
        assert abs(total_days - expected_days) < 10  # Allow small rounding difference
    
    def test_calculate_pratyantardasha_periods(self, dasha_calculator):
        """Test pratyantardasha period calculation."""
        antardasha_lord = "Sun"
        antardasha_years = 1.0
        start_date = datetime(2000, 1, 1)
        
        pratyantardashas = dasha_calculator._calculate_pratyantardasha_periods(
            antardasha_lord,
            antardasha_years,
            start_date
        )
        
        assert len(pratyantardashas) == 9
        
        # First pratyantardasha should be of same lord
        assert pratyantardashas[0]['lord'] == "Sun"
        
        # Check continuity
        for i in range(1, len(pratyantardashas)):
            assert pratyantardashas[i]['start_date'] == pratyantardashas[i-1]['end_date']
    
    def test_get_current_dasha_period(self, dasha_calculator, birth_datetime):
        """Test getting current dasha period."""
        moon_longitude = 90.0
        current_date = birth_datetime + timedelta(days=365 * 10)  # 10 years later
        
        result = dasha_calculator.get_current_dasha_period(
            birth_datetime,
            moon_longitude,
            current_date
        )
        
        assert 'mahadasha' in result
        assert 'antardasha' in result
        assert 'pratyantardasha' in result
        
        # Current date should be within the period
        assert result['mahadasha']['start_date'] <= current_date <= result['mahadasha']['end_date']
    
    def test_get_dasha_predictions(self, dasha_calculator):
        """Test dasha predictions/interpretations."""
        dasha_lord = "Jupiter"
        chart_data = {
            'planets': {
                'Jupiter': {
                    'sign': 'Sagittarius',
                    'house': 9,
                    'is_exalted': False,
                    'is_debilitated': False,
                    'is_retrograde': False
                }
            }
        }
        
        predictions = dasha_calculator.get_dasha_predictions(dasha_lord, chart_data)
        
        assert 'general' in predictions
        assert 'specific' in predictions
        assert isinstance(predictions['general'], str)
        assert len(predictions['general']) > 0
    
    def test_edge_cases(self, dasha_calculator, birth_datetime):
        """Test edge cases in dasha calculation."""
        # Longitude at 0 degrees
        result = dasha_calculator.calculate_dasha_periods(
            birth_datetime,
            0.0,
            include_antardashas=False
        )
        assert result['birth_nakshatra'] == "Ashwini"
        assert result['birth_nakshatra_lord'] == "Ketu"
        
        # Longitude at 360 degrees (wraps to 0)
        result = dasha_calculator.calculate_dasha_periods(
            birth_datetime,
            360.0,
            include_antardashas=False
        )
        assert result['birth_nakshatra'] == "Ashwini"
        
        # Very close to nakshatra boundary
        result = dasha_calculator.calculate_dasha_periods(
            birth_datetime,
            13.333,
            include_antardashas=False
        )
        assert result['elapsed_in_birth_dasha'] == pytest.approx(1.0, abs=0.01)
    
    def test_years_to_days_conversion(self, dasha_calculator):
        """Test accurate year to days conversion."""
        years = 7.5
        days = years * 365.25
        
        # Test with leap year considerations
        start_date = datetime(2000, 1, 1)  # Leap year
        end_date = start_date + timedelta(days=days)
        
        actual_years = (end_date - start_date).days / 365.25
        assert actual_years == pytest.approx(years, abs=0.01)
    
    def test_special_yogas_in_dasha(self, dasha_calculator):
        """Test special yoga considerations in dasha."""
        chart_data = {
            'planets': {
                'Mars': {
                    'sign': 'Aries',  # Own sign
                    'house': 1,
                    'is_exalted': False,
                    'is_debilitated': False
                }
            },
            'yogas': ['Ruchaka Yoga']  # Pancha Mahapurusha Yoga
        }
        
        predictions = dasha_calculator.get_dasha_predictions('Mars', chart_data)
        
        # Should recognize beneficial placement
        assert 'strong' in predictions['specific'].lower() or 'beneficial' in predictions['specific'].lower()
    
    def test_dasha_balance_at_birth(self, dasha_calculator, birth_datetime):
        """Test dasha balance calculation at birth."""
        # Moon at 15 degrees (in Bharani, Venus ruled)
        moon_longitude = 15.0
        
        result = dasha_calculator.calculate_dasha_periods(
            birth_datetime,
            moon_longitude,
            include_antardashas=False
        )
        
        # Bharani is ruled by Venus (20 years)
        # 15 degrees is (15-13.333)/13.333 = 0.125 into Bharani
        # So 0.875 of Venus dasha remains = 17.5 years
        first_dasha = result['mahadashas'][0]
        assert first_dasha['lord'] == "Venus"
        
        remaining_days = (first_dasha['end_date'] - first_dasha['start_date']).days
        remaining_years = remaining_days / 365.25
        assert remaining_years == pytest.approx(17.5, abs=0.1)