"""
Base models for SQLModel entities.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import text
from sqlmodel import Field, SQLModel


class SQLBaseModel(SQLModel):
    """Base model with common fields for all entities."""
    
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "nullable": False
        }
    )
    
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": text("CURRENT_TIMESTAMP"),
            "nullable": False
        }
    )
    
    is_deleted: Optional[bool] = Field(default=False, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    


class TenantBaseModel(SQLBaseModel):
    """Base model for multi-tenant entities."""
    
    organization_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="organization.organization_id"
    )