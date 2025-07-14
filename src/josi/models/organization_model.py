"""
Organization model using SQLModel.
"""
import secrets
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy import text, JSON
from sqlmodel import Field, SQLModel
import strawberry
from strawberry.scalars import JSON as StrawberryJSON
from pydantic import field_validator

from .base import SQLBaseModel


class OrganizationEntity(SQLModel):
    """Organization entity fields."""
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False, unique=True, index=True)
    api_key: Optional[str] = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Settings
    is_active: Optional[bool] = Field(default=True, nullable=False)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_type=JSON)
    
    # Billing
    plan_type: Optional[str] = Field(default="free", nullable=False)
    monthly_api_limit: Optional[int] = Field(default=1000, nullable=False)
    current_month_usage: Optional[int] = Field(default=0, nullable=False)
    
    # Contact
    contact_email: Optional[str] = Field(default=None, nullable=True)
    contact_name: Optional[str] = Field(default=None, nullable=True)
    contact_phone: Optional[str] = Field(default=None, nullable=True)
    
    # Address
    address_line1: Optional[str] = Field(default=None, nullable=True)
    address_line2: Optional[str] = Field(default=None, nullable=True)
    city: Optional[str] = Field(default=None, nullable=True)
    state: Optional[str] = Field(default=None, nullable=True)
    country: Optional[str] = Field(default=None, nullable=True)
    postal_code: Optional[str] = Field(default=None, nullable=True)


class OrganizationBase(SQLModel):
    """Organization base with primary key."""
    organization_id: Optional[UUID] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "nullable": False
        }
    )
    
    @field_validator('organization_id', mode='before')
    @classmethod
    def validate_organization_id(cls, v):
        if v is not None and not isinstance(v, UUID):
            try:
                return UUID(str(v))
            except ValueError:
                raise ValueError('Invalid UUID format')
        return v


class OrganizationModel(SQLBaseModel, OrganizationEntity, OrganizationBase):
    """Complete organization model."""
    pass


class Organization(OrganizationModel, table=True):
    """Organization table."""
    __tablename__ = "organization"


# Strawberry GraphQL schemas
@strawberry.experimental.pydantic.type(
    model=Organization,
    fields=[
        "organization_id", "name", "slug", "api_key", "is_active", 
        "plan_type", "monthly_api_limit", "current_month_usage",
        "contact_email", "contact_name", "contact_phone",
        "address_line1", "address_line2", "city", "state", "country", "postal_code",
        "created_at", "updated_at", "is_deleted", "deleted_at"
    ]
)
class OrganizationSchema:
    def to_pydantic(self):
        """Convert the schema to a pydantic model"""
        return Organization(**self.__dict__)


@strawberry.experimental.pydantic.input(
    model=Organization,
    fields=[
        "organization_id", "name", "slug", "api_key", "is_active", 
        "plan_type", "monthly_api_limit", "current_month_usage",
        "contact_email", "contact_name", "contact_phone",
        "address_line1", "address_line2", "city", "state", "country", "postal_code",
        "created_at", "updated_at", "is_deleted", "deleted_at"
    ]
)
class OrganizationInput:
    def to_pydantic(self):
        """Convert the input to a pydantic model"""
        return Organization(**self.__dict__)


@strawberry.experimental.pydantic.input(
    model=OrganizationEntity,
    fields=[
        "name", "slug", "api_key", "is_active", 
        "plan_type", "monthly_api_limit", "current_month_usage",
        "contact_email", "contact_name", "contact_phone",
        "address_line1", "address_line2", "city", "state", "country", "postal_code"
    ]
)
class OrganizationCreateInput:
    def to_pydantic(self):
        """Convert the input to a pydantic model"""
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        return OrganizationEntity(**data)


@strawberry.experimental.pydantic.input(
    model=OrganizationEntity,
    fields=[
        "name", "slug", "api_key", "is_active", 
        "plan_type", "monthly_api_limit", "current_month_usage",
        "contact_email", "contact_name", "contact_phone",
        "address_line1", "address_line2", "city", "state", "country", "postal_code"
    ]
)
class OrganizationUpdateInput:
    def to_pydantic(self):
        """Convert the input to a pydantic model"""
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        return OrganizationEntity(**data)