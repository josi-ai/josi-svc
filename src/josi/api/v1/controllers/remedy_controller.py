"""
Remedy (Pariharam) recommendation API controller.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from josi.core.database import get_db
from josi.api.v1.dependencies import get_current_organization
from josi.services.auth_service import get_current_active_user as get_current_user
from josi.models.organization_model import Organization
from josi.models.user_model import User
from josi.models.remedy_model import (
    RemedyCreate, RemedyUpdate, RemedyResponse, 
    RecommendationRequest, RecommendationResponse,
    ProgressUpdate, ProgressResponse,
    RemedyType, Tradition, DoshaType
)
from josi.services.remedy_recommendation_service import RemedyRecommendationService
from josi.repositories.remedy_repository import RemedyRepository
from josi.api.response import ResponseModel
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/remedies", tags=["Remedies"])


@router.post("/recommend")
async def get_remedy_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Get AI-powered remedy recommendations based on chart analysis.
    
    Analyzes the chart for doshas, planetary afflictions, and weaknesses,
    then recommends personalized remedies with AI-enhanced instructions.
    """
    try:
        service = RemedyRecommendationService(db)
        
        recommendations = await service.analyze_and_recommend(
            user_id=current_user.user_id,
            request=request
        )
        
        logger.info(
            "Remedy recommendations generated",
            user_id=str(current_user.user_id),
            chart_id=str(request.chart_id),
            recommendation_count=len(recommendations),
            organization_id=str(organization.organization_id)
        )
        
        return ResponseModel(
            success=True,
            message="Remedy recommendations generated successfully",
            data={
                "recommendations": [rec.dict() for rec in recommendations],
                "total_recommendations": len(recommendations),
                "chart_id": str(request.chart_id),
                "analysis_criteria": {
                    "concern_areas": request.concern_areas,
                    "tradition_preference": request.tradition_preference,
                    "difficulty_preference": request.difficulty_preference,
                    "cost_preference": request.cost_preference
                }
            }
        )
    
    except ValueError as e:
        logger.warning(
            "Invalid request for remedy recommendations",
            error=str(e),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(
            "Failed to generate remedy recommendations",
            error=str(e),
            user_id=str(current_user.user_id),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate remedy recommendations"
        )


@router.get("/")
async def list_remedies(
    tradition: Optional[Tradition] = Query(None, description="Filter by tradition"),
    remedy_type: Optional[RemedyType] = Query(None, description="Filter by remedy type"),
    planet: Optional[str] = Query(None, description="Filter by planet"),
    dosha_type: Optional[DoshaType] = Query(None, description="Filter by dosha type"),
    difficulty_max: Optional[int] = Query(None, ge=1, le=5, description="Maximum difficulty level"),
    cost_max: Optional[int] = Query(None, ge=1, le=5, description="Maximum cost level"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    List available remedies with optional filtering.
    """
    try:
        repository = RemedyRepository(db, organization.organization_id)
        
        remedies = await repository.list_remedies(
            tradition=tradition,
            remedy_type=remedy_type,
            planet=planet,
            dosha_type=dosha_type,
            difficulty_max=difficulty_max,
            cost_max=cost_max,
            skip=skip,
            limit=limit
        )
        
        total_count = await repository.count_remedies(
            tradition=tradition,
            remedy_type=remedy_type,
            planet=planet,
            dosha_type=dosha_type,
            difficulty_max=difficulty_max,
            cost_max=cost_max
        )
        
        return ResponseModel(
            success=True,
            message="Remedies retrieved successfully",
            data={
                "remedies": [RemedyResponse.from_orm(remedy).dict() for remedy in remedies],
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": total_count,
                    "has_more": skip + len(remedies) < total_count
                },
                "filters_applied": {
                    "tradition": tradition,
                    "remedy_type": remedy_type,
                    "planet": planet,
                    "dosha_type": dosha_type,
                    "difficulty_max": difficulty_max,
                    "cost_max": cost_max
                }
            }
        )
    
    except Exception as e:
        logger.error(
            "Failed to list remedies",
            error=str(e),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve remedies"
        )


@router.get("/{remedy_id}")
async def get_remedy(
    remedy_id: UUID = Path(..., description="Remedy ID"),
    language: str = Query("en", description="Language for localized content"),
    db: AsyncSession = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Get detailed information about a specific remedy.
    """
    try:
        repository = RemedyRepository(db, organization.organization_id)
        remedy = await repository.get(remedy_id)
        
        if not remedy:
            raise HTTPException(status_code=404, detail="Remedy not found")
        
        # Get localized content
        remedy_data = RemedyResponse.from_orm(remedy).dict()
        remedy_data["localized_content"] = {
            "description": remedy.get_localized_content("description", language),
            "instructions": remedy.get_localized_content("instructions", language),
            "benefits": remedy.get_localized_content("benefits", language),
            "precautions": remedy.get_localized_content("precautions", language)
        }
        
        return ResponseModel(
            success=True,
            message="Remedy retrieved successfully",
            data=remedy_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get remedy",
            error=str(e),
            remedy_id=str(remedy_id),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve remedy"
        )


@router.post("/")
async def create_remedy(
    remedy_data: RemedyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Create a new remedy (admin/expert only).
    """
    try:
        # Check if user has permission to create remedies
        if current_user.subscription_tier not in ["MASTER"]:  # Add admin check later
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to create remedies"
            )
        
        repository = RemedyRepository(db, organization.organization_id)
        remedy = await repository.create_remedy(remedy_data, str(current_user.user_id))
        
        logger.info(
            "Remedy created",
            remedy_id=str(remedy.remedy_id),
            created_by=str(current_user.user_id),
            organization_id=str(organization.organization_id)
        )
        
        return ResponseModel(
            success=True,
            message="Remedy created successfully",
            data=RemedyResponse.from_orm(remedy).dict()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create remedy",
            error=str(e),
            user_id=str(current_user.user_id),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to create remedy"
        )


@router.put("/{remedy_id}")
async def update_remedy(
    remedy_id: UUID,
    remedy_data: RemedyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Update an existing remedy (admin/expert only).
    """
    try:
        # Check permissions
        if current_user.subscription_tier not in ["MASTER"]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to update remedies"
            )
        
        repository = RemedyRepository(db, organization.organization_id)
        remedy = await repository.update_remedy(remedy_id, remedy_data)
        
        if not remedy:
            raise HTTPException(status_code=404, detail="Remedy not found")
        
        logger.info(
            "Remedy updated",
            remedy_id=str(remedy_id),
            updated_by=str(current_user.user_id),
            organization_id=str(organization.organization_id)
        )
        
        return ResponseModel(
            success=True,
            message="Remedy updated successfully",
            data=RemedyResponse.from_orm(remedy).dict()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update remedy",
            error=str(e),
            remedy_id=str(remedy_id),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to update remedy"
        )


@router.post("/{remedy_id}/start-progress")
async def start_remedy_progress(
    remedy_id: UUID,
    target_days: Optional[int] = Query(None, ge=1, le=365, description="Target duration in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Start tracking progress for a remedy.
    """
    try:
        repository = RemedyRepository(db, organization.organization_id)
        
        # Check if remedy exists
        remedy = await repository.get(remedy_id)
        if not remedy:
            raise HTTPException(status_code=404, detail="Remedy not found")
        
        # Start progress tracking
        progress = await repository.start_progress(
            user_id=current_user.user_id,
            remedy_id=remedy_id,
            target_days=target_days or remedy.duration_days
        )
        
        logger.info(
            "Remedy progress started",
            progress_id=str(progress.progress_id),
            user_id=str(current_user.user_id),
            remedy_id=str(remedy_id)
        )
        
        return ResponseModel(
            success=True,
            message="Remedy progress tracking started",
            data=ProgressResponse.from_orm(progress).dict()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to start remedy progress",
            error=str(e),
            user_id=str(current_user.user_id),
            remedy_id=str(remedy_id)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to start remedy progress tracking"
        )


@router.put("/progress/{progress_id}")
async def update_remedy_progress(
    progress_id: UUID,
    progress_data: ProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Update progress for a remedy.
    """
    try:
        repository = RemedyRepository(db, organization.organization_id)
        progress = await repository.update_progress(progress_id, progress_data)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Progress record not found")
        
        # Verify ownership
        if progress.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return ResponseModel(
            success=True,
            message="Remedy progress updated successfully",
            data=ProgressResponse.from_orm(progress).dict()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update remedy progress",
            error=str(e),
            progress_id=str(progress_id),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to update remedy progress"
        )


@router.get("/my-remedies/active")
async def get_active_remedies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Get user's currently active remedies with progress.
    """
    try:
        repository = RemedyRepository(db, organization.organization_id)
        active_remedies = await repository.get_user_active_remedies(current_user.user_id)
        
        return ResponseModel(
            success=True,
            message="Active remedies retrieved successfully",
            data={
                "active_remedies": [
                    {
                        "progress": ProgressResponse.from_orm(progress).dict(),
                        "remedy": RemedyResponse.from_orm(progress.remedy).dict()
                    }
                    for progress in active_remedies
                ],
                "count": len(active_remedies)
            }
        )
    
    except Exception as e:
        logger.error(
            "Failed to get active remedies",
            error=str(e),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve active remedies"
        )


@router.get("/categories")
async def get_remedy_categories(
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Get available remedy categories and filters.
    """
    categories = {
        "remedy_types": [
            {"value": "mantra", "label": "Mantra", "description": "Sacred chants and recitations"},
            {"value": "gemstone", "label": "Gemstone", "description": "Planetary gemstone recommendations"},
            {"value": "yantra", "label": "Yantra", "description": "Sacred geometric symbols"},
            {"value": "ritual", "label": "Ritual", "description": "Religious ceremonies and practices"},
            {"value": "charity", "label": "Charity", "description": "Charitable acts and donations"},
            {"value": "fasting", "label": "Fasting", "description": "Spiritual fasting practices"},
            {"value": "pilgrimage", "label": "Pilgrimage", "description": "Sacred journey recommendations"},
            {"value": "lifestyle", "label": "Lifestyle", "description": "Lifestyle changes and habits"},
            {"value": "meditation", "label": "Meditation", "description": "Meditation and mindfulness practices"},
            {"value": "prayer", "label": "Prayer", "description": "Prayer and devotional practices"}
        ],
        "traditions": [
            {"value": "vedic", "label": "Vedic", "description": "Traditional Vedic astrology remedies"},
            {"value": "western", "label": "Western", "description": "Western astrological approaches"},
            {"value": "chinese", "label": "Chinese", "description": "Chinese astrology and feng shui"},
            {"value": "hellenistic", "label": "Hellenistic", "description": "Hellenistic astrology traditions"},
            {"value": "tantric", "label": "Tantric", "description": "Tantric spiritual practices"}
        ],
        "dosha_types": [
            {"value": "mangal_dosha", "label": "Mangal Dosha", "description": "Mars-related afflictions"},
            {"value": "kaal_sarp_dosha", "label": "Kaal Sarp Dosha", "description": "Rahu-Ketu axis afflictions"},
            {"value": "pitra_dosha", "label": "Pitra Dosha", "description": "Ancestral karma issues"},
            {"value": "guru_chandal_dosha", "label": "Guru Chandal Dosha", "description": "Jupiter-Rahu conjunction"},
            {"value": "nadi_dosha", "label": "Nadi Dosha", "description": "Compatibility issues"},
            {"value": "rahu_dosha", "label": "Rahu Dosha", "description": "Rahu-related afflictions"},
            {"value": "ketu_dosha", "label": "Ketu Dosha", "description": "Ketu-related afflictions"},
            {"value": "shani_dosha", "label": "Shani Dosha", "description": "Saturn-related challenges"}
        ],
        "planets": [
            "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
        ],
        "difficulty_levels": [
            {"value": 1, "label": "Very Easy", "description": "Simple daily practices"},
            {"value": 2, "label": "Easy", "description": "Basic requirements, minimal time"},
            {"value": 3, "label": "Moderate", "description": "Regular commitment required"},
            {"value": 4, "label": "Challenging", "description": "Significant dedication needed"},
            {"value": 5, "label": "Advanced", "description": "Intensive spiritual practice"}
        ],
        "cost_levels": [
            {"value": 1, "label": "Free", "description": "No monetary cost"},
            {"value": 2, "label": "Low Cost", "description": "Minimal expense"},
            {"value": 3, "label": "Moderate Cost", "description": "Some investment required"},
            {"value": 4, "label": "High Cost", "description": "Significant expense"},
            {"value": 5, "label": "Premium", "description": "Expensive items/services"}
        ]
    }
    
    return ResponseModel(
        success=True,
        message="Remedy categories retrieved successfully",
        data=categories
    )