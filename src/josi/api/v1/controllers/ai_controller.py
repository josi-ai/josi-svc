"""
AI interpretation API endpoints.
"""
from typing import List, Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from josi.core.database import get_db
from josi.core.config import settings
from josi.services.ai.interpretation_service import (
    AIInterpretationService, 
    InterpretationStyle,
    AIProvider
)
from josi.services.chart_service import ChartService
from josi.auth.middleware import resolve_current_user
from josi.auth.schemas import CurrentUser
from josi.api.response import ResponseModel
from cache.cache_decorator import cache
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["AI Interpretations"], prefix="/ai")


class InterpretationRequest(SQLModel):
    """Request model for AI interpretation."""
    chart_id: UUID
    question: str
    style: InterpretationStyle = InterpretationStyle.BALANCED
    provider: Optional[AIProvider] = None
    user_context: Optional[Dict] = None


class NeuralPathwayRequest(SQLModel):
    """Request model for neural pathway questions."""
    chart_id: UUID
    previous_responses: List[Dict] = []
    focus_area: Optional[str] = None


@router.post("/interpret", response_model=ResponseModel)
@cache(expire=3600, prefix="ai_interpretation")
async def generate_interpretation(
    request: InterpretationRequest,
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Generate AI-powered interpretation for a chart."""
    try:
        # Check user limits
        tier_limits = current_user.get_tier_limits()
        if tier_limits["ai_interpretations_per_month"] != -1:
            # TODO: Implement usage tracking
            pass
        
        # Get chart
        chart_service = ChartService(db, user_id=current_user.user_id)
        chart = await chart_service.get_chart(request.chart_id)
        
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found"
            )
        
        # Generate interpretation
        ai_service = AIInterpretationService()
        interpretation = await ai_service.generate_interpretation(
            chart_data=chart.chart_data,
            question=request.question,
            user_context=request.user_context,
            style=request.style,
            provider=request.provider
        )
        
        logger.info(
            "AI interpretation generated",
            user_id=str(current_user.user_id),
            chart_id=str(request.chart_id),
            style=request.style.description
        )
        
        return ResponseModel(
            success=True,
            message="Interpretation generated successfully",
            data=interpretation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to generate interpretation",
            error=str(e),
            user_id=str(current_user.user_id),
            chart_id=str(request.chart_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate interpretation: {str(e)}"
        )


@router.post("/neural-pathway", response_model=ResponseModel)
async def generate_neural_pathway_questions(
    request: NeuralPathwayRequest,
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Generate psychological self-awareness questions based on chart."""
    try:
        # Check premium features
        if not current_user.has_premium_features():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Neural pathway questions require a premium subscription"
            )
        
        # Get chart
        chart_service = ChartService(db, user_id=current_user.user_id)
        chart = await chart_service.get_chart(request.chart_id)
        
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found"
            )
        
        # Generate questions
        ai_service = AIInterpretationService()
        questions = await ai_service.generate_neural_pathway_questions(
            chart_data=chart.chart_data,
            previous_responses=request.previous_responses,
            focus_area=request.focus_area
        )
        
        return ResponseModel(
            success=True,
            message="Neural pathway questions generated",
            data={"questions": questions}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to generate neural pathway questions",
            error=str(e),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {str(e)}"
        )


@router.get("/styles", response_model=ResponseModel)
async def get_interpretation_styles() -> ResponseModel:
    """Get available interpretation styles."""
    styles = [
        {
            "value": style.id,
            "name": style.description,
            "description": {
                InterpretationStyle.BALANCED: "A balanced blend of traditional and modern interpretations",
                InterpretationStyle.PSYCHOLOGICAL: "Focus on psychological patterns and personal growth",
                InterpretationStyle.SPIRITUAL: "Emphasis on spiritual lessons and soul evolution",
                InterpretationStyle.PRACTICAL: "Practical advice and real-world applications",
                InterpretationStyle.PREDICTIVE: "Timing, cycles, and potential developments"
            }.get(style, "")
        }
        for style in InterpretationStyle
    ]
    
    return ResponseModel(
        success=True,
        message="Interpretation styles retrieved",
        data={"styles": styles}
    )


@router.get("/providers", response_model=ResponseModel)
async def get_ai_providers() -> ResponseModel:
    """Get available AI providers."""
    providers = []
    
    if settings.openai_api_key:
        providers.append({
            "value": AIProvider.OPENAI.id,
            "name": "OpenAI GPT-4",
            "description": "Advanced language model with broad knowledge"
        })

    if settings.anthropic_api_key:
        providers.append({
            "value": AIProvider.ANTHROPIC.id,
            "name": "Anthropic Claude",
            "description": "Thoughtful and nuanced interpretations"
        })
    
    return ResponseModel(
        success=True,
        message="AI providers retrieved",
        data={"providers": providers}
    )