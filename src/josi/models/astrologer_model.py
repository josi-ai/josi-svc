"""
Astrologer model for marketplace functionality.
"""
from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

from josi.enums.verification_status_enum import VerificationStatusEnum

if TYPE_CHECKING:
    from josi.models.user_model import User
    from josi.models.consultation_model import Consultation


class Astrologer(SQLModel, table=True):
    """Astrologer model for marketplace."""
    
    __tablename__ = "astrologers"
    
    astrologer_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.user_id", unique=True, index=True)
    
    # Professional Information
    professional_name: str
    bio: str
    years_experience: int
    certifications: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))
    specializations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    languages: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Availability and Services
    timezone: str
    availability_schedule: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    consultation_types: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Pricing
    hourly_rate: float
    currency: str = Field(default="USD")
    accepts_sliding_scale: bool = Field(default=False)
    minimum_session_duration: int = Field(default=30)  # minutes
    
    # Performance Metrics
    rating: float = Field(default=0.0)
    total_consultations: int = Field(default=0)
    total_reviews: int = Field(default=0)
    response_time_hours: float = Field(default=24.0)
    completion_rate: float = Field(default=100.0)
    
    # Profile Media
    profile_image_url: Optional[str] = Field(default=None)
    sample_reading_url: Optional[str] = Field(default=None)
    portfolio_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Verification and Status
    verification_status_id: Optional[int] = Field(default=1)
    verification_status_name: Optional[str] = Field(default="Pending")
    verification_date: Optional[datetime] = Field(default=None)
    verification_notes: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    
    # Business Information
    business_name: Optional[str] = Field(default=None)
    business_registration: Optional[str] = Field(default=None)
    tax_id: Optional[str] = Field(default=None)
    
    # Communication Preferences
    preferred_communication_style: Optional[str] = Field(default=None)
    consultation_preparation_notes: Optional[str] = Field(default=None)
    
    # Timestamps
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    
    class Config:
        """SQLModel config."""
        json_schema_extra = {
            "example": {
                "professional_name": "Dr. Sarah Johnson",
                "bio": "Experienced Vedic astrologer with 15+ years of practice",
                "years_experience": 15,
                "specializations": ["vedic", "relationship", "career"],
                "languages": ["en", "hi"],
                "hourly_rate": 120.0,
                "timezone": "America/New_York"
            }
        }
    
    def calculate_average_rating(self, reviews: List[Dict]) -> float:
        """Calculate average rating from reviews."""
        if not reviews:
            return 0.0
        total_rating = sum(review.get("rating", 0) for review in reviews)
        return round(total_rating / len(reviews), 2)
    
    def is_available_now(self) -> bool:
        """Check if astrologer is currently available."""
        if not self.is_active or self.verification_status_id != VerificationStatusEnum.VERIFIED.id:
            return False
        
        # TODO: Implement actual availability checking based on schedule
        return True
    
    def get_specialization_display(self) -> List[str]:
        """Get formatted specialization names."""
        spec_map = {
            "vedic": "Vedic Astrology",
            "western": "Western Astrology",
            "chinese": "Chinese Astrology",
            "medical": "Medical Astrology",
            "karmic": "Karmic Astrology",
            "relationship": "Relationship Counseling",
            "career": "Career Guidance",
            "spiritual": "Spiritual Guidance",
            "predictive": "Predictive Astrology"
        }
        return [spec_map.get(spec, spec.title()) for spec in self.specializations]


class AstrologerReview(SQLModel, table=True):
    """Reviews and ratings for astrologers."""
    
    __tablename__ = "astrologer_reviews"
    
    review_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    astrologer_id: UUID = Field(foreign_key="astrologers.astrologer_id", index=True)
    user_id: UUID = Field(foreign_key="users.user_id", index=True)
    consultation_id: UUID = Field(foreign_key="consultations.consultation_id", unique=True)
    
    # Review Content
    rating: int = Field(ge=1, le=5)  # 1-5 stars
    title: Optional[str] = Field(default=None)
    review_text: Optional[str] = Field(default=None)
    
    # Review Categories
    accuracy_rating: Optional[int] = Field(default=None, ge=1, le=5)
    communication_rating: Optional[int] = Field(default=None, ge=1, le=5)
    empathy_rating: Optional[int] = Field(default=None, ge=1, le=5)
    
    # Metadata
    is_verified: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    helpful_votes: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


# Request/Response Models
class AstrologerCreate(SQLModel):
    """Schema for creating astrologer profile."""
    professional_name: str
    bio: str
    years_experience: int
    specializations: List[str]
    languages: List[str]
    timezone: str
    hourly_rate: float
    consultation_types: List[str]
    certifications: List[Dict] = []
    accepts_sliding_scale: bool = False


class AstrologerUpdate(SQLModel):
    """Schema for updating astrologer profile."""
    professional_name: Optional[str] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    specializations: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    timezone: Optional[str] = None
    hourly_rate: Optional[float] = None
    consultation_types: Optional[List[str]] = None
    availability_schedule: Optional[Dict] = None
    accepts_sliding_scale: Optional[bool] = None


class AstrologerResponse(SQLModel):
    """Schema for astrologer response."""
    astrologer_id: UUID
    user_id: UUID
    professional_name: str
    bio: str
    years_experience: int
    specializations: List[str]
    languages: List[str]
    hourly_rate: float
    currency: str
    rating: float
    total_consultations: int
    total_reviews: int
    verification_status_id: Optional[int]
    verification_status_name: Optional[str]
    is_active: bool
    is_featured: bool
    profile_image_url: Optional[str]
    joined_at: datetime


class ReviewCreate(SQLModel):
    """Schema for creating a review."""
    consultation_id: UUID
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    review_text: Optional[str] = None
    accuracy_rating: Optional[int] = Field(default=None, ge=1, le=5)
    communication_rating: Optional[int] = Field(default=None, ge=1, le=5)
    empathy_rating: Optional[int] = Field(default=None, ge=1, le=5)


class ReviewResponse(SQLModel):
    """Schema for review response."""
    review_id: UUID
    astrologer_id: UUID
    user_id: UUID
    rating: int
    title: Optional[str]
    review_text: Optional[str]
    accuracy_rating: Optional[int]
    communication_rating: Optional[int]
    empathy_rating: Optional[int]
    is_verified: bool
    helpful_votes: int
    created_at: datetime