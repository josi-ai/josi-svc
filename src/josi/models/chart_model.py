"""
Astrology Chart models using SQLModel.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from sqlalchemy import text, JSON, ForeignKey
from sqlmodel import Field, SQLModel, Relationship
import strawberry
from pydantic import field_validator

from .base import TenantBaseModel


class AstrologySystem(str, Enum):
    """Supported astrology systems."""
    VEDIC = "vedic"
    WESTERN = "western"
    CHINESE = "chinese"
    HELLENISTIC = "hellenistic"
    MAYAN = "mayan"
    CELTIC = "celtic"
    SIDEREAL = "sidereal"
    TROPICAL = "tropical"


class HouseSystem(str, Enum):
    """Supported house systems."""
    PLACIDUS = "placidus"
    KOCH = "koch"
    EQUAL = "equal"
    WHOLE_SIGN = "whole_sign"
    REGIOMONTANUS = "regiomontanus"
    CAMPANUS = "campanus"
    PORPHYRY = "porphyry"
    ALCABITIUS = "alcabitius"


class Ayanamsa(str, Enum):
    """Supported ayanamsa systems."""
    LAHIRI = "lahiri"
    KRISHNAMURTI = "krishnamurti"
    RAMAN = "raman"
    FAGAN_BRADLEY = "fagan_bradley"
    TRUE_CHITRAPAKSHA = "true_chitrapaksha"


class ChartEntity(SQLModel):
    """Chart entity fields."""
    # Chart Information
    chart_type: str = Field(nullable=False, index=True)  # vedic, western, chinese, etc.
    house_system: Optional[str] = Field(default="placidus", nullable=True)
    ayanamsa: Optional[str] = Field(default=None, nullable=True)
    
    # Calculation Details
    calculated_at: datetime = Field(nullable=False)
    calculation_version: str = Field(nullable=False)
    
    # Chart Data
    chart_data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    planet_positions: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    house_cusps: List[float] = Field(default_factory=list, sa_type=JSON)
    aspects: List[Dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    
    # Additional Data
    divisional_chart_type: Optional[int] = Field(default=None, nullable=True)  # For divisional charts
    progression_type: Optional[str] = Field(default=None, nullable=True)  # For progressed charts


class ChartBase(SQLModel):
    """Chart base with primary key and foreign key."""
    chart_id: Optional[UUID] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "nullable": False
        }
    )
    
    # Foreign key to Person
    person_id: UUID = Field(
        foreign_key="person.person_id",
        nullable=False,
        index=True
    )
    
    @field_validator('chart_id', mode='before')
    @classmethod
    def validate_chart_id(cls, v):
        if v is not None and not isinstance(v, UUID):
            try:
                return UUID(str(v))
            except ValueError:
                raise ValueError('Invalid UUID format')
        return v


class ChartModel(TenantBaseModel, ChartEntity, ChartBase):
    """Complete chart model."""
    pass


class AstrologyChart(ChartModel, table=True):
    """Astrology Chart table."""
    __tablename__ = "astrology_chart"
    
    # Relationships
    person: Optional["Person"] = Relationship(back_populates="charts")
    interpretations: List["ChartInterpretation"] = Relationship(back_populates="chart")
    planet_positions_list: List["PlanetPosition"] = Relationship(back_populates="chart")


# Planet Position Model
class PlanetPositionEntity(SQLModel):
    """Planet position entity fields."""
    planet_name: str = Field(nullable=False)
    longitude: float = Field(nullable=False)
    latitude: float = Field(nullable=False)
    distance: Optional[float] = Field(default=None, nullable=True)
    speed: float = Field(nullable=False)
    
    # Sign and House
    sign: str = Field(nullable=False)
    sign_degree: float = Field(nullable=False)
    house: int = Field(nullable=False)
    house_degree: Optional[float] = Field(default=None, nullable=True)
    
    # Vedic specific
    nakshatra: Optional[str] = Field(default=None, nullable=True)
    nakshatra_pada: Optional[int] = Field(default=None, nullable=True)
    
    # Dignities
    dignity: Optional[str] = Field(default=None, nullable=True)
    is_retrograde: bool = Field(default=False, nullable=False)
    is_combust: bool = Field(default=False, nullable=False)


class PlanetPositionBase(SQLModel):
    """Planet position base with primary key."""
    planet_position_id: Optional[UUID] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "nullable": False
        }
    )
    
    # Foreign key to Chart
    chart_id: UUID = Field(
        foreign_key="astrology_chart.chart_id",
        nullable=False,
        index=True
    )


class PlanetPositionModel(TenantBaseModel, PlanetPositionEntity, PlanetPositionBase):
    """Complete planet position model."""
    pass


class PlanetPosition(PlanetPositionModel, table=True):
    """Planet Position table."""
    __tablename__ = "planet_position"
    
    # Relationships
    chart: Optional["AstrologyChart"] = Relationship(back_populates="planet_positions_list")


# Chart Interpretation Model
class ChartInterpretationEntity(SQLModel):
    """Chart interpretation entity fields."""
    interpretation_type: str = Field(nullable=False)  # general, career, relationships, etc.
    language: str = Field(default="en", nullable=False)
    
    # Content
    title: str = Field(nullable=False)
    summary: str = Field(nullable=False)
    detailed_text: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    
    # Metadata
    interpreter_version: str = Field(nullable=False)
    confidence_score: float = Field(default=0.8, nullable=False)
    keywords: List[str] = Field(default_factory=list, sa_type=JSON)


class ChartInterpretationBase(SQLModel):
    """Chart interpretation base with primary key."""
    chart_interpretation_id: Optional[UUID] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "nullable": False
        }
    )
    
    # Foreign key to Chart
    chart_id: UUID = Field(
        foreign_key="astrology_chart.chart_id",
        nullable=False,
        index=True
    )


class ChartInterpretationModel(TenantBaseModel, ChartInterpretationEntity, ChartInterpretationBase):
    """Complete chart interpretation model."""
    pass


class ChartInterpretation(ChartInterpretationModel, table=True):
    """Chart Interpretation table."""
    __tablename__ = "chart_interpretation"
    
    # Relationships
    chart: Optional["AstrologyChart"] = Relationship(back_populates="interpretations")


# Add back reference to Person model
from .person_model import Person
Person.model_rebuild()
Person.__annotations__["charts"] = List["AstrologyChart"]


# Strawberry GraphQL schemas for Chart
@strawberry.experimental.pydantic.type(
    model=AstrologyChart,
    fields=[
        "chart_id", "organization_id", "person_id", "chart_type",
        "house_system", "ayanamsa", "calculated_at", "calculation_version",
        "divisional_chart_type", "progression_type",
        "created_at", "updated_at", "is_deleted", "deleted_at"
    ]
)
class ChartSchema:
    def to_pydantic(self):
        """Convert the schema to a pydantic model"""
        return AstrologyChart(**self.__dict__)


@strawberry.experimental.pydantic.input(
    model=ChartEntity,
    fields=[
        "chart_type", "house_system", "ayanamsa",
        "calculated_at", "calculation_version",
        "divisional_chart_type", "progression_type"
    ]
)
class ChartCreateInput:
    person_id: UUID
    
    def to_pydantic(self):
        """Convert the input to a pydantic model"""
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        return ChartEntity(**data)


# Strawberry GraphQL schemas for PlanetPosition
@strawberry.experimental.pydantic.type(
    model=PlanetPosition,
    fields=[
        "planet_position_id", "organization_id", "chart_id",
        "planet_name", "longitude", "latitude", "distance", "speed",
        "sign", "sign_degree", "house", "house_degree",
        "nakshatra", "nakshatra_pada", "dignity",
        "is_retrograde", "is_combust",
        "created_at", "updated_at", "is_deleted", "deleted_at"
    ]
)
class PlanetPositionSchema:
    def to_pydantic(self):
        """Convert the schema to a pydantic model"""
        return PlanetPosition(**self.__dict__)


# Strawberry GraphQL schemas for ChartInterpretation
@strawberry.experimental.pydantic.type(
    model=ChartInterpretation,
    fields=[
        "chart_interpretation_id", "organization_id", "chart_id",
        "interpretation_type", "language", "title", "summary",
        "interpreter_version", "confidence_score",
        "created_at", "updated_at", "is_deleted", "deleted_at"
    ]
)
class ChartInterpretationSchema:
    def to_pydantic(self):
        """Convert the schema to a pydantic model"""
        return ChartInterpretation(**self.__dict__)


@strawberry.experimental.pydantic.input(
    model=ChartInterpretationEntity,
    fields=[
        "interpretation_type", "language", "title", "summary",
        "interpreter_version", "confidence_score"
    ]
)
class ChartInterpretationCreateInput:
    chart_id: UUID
    
    def to_pydantic(self):
        """Convert the input to a pydantic model"""
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        return ChartInterpretationEntity(**data)