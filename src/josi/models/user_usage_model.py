"""Monthly usage tracking per user."""
from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4


class UserUsage(SQLModel, table=True):
    """Tracks per-user monthly usage against subscription tier limits."""
    __tablename__ = "user_usage"

    usage_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True)
    period: str = Field(index=True)  # YYYY-MM format

    charts_calculated: int = Field(default=0)
    ai_interpretations_used: int = Field(default=0)
    consultations_booked: int = Field(default=0)
    saved_charts_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "period": "2026-03",
                "charts_calculated": 5,
                "ai_interpretations_used": 12,
            }
        }


class UserUsageResponse(SQLModel):
    """Response schema with usage + tier limits."""
    period: str
    charts_calculated: int
    ai_interpretations_used: int
    consultations_booked: int
    saved_charts_count: int
    limits: dict
