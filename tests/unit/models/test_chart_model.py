"""Unit tests for Chart models."""
import pytest
from datetime import datetime
from uuid import uuid4
from decimal import Decimal
from pydantic import ValidationError

from josi.models.chart_model import (
    AstrologyChart, ChartBase, ChartEntity,
    PlanetPosition, PlanetPositionBase, PlanetPositionEntity,
    ChartInterpretation, ChartInterpretationBase, ChartInterpretationEntity,
    AstrologySystem, HouseSystem, Ayanamsa
)


class TestAstrologyChartModel:
    """Test AstrologyChart model functionality."""
    
    def test_chart_entity_validation(self):
        """Test ChartEntity field validation."""
        valid_data = {
            "chart_type": "vedic",
            "house_system": "placidus",
            "ayanamsa": "lahiri",
            "calculated_at": datetime.now(),
            "calculation_version": "1.0"
        }
        
        chart_entity = ChartEntity(**valid_data)
        assert chart_entity.chart_type == "vedic"
        assert chart_entity.house_system == "placidus"
        assert chart_entity.ayanamsa == "lahiri"
    
    def test_chart_entity_default_values(self):
        """Test default values for optional fields."""
        chart_entity = ChartEntity(
            chart_type="vedic",
            calculated_at=datetime.now(),
            calculation_version="1.0"
        )
        
        assert chart_entity.house_system == "placidus"
        assert chart_entity.ayanamsa is None
        assert chart_entity.chart_data == {}
    
    def test_astrology_chart_model_creation(self):
        """Test AstrologyChart model instance creation."""
        chart = AstrologyChart(
            chart_id=uuid4(),
            organization_id=uuid4(),
            person_id=uuid4(),
            chart_type="natal",
            calculated_at=datetime.now(),
            calculation_version="1.0",
            chart_data={"houses": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
        )
        
        assert chart.chart_type == "natal"
        assert "houses" in chart.chart_data
        assert len(chart.chart_data["houses"]) == 12
    
    def test_astrology_chart_table_name(self):
        """Test that AstrologyChart has correct table name."""
        assert AstrologyChart.__tablename__ == "astrology_chart"


class TestPlanetPositionModel:
    """Test PlanetPosition model functionality."""
    
    def test_planet_position_entity_validation(self):
        """Test PlanetPositionEntity field validation."""
        valid_data = {
            "planet_name": "Sun",
            "longitude": 120.5,
            "latitude": 0.0,
            "distance": 1.0,
            "speed": 0.98,
            "sign": "Leo",
            "sign_degree": 0.5,
            "house": 5,
            "is_retrograde": False
        }
        
        position_entity = PlanetPositionEntity(**valid_data)
        assert position_entity.planet_name == "Sun"
        assert position_entity.longitude == 120.5
        assert position_entity.sign == "Leo"
        assert position_entity.house == 5
        assert position_entity.is_retrograde is False
    
    def test_planet_position_float_fields(self):
        """Test float field precision."""
        position = PlanetPositionEntity(
            planet_name="Mars",
            longitude=45.123456,
            latitude=-2.345678,
            distance=1.523679,
            speed=-0.123456,
            sign="Aries",
            sign_degree=15.123456,
            house=1
        )
        
        assert position.longitude == 45.123456
        assert position.latitude == -2.345678
        assert position.distance == 1.523679
        assert position.speed == -0.123456
    
    def test_planet_position_model_creation(self):
        """Test PlanetPosition model instance creation."""
        position = PlanetPosition(
            planet_position_id=uuid4(),
            organization_id=uuid4(),
            chart_id=uuid4(),
            planet_name="Venus",
            longitude=60.0,
            sign="Gemini",
            house=3
        )
        
        assert position.planet_name == "Venus"
        assert position.longitude == 60.0
        assert position.sign == "Gemini"
        assert position.house == 3
    
    def test_planet_position_table_name(self):
        """Test that PlanetPosition has correct table name."""
        assert PlanetPosition.__tablename__ == "planet_position"


class TestChartInterpretationModel:
    """Test ChartInterpretation model functionality."""
    
    def test_chart_interpretation_entity_validation(self):
        """Test ChartInterpretationEntity field validation."""
        valid_data = {
            "interpretation_type": "general",
            "language": "en",
            "title": "Birth Chart Analysis",
            "summary": "A comprehensive analysis of your birth chart",
            "interpreter_version": "1.0",
            "confidence_score": 0.85
        }
        
        interp_entity = ChartInterpretationEntity(**valid_data)
        assert interp_entity.interpretation_type == "general"
        assert interp_entity.language == "en"
        assert interp_entity.title == "Birth Chart Analysis"
        assert interp_entity.confidence_score == 0.85
    
    def test_chart_interpretation_confidence_score(self):
        """Test confidence_score field."""
        # Valid score
        interp = ChartInterpretationEntity(
            interpretation_type="general",
            language="en",
            title="Test",
            summary="Test summary",
            interpreter_version="1.0",
            confidence_score=0.9
        )
        assert interp.confidence_score == 0.9
        
        # Test default value
        interp2 = ChartInterpretationEntity(
            interpretation_type="general",
            language="en",
            title="Test",
            summary="Test summary",
            interpreter_version="1.0"
        )
        assert interp2.confidence_score == 0.8
    
    def test_chart_interpretation_model_creation(self):
        """Test ChartInterpretation model instance creation."""
        interpretation = ChartInterpretation(
            chart_interpretation_id=uuid4(),
            organization_id=uuid4(),
            chart_id=uuid4(),
            interpretation_type="relationship",
            language="en",
            title="Relationship Analysis",
            summary="Your relationship patterns and compatibility",
            interpreter_version="1.0",
            confidence_score=0.75
        )
        
        assert interpretation.interpretation_type == "relationship"
        assert interpretation.language == "en"
        assert interpretation.title == "Relationship Analysis"
        assert interpretation.confidence_score == 0.75
    
    def test_chart_interpretation_table_name(self):
        """Test that ChartInterpretation has correct table name."""
        assert ChartInterpretation.__tablename__ == "chart_interpretation"