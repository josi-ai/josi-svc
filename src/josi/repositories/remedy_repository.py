"""
Repository for remedy-related database operations.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from josi.repositories.base_repository import BaseRepository
from josi.models.remedy_model import (
    Remedy, RemedyRecommendation, UserRemedyProgress,
    RemedyCreate, RemedyUpdate, ProgressUpdate,
)
from josi.enums.remedy_type_enum import RemedyTypeEnum as RemedyType
from josi.enums.tradition_enum import TraditionEnum as Tradition
from josi.enums.dosha_type_enum import DoshaTypeEnum as DoshaType
import structlog

logger = structlog.get_logger(__name__)


class RemedyRepository(BaseRepository[Remedy]):
    """Repository for remedy operations."""
    
    def __init__(self, db: AsyncSession, organization_id: UUID):
        super().__init__(db, Remedy, organization_id)
    
    async def list_remedies(
        self,
        tradition: Optional[Tradition] = None,
        remedy_type: Optional[RemedyType] = None,
        planet: Optional[str] = None,
        dosha_type: Optional[DoshaType] = None,
        difficulty_max: Optional[int] = None,
        cost_max: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Remedy]:
        """List remedies with filtering options."""
        query = select(Remedy).where(
            Remedy.is_active == True,
            Remedy.is_deleted == False
        )
        
        # Apply filters
        if tradition:
            query = query.where(Remedy.tradition_id == tradition.id)
        
        if remedy_type:
            query = query.where(Remedy.type_id == remedy_type.id)
        
        if planet:
            query = query.where(Remedy.planet == planet)
        
        if dosha_type:
            query = query.where(Remedy.dosha_type_id == dosha_type.id)
        
        if difficulty_max:
            query = query.where(Remedy.difficulty_level <= difficulty_max)
        
        if cost_max:
            query = query.where(Remedy.cost_level <= cost_max)
        
        # Add ordering and pagination
        query = query.order_by(Remedy.effectiveness_rating.desc(), Remedy.name)
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count_remedies(
        self,
        tradition: Optional[Tradition] = None,
        remedy_type: Optional[RemedyType] = None,
        planet: Optional[str] = None,
        dosha_type: Optional[DoshaType] = None,
        difficulty_max: Optional[int] = None,
        cost_max: Optional[int] = None
    ) -> int:
        """Count remedies with filtering options."""
        query = select(func.count(Remedy.remedy_id)).where(
            Remedy.is_active == True,
            Remedy.is_deleted == False
        )
        
        # Apply same filters as list_remedies
        if tradition:
            query = query.where(Remedy.tradition_id == tradition.id)
        
        if remedy_type:
            query = query.where(Remedy.type_id == remedy_type.id)
        
        if planet:
            query = query.where(Remedy.planet == planet)
        
        if dosha_type:
            query = query.where(Remedy.dosha_type_id == dosha_type.id)
        
        if difficulty_max:
            query = query.where(Remedy.difficulty_level <= difficulty_max)
        
        if cost_max:
            query = query.where(Remedy.cost_level <= cost_max)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def create_remedy(self, remedy_data: RemedyCreate, created_by: str) -> Remedy:
        """Create a new remedy."""
        remedy = Remedy(
            **remedy_data.dict(),
            created_by=created_by,
            verified=False  # New remedies need verification
        )
        
        self.db.add(remedy)
        await self.db.commit()
        await self.db.refresh(remedy)
        
        return remedy
    
    async def update_remedy(self, remedy_id: UUID, remedy_data: RemedyUpdate) -> Optional[Remedy]:
        """Update an existing remedy."""
        remedy = await self.get(remedy_id)
        if not remedy:
            return None
        
        # Update fields
        update_data = remedy_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(remedy, field, value)
        
        remedy.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(remedy)
        
        return remedy
    
    async def start_progress(
        self,
        user_id: UUID,
        remedy_id: UUID,
        target_days: Optional[int] = None,
        chart_id: Optional[UUID] = None
    ) -> UserRemedyProgress:
        """Start tracking progress for a remedy."""
        
        # Check if user already has active progress for this remedy
        existing_query = select(UserRemedyProgress).where(
            UserRemedyProgress.user_id == user_id,
            UserRemedyProgress.remedy_id == remedy_id,
            UserRemedyProgress.is_active == True,
            UserRemedyProgress.is_deleted == False
        )
        
        result = await self.db.execute(existing_query)
        existing_progress = result.scalar_one_or_none()
        
        if existing_progress:
            # Reactivate existing progress
            existing_progress.is_active = True
            existing_progress.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(existing_progress)
            return existing_progress
        
        # Create new progress
        progress = UserRemedyProgress(
            user_id=user_id,
            remedy_id=remedy_id,
            chart_id=chart_id,
            total_days=target_days,
            current_day=1,
            completion_percentage=0.0
        )
        
        if target_days:
            progress.target_end_date = datetime.utcnow() + timedelta(days=target_days)
        
        self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(progress)
        
        return progress
    
    async def update_progress(
        self,
        progress_id: UUID,
        progress_data: ProgressUpdate
    ) -> Optional[UserRemedyProgress]:
        """Update remedy progress."""
        query = select(UserRemedyProgress).where(
            UserRemedyProgress.progress_id == progress_id,
            UserRemedyProgress.is_deleted == False
        )
        
        result = await self.db.execute(query)
        progress = result.scalar_one_or_none()
        
        if not progress:
            return None
        
        # Update fields
        update_data = progress_data.dict(exclude_unset=True)
        
        if "current_day" in update_data:
            progress.current_day = update_data["current_day"]
        
        if "completion_percentage" in update_data:
            progress.completion_percentage = update_data["completion_percentage"]
        
        if "daily_log" in update_data and update_data["daily_log"]:
            if not progress.daily_logs:
                progress.daily_logs = []
            progress.daily_logs.append({
                "date": datetime.utcnow().date().isoformat(),
                "log": update_data["daily_log"]
            })
        
        if "notes" in update_data:
            progress.notes = update_data["notes"]
        
        if "challenges" in update_data:
            progress.challenges = update_data["challenges"] or []
        
        if "benefits_experienced" in update_data:
            progress.benefits_experienced = update_data["benefits_experienced"] or []
        
        # Check if completed
        if progress.completion_percentage >= 100 and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
        
        progress.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(progress)
        
        return progress
    
    async def get_user_active_remedies(self, user_id: UUID) -> List[UserRemedyProgress]:
        """Get user's active remedy progress with remedy details."""
        query = select(UserRemedyProgress).join(Remedy).where(
            UserRemedyProgress.user_id == user_id,
            UserRemedyProgress.is_active == True,
            UserRemedyProgress.is_deleted == False,
            Remedy.is_deleted == False
        ).order_by(UserRemedyProgress.started_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_remedy_history(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[UserRemedyProgress]:
        """Get user's remedy history."""
        query = select(UserRemedyProgress).join(Remedy).where(
            UserRemedyProgress.user_id == user_id,
            UserRemedyProgress.is_deleted == False,
            Remedy.is_deleted == False
        ).order_by(UserRemedyProgress.started_at.desc())
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_recommendations_for_user(
        self,
        user_id: UUID,
        chart_id: Optional[UUID] = None,
        active_only: bool = True
    ) -> List[RemedyRecommendation]:
        """Get remedy recommendations for a user."""
        query = select(RemedyRecommendation).where(
            RemedyRecommendation.user_id == user_id,
            RemedyRecommendation.is_deleted == False
        )
        
        if chart_id:
            query = query.where(RemedyRecommendation.chart_id == chart_id)
        
        if active_only:
            query = query.where(RemedyRecommendation.is_active == True)
        
        query = query.order_by(
            RemedyRecommendation.priority_level.desc(),
            RemedyRecommendation.relevance_score.desc()
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_popular_remedies(
        self,
        limit: int = 10,
        tradition: Optional[Tradition] = None
    ) -> List[Remedy]:
        """Get most popular remedies based on user ratings and usage."""
        query = select(Remedy).where(
            Remedy.is_active == True,
            Remedy.is_deleted == False,
            Remedy.user_ratings_count > 0
        )
        
        if tradition:
            query = query.where(Remedy.tradition_id == tradition.id)
        
        query = query.order_by(
            Remedy.effectiveness_rating.desc(),
            Remedy.user_ratings_count.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_remedies(
        self,
        search_term: str,
        tradition: Optional[Tradition] = None,
        limit: int = 20
    ) -> List[Remedy]:
        """Search remedies by name, description, or benefits."""
        query = select(Remedy).where(
            Remedy.is_active == True,
            Remedy.is_deleted == False,
            or_(
                Remedy.name.ilike(f"%{search_term}%"),
                # For JSON search, you might need to use database-specific functions
                # This is a simplified version
                func.cast(Remedy.description, str).ilike(f"%{search_term}%")
            )
        )
        
        if tradition:
            query = query.where(Remedy.tradition_id == tradition.id)
        
        query = query.order_by(Remedy.effectiveness_rating.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()