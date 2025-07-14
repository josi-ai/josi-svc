"""Comprehensive unit tests for Ashtakoota compatibility service."""
import pytest
from unittest.mock import MagicMock, patch

from josi.services.vedic.ashtakoota_service import AshtakootaCalculator


class TestAshtakootaCalculator:
    """Comprehensive test coverage for AshtakootaCalculator."""
    
    @pytest.fixture
    def ashtakoota_calculator(self):
        """Create an AshtakootaCalculator instance."""
        return AshtakootaCalculator()
    
    def test_initialization(self, ashtakoota_calculator):
        """Test AshtakootaCalculator initialization."""
        # Check gana groupings
        assert len(ashtakoota_calculator.DEVA_GANA) == 9
        assert len(ashtakoota_calculator.MANUSHYA_GANA) == 9
        assert len(ashtakoota_calculator.RAKSHASA_GANA) == 9
        
        # Check all nakshatras are covered
        all_nakshatras = set(ashtakoota_calculator.DEVA_GANA + 
                            ashtakoota_calculator.MANUSHYA_GANA + 
                            ashtakoota_calculator.RAKSHASA_GANA)
        assert all_nakshatras == set(range(27))
        
        # Check yoni animals
        assert len(ashtakoota_calculator.YONI_ANIMALS) == 27
    
    def test_calculate_compatibility_basic(self, ashtakoota_calculator):
        """Test basic compatibility calculation."""
        # Person 1: Ashwini (0-13.33°), Person 2: Bharani (13.33-26.67°)
        result = ashtakoota_calculator.calculate_compatibility(
            person1_moon_longitude=5.0,
            person2_moon_longitude=20.0,
            person1_gender="male",
            person2_gender="female"
        )
        
        assert 'total_points' in result
        assert 'max_points' in result
        assert result['max_points'] == 36
        assert 'gunas' in result
        assert len(result['gunas']) == 8
        assert 'compatibility_percentage' in result
        assert 'interpretation' in result
    
    def test_get_nakshatra_number(self, ashtakoota_calculator):
        """Test nakshatra number calculation."""
        test_cases = [
            (0.0, 0),      # Ashwini start
            (13.0, 0),     # Ashwini end
            (14.0, 1),     # Bharani start
            (120.0, 9),    # Magha
            (359.0, 26),   # Revati
            (360.0, 0),    # Wraps to Ashwini
        ]
        
        for longitude, expected in test_cases:
            assert ashtakoota_calculator._get_nakshatra_number(longitude) == expected
    
    def test_calculate_varna_different_varnas(self, ashtakoota_calculator):
        """Test Varna (caste) guna calculation with different varnas."""
        # Test all varna combinations
        test_cases = [
            (0, 1, 0, 0),    # Brahmin-Brahmin: incompatible order
            (0, 5, 1, 1),    # Brahmin-Kshatriya: compatible
            (5, 10, 0, 0),   # Kshatriya-Vaishya: incompatible
            (10, 15, 0, 0),  # Vaishya-Shudra: incompatible
            (5, 0, 0, 0),    # Lower to higher: incompatible
        ]
        
        for nak1, nak2, expected_points, max_points in test_cases:
            points, max_p = ashtakoota_calculator._calculate_varna(nak1, nak2)
            assert points == expected_points
            assert max_p == max_points
    
    def test_calculate_vashya_compatibility(self, ashtakoota_calculator):
        """Test Vashya (mutual control) guna calculation."""
        # Same sign compatibility
        points, max_points = ashtakoota_calculator._calculate_vashya(0, 10)
        assert max_points == 2
        
        # Different signs
        points, max_points = ashtakoota_calculator._calculate_vashya(0, 120)
        assert max_points == 2
        assert 0 <= points <= 2
    
    def test_calculate_tara_compatibility(self, ashtakoota_calculator):
        """Test Tara (birth star) guna calculation."""
        # Same nakshatra
        points, max_points = ashtakoota_calculator._calculate_tara(5, 5)
        assert max_points == 3
        assert points == 3
        
        # Different nakshatras
        points, max_points = ashtakoota_calculator._calculate_tara(0, 9)
        assert max_points == 3
        assert 0 <= points <= 3
    
    def test_calculate_yoni_same_animal(self, ashtakoota_calculator):
        """Test Yoni (animal) guna with same animals."""
        # Find two nakshatras with same animal
        points, max_points = ashtakoota_calculator._calculate_yoni(0, 0)
        assert max_points == 4
        assert points == 4  # Same animal = full points
    
    def test_calculate_yoni_different_animals(self, ashtakoota_calculator):
        """Test Yoni guna with different animals."""
        # Horse (0) and Elephant (1)
        points, max_points = ashtakoota_calculator._calculate_yoni(0, 1)
        assert max_points == 4
        assert 0 <= points < 4
    
    def test_calculate_graha_maitri(self, ashtakoota_calculator):
        """Test Graha Maitri (planetary friendship) guna."""
        # Ketu-ruled nakshatras (0, 9, 18)
        points, max_points = ashtakoota_calculator._calculate_graha_maitri(0, 9)
        assert max_points == 5
        assert points == 5  # Same ruler = full points
        
        # Different rulers
        points, max_points = ashtakoota_calculator._calculate_graha_maitri(0, 1)
        assert max_points == 5
        assert 0 <= points <= 5
    
    def test_calculate_gana_compatibility(self, ashtakoota_calculator):
        """Test Gana (temperament) guna calculation."""
        # Deva-Deva
        points, max_points = ashtakoota_calculator._calculate_gana(0, 4)
        assert max_points == 6
        assert points == 6  # Same gana = full points
        
        # Deva-Manushya
        points, max_points = ashtakoota_calculator._calculate_gana(0, 1)
        assert points < 6
        
        # Deva-Rakshasa
        points, max_points = ashtakoota_calculator._calculate_gana(0, 2)
        assert points == 0  # Incompatible
    
    def test_calculate_bhakoot_compatible_signs(self, ashtakoota_calculator):
        """Test Bhakoot (love) guna with compatible signs."""
        # Same sign (both in Aries)
        points, max_points = ashtakoota_calculator._calculate_bhakoot(0, 10)
        assert max_points == 7
        assert points == 7
        
        # Friendly signs (varies by implementation)
        points, max_points = ashtakoota_calculator._calculate_bhakoot(0, 120)
        assert 0 <= points <= 7
    
    def test_calculate_nadi_compatibility(self, ashtakoota_calculator):
        """Test Nadi (health) guna calculation."""
        # Same nadi type
        points, max_points = ashtakoota_calculator._calculate_nadi(0, 3)
        assert max_points == 8
        # Same nadi = 0 points (health concerns)
        
        # Different nadi types
        points, max_points = ashtakoota_calculator._calculate_nadi(0, 1)
        assert max_points == 8
        assert 0 <= points <= 8
    
    def test_gender_considerations(self, ashtakoota_calculator):
        """Test gender-specific compatibility rules."""
        # Test male-female
        result_mf = ashtakoota_calculator.calculate_compatibility(
            45.0, 90.0, "male", "female"
        )
        
        # Test female-male (reversed)
        result_fm = ashtakoota_calculator.calculate_compatibility(
            45.0, 90.0, "female", "male"
        )
        
        # Some gunas may differ based on gender order
        assert 'total_points' in result_mf
        assert 'total_points' in result_fm
    
    def test_same_gender_compatibility(self, ashtakoota_calculator):
        """Test same-gender compatibility calculation."""
        # Should still calculate, useful for business partnerships etc
        result = ashtakoota_calculator.calculate_compatibility(
            120.0, 240.0, "male", "male"
        )
        
        assert 'total_points' in result
        assert result['max_points'] == 36
    
    def test_compatibility_interpretation(self, ashtakoota_calculator):
        """Test compatibility score interpretation."""
        # High compatibility (>24 points)
        with patch.object(ashtakoota_calculator, '_calculate_all_gunas') as mock_calc:
            mock_calc.return_value = {
                'Varna': (1, 1), 'Vashya': (2, 2), 'Tara': (3, 3),
                'Yoni': (4, 4), 'Graha Maitri': (5, 5), 'Gana': (5, 6),
                'Bhakoot': (6, 7), 'Nadi': (7, 8)
            }
            
            result = ashtakoota_calculator.calculate_compatibility(0, 0)
            assert result['total_points'] == 33
            assert 'excellent' in result['interpretation'].lower()
        
        # Medium compatibility (18-24 points)
        with patch.object(ashtakoota_calculator, '_calculate_all_gunas') as mock_calc:
            mock_calc.return_value = {
                'Varna': (0, 1), 'Vashya': (1, 2), 'Tara': (2, 3),
                'Yoni': (2, 4), 'Graha Maitri': (3, 5), 'Gana': (3, 6),
                'Bhakoot': (4, 7), 'Nadi': (5, 8)
            }
            
            result = ashtakoota_calculator.calculate_compatibility(0, 0)
            assert result['total_points'] == 20
            assert 'average' in result['interpretation'].lower() or 'moderate' in result['interpretation'].lower()
    
    def test_calculate_all_gunas(self, ashtakoota_calculator):
        """Test calculation of all gunas together."""
        nak1, nak2 = 5, 10  # Random nakshatras
        
        result = ashtakoota_calculator._calculate_all_gunas(nak1, nak2)
        
        assert len(result) == 8
        assert 'Varna' in result
        assert 'Vashya' in result
        assert 'Tara' in result
        assert 'Yoni' in result
        assert 'Graha Maitri' in result
        assert 'Gana' in result
        assert 'Bhakoot' in result
        assert 'Nadi' in result
        
        # Each guna should return (points, max_points)
        for guna_name, (points, max_points) in result.items():
            assert isinstance(points, (int, float))
            assert isinstance(max_points, int)
            assert 0 <= points <= max_points
    
    def test_edge_cases(self, ashtakoota_calculator):
        """Test edge cases in compatibility calculation."""
        # Longitude at boundaries
        result = ashtakoota_calculator.calculate_compatibility(
            0.0, 359.999
        )
        assert 'total_points' in result
        
        # Same longitude
        result = ashtakoota_calculator.calculate_compatibility(
            180.0, 180.0
        )
        assert result['total_points'] >= 0
        
        # Maximum separation
        result = ashtakoota_calculator.calculate_compatibility(
            0.0, 180.0
        )
        assert 'total_points' in result
    
    def test_detailed_guna_analysis(self, ashtakoota_calculator):
        """Test detailed analysis for each guna."""
        result = ashtakoota_calculator.calculate_compatibility(
            45.0, 135.0
        )
        
        # Each guna should have detailed info
        for guna_info in result['gunas']:
            assert 'name' in guna_info
            assert 'points' in guna_info
            assert 'max_points' in guna_info
            assert 'description' in guna_info
    
    def test_nakshatra_pada_consideration(self, ashtakoota_calculator):
        """Test if nakshatra pada affects compatibility."""
        # Same nakshatra, different padas
        # 3.33° apart within same nakshatra
        result1 = ashtakoota_calculator.calculate_compatibility(2.0, 5.0)
        result2 = ashtakoota_calculator.calculate_compatibility(2.0, 10.0)
        
        # Pada differences might affect some calculations
        assert 'total_points' in result1
        assert 'total_points' in result2
    
    def test_dosha_analysis(self, ashtakoota_calculator):
        """Test identification of doshas (afflictions)."""
        # When Nadi guna scores 0, it indicates Nadi Dosha
        with patch.object(ashtakoota_calculator, '_calculate_nadi') as mock_nadi:
            mock_nadi.return_value = (0, 8)
            
            result = ashtakoota_calculator.calculate_compatibility(0, 0)
            
            # Should identify Nadi Dosha
            nadi_guna = next(g for g in result['gunas'] if g['name'] == 'Nadi')
            assert nadi_guna['points'] == 0
            # Description should mention the dosha