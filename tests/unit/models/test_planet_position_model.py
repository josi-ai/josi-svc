"""
Unit tests for PlanetPosition model.
"""
import pytest
from datetime import datetime
from uuid import uuid4

from josi.models.chart_model import (
    PlanetPosition,
    PlanetPositionEntity
)


class TestPlanetPositionModel:
    """Test PlanetPosition model validation and behavior."""
    
    def test_planet_position_creation_basic(self):
        """Test creating planet position with required fields."""
        position = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Sun",
            longitude=45.5,
            latitude=0.0,
            speed=0.98,
            sign="Taurus",
            sign_degree=15.5,
            house=2,
            is_retrograde=False,
            is_combust=False,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert position.planet_name == "Sun"
        assert position.longitude == 45.5
        assert position.sign == "Taurus"
        assert position.sign_degree == 15.5
        assert position.house == 2
    
    def test_planet_position_with_vedic_fields(self):
        """Test planet position with Vedic-specific fields."""
        position = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Moon",
            longitude=120.75,
            latitude=-2.5,
            distance=0.0025,  # AU
            speed=13.5,
            sign="Leo",
            sign_degree=0.75,
            house=5,
            house_degree=5.25,
            nakshatra="Magha",
            nakshatra_pada=1,
            dignity="neutral",
            is_retrograde=False,
            is_combust=False,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert position.nakshatra == "Magha"
        assert position.nakshatra_pada == 1
        assert position.dignity == "neutral"
        assert position.distance == 0.0025
    
    def test_retrograde_planet(self):
        """Test retrograde planet position."""
        position = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Mercury",
            longitude=234.5,
            latitude=1.2,
            speed=-0.5,  # Negative speed indicates retrograde
            sign="Scorpio",
            sign_degree=24.5,
            house=8,
            is_retrograde=True,
            is_combust=False,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert position.is_retrograde is True
        assert position.speed < 0
    
    def test_combust_planet(self):
        """Test combust planet position."""
        position = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Venus",
            longitude=92.0,  # Close to Sun
            latitude=0.5,
            speed=1.2,
            sign="Cancer",
            sign_degree=2.0,
            house=4,
            is_retrograde=False,
            is_combust=True,  # Within combustion range of Sun
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert position.is_combust is True
    
    def test_planet_dignities(self):
        """Test different planetary dignities."""
        dignities = ["exalted", "own", "friendly", "neutral", "enemy", "debilitated"]
        
        for dignity in dignities:
            position = PlanetPosition(
                planet_position_id=uuid4(),
                chart_id=uuid4(),
                organization_id=uuid4(),
                planet_name="Jupiter",
                longitude=90.0,
                latitude=0.0,
                speed=0.08,
                sign="Cancer",
                sign_degree=0.0,
                house=4,
                dignity=dignity,
                is_retrograde=False,
                is_combust=False,
                is_deleted=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            assert position.dignity == dignity
    
    def test_outer_planets(self):
        """Test outer planets with larger distances."""
        position = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Neptune",
            longitude=350.25,
            latitude=-1.5,
            distance=30.05,  # Neptune ~30 AU from Sun
            speed=0.006,
            sign="Pisces",
            sign_degree=20.25,
            house=12,
            is_retrograde=False,
            is_combust=False,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert position.distance == 30.05
        assert position.planet_name == "Neptune"
        assert position.sign == "Pisces"
    
    def test_lunar_nodes(self):
        """Test lunar nodes (Rahu/Ketu or North/South Node)."""
        # North Node (Rahu)
        north_node = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Rahu",
            longitude=150.0,
            latitude=0.0,  # Nodes are on ecliptic
            speed=-0.053,  # Always retrograde
            sign="Virgo",
            sign_degree=0.0,
            house=6,
            nakshatra="Hasta",
            nakshatra_pada=3,
            is_retrograde=True,
            is_combust=False,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert north_node.planet_name == "Rahu"
        assert north_node.is_retrograde is True
        assert north_node.latitude == 0.0
    
    def test_ascendant_position(self):
        """Test Ascendant as a planet position."""
        position = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Ascendant",
            longitude=180.0,
            latitude=0.0,  # Always on ecliptic
            speed=0.0,  # Fixed point
            sign="Libra",
            sign_degree=0.0,
            house=1,  # Always in first house
            house_degree=0.0,
            is_retrograde=False,
            is_combust=False,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert position.planet_name == "Ascendant"
        assert position.house == 1
        assert position.speed == 0.0
    
    def test_planet_position_edge_cases(self):
        """Test edge cases for planetary positions."""
        # Planet at 0 degrees
        position1 = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Mars",
            longitude=0.0,
            latitude=0.0,
            speed=0.5,
            sign="Aries",
            sign_degree=0.0,
            house=1,
            is_retrograde=False,
            is_combust=False,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert position1.longitude == 0.0
        assert position1.sign == "Aries"
        
        # Planet at 359.99 degrees
        position2 = PlanetPosition(
            planet_position_id=uuid4(),
            chart_id=uuid4(),
            organization_id=uuid4(),
            planet_name="Saturn",
            longitude=359.99,
            latitude=2.1,
            speed=0.03,
            sign="Pisces",
            sign_degree=29.99,
            house=12,
            is_retrograde=False,
            is_combust=False,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert position2.longitude == 359.99
        assert position2.sign == "Pisces"
        assert position2.sign_degree == 29.99
    
    def test_planet_position_entity(self):
        """Test PlanetPositionEntity base fields."""
        entity = PlanetPositionEntity(
            planet_name="Jupiter",
            longitude=270.5,
            latitude=1.2,
            speed=0.08,
            sign="Capricorn",
            sign_degree=0.5,
            house=10
        )
        
        assert entity.planet_name == "Jupiter"
        assert entity.longitude == 270.5
        assert entity.nakshatra is None  # Optional field
        assert entity.is_retrograde is False  # Default value