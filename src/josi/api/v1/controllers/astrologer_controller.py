"""
Astrologer marketplace API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from josi.core.database import get_db
from josi.services.auth_service import get_current_active_user
from josi.models.user_model import User
from josi.models.astrologer_model import (
    Astrologer, 
    AstrologerReview,
    AstrologerCreate,
    AstrologerUpdate,
    AstrologerResponse,
    ReviewCreate,
    ReviewResponse,
    VerificationStatus
)
from josi.api.response import ResponseModel
from cache.cache_decorator import cache
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Astrologer Marketplace"], prefix="/astrologers")


@router.post("/register", response_model=ResponseModel)
async def register_as_astrologer(
    astrologer_data: AstrologerCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Register current user as an astrologer."""
    try:
        # Check if user is already registered as astrologer
        existing = await db.execute(
            select(Astrologer).where(
                Astrologer.user_id == current_user.user_id,
                Astrologer.is_deleted == False
            )
        )
        
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already registered as an astrologer"
            )
        
        # Create astrologer profile
        astrologer_dict = astrologer_data.model_dump()
        astrologer_dict["user_id"] = current_user.user_id
        
        astrologer = Astrologer(**astrologer_dict)
        db.add(astrologer)
        await db.commit()
        await db.refresh(astrologer)
        
        logger.info(
            "Astrologer registered",
            user_id=str(current_user.user_id),
            astrologer_id=str(astrologer.astrologer_id)
        )
        
        return ResponseModel(
            success=True,
            message="Astrologer registration submitted for review",
            data={
                "astrologer_id": astrologer.astrologer_id,
                "verification_status": astrologer.verification_status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to register astrologer",
            error=str(e),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/search", response_model=ResponseModel)
@cache(expire=300, prefix="astrologer_search")
async def search_astrologers(
    db: AsyncSession = Depends(get_db),
    specializations: Optional[List[str]] = Query(default=None),
    languages: Optional[List[str]] = Query(default=None),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    max_hourly_rate: Optional[float] = Query(default=None, gt=0),
    is_available_now: Optional[bool] = Query(default=None),
    sort_by: str = Query(default="rating", regex="^(rating|hourly_rate|total_consultations|joined_at)$"),
    sort_order: str = Query(default="desc", regex="^(asc|desc)$"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
) -> ResponseModel:
    """Search for astrologers with filters."""
    try:
        # Build query
        query = select(Astrologer).where(
            Astrologer.is_active == True,
            Astrologer.verification_status == VerificationStatus.VERIFIED,
            Astrologer.is_deleted == False
        )
        
        # Apply filters
        if specializations:
            # Check if any of the requested specializations match
            spec_conditions = []
            for spec in specializations:
                spec_conditions.append(
                    func.json_contains(Astrologer.specializations, f'"{spec}"')
                )
            query = query.where(or_(*spec_conditions))
        
        if languages:
            # Check if any of the requested languages match
            lang_conditions = []
            for lang in languages:
                lang_conditions.append(
                    func.json_contains(Astrologer.languages, f'"{lang}"')
                )
            query = query.where(or_(*lang_conditions))
        
        if min_rating is not None:
            query = query.where(Astrologer.rating >= min_rating)
        
        if max_hourly_rate is not None:
            query = query.where(Astrologer.hourly_rate <= max_hourly_rate)
        
        # TODO: Implement real-time availability checking
        if is_available_now:
            query = query.where(Astrologer.is_active == True)
        
        # Apply sorting
        sort_column = getattr(Astrologer, sort_by)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        astrologers = result.scalars().all()
        
        # Format response
        astrologer_list = []
        for astrologer in astrologers:
            astrologer_list.append(AstrologerResponse(
                astrologer_id=astrologer.astrologer_id,
                user_id=astrologer.user_id,
                professional_name=astrologer.professional_name,
                bio=astrologer.bio,
                years_experience=astrologer.years_experience,
                specializations=astrologer.specializations,
                languages=astrologer.languages,
                hourly_rate=astrologer.hourly_rate,
                currency=astrologer.currency,
                rating=astrologer.rating,
                total_consultations=astrologer.total_consultations,
                total_reviews=astrologer.total_reviews,
                verification_status=astrologer.verification_status.value,
                is_active=astrologer.is_active,
                is_featured=astrologer.is_featured,
                profile_image_url=astrologer.profile_image_url,
                joined_at=astrologer.joined_at
            ))
        
        return ResponseModel(
            success=True,
            message=f"Found {len(astrologer_list)} astrologers",
            data={
                "astrologers": astrologer_list,
                "total": len(astrologer_list),
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        logger.error(
            "Failed to search astrologers",
            error=str(e),
            filters={
                "specializations": specializations,
                "languages": languages,
                "min_rating": min_rating
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{astrologer_id}", response_model=ResponseModel)
@cache(expire=600, prefix="astrologer_profile")
async def get_astrologer_profile(
    astrologer_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Get detailed astrologer profile."""
    try:
        # Get astrologer
        result = await db.execute(
            select(Astrologer).where(
                Astrologer.astrologer_id == astrologer_id,
                Astrologer.is_deleted == False
            )
        )
        astrologer = result.scalar_one_or_none()
        
        if not astrologer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Astrologer not found"
            )
        
        # Get recent reviews
        reviews_result = await db.execute(
            select(AstrologerReview).where(
                AstrologerReview.astrologer_id == astrologer_id,
                AstrologerReview.is_deleted == False
            ).order_by(AstrologerReview.created_at.desc()).limit(10)
        )
        reviews = reviews_result.scalars().all()
        
        review_list = []
        for review in reviews:
            review_list.append(ReviewResponse(
                review_id=review.review_id,
                astrologer_id=review.astrologer_id,
                user_id=review.user_id,
                rating=review.rating,
                title=review.title,
                review_text=review.review_text,
                accuracy_rating=review.accuracy_rating,
                communication_rating=review.communication_rating,
                empathy_rating=review.empathy_rating,
                is_verified=review.is_verified,
                helpful_votes=review.helpful_votes,
                created_at=review.created_at
            ))
        
        return ResponseModel(
            success=True,
            message="Astrologer profile retrieved",
            data={
                "astrologer": AstrologerResponse(
                    astrologer_id=astrologer.astrologer_id,
                    user_id=astrologer.user_id,
                    professional_name=astrologer.professional_name,
                    bio=astrologer.bio,
                    years_experience=astrologer.years_experience,
                    specializations=astrologer.specializations,
                    languages=astrologer.languages,
                    hourly_rate=astrologer.hourly_rate,
                    currency=astrologer.currency,
                    rating=astrologer.rating,
                    total_consultations=astrologer.total_consultations,
                    total_reviews=astrologer.total_reviews,
                    verification_status=astrologer.verification_status.value,
                    is_active=astrologer.is_active,
                    is_featured=astrologer.is_featured,
                    profile_image_url=astrologer.profile_image_url,
                    joined_at=astrologer.joined_at
                ),
                "recent_reviews": review_list,
                "specialization_display": astrologer.get_specialization_display()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get astrologer profile",
            error=str(e),
            astrologer_id=str(astrologer_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {str(e)}"
        )


@router.put("/profile", response_model=ResponseModel)
async def update_astrologer_profile(
    updates: AstrologerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Update astrologer profile (for current user)."""
    try:
        # Get astrologer profile
        result = await db.execute(
            select(Astrologer).where(
                Astrologer.user_id == current_user.user_id,
                Astrologer.is_deleted == False
            )
        )
        astrologer = result.scalar_one_or_none()
        
        if not astrologer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Astrologer profile not found"
            )
        
        # Update fields
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(astrologer, field, value)
        
        astrologer.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(astrologer)
        
        return ResponseModel(
            success=True,
            message="Profile updated successfully",
            data={"astrologer_id": astrologer.astrologer_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to update astrologer profile",
            error=str(e),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )


@router.post("/{astrologer_id}/reviews", response_model=ResponseModel)
async def create_review(
    astrologer_id: UUID,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Create a review for an astrologer."""
    try:
        # Verify consultation exists and was completed
        from josi.models.consultation_model import Consultation, ConsultationStatus
        
        consultation_result = await db.execute(
            select(Consultation).where(
                Consultation.consultation_id == review_data.consultation_id,
                Consultation.user_id == current_user.user_id,
                Consultation.astrologer_id == astrologer_id,
                Consultation.status == ConsultationStatus.COMPLETED,
                Consultation.is_deleted == False
            )
        )
        consultation = consultation_result.scalar_one_or_none()
        
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid consultation or consultation not completed"
            )
        
        # Check if review already exists
        existing_review = await db.execute(
            select(AstrologerReview).where(
                AstrologerReview.consultation_id == review_data.consultation_id,
                AstrologerReview.is_deleted == False
            )
        )
        
        if existing_review.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review already exists for this consultation"
            )
        
        # Create review
        review = AstrologerReview(
            astrologer_id=astrologer_id,
            user_id=current_user.user_id,
            consultation_id=review_data.consultation_id,
            rating=review_data.rating,
            title=review_data.title,
            review_text=review_data.review_text,
            accuracy_rating=review_data.accuracy_rating,
            communication_rating=review_data.communication_rating,
            empathy_rating=review_data.empathy_rating,
            is_verified=True  # Auto-verify since we confirmed the consultation
        )
        
        db.add(review)
        
        # Update astrologer rating
        await _update_astrologer_rating(db, astrologer_id)
        
        await db.commit()
        await db.refresh(review)
        
        logger.info(
            "Review created",
            astrologer_id=str(astrologer_id),
            user_id=str(current_user.user_id),
            rating=review_data.rating
        )
        
        return ResponseModel(
            success=True,
            message="Review submitted successfully",
            data={"review_id": review.review_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to create review",
            error=str(e),
            astrologer_id=str(astrologer_id),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Review creation failed: {str(e)}"
        )


@router.get("/specializations", response_model=ResponseModel)
async def get_specializations() -> ResponseModel:
    """Get available astrologer specializations."""
    from josi.models.astrologer_model import AstrologerSpecialization
    
    specializations = []
    for spec in AstrologerSpecialization:
        specializations.append({
            "value": spec.value,
            "name": spec.value.replace("_", " ").title(),
            "description": {
                "vedic": "Traditional Indian astrology with emphasis on karma and spiritual growth",
                "western": "Modern psychological astrology focusing on personality and life patterns",
                "chinese": "Ancient Chinese divination including BaZi and feng shui",
                "hellenistic": "Classical Greco-Roman astrology with traditional techniques",
                "medical": "Astrology applied to health and wellness",
                "karmic": "Focus on past-life influences and soul evolution",
                "relationship": "Compatibility analysis and relationship counseling",
                "career": "Professional guidance and life path analysis",
                "spiritual": "Spiritual development and consciousness evolution",
                "predictive": "Future trends and timing of events"
            }.get(spec.value, "")
        })
    
    return ResponseModel(
        success=True,
        message="Specializations retrieved",
        data={"specializations": specializations}
    )


# Helper functions

async def _update_astrologer_rating(db: AsyncSession, astrologer_id: UUID):
    """Update astrologer's average rating."""
    try:
        # Calculate average rating
        rating_result = await db.execute(
            select(
                func.avg(AstrologerReview.rating),
                func.count(AstrologerReview.review_id)
            ).where(
                AstrologerReview.astrologer_id == astrologer_id,
                AstrologerReview.is_deleted == False
            )
        )
        
        avg_rating, review_count = rating_result.first()
        
        # Update astrologer
        astrologer_result = await db.execute(
            select(Astrologer).where(
                Astrologer.astrologer_id == astrologer_id,
                Astrologer.is_deleted == False
            )
        )
        astrologer = astrologer_result.scalar_one_or_none()
        
        if astrologer:
            astrologer.rating = round(float(avg_rating or 0), 2)
            astrologer.total_reviews = int(review_count or 0)
        
    except Exception as e:
        logger.warning(
            "Failed to update astrologer rating",
            error=str(e),
            astrologer_id=str(astrologer_id)
        )