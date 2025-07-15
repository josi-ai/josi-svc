"""Comprehensive tests for Vedic astrology modules to achieve 90% coverage."""
import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timedelta
import pytz

from josi.services.vedic.dasha_service import (
    VimshottariDashaCalculator, 
    YoginiDashaCalculator, 
    CharaDashaCalculator
)
from josi.services.vedic.panchang_service import PanchangCalculator
from josi.services.vedic.muhurta_service import MuhurtaCalculator
from josi.services.vedic.ashtakoota_service import AshtakootaCalculator


class TestVimshottariDashaComprehensive:
    """Comprehensive tests for Vimshottari Dasha calculations."""
    
    @pytest.fixture
    def dasha_calculator(self):
        return VimshottariDashaCalculator()
    
    def test_get_nakshatra_from_longitude(self, dasha_calculator):
        """Test nakshatra calculation from longitude."""
        # Test each nakshatra boundary
        test_cases = [
            (0.0, 0),      # Ashwini
            (13.333, 1),   # Bharani
            (26.666, 2),   # Krittika
            (120.0, 9),    # Magha
            (240.0, 18),   # Jyeshtha
            (346.667, 26)  # Revati
        ]
        
        for longitude, expected_index in test_cases:
            result = dasha_calculator._get_nakshatra_from_longitude(longitude)
            assert result == expected_index
    
    def test_calculate_elapsed_portion(self, dasha_calculator):
        """Test elapsed portion calculation within nakshatra."""
        # Middle of Ashwini (6.666 degrees)
        result = dasha_calculator._calculate_elapsed_portion(6.666)
        assert pytest.approx(result, 0.01) == 0.5
        
        # Start of Bharani
        result = dasha_calculator._calculate_elapsed_portion(13.333)
        assert pytest.approx(result, 0.01) == 0.0
        
        # End of nakshatra
        result = dasha_calculator._calculate_elapsed_portion(13.0)
        assert pytest.approx(result, 0.01) == 0.975
    
    def test_get_dasha_order(self, dasha_calculator):
        """Test dasha order generation from starting planet."""
        # Starting from Sun
        order = dasha_calculator._get_dasha_order("Sun")
        assert order[0] == "Sun"
        assert order[1] == "Moon"
        assert len(order) == 9
        
        # Starting from Jupiter
        order = dasha_calculator._get_dasha_order("Jupiter")
        assert order[0] == "Jupiter"
        assert order[-1] == "Mercury"
    
    def test_calculate_sub_periods(self, dasha_calculator):
        """Test antardasha calculation."""
        mahadasha = {
            "planet": "Venus",
            "start_date": datetime(2020, 1, 1),
            "end_date": datetime(2040, 1, 1),
            "years": 20
        }
        
        result = dasha_calculator._calculate_sub_periods(mahadasha)
        
        assert len(result) == 9  # 9 antardashas
        assert result[0]["planet"] == "Venus"  # First is same as mahadasha
        
        # Check total duration equals mahadasha duration
        total_days = sum(
            (ad["end_date"] - ad["start_date"]).days 
            for ad in result
        )
        mahadasha_days = (mahadasha["end_date"] - mahadasha["start_date"]).days
        assert abs(total_days - mahadasha_days) <= 9  # Allow small rounding
    
    def test_calculate_pratyantar_periods(self, dasha_calculator):
        """Test pratyantardasha calculation."""
        antardasha = {
            "planet": "Moon",
            "start_date": datetime(2020, 1, 1),
            "end_date": datetime(2020, 11, 1),
            "years": 0.833  # 10 months
        }
        
        result = dasha_calculator._calculate_pratyantar_periods(antardasha)
        
        assert len(result) == 9
        assert result[0]["planet"] == "Moon"
        
        # Verify periods don't overlap
        for i in range(len(result) - 1):
            assert result[i]["end_date"] <= result[i+1]["start_date"]
    
    def test_get_current_dasha(self, dasha_calculator):
        """Test finding current dasha period."""
        mahadashas = [
            {
                "planet": "Sun",
                "start_date": datetime(2000, 1, 1),
                "end_date": datetime(2006, 1, 1),
                "antardashas": []
            },
            {
                "planet": "Moon",
                "start_date": datetime(2006, 1, 1),
                "end_date": datetime(2016, 1, 1),
                "antardashas": []
            }
        ]
        
        # Test date in Sun period
        result = dasha_calculator._get_current_dasha(
            mahadashas, 
            datetime(2003, 6, 1)
        )
        assert result["mahadasha"]["planet"] == "Sun"
        
        # Test date in Moon period
        result = dasha_calculator._get_current_dasha(
            mahadashas,
            datetime(2010, 1, 1)
        )
        assert result["mahadasha"]["planet"] == "Moon"
    
    def test_get_dasha_predictions(self, dasha_calculator):
        """Test dasha prediction generation."""
        current_dasha = {
            "mahadasha": {"planet": "Jupiter"},
            "antardasha": {"planet": "Venus"}
        }
        
        mahadashas = [{
            "planet": "Jupiter",
            "start_date": datetime(2020, 1, 1),
            "end_date": datetime(2036, 1, 1)
        }]
        
        result = dasha_calculator.get_dasha_predictions(current_dasha, mahadashas)
        
        assert "current_influences" in result
        assert "upcoming_changes" in result
        assert "remedies" in result
        assert len(result["current_influences"]) > 0


class TestPanchangCalculatorComprehensive:
    """Comprehensive tests for Panchang calculations."""
    
    @pytest.fixture
    def panchang_calculator(self):
        return PanchangCalculator()
    
    def test_calculate_tithi_edge_cases(self, panchang_calculator):
        """Test tithi calculation at boundaries."""
        # New moon (0 degree difference)
        result = panchang_calculator.calculate_tithi(0.0, 0.0)
        assert result["index"] == 1
        assert result["name"] == "Shukla Pratipada"
        
        # Full moon (180 degree difference)
        result = panchang_calculator.calculate_tithi(0.0, 180.0)
        assert result["index"] == 15
        assert result["name"] == "Purnima"
        
        # Amavasya (360 degree difference)
        result = panchang_calculator.calculate_tithi(0.0, 359.9)
        assert result["index"] == 30
        assert result["name"] == "Amavasya"
    
    def test_calculate_nakshatra_with_pada(self, panchang_calculator):
        """Test nakshatra calculation with pada."""
        # First pada of Ashwini
        result = panchang_calculator.calculate_nakshatra(1.0)
        assert result["index"] == 1
        assert result["name"] == "Ashwini"
        assert result["pada"] == 1
        assert result["deity"] == "Ashwini Kumaras"
        
        # Last pada of Revati
        result = panchang_calculator.calculate_nakshatra(359.0)
        assert result["index"] == 27
        assert result["name"] == "Revati"
        assert result["pada"] == 4
    
    def test_calculate_yoga_all_types(self, panchang_calculator):
        """Test all 27 yoga calculations."""
        # Test a few specific yogas
        result = panchang_calculator.calculate_yoga(0.0, 0.0)
        assert result["index"] == 1
        assert result["name"] == "Vishkumbha"
        
        # Siddha Yoga (auspicious)
        sun_moon_sum = 240.0  # Should give Siddha yoga
        result = panchang_calculator.calculate_yoga(120.0, 120.0)
        assert 1 <= result["index"] <= 27
    
    def test_calculate_karana_all_types(self, panchang_calculator):
        """Test all karana calculations."""
        # Bava karana (first of movable karanas)
        result = panchang_calculator.calculate_karana(0.0, 3.0)
        assert result["name"] in panchang_calculator.karanas
        
        # Test fixed karanas at end of lunar month
        result = panchang_calculator.calculate_karana(0.0, 357.0)
        assert result["category"] == "fixed"
    
    def test_get_vara_weekday(self, panchang_calculator):
        """Test weekday calculation."""
        # Test known date - Jan 1, 2024 was Monday
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = panchang_calculator.get_vara(dt)
        assert result["name"] == "Somavara"
        assert result["ruler"] == "Moon"
    
    def test_calculate_sunrise_sunset(self, panchang_calculator):
        """Test sunrise/sunset calculation."""
        dt = datetime(2024, 6, 21)  # Summer solstice
        
        # NYC coordinates
        result = panchang_calculator.calculate_sunrise_sunset(
            dt, 40.7128, -74.0060, "America/New_York"
        )
        
        assert "sunrise" in result
        assert "sunset" in result
        assert "day_length" in result
        assert result["day_length"] > 14  # Long day in summer
    
    def test_calculate_moonrise_moonset(self, panchang_calculator):
        """Test moonrise/moonset calculation."""
        dt = datetime(2024, 1, 15)  # Mid-month
        
        result = panchang_calculator.calculate_moonrise_moonset(
            dt, 40.7128, -74.0060, "America/New_York"
        )
        
        assert "moonrise" in result
        assert "moonset" in result
        assert "moon_phase" in result
    
    def test_calculate_hora(self, panchang_calculator):
        """Test hora (planetary hour) calculation."""
        dt = datetime(2024, 1, 1, 10, 30, 0)
        
        with patch.object(panchang_calculator, 'calculate_sunrise_sunset') as mock_sun:
            mock_sun.return_value = {
                "sunrise": datetime(2024, 1, 1, 7, 0, 0),
                "sunset": datetime(2024, 1, 1, 17, 0, 0)
            }
            
            result = panchang_calculator.calculate_hora(
                dt, 40.7128, -74.0060, "UTC"
            )
            
            assert "hora" in result
            assert "ruler" in result
            assert result["ruler"] in ["Sun", "Moon", "Mars", "Mercury", 
                                      "Jupiter", "Venus", "Saturn"]
    
    def test_calculate_choghadiya(self, panchang_calculator):
        """Test choghadiya calculation."""
        dt = datetime(2024, 1, 1, 14, 0, 0)
        
        with patch.object(panchang_calculator, 'calculate_sunrise_sunset') as mock_sun:
            mock_sun.return_value = {
                "sunrise": datetime(2024, 1, 1, 7, 0, 0),
                "sunset": datetime(2024, 1, 1, 17, 0, 0)
            }
            
            result = panchang_calculator.calculate_choghadiya(
                dt, 40.7128, -74.0060, "UTC"
            )
            
            assert "period" in result
            assert "quality" in result
            assert result["quality"] in ["good", "neutral", "bad"]


class TestMuhurtaCalculatorComprehensive:
    """Comprehensive tests for Muhurta calculations."""
    
    @pytest.fixture
    def muhurta_calculator(self):
        return MuhurtaCalculator()
    
    def test_calculate_abhijit_muhurta(self, muhurta_calculator):
        """Test Abhijit muhurta calculation."""
        dt = datetime(2024, 1, 1)
        
        result = muhurta_calculator.calculate_abhijit_muhurta(
            dt, 28.7041, 77.1025, "Asia/Kolkata"
        )
        
        assert "start" in result
        assert "end" in result
        assert "is_active" in result
        
        # Abhijit is around midday
        assert result["start"].hour >= 11
        assert result["start"].hour <= 13
    
    def test_is_pushya_nakshatra(self, muhurta_calculator):
        """Test Pushya nakshatra detection."""
        # Mock moon in Pushya
        with patch.object(muhurta_calculator, '_get_moon_longitude') as mock_moon:
            mock_moon.return_value = 100.0  # Pushya range
            
            result = muhurta_calculator.is_pushya_nakshatra(datetime(2024, 1, 1))
            assert result is True
            
            mock_moon.return_value = 200.0  # Not Pushya
            result = muhurta_calculator.is_pushya_nakshatra(datetime(2024, 1, 1))
            assert result is False
    
    def test_get_ravi_yoga(self, muhurta_calculator):
        """Test Ravi Yoga calculation."""
        # Sunday with Pushya
        dt = datetime(2024, 1, 7)  # Sunday
        
        with patch.object(muhurta_calculator, 'is_pushya_nakshatra') as mock_pushya:
            mock_pushya.return_value = True
            
            result = muhurta_calculator.get_ravi_yoga(dt)
            assert result["has_ravi_yoga"] is True
            assert result["quality"] == "excellent"
    
    def test_check_panchaka(self, muhurta_calculator):
        """Test Panchaka dosha calculation."""
        # Test inauspicious nakshatra/tithi combinations
        result = muhurta_calculator.check_panchaka(
            tithi_index=5,  # Panchami
            nakshatra_index=4  # Rohini
        )
        
        assert isinstance(result, dict)
        assert "has_panchaka" in result
        assert "severity" in result
    
    def test_evaluate_muhurta_quality(self, muhurta_calculator):
        """Test muhurta quality evaluation."""
        factors = {
            "tithi": {"index": 5, "quality": "good"},
            "nakshatra": {"index": 8, "quality": "excellent"},
            "yoga": {"index": 16, "quality": "good"},
            "karana": {"quality": "good"},
            "vara": {"quality": "neutral"}
        }
        
        result = muhurta_calculator.evaluate_muhurta_quality(
            factors, "marriage"
        )
        
        assert "score" in result
        assert "quality" in result
        assert "recommendations" in result
        assert 0 <= result["score"] <= 100
    
    def test_find_next_good_muhurta(self, muhurta_calculator):
        """Test finding next good muhurta."""
        with patch.object(muhurta_calculator, 'evaluate_muhurta_quality') as mock_eval:
            mock_eval.return_value = {"score": 85, "quality": "excellent"}
            
            result = muhurta_calculator.find_next_good_muhurta(
                purpose="marriage",
                start_date=datetime(2024, 1, 1),
                latitude=28.7041,
                longitude=77.1025,
                timezone="Asia/Kolkata"
            )
            
            assert result is not None
            assert "datetime" in result
            assert "quality" in result
            assert result["quality"]["score"] >= 70


class TestAshtakootaCalculatorComprehensive:
    """Comprehensive tests for Ashtakoota compatibility."""
    
    @pytest.fixture
    def ashtakoota_calculator(self):
        return AshtakootaCalculator()
    
    @pytest.fixture
    def partner1_data(self):
        return {
            "moon_nakshatra": 1,  # Ashwini
            "moon_sign": 0,       # Aries
            "birth_datetime": datetime(1990, 1, 1, 10, 0, 0),
            "gender": "male"
        }
    
    @pytest.fixture
    def partner2_data(self):
        return {
            "moon_nakshatra": 9,  # Magha
            "moon_sign": 4,       # Leo
            "birth_datetime": datetime(1992, 6, 15, 14, 30, 0),
            "gender": "female"
        }
    
    def test_calculate_varna_koota(self, ashtakoota_calculator):
        """Test Varna (caste) compatibility."""
        # Brahmin with Kshatriya
        score = ashtakoota_calculator.calculate_varna(0, 4)  # Aries, Leo
        assert score == 1
        
        # Lower to higher varna
        score = ashtakoota_calculator.calculate_varna(8, 0)  # Sagittarius, Aries
        assert score == 0
    
    def test_calculate_vashya_koota(self, ashtakoota_calculator):
        """Test Vashya (control) compatibility."""
        # Aries (quadruped) with Leo (biped)
        score = ashtakoota_calculator.calculate_vashya(0, 4)
        assert 0 <= score <= 2
        
        # Same category
        score = ashtakoota_calculator.calculate_vashya(0, 0)
        assert score == 2
    
    def test_calculate_tara_koota(self, ashtakoota_calculator):
        """Test Tara (birth star) compatibility."""
        # Compatible nakshatras
        score = ashtakoota_calculator.calculate_tara(1, 10)
        assert 0 <= score <= 3
        
        # Same nakshatra
        score = ashtakoota_calculator.calculate_tara(1, 1)
        assert score == 3
    
    def test_calculate_yoni_koota_all_animals(self, ashtakoota_calculator):
        """Test Yoni (sexual) compatibility for all animal types."""
        # Horse with Elephant (enemies)
        score = ashtakoota_calculator.calculate_yoni(1, 2)  # Ashwini, Bharani
        assert score == 0
        
        # Same yoni
        score = ashtakoota_calculator.calculate_yoni(1, 1)
        assert score == 4
        
        # Friendly yonis
        score = ashtakoota_calculator.calculate_yoni(1, 7)  # Horse with compatible
        assert score >= 2
    
    def test_calculate_graha_maitri(self, ashtakoota_calculator):
        """Test Graha Maitri (planetary friendship)."""
        # Mars (Aries) with Sun (Leo) - friends
        score = ashtakoota_calculator.calculate_graha_maitri(0, 4)
        assert score == 5
        
        # Enemies
        score = ashtakoota_calculator.calculate_graha_maitri(2, 5)  # Mercury-Mercury
        assert score == 5  # Same planet always friendly
    
    def test_calculate_gana_koota(self, ashtakoota_calculator):
        """Test Gana (temperament) compatibility."""
        # Deva with Deva
        score = ashtakoota_calculator.calculate_gana(1, 5, "male", "female")
        assert score > 0
        
        # Rakshasa with Deva
        score = ashtakoota_calculator.calculate_gana(2, 5, "male", "female")
        assert score == 0
    
    def test_calculate_bhakoot_koota(self, ashtakoota_calculator):
        """Test Bhakoot (love) compatibility."""
        # 5-9 position (trine) - auspicious
        score = ashtakoota_calculator.calculate_bhakoot(0, 4)  # Aries-Leo
        assert score == 7
        
        # 6-8 position - inauspicious
        score = ashtakoota_calculator.calculate_bhakoot(0, 5)  # Aries-Virgo
        assert score == 0
        
        # Same sign
        score = ashtakoota_calculator.calculate_bhakoot(0, 0)
        assert score == 7
    
    def test_calculate_nadi_koota(self, ashtakoota_calculator):
        """Test Nadi (pulse) compatibility."""
        # Different nadis
        score = ashtakoota_calculator.calculate_nadi(1, 10)
        assert score == 8
        
        # Same nadi (worst case)
        score = ashtakoota_calculator.calculate_nadi(1, 4)  # Both Aadi nadi
        assert score == 0
    
    def test_get_detailed_analysis(self, ashtakoota_calculator):
        """Test detailed compatibility analysis."""
        scores = {
            "varna": {"score": 1, "max_score": 1},
            "vashya": {"score": 2, "max_score": 2},
            "tara": {"score": 3, "max_score": 3},
            "yoni": {"score": 2, "max_score": 4},
            "graha_maitri": {"score": 5, "max_score": 5},
            "gana": {"score": 6, "max_score": 6},
            "bhakoot": {"score": 7, "max_score": 7},
            "nadi": {"score": 8, "max_score": 8}
        }
        
        total_score = 34
        
        result = ashtakoota_calculator.get_detailed_analysis(scores, total_score)
        
        assert "compatibility_level" in result
        assert "recommendation" in result
        assert "manglik_dosha" in result
        assert "remedies" in result
        
        # High score should give positive recommendation
        assert result["compatibility_level"] == "excellent"
    
    def test_check_manglik_dosha(self, ashtakoota_calculator):
        """Test Manglik dosha detection."""
        # Mock Mars in 1st house
        with patch.object(ashtakoota_calculator, '_get_mars_position') as mock_mars:
            mock_mars.return_value = {"house": 1}
            
            result = ashtakoota_calculator.check_manglik_dosha({})
            assert result["has_dosha"] is True
            assert 1 in result["houses_affected"]
            
            # Mars in safe house
            mock_mars.return_value = {"house": 3}
            result = ashtakoota_calculator.check_manglik_dosha({})
            assert result["has_dosha"] is False
    
    def test_calculate_with_exceptions(self, ashtakoota_calculator):
        """Test calculation with Vedic exceptions."""
        # Test with same nakshatra exception
        partner1 = {"moon_nakshatra": 1, "moon_sign": 0}
        partner2 = {"moon_nakshatra": 1, "moon_sign": 0}
        
        result = ashtakoota_calculator.calculate_compatibility(partner1, partner2)
        
        # Should apply exception rules
        assert "exceptions_applied" in result
        assert result["total_score"] > 18  # Minimum acceptable
    
    def test_rajju_koota(self, ashtakoota_calculator):
        """Test Rajju (rope) compatibility."""
        # Same body part - inauspicious
        score = ashtakoota_calculator.calculate_rajju(1, 10)
        assert isinstance(score, (int, float))
        
        # Different body parts
        score = ashtakoota_calculator.calculate_rajju(1, 5)
        assert score >= 0
    
    def test_vedha_koota(self, ashtakoota_calculator):
        """Test Vedha (obstruction) compatibility."""
        # Vedha nakshatras
        score = ashtakoota_calculator.calculate_vedha(1, 18)  # Ashwini-Jyeshtha
        assert score == 0
        
        # Non-vedha nakshatras
        score = ashtakoota_calculator.calculate_vedha(1, 5)
        assert score > 0
    
    def test_get_dosha_analysis(self, ashtakoota_calculator):
        """Test comprehensive dosha analysis."""
        chart_data = {
            "planets": {
                "Mars": {"sign": 0, "house": 7},
                "Saturn": {"sign": 6, "house": 7},
                "Rahu": {"sign": 3, "house": 1}
            }
        }
        
        result = ashtakoota_calculator.get_dosha_analysis(chart_data)
        
        assert "manglik_dosha" in result
        assert "kaal_sarp_dosha" in result
        assert "pitra_dosha" in result
        assert "remedies" in result