"""
Consultation model for astrologer marketplace.
"""
from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from josi.models.user_model import User
    from josi.models.astrologer_model import Astrologer
    from josi.models.chart_model import AstrologyChart


class ConsultationStatus(str, enum.Enum):
    """Consultation status options."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ConsultationType(str, enum.Enum):
    """Types of consultations."""
    VIDEO = "video"
    CHAT = "chat"
    EMAIL = "email"
    VOICE = "voice"


class PaymentStatus(str, enum.Enum):
    """Payment status for consultations."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Consultation(SQLModel, table=True):
    """Consultation model."""
    
    __tablename__ = "consultations"
    
    consultation_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.user_id", index=True)
    astrologer_id: UUID = Field(foreign_key="astrologers.astrologer_id", index=True)
    chart_id: UUID = Field(foreign_key="astrology_chart.chart_id", index=True)
    
    # Consultation Details
    type: ConsultationType
    status: ConsultationStatus = Field(default=ConsultationStatus.PENDING)
    
    # Questions and Focus Areas
    user_questions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    focus_areas: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    special_requests: Optional[str] = Field(default=None)
    
    # Astrologer Response
    astrologer_notes: Optional[str] = Field(default=None)
    interpretation: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    recommendations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    follow_up_suggestions: Optional[str] = Field(default=None)
    
    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)
    duration_minutes: int = Field(default=60)
    timezone: str = Field(default="UTC")
    
    # Video/Audio Call Details
    video_room_id: Optional[str] = Field(default=None)
    video_access_token: Optional[str] = Field(default=None)
    recording_url: Optional[str] = Field(default=None)
    
    # AI Enhancement
    ai_summary: Optional[str] = Field(default=None)
    ai_key_points: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    ai_generated_questions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Payment Information
    total_amount: float
    currency: str = Field(default="USD")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_intent_id: Optional[str] = Field(default=None)
    stripe_session_id: Optional[str] = Field(default=None)
    
    # Communication
    chat_room_id: Optional[str] = Field(default=None)
    email_thread_id: Optional[str] = Field(default=None)
    
    # Quality Assurance
    quality_score: Optional[float] = Field(default=None)
    moderation_flags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    
    class Config:
        """SQLModel config."""
        json_schema_extra = {
            "example": {
                "type": "video",
                "user_questions": ["What does my chart say about my career path?"],
                "focus_areas": ["career", "life_purpose"],
                "duration_minutes": 60,
                "total_amount": 120.0
            }
        }
    
    def calculate_total_amount(self, hourly_rate: float) -> float:
        """Calculate total amount based on duration and hourly rate."""
        hours = self.duration_minutes / 60
        return round(hourly_rate * hours, 2)
    
    def is_upcoming(self) -> bool:
        """Check if consultation is upcoming."""
        if not self.scheduled_at:
            return False
        return self.scheduled_at > datetime.utcnow() and self.status == ConsultationStatus.SCHEDULED
    
    def can_be_cancelled(self) -> bool:
        """Check if consultation can be cancelled."""
        if self.status in [ConsultationStatus.COMPLETED, ConsultationStatus.CANCELLED]:
            return False
        
        # Allow cancellation up to 2 hours before scheduled time
        if self.scheduled_at:
            time_until = self.scheduled_at - datetime.utcnow()
            return time_until.total_seconds() > 7200  # 2 hours
        
        return True


class ConsultationMessage(SQLModel, table=True):
    """Messages within a consultation."""
    
    __tablename__ = "consultation_messages"
    
    message_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    consultation_id: UUID = Field(foreign_key="consultations.consultation_id", index=True)
    sender_id: UUID = Field(foreign_key="users.user_id", index=True)
    
    # Message Content
    message_type: str = Field(default="text")  # text, image, file, chart_annotation
    content: str
    message_metadata: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    
    # File attachments
    attachment_url: Optional[str] = Field(default=None)
    attachment_type: Optional[str] = Field(default=None)
    
    # Message status
    is_read: bool = Field(default=False)
    read_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


# Request/Response Models
class ConsultationRequest(SQLModel):
    """Schema for requesting a consultation."""
    astrologer_id: UUID
    chart_id: UUID
    type: ConsultationType
    user_questions: List[str]
    focus_areas: List[str] = []
    special_requests: Optional[str] = None
    preferred_times: List[datetime] = []
    duration_minutes: int = 60
    timezone: str = "UTC"


class ConsultationUpdate(SQLModel):
    """Schema for updating consultation."""
    status: Optional[ConsultationStatus] = None
    scheduled_at: Optional[datetime] = None
    astrologer_notes: Optional[str] = None
    interpretation: Optional[Dict] = None
    recommendations: Optional[List[str]] = None
    follow_up_suggestions: Optional[str] = None


class AstrologerResponse(SQLModel):
    """Schema for astrologer's response to consultation."""
    consultation_id: UUID
    interpretation: Dict
    recommendations: List[str] = []
    follow_up_suggestions: Optional[str] = None
    astrologer_notes: Optional[str] = None


class ConsultationResponse(SQLModel):
    """Schema for consultation response."""
    consultation_id: UUID
    user_id: UUID
    astrologer_id: UUID
    chart_id: UUID
    type: str
    status: str
    user_questions: List[str]
    focus_areas: List[str]
    scheduled_at: Optional[datetime]
    duration_minutes: int
    total_amount: float
    currency: str
    payment_status: str
    ai_summary: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class MessageCreate(SQLModel):
    """Schema for creating a consultation message."""
    consultation_id: UUID
    content: str
    message_type: str = "text"
    attachment_url: Optional[str] = None
    attachment_type: Optional[str] = None


class MessageResponse(SQLModel):
    """Schema for message response."""
    message_id: UUID
    consultation_id: UUID
    sender_id: UUID
    message_type: str
    content: str
    attachment_url: Optional[str]
    is_read: bool
    created_at: datetime


class ConsultationStats(SQLModel):
    """Schema for consultation statistics."""
    total_consultations: int
    completed_consultations: int
    average_rating: float
    total_revenue: float
    response_time_hours: float
    completion_rate: float