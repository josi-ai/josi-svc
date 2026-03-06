"""User model with Descope authentication and subscription tiers."""
from sqlmodel import Field, SQLModel, Column, JSON
from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from josi.models.consultation_model import Consultation
    from josi.models.saved_chart_model import SavedChart
    from josi.models.quiz_response_model import QuizResponse


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels for users."""
    FREE = "free"
    EXPLORER = "explorer"
    MYSTIC = "mystic"
    MASTER = "master"


class User(SQLModel, table=True):
    """User model — identity owned by Descope, profile and authz owned by us."""

    __tablename__ = "users"

    user_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    descope_id: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = Field(default=None, index=True)

    # Profile
    full_name: str
    avatar_url: Optional[str] = Field(default=None)
    date_of_birth: Optional[datetime] = Field(default=None)
    birth_location: Optional[Dict] = Field(default=None, sa_column=Column(JSON))

    # Subscription
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE)
    subscription_end_date: Optional[datetime] = Field(default=None)
    stripe_customer_id: Optional[str] = Field(default=None, index=True)

    # Settings
    preferences: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    notification_settings: Dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Authorization (owned by us, not Descope)
    roles: List[str] = Field(default=["user"], sa_column=Column(JSON))

    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "descope_id": "U3AXkLL5ULmyFWqbfyRwVpL2WjCi",
                "subscription_tier": "free",
            }
        }

    def has_premium_features(self) -> bool:
        return self.subscription_tier != SubscriptionTier.FREE

    def is_subscription_active(self) -> bool:
        if self.subscription_tier == SubscriptionTier.FREE:
            return True
        return (
            self.subscription_end_date is not None
            and self.subscription_end_date > datetime.utcnow()
        )

    def get_tier_limits(self) -> Dict[str, int]:
        limits = {
            SubscriptionTier.FREE: {
                "charts_per_month": 3,
                "ai_interpretations_per_month": 5,
                "saved_charts": 1,
                "consultations_per_month": 0,
            },
            SubscriptionTier.EXPLORER: {
                "charts_per_month": 50,
                "ai_interpretations_per_month": 100,
                "saved_charts": 10,
                "consultations_per_month": 1,
            },
            SubscriptionTier.MYSTIC: {
                "charts_per_month": 500,
                "ai_interpretations_per_month": 500,
                "saved_charts": 100,
                "consultations_per_month": 3,
            },
            SubscriptionTier.MASTER: {
                "charts_per_month": -1,
                "ai_interpretations_per_month": -1,
                "saved_charts": -1,
                "consultations_per_month": 10,
            },
        }
        return limits.get(self.subscription_tier, limits[SubscriptionTier.FREE])


class UserCreate(SQLModel):
    """Schema for creating a user from Descope webhook data."""
    descope_id: str
    email: str
    full_name: str
    phone: Optional[str] = None


class UserUpdate(SQLModel):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    birth_location: Optional[Dict] = None
    preferences: Optional[Dict] = None
    notification_settings: Optional[Dict] = None


class UserResponse(SQLModel):
    """Schema for user response (excludes sensitive data)."""
    user_id: UUID
    email: str
    full_name: str
    phone: Optional[str]
    avatar_url: Optional[str]
    subscription_tier: SubscriptionTier
    subscription_end_date: Optional[datetime]
    roles: List[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    preferences: Dict
    notification_settings: Dict
