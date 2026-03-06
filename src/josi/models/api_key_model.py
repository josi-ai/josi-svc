"""API Key model for B2B programmatic access."""
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class ApiKey(SQLModel, table=True):
    """API key for programmatic access. Keys are stored hashed."""

    __tablename__ = "api_keys"

    api_key_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.user_id", index=True)
    key_hash: str = Field(index=True)
    key_prefix: str = Field(max_length=12)
    name: str = Field(max_length=255)
    last_used_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApiKeyCreate(SQLModel):
    """Schema for creating an API key."""
    name: str


class ApiKeyResponse(SQLModel):
    """Schema for API key response (never includes the full key)."""
    api_key_id: UUID
    key_prefix: str
    name: str
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime


class ApiKeyCreatedResponse(SQLModel):
    """Returned only at creation time — includes the plaintext key."""
    api_key_id: UUID
    key: str  # Plaintext — shown once, never stored
    key_prefix: str
    name: str
