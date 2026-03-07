"""
Remedy (Pariharam) model for astrological remedies and recommendations.
"""
from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

from josi.enums.remedy_type_enum import RemedyTypeEnum
from josi.enums.tradition_enum import TraditionEnum
from josi.enums.dosha_type_enum import DoshaTypeEnum

if TYPE_CHECKING:
    from josi.models.user_model import User
    from josi.models.chart_model import AstrologyChart


class Remedy(SQLModel, table=True):
    """Remedy model for storing astrological remedies."""
    
    __tablename__ = "remedies"
    
    remedy_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    
    # Basic Information
    name: str = Field(index=True)
    type_id: Optional[int] = Field(default=None)
    type_name: Optional[str] = Field(default=None)
    tradition_id: Optional[int] = Field(default=1)
    tradition_name: Optional[str] = Field(default="Vedic")

    # Associations
    planet: Optional[str] = Field(default=None, index=True)
    dosha_type_id: Optional[int] = Field(default=None, index=True)
    dosha_type_name: Optional[str] = Field(default=None)
    affliction_type: Optional[str] = Field(default=None)  # More specific afflictions
    
    # Multi-language content
    description: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    instructions: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    benefits: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    precautions: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Remedy Details
    duration_days: Optional[int] = Field(default=None)
    frequency: Optional[str] = Field(default=None)  # daily, weekly, monthly, etc.
    best_time: Optional[str] = Field(default=None)  # morning, evening, etc.
    materials_needed: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Effectiveness and Ratings
    effectiveness_rating: float = Field(default=0.0, ge=0, le=10)
    user_ratings_count: int = Field(default=0)
    difficulty_level: int = Field(default=1, ge=1, le=5)  # 1=easy, 5=difficult
    cost_level: int = Field(default=1, ge=1, le=5)  # 1=free, 5=expensive
    
    # Scientific and Traditional Basis
    scientific_basis: Optional[str] = Field(default=None)
    traditional_reference: Optional[str] = Field(default=None)
    
    # Media and Resources
    mantra_text: Optional[str] = Field(default=None)
    mantra_audio_url: Optional[str] = Field(default=None)
    instruction_video_url: Optional[str] = Field(default=None)
    yantra_image_url: Optional[str] = Field(default=None)
    additional_resources: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Timing and Conditions
    optimal_conditions: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    contraindications: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Metadata
    is_active: bool = Field(default=True)
    created_by: Optional[str] = Field(default=None)  # Admin/expert who added
    verified: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    
    class Config:
        """SQLModel config."""
        json_schema_extra = {
            "example": {
                "name": "Ganesha Mantra for Jupiter",
                "type_id": 1,
                "type_name": "Mantra",
                "tradition_id": 1,
                "tradition_name": "Vedic",
                "planet": "Jupiter",
                "description": {
                    "en": "Powerful mantra to strengthen Jupiter and remove obstacles",
                    "hi": "गुरु को मजबूत करने और बाधाओं को दूर करने के लिए शक्तिशाली मंत्र"
                },
                "mantra_text": "Om Gam Ganapataye Namaha",
                "duration_days": 40,
                "frequency": "daily",
                "best_time": "morning"
            }
        }
    
    def get_localized_content(self, field: str, language: str = "en") -> str:
        """Get localized content for a field."""
        content_dict = getattr(self, field, {})
        if isinstance(content_dict, dict):
            return content_dict.get(language, content_dict.get("en", ""))
        return str(content_dict)


class UserRemedyProgress(SQLModel, table=True):
    """Track user's progress with remedies."""
    
    __tablename__ = "user_remedy_progress"
    
    progress_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.user_id", index=True)
    remedy_id: UUID = Field(foreign_key="remedies.remedy_id", index=True)
    chart_id: Optional[UUID] = Field(foreign_key="astrology_chart.chart_id", default=None)
    
    # Progress Tracking
    started_at: datetime = Field(default_factory=datetime.utcnow)
    target_end_date: Optional[datetime] = Field(default=None)
    current_day: int = Field(default=1)
    total_days: Optional[int] = Field(default=None)
    completion_percentage: float = Field(default=0.0, ge=0, le=100)
    
    # Tracking Data
    daily_logs: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))
    notes: Optional[str] = Field(default=None)
    challenges: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    benefits_experienced: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Status
    is_active: bool = Field(default=True)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)
    
    # User Feedback
    effectiveness_rating: Optional[int] = Field(default=None, ge=1, le=10)
    difficulty_rating: Optional[int] = Field(default=None, ge=1, le=5)
    would_recommend: Optional[bool] = Field(default=None)
    feedback: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


class RemedyRecommendation(SQLModel, table=True):
    """AI/Expert recommendations for specific chart issues."""
    
    __tablename__ = "remedy_recommendations"
    
    recommendation_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.user_id", index=True)
    chart_id: UUID = Field(foreign_key="astrology_chart.chart_id", index=True)
    remedy_id: UUID = Field(foreign_key="remedies.remedy_id", index=True)
    
    # Recommendation Details
    relevance_score: float = Field(ge=0, le=100)  # How relevant this remedy is
    priority_level: int = Field(ge=1, le=5)  # 1=low, 5=urgent
    
    # Issue Addressed
    issue_type: str  # "planetary_weakness", "dosha", "general_improvement"
    issue_description: str
    expected_timeline: Optional[str] = Field(default=None)  # "2-3 months", "immediate", etc.
    
    # Personalized Instructions
    personalized_instructions: Optional[str] = Field(default=None)
    modifications: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # AI/Expert Details
    recommended_by: str  # "ai", "expert", "astrologer"
    recommender_id: Optional[str] = Field(default=None)
    confidence_score: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Status
    is_active: bool = Field(default=True)
    user_acknowledged: bool = Field(default=False)
    user_started: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = Field(default=None)
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


# Request/Response Models
class RemedyCreate(SQLModel):
    """Schema for creating a remedy."""
    name: str
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    tradition_id: Optional[int] = 1
    tradition_name: Optional[str] = "Vedic"
    planet: Optional[str] = None
    dosha_type_id: Optional[int] = None
    dosha_type_name: Optional[str] = None
    description: Dict
    instructions: Dict
    benefits: Dict = {}
    precautions: Dict = {}
    duration_days: Optional[int] = None
    frequency: Optional[str] = None
    best_time: Optional[str] = None
    materials_needed: List[str] = []
    difficulty_level: int = 1
    cost_level: int = 1
    mantra_text: Optional[str] = None


class RemedyUpdate(SQLModel):
    """Schema for updating a remedy."""
    name: Optional[str] = None
    description: Optional[Dict] = None
    instructions: Optional[Dict] = None
    benefits: Optional[Dict] = None
    precautions: Optional[Dict] = None
    duration_days: Optional[int] = None
    frequency: Optional[str] = None
    best_time: Optional[str] = None
    materials_needed: Optional[List[str]] = None
    difficulty_level: Optional[int] = None
    cost_level: Optional[int] = None


class RemedyResponse(SQLModel):
    """Schema for remedy response."""
    remedy_id: UUID
    name: str
    type_id: Optional[int]
    type_name: Optional[str]
    tradition_id: Optional[int]
    tradition_name: Optional[str]
    planet: Optional[str]
    dosha_type_id: Optional[int]
    dosha_type_name: Optional[str]
    description: Dict
    instructions: Dict
    benefits: Dict
    precautions: Dict
    duration_days: Optional[int]
    frequency: Optional[str]
    best_time: Optional[str]
    materials_needed: List[str]
    effectiveness_rating: float
    difficulty_level: int
    cost_level: int
    mantra_text: Optional[str]
    mantra_audio_url: Optional[str]
    instruction_video_url: Optional[str]
    yantra_image_url: Optional[str]
    created_at: datetime


class RecommendationRequest(SQLModel):
    """Schema for requesting remedy recommendations."""
    chart_id: UUID
    concern_areas: List[str] = []
    tradition_preference: Optional[str] = None
    difficulty_preference: Optional[int] = None  # 1-5
    cost_preference: Optional[int] = None  # 1-5


class RecommendationResponse(SQLModel):
    """Schema for remedy recommendation response."""
    recommendation_id: UUID
    remedy: RemedyResponse
    relevance_score: float
    priority_level: int
    issue_description: str
    expected_timeline: Optional[str]
    personalized_instructions: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime


class ProgressUpdate(SQLModel):
    """Schema for updating remedy progress."""
    current_day: int
    completion_percentage: float
    daily_log: Optional[Dict] = None
    notes: Optional[str] = None
    challenges: Optional[List[str]] = None
    benefits_experienced: Optional[List[str]] = None


class ProgressResponse(SQLModel):
    """Schema for remedy progress response."""
    progress_id: UUID
    remedy_id: UUID
    started_at: datetime
    current_day: int
    total_days: Optional[int]
    completion_percentage: float
    is_completed: bool
    effectiveness_rating: Optional[int]
    would_recommend: Optional[bool]