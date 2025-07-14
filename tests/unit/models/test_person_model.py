"""Unit tests for Person model."""
import pytest
from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError

from josi.models.person_model import Person, PersonBase, PersonEntity


class TestPersonModel:
    """Test Person model functionality."""
    
    def test_person_entity_validation(self):
        """Test PersonEntity field validation."""
        # Valid person data
        valid_data = {
            "name": "John Doe",
            "date_of_birth": date(1990, 1, 1),
            "time_of_birth": datetime(1990, 1, 1, 12, 0, 0),
            "place_of_birth": "New York, NY, USA",
            "latitude": Decimal("40.7128"),
            "longitude": Decimal("-74.0060"),
            "timezone": "America/New_York"
        }
        
        person_entity = PersonEntity(**valid_data)
        assert person_entity.name == "John Doe"
        assert person_entity.date_of_birth == date(1990, 1, 1)
        assert person_entity.time_of_birth == datetime(1990, 1, 1, 12, 0, 0)
        assert person_entity.latitude == Decimal("40.7128")
        assert person_entity.longitude == Decimal("-74.0060")
    
    def test_person_entity_optional_fields(self):
        """Test PersonEntity with optional fields."""
        minimal_data = {
            "name": "Jane Doe",
            "date_of_birth": date(1995, 5, 15),
            "time_of_birth": datetime(1995, 5, 15, 9, 0, 0),
            "place_of_birth": "Los Angeles, CA, USA",
            "latitude": Decimal("34.0522"),
            "longitude": Decimal("-118.2437"),
            "timezone": "America/Los_Angeles"
        }
        
        person_entity = PersonEntity(**minimal_data)
        assert person_entity.name == "Jane Doe"
        assert person_entity.email is None
        assert person_entity.phone is None
        assert person_entity.gender is None
        assert person_entity.notes is None
    
    def test_person_entity_with_email(self):
        """Test PersonEntity with email field."""
        data = {
            "name": "Test User",
            "date_of_birth": date(2000, 1, 1),
            "time_of_birth": datetime(2000, 1, 1, 0, 0, 0),
            "place_of_birth": "Test City",
            "latitude": Decimal("0.0"),
            "longitude": Decimal("0.0"),
            "timezone": "UTC",
            "email": "test@example.com",
            "phone": "+1234567890"
        }
        
        person_entity = PersonEntity(**data)
        assert person_entity.email == "test@example.com"
        assert person_entity.phone == "+1234567890"
    
    def test_person_latitude_validation(self):
        """Test latitude validation (must be between -90 and 90)."""
        # Valid latitude
        data = {
            "name": "Test User",
            "date_of_birth": date(2000, 1, 1),
            "time_of_birth": datetime(2000, 1, 1, 0, 0, 0),
            "place_of_birth": "Test City",
            "latitude": Decimal("45.0"),
            "longitude": Decimal("0.0"),
            "timezone": "UTC"
        }
        person_entity = PersonEntity(**data)
        assert person_entity.latitude == Decimal("45.0")
        
        # Invalid latitude
        data["latitude"] = Decimal("91.0")
        with pytest.raises(ValidationError):
            PersonEntity(**data)
        
        data["latitude"] = Decimal("-91.0")
        with pytest.raises(ValidationError):
            PersonEntity(**data)
    
    def test_person_longitude_validation(self):
        """Test longitude validation (must be between -180 and 180)."""
        # Valid longitude
        data = {
            "name": "Test User",
            "date_of_birth": date(2000, 1, 1),
            "time_of_birth": datetime(2000, 1, 1, 0, 0, 0),
            "place_of_birth": "Test City",
            "latitude": Decimal("0.0"),
            "longitude": Decimal("120.0"),
            "timezone": "UTC"
        }
        person_entity = PersonEntity(**data)
        assert person_entity.longitude == Decimal("120.0")
        
        # Invalid longitude
        data["longitude"] = Decimal("181.0")
        with pytest.raises(ValidationError):
            PersonEntity(**data)
        
        data["longitude"] = Decimal("-181.0")
        with pytest.raises(ValidationError):
            PersonEntity(**data)
    
    def test_person_model_creation(self):
        """Test Person model instance creation."""
        person = Person(
            person_id=uuid4(),
            organization_id=uuid4(),
            name="Test Person",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            latitude=Decimal("40.7128"),
            longitude=Decimal("-74.0060"),
            timezone="America/New_York"
        )
        
        assert person.name == "Test Person"
        assert person.date_of_birth == date(1990, 1, 1)
        assert isinstance(person.person_id, type(uuid4()))
        assert isinstance(person.organization_id, type(uuid4()))
    
    def test_person_table_name(self):
        """Test that Person has correct table name."""
        assert Person.__tablename__ == "person"
    
    def test_person_base_with_uuid(self):
        """Test PersonBase UUID field handling."""
        person_id = uuid4()
        person_base = PersonBase(person_id=person_id)
        assert person_base.person_id == person_id
        
        # Test string UUID conversion
        person_base2 = PersonBase(person_id=str(person_id))
        assert person_base2.person_id == person_id
        
        # Test invalid UUID
        with pytest.raises(ValidationError):
            PersonBase(person_id="invalid-uuid")