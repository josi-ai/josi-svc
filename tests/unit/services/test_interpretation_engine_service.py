"""Comprehensive unit tests for InterpretationEngine."""
import pytest
from unittest.mock import MagicMock, patch
from josi.services.interpretation_engine_service import InterpretationEngine


class TestInterpretationEngine:
    """Comprehensive test coverage for InterpretationEngine."""
    
    @pytest.fixture
    def interpretation_engine(self):
        """Create an InterpretationEngine instance."""
        with patch.object(InterpretationEngine, '_load_planet_meanings') as mock_planet:
            with patch.object(InterpretationEngine, '_load_sign_meanings') as mock_sign:
                with patch.object(InterpretationEngine, '_load_house_meanings') as mock_house:
                    with patch.object(InterpretationEngine, '_load_aspect_meanings') as mock_aspect:
                        mock_planet.return_value = self.get_mock_planet_meanings()
                        mock_sign.return_value = self.get_mock_sign_meanings()
                        mock_house.return_value = self.get_mock_house_meanings()
                        mock_aspect.return_value = self.get_mock_aspect_meanings()
                        return InterpretationEngine()
    
    @pytest.fixture
    def vedic_chart_data(self):
        """Sample Vedic chart data."""
        return {
            'chart_type': 'vedic',
            'ascendant': {
                'sign': 'Aries',
                'nakshatra': 'Ashwini',
                'pada': 1,
                'longitude': 5.0
            },
            'planets': {
                'Sun': {
                    'sign': 'Leo',
                    'house': 5,
                    'nakshatra': 'Magha',
                    'pada': 2,
                    'longitude': 125.0
                },
                'Moon': {
                    'sign': 'Cancer',
                    'house': 4,
                    'nakshatra': 'Pushya',
                    'pada': 3,
                    'longitude': 105.0
                },
                'Mars': {
                    'sign': 'Scorpio',
                    'house': 8,
                    'nakshatra': 'Anuradha',
                    'pada': 1,
                    'longitude': 225.0
                }
            },
            'houses': [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
        }
    
    @pytest.fixture
    def western_chart_data(self):
        """Sample Western chart data."""
        return {
            'chart_type': 'western',
            'ascendant': {
                'sign': 'Libra',
                'longitude': 185.0
            },
            'planets': {
                'Sun': {
                    'sign': 'Virgo',
                    'house': 12,
                    'longitude': 165.0
                },
                'Moon': {
                    'sign': 'Pisces',
                    'house': 6,
                    'longitude': 345.0
                },
                'Venus': {
                    'sign': 'Libra',
                    'house': 1,
                    'longitude': 190.0
                }
            },
            'houses': [185.0, 215.0, 245.0, 275.0, 305.0, 335.0, 5.0, 35.0, 65.0, 95.0, 125.0, 155.0]
        }
    
    def get_mock_planet_meanings(self):
        """Get mock planet meanings."""
        return {
            'Sun': {
                'general': 'Self, ego, vitality',
                'personality': 'Leadership, confidence',
                'career': 'Authority, management',
                'relationships': 'Father, authority figures',
                'spiritual': 'Soul purpose'
            },
            'Moon': {
                'general': 'Emotions, mind, mother',
                'personality': 'Sensitivity, intuition',
                'career': 'Public, nurturing roles',
                'relationships': 'Mother, emotional needs',
                'spiritual': 'Inner peace'
            },
            'Mars': {
                'general': 'Energy, action, courage',
                'personality': 'Assertiveness, passion',
                'career': 'Competition, sports',
                'relationships': 'Passion, conflict',
                'spiritual': 'Will power'
            },
            'Venus': {
                'general': 'Love, beauty, harmony',
                'personality': 'Charm, artistic nature',
                'career': 'Arts, luxury',
                'relationships': 'Romance, partnerships',
                'spiritual': 'Divine love'
            }
        }
    
    def get_mock_sign_meanings(self):
        """Get mock sign meanings."""
        return {
            'Aries': {
                'traits': 'Independent, pioneering',
                'element': 'Fire',
                'quality': 'Cardinal'
            },
            'Leo': {
                'traits': 'Creative, generous',
                'element': 'Fire',
                'quality': 'Fixed'
            },
            'Cancer': {
                'traits': 'Nurturing, protective',
                'element': 'Water',
                'quality': 'Cardinal'
            },
            'Scorpio': {
                'traits': 'Intense, transformative',
                'element': 'Water',
                'quality': 'Fixed'
            },
            'Libra': {
                'traits': 'Balanced, diplomatic',
                'element': 'Air',
                'quality': 'Cardinal'
            },
            'Virgo': {
                'traits': 'Analytical, practical',
                'element': 'Earth',
                'quality': 'Mutable'
            },
            'Pisces': {
                'traits': 'Compassionate, intuitive',
                'element': 'Water',
                'quality': 'Mutable'
            }
        }
    
    def get_mock_house_meanings(self):
        """Get mock house meanings."""
        return {
            1: {'area': 'Self, appearance', 'keywords': 'Identity, body'},
            4: {'area': 'Home, family', 'keywords': 'Roots, mother'},
            5: {'area': 'Creativity, children', 'keywords': 'Romance, hobbies'},
            6: {'area': 'Health, service', 'keywords': 'Work, illness'},
            8: {'area': 'Transformation', 'keywords': 'Death, rebirth'},
            12: {'area': 'Spirituality', 'keywords': 'Hidden, isolation'}
        }
    
    def get_mock_aspect_meanings(self):
        """Get mock aspect meanings."""
        return {
            'conjunction': {'nature': 'Blending', 'orb': 8},
            'opposition': {'nature': 'Tension', 'orb': 8},
            'trine': {'nature': 'Harmony', 'orb': 8},
            'square': {'nature': 'Challenge', 'orb': 7},
            'sextile': {'nature': 'Opportunity', 'orb': 6}
        }
    
    def test_initialization(self):
        """Test InterpretationEngine initialization."""
        with patch.object(InterpretationEngine, '_load_planet_meanings') as mock_planet:
            with patch.object(InterpretationEngine, '_load_sign_meanings') as mock_sign:
                with patch.object(InterpretationEngine, '_load_house_meanings') as mock_house:
                    with patch.object(InterpretationEngine, '_load_aspect_meanings') as mock_aspect:
                        engine = InterpretationEngine()
                        
                        # Verify all loaders were called
                        mock_planet.assert_called_once()
                        mock_sign.assert_called_once()
                        mock_house.assert_called_once()
                        mock_aspect.assert_called_once()
                        
                        # Verify attributes were set
                        assert hasattr(engine, 'planet_meanings')
                        assert hasattr(engine, 'sign_meanings')
                        assert hasattr(engine, 'house_meanings')
                        assert hasattr(engine, 'aspect_meanings')
    
    def test_generate_interpretations_vedic(self, interpretation_engine, vedic_chart_data):
        """Test generating interpretations for Vedic chart."""
        result = interpretation_engine.generate_interpretations(
            vedic_chart_data,
            'vedic'
        )
        
        # Should have all interpretation types
        assert 'general' in result
        assert 'personality' in result
        assert 'career' in result
        assert 'relationships' in result
        assert 'life_purpose' in result
        
        # Each interpretation should be a dict
        assert isinstance(result['general'], dict)
        assert isinstance(result['personality'], dict)
        assert isinstance(result['career'], dict)
        assert isinstance(result['relationships'], dict)
        assert isinstance(result['life_purpose'], dict)
    
    def test_generate_interpretations_western(self, interpretation_engine, western_chart_data):
        """Test generating interpretations for Western chart."""
        result = interpretation_engine.generate_interpretations(
            western_chart_data,
            'western'
        )
        
        # Should have all interpretation types
        assert 'general' in result
        assert 'personality' in result
        assert 'career' in result
        assert 'relationships' in result
        assert 'life_purpose' in result
    
    def test_generate_general_interpretation(self, interpretation_engine, vedic_chart_data):
        """Test general interpretation generation."""
        result = interpretation_engine._generate_general_interpretation(
            vedic_chart_data,
            'vedic'
        )
        
        assert isinstance(result, dict)
        assert 'summary' in result
        assert 'key_themes' in result
        assert 'strengths' in result
        assert 'challenges' in result
    
    def test_generate_personality_interpretation(self, interpretation_engine, vedic_chart_data):
        """Test personality interpretation generation."""
        result = interpretation_engine._generate_personality_interpretation(
            vedic_chart_data,
            'vedic'
        )
        
        assert isinstance(result, dict)
        assert 'core_traits' in result
        assert 'emotional_nature' in result
        assert 'mental_approach' in result
        assert 'behavioral_patterns' in result
    
    def test_generate_career_interpretation(self, interpretation_engine, vedic_chart_data):
        """Test career interpretation generation."""
        result = interpretation_engine._generate_career_interpretation(
            vedic_chart_data,
            'vedic'
        )
        
        assert isinstance(result, dict)
        assert 'suitable_fields' in result
        assert 'work_style' in result
        assert 'success_factors' in result
        assert 'timing' in result
    
    def test_generate_relationship_interpretation(self, interpretation_engine, vedic_chart_data):
        """Test relationship interpretation generation."""
        result = interpretation_engine._generate_relationship_interpretation(
            vedic_chart_data,
            'vedic'
        )
        
        assert isinstance(result, dict)
        assert 'relationship_style' in result
        assert 'compatibility_factors' in result
        assert 'challenges' in result
        assert 'growth_areas' in result
    
    def test_generate_life_purpose_interpretation(self, interpretation_engine, vedic_chart_data):
        """Test life purpose interpretation generation."""
        result = interpretation_engine._generate_life_purpose_interpretation(
            vedic_chart_data,
            'vedic'
        )
        
        assert isinstance(result, dict)
        assert 'soul_mission' in result
        assert 'karmic_lessons' in result
        assert 'spiritual_path' in result
        assert 'dharma' in result
    
    def test_interpret_planet_in_sign(self, interpretation_engine):
        """Test interpreting planet in sign."""
        result = interpretation_engine._interpret_planet_in_sign(
            'Sun',
            'Leo'
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should combine planet and sign meanings
    
    def test_interpret_planet_in_house(self, interpretation_engine):
        """Test interpreting planet in house."""
        result = interpretation_engine._interpret_planet_in_house(
            'Moon',
            4
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should combine planet and house meanings
    
    def test_interpret_ascendant(self, interpretation_engine):
        """Test interpreting ascendant."""
        ascendant_data = {
            'sign': 'Aries',
            'nakshatra': 'Ashwini',
            'pada': 1
        }
        
        result = interpretation_engine._interpret_ascendant(
            ascendant_data,
            'vedic'
        )
        
        assert isinstance(result, dict)
        assert 'physical_appearance' in result
        assert 'personality_traits' in result
        assert 'life_approach' in result
    
    def test_calculate_aspects(self, interpretation_engine, vedic_chart_data):
        """Test calculating aspects between planets."""
        result = interpretation_engine._calculate_aspects(
            vedic_chart_data['planets']
        )
        
        assert isinstance(result, list)
        # Each aspect should have structure
        for aspect in result:
            assert 'planet1' in aspect
            assert 'planet2' in aspect
            assert 'type' in aspect
            assert 'orb' in aspect
    
    def test_interpret_aspects(self, interpretation_engine):
        """Test interpreting aspects."""
        aspects = [
            {
                'planet1': 'Sun',
                'planet2': 'Moon',
                'type': 'trine',
                'orb': 2.5
            }
        ]
        
        result = interpretation_engine._interpret_aspects(aspects)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], dict)
        assert 'description' in result[0]
    
    def test_synthesize_interpretation(self, interpretation_engine):
        """Test synthesizing multiple interpretations."""
        interpretations = [
            {'type': 'planet_sign', 'text': 'Sun in Leo shows leadership'},
            {'type': 'planet_house', 'text': 'Sun in 5th house indicates creativity'}
        ]
        
        result = interpretation_engine._synthesize_interpretation(interpretations)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_apply_vedic_principles(self, interpretation_engine, vedic_chart_data):
        """Test applying Vedic-specific principles."""
        interpretation = {
            'general': 'Basic interpretation'
        }
        
        result = interpretation_engine._apply_vedic_principles(
            interpretation,
            vedic_chart_data
        )
        
        assert isinstance(result, dict)
        # Should add Vedic-specific elements
        assert 'nakshatras' in result or 'dashas' in result or 'yogas' in result
    
    def test_apply_western_principles(self, interpretation_engine, western_chart_data):
        """Test applying Western-specific principles."""
        interpretation = {
            'general': 'Basic interpretation'
        }
        
        result = interpretation_engine._apply_western_principles(
            interpretation,
            western_chart_data
        )
        
        assert isinstance(result, dict)
        # Should add Western-specific elements
    
    def test_empty_chart_data(self, interpretation_engine):
        """Test handling empty chart data."""
        empty_chart = {
            'planets': {},
            'houses': []
        }
        
        result = interpretation_engine.generate_interpretations(
            empty_chart,
            'vedic'
        )
        
        assert isinstance(result, dict)
        # Should handle gracefully
    
    def test_missing_planet_data(self, interpretation_engine):
        """Test handling missing planet data."""
        partial_chart = {
            'planets': {
                'Sun': {'sign': 'Leo'}  # Missing house, nakshatra etc
            }
        }
        
        result = interpretation_engine.generate_interpretations(
            partial_chart,
            'vedic'
        )
        
        assert isinstance(result, dict)
        # Should handle missing data gracefully
    
    def test_format_interpretation_text(self, interpretation_engine):
        """Test formatting interpretation text."""
        raw_text = "This is a test interpretation with multiple sentences. It should be formatted nicely."
        
        result = interpretation_engine._format_interpretation_text(raw_text)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_get_element_compatibility(self, interpretation_engine):
        """Test element compatibility analysis."""
        result = interpretation_engine._get_element_compatibility('Fire', 'Water')
        
        assert isinstance(result, dict)
        assert 'compatibility' in result
        assert 'description' in result
    
    def test_load_planet_meanings(self, interpretation_engine):
        """Test loading planet meanings."""
        # Test the actual loader (not mocked)
        engine = InterpretationEngine()
        
        assert isinstance(engine.planet_meanings, dict)
        assert 'Sun' in engine.planet_meanings
        assert 'Moon' in engine.planet_meanings
        assert 'Mars' in engine.planet_meanings
    
    def test_load_sign_meanings(self, interpretation_engine):
        """Test loading sign meanings."""
        engine = InterpretationEngine()
        
        assert isinstance(engine.sign_meanings, dict)
        assert len(engine.sign_meanings) == 12
        assert 'Aries' in engine.sign_meanings
        assert 'Pisces' in engine.sign_meanings
    
    def test_load_house_meanings(self, interpretation_engine):
        """Test loading house meanings."""
        engine = InterpretationEngine()
        
        assert isinstance(engine.house_meanings, dict)
        assert len(engine.house_meanings) == 12
        assert 1 in engine.house_meanings
        assert 12 in engine.house_meanings
    
    def test_load_aspect_meanings(self, interpretation_engine):
        """Test loading aspect meanings."""
        engine = InterpretationEngine()
        
        assert isinstance(engine.aspect_meanings, dict)
        assert 'conjunction' in engine.aspect_meanings
        assert 'opposition' in engine.aspect_meanings
        assert 'trine' in engine.aspect_meanings