"""
Person model using SQLModel.
"""
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from decimal import Decimal
from sqlalchemy import text
from sqlmodel import Field, SQLModel, Relationship
import strawberry
from pydantic import field_validator

from .base import TenantBaseModel

if TYPE_CHECKING:
    from .chart_model import AstrologyChart


class PersonEntity(SQLModel):
    """Person entity fields."""
    # Basic Information
    name: str = Field(nullable=False)
    email: Optional[str] = Field(default=None, nullable=True, index=True)
    phone: Optional[str] = Field(default=None, nullable=True)
    
    # Birth Information
    date_of_birth: Optional[date] = Field(default=None, nullable=True)
    time_of_birth: Optional[datetime] = Field(default=None, nullable=True)
    place_of_birth: Optional[str] = Field(default=None, nullable=True)

    # Location coordinates
    latitude: Optional[Decimal] = Field(default=None, nullable=True, decimal_places=6, max_digits=9)
    longitude: Optional[Decimal] = Field(default=None, nullable=True, decimal_places=6, max_digits=9)
    timezone: Optional[str] = Field(default=None, nullable=True)

    # Profile flags
    is_default: Optional[bool] = Field(default=False, nullable=False)
    
    # Additional Information
    gender: Optional[str] = Field(default=None, nullable=True)
    birth_certificate_id: Optional[str] = Field(default=None, nullable=True)
    notes: Optional[str] = Field(default=None, nullable=True)
    
    # External IDs
    external_id: Optional[str] = Field(default=None, nullable=True, index=True)
    source_system: Optional[str] = Field(default=None, nullable=True)
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if v is not None:
            lat_val = float(v)
            if not -90 <= lat_val <= 90:
                raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if v is not None:
            lon_val = float(v)
            if not -180 <= lon_val <= 180:
                raise ValueError('Longitude must be between -180 and 180')
        return v


class PersonBase(SQLModel):
    """Person base with primary key."""
    person_id: Optional[UUID] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "nullable": False
        }
    )
    
    @field_validator('person_id', mode='before')
    @classmethod
    def validate_person_id(cls, v):
        if v is not None and not isinstance(v, UUID):
            try:
                return UUID(str(v))
            except ValueError:
                raise ValueError('Invalid UUID format')
        return v


class PersonModel(TenantBaseModel, PersonEntity, PersonBase):
    """Complete person model."""
    pass


class Person(PersonModel, table=True):
    """Person table."""
    __tablename__ = "person"
    
    # Relationships
    charts: List["AstrologyChart"] = Relationship(back_populates="person")


# Strawberry GraphQL schemas
@strawberry.experimental.pydantic.type(
    model=Person,
    fields=[
        "person_id", "organization_id", "user_id", "name", "email", "phone",
        "date_of_birth", "time_of_birth", "place_of_birth",
        "latitude", "longitude", "timezone",
        "gender", "birth_certificate_id", "notes",
        "external_id", "source_system", "is_default",
        "created_at", "updated_at", "is_deleted", "deleted_at"
    ]
)
class PersonSchema:
    def to_pydantic(self):
        """Convert the schema to a pydantic model"""
        return Person(**self.__dict__)


@strawberry.experimental.pydantic.input(model=Person, all_fields=True)
class PersonInput:
    def to_pydantic(self):
        """Convert the input to a pydantic model"""
        return Person(**self.__dict__)


@strawberry.experimental.pydantic.input(model=PersonEntity, all_fields=True)
class PersonCreateInput:
    def to_pydantic(self):
        """Convert the input to a pydantic model"""
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        return PersonEntity(**data)


@strawberry.experimental.pydantic.input(model=PersonEntity, all_fields=True)
class PersonUpdateInput:
    def to_pydantic(self):
        """Convert the input to a pydantic model"""
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        return PersonEntity(**data)