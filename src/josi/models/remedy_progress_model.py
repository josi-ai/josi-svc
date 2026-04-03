"""
Remedy Progress Tracking model — tracks which remedies a user has started/completed.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Field, SQLModel

from josi.models.base import TenantBaseModel


class RemedyProgress(TenantBaseModel, table=True):
    """Track a user's progress with individual remedies (mantra, gemstone, etc.)."""

    __tablename__ = "remedy_progress"

    remedy_progress_id: UUID = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    person_id: UUID = Field(foreign_key="person.person_id", index=True)
    remedy_type: str  # "mantra", "gemstone", "donation", "ritual", "temple_visit", etc.
    remedy_name: str  # Name/description of the specific remedy
    status: str = Field(default="not_started")  # "not_started", "in_progress", "completed", "skipped"
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class RemedyProgressCreate(SQLModel):
    """Schema for creating or updating remedy progress."""
    person_id: UUID
    remedy_type: str
    remedy_name: str
    status: str = "not_started"
    notes: Optional[str] = None


class RemedyProgressResponse(SQLModel):
    """Schema for remedy progress response."""
    remedy_progress_id: UUID
    person_id: UUID
    remedy_type: str
    remedy_name: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
