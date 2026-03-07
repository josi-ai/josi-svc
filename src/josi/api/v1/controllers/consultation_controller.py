"""
Consultation API endpoints for booking and managing consultations.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from josi.core.database import get_db
from josi.auth.middleware import resolve_current_user
from josi.services.consultation_service import ConsultationService
from josi.auth.schemas import CurrentUser
from josi.models.consultation_model import (
    ConsultationRequest,
    ConsultationUpdate,
    AstrologerResponse,
    ConsultationResponse,
    MessageCreate,
    MessageResponse,
)
from josi.enums.consultation_status_enum import ConsultationStatusEnum as ConsultationStatus
from josi.enums.consultation_type_enum import ConsultationTypeEnum as ConsultationType
from josi.api.response import ResponseModel
from cache.cache_decorator import cache
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Consultations"], prefix="/consultations")


@router.post("/book", response_model=ResponseModel)
async def book_consultation(
    consultation_request: ConsultationRequest,
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Book a new consultation with an astrologer."""
    try:
        # Check user's subscription limits
        if not current_user.has_premium_features() and not current_user.get_tier_limits()["consultations_per_month"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Consultations require a premium subscription"
            )
        
        consultation_service = ConsultationService(db)
        consultation = await consultation_service.book_consultation(
            user_id=current_user.user_id,
            consultation_request=consultation_request
        )
        
        return ResponseModel(
            success=True,
            message="Consultation booked successfully",
            data={
                "consultation_id": consultation.consultation_id,
                "status_id": consultation.status_id,
                "status_name": consultation.status_name,
                "scheduled_at": consultation.scheduled_at,
                "total_amount": consultation.total_amount,
                "video_room_id": consultation.video_room_id,
                "ai_suggested_questions": consultation.ai_generated_questions
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to book consultation",
            error=str(e),
            user_id=str(current_user.user_id),
            astrologer_id=str(consultation_request.astrologer_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Booking failed: {str(e)}"
        )


@router.get("/my-consultations", response_model=ResponseModel)
async def get_my_consultations(
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(default=None, description="Filter by status"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
) -> ResponseModel:
    """Get consultations for the current user."""
    try:
        # Resolve status filter string to enum
        status_enum = ConsultationStatus.lookup(status_filter) if status_filter else None

        consultation_service = ConsultationService(db)
        consultations = await consultation_service.get_user_consultations(
            user_id=current_user.user_id,
            status_filter=status_enum,
            limit=limit,
            offset=offset
        )
        
        consultation_list = []
        for consultation in consultations:
            consultation_list.append(ConsultationResponse(
                consultation_id=consultation.consultation_id,
                user_id=consultation.user_id,
                astrologer_id=consultation.astrologer_id,
                chart_id=consultation.chart_id,
                consultation_type_id=consultation.consultation_type_id,
                consultation_type_name=consultation.consultation_type_name,
                status_id=consultation.status_id,
                status_name=consultation.status_name,
                user_questions=consultation.user_questions,
                focus_areas=consultation.focus_areas,
                scheduled_at=consultation.scheduled_at,
                duration_minutes=consultation.duration_minutes,
                total_amount=consultation.total_amount,
                currency=consultation.currency,
                payment_status_id=consultation.payment_status_id,
                payment_status_name=consultation.payment_status_name,
                ai_summary=consultation.ai_summary,
                created_at=consultation.created_at,
                completed_at=consultation.completed_at
            ))

        return ResponseModel(
            success=True,
            message=f"Retrieved {len(consultation_list)} consultations",
            data={
                "consultations": consultation_list,
                "total": len(consultation_list),
                "limit": limit,
                "offset": offset
            }
        )

    except Exception as e:
        logger.error(
            "Failed to get user consultations",
            error=str(e),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve consultations: {str(e)}"
        )


@router.get("/{consultation_id}", response_model=ResponseModel)
async def get_consultation_details(
    consultation_id: UUID,
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Get detailed consultation information."""
    try:
        consultation_service = ConsultationService(db)
        consultation = await consultation_service._get_consultation(consultation_id)
        
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        # Check access permissions
        if consultation.user_id != current_user.user_id:
            # Check if user is the astrologer
            from josi.models.astrologer_model import Astrologer
            astrologer_result = await db.execute(
                select(Astrologer).where(
                    Astrologer.user_id == current_user.user_id,
                    Astrologer.astrologer_id == consultation.astrologer_id,
                    Astrologer.is_deleted == False
                )
            )
            if not astrologer_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        # Get consultation messages
        from josi.models.consultation_model import ConsultationMessage
        messages_result = await db.execute(
            select(ConsultationMessage).where(
                ConsultationMessage.consultation_id == consultation_id,
                ConsultationMessage.is_deleted == False
            ).order_by(ConsultationMessage.created_at.asc())
        )
        messages = messages_result.scalars().all()
        
        message_list = []
        for message in messages:
            message_list.append(MessageResponse(
                message_id=message.message_id,
                consultation_id=message.consultation_id,
                sender_id=message.sender_id,
                message_type=message.message_type,
                content=message.content,
                attachment_url=message.attachment_url,
                is_read=message.is_read,
                created_at=message.created_at
            ))
        
        return ResponseModel(
            success=True,
            message="Consultation details retrieved",
            data={
                "consultation": ConsultationResponse(
                    consultation_id=consultation.consultation_id,
                    user_id=consultation.user_id,
                    astrologer_id=consultation.astrologer_id,
                    chart_id=consultation.chart_id,
                    consultation_type_id=consultation.consultation_type_id,
                    consultation_type_name=consultation.consultation_type_name,
                    status_id=consultation.status_id,
                    status_name=consultation.status_name,
                    user_questions=consultation.user_questions,
                    focus_areas=consultation.focus_areas,
                    scheduled_at=consultation.scheduled_at,
                    duration_minutes=consultation.duration_minutes,
                    total_amount=consultation.total_amount,
                    currency=consultation.currency,
                    payment_status_id=consultation.payment_status_id,
                    payment_status_name=consultation.payment_status_name,
                    ai_summary=consultation.ai_summary,
                    created_at=consultation.created_at,
                    completed_at=consultation.completed_at
                ),
                "messages": message_list,
                "interpretation": consultation.interpretation,
                "recommendations": consultation.recommendations,
                "video_room_id": consultation.video_room_id,
                "ai_key_points": consultation.ai_key_points
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get consultation details",
            error=str(e),
            consultation_id=str(consultation_id),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve consultation: {str(e)}"
        )


@router.post("/{consultation_id}/respond", response_model=ResponseModel)
async def respond_to_consultation(
    consultation_id: UUID,
    response: AstrologerResponse,
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Submit astrologer's response to a consultation."""
    try:
        # Verify user is an astrologer
        from josi.models.astrologer_model import Astrologer
        astrologer_result = await db.execute(
            select(Astrologer).where(
                Astrologer.user_id == current_user.user_id,
                Astrologer.is_deleted == False
            )
        )
        astrologer = astrologer_result.scalar_one_or_none()
        
        if not astrologer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only verified astrologers can respond to consultations"
            )
        
        consultation_service = ConsultationService(db)
        consultation = await consultation_service.process_astrologer_response(
            consultation_id=consultation_id,
            astrologer_id=astrologer.astrologer_id,
            response=response
        )
        
        return ResponseModel(
            success=True,
            message="Response submitted successfully",
            data={
                "consultation_id": consultation.consultation_id,
                "status_id": consultation.status_id,
                "status_name": consultation.status_name,
                "completed_at": consultation.completed_at
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to submit astrologer response",
            error=str(e),
            consultation_id=str(consultation_id),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Response submission failed: {str(e)}"
        )


@router.post("/{consultation_id}/messages", response_model=ResponseModel)
async def send_message(
    consultation_id: UUID,
    message_data: MessageCreate,
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Send a message in a consultation."""
    try:
        consultation_service = ConsultationService(db)
        message = await consultation_service.send_message(
            consultation_id=consultation_id,
            sender_id=current_user.user_id,
            content=message_data.content,
            message_type=message_data.message_type,
            attachment_url=message_data.attachment_url
        )
        
        return ResponseModel(
            success=True,
            message="Message sent successfully",
            data={
                "message_id": message.message_id,
                "created_at": message.created_at
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to send message",
            error=str(e),
            consultation_id=str(consultation_id),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Message sending failed: {str(e)}"
        )


@router.delete("/{consultation_id}/cancel", response_model=ResponseModel)
async def cancel_consultation(
    consultation_id: UUID,
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db),
    reason: Optional[str] = Query(default=None)
) -> ResponseModel:
    """Cancel a consultation."""
    try:
        consultation_service = ConsultationService(db)
        success = await consultation_service.cancel_consultation(
            consultation_id=consultation_id,
            user_id=current_user.user_id,
            reason=reason
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consultation cannot be cancelled"
            )
        
        return ResponseModel(
            success=True,
            message="Consultation cancelled successfully",
            data={"consultation_id": consultation_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to cancel consultation",
            error=str(e),
            consultation_id=str(consultation_id),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cancellation failed: {str(e)}"
        )


@router.get("/types", response_model=ResponseModel)
async def get_consultation_types() -> ResponseModel:
    """Get available consultation types."""
    types = []
    for consult_type in ConsultationType:
        types.append({
            "value": consult_type.id,
            "name": consult_type.description,
            "description": {
                ConsultationType.VIDEO: "Live video consultation with screen sharing",
                ConsultationType.CHAT: "Real-time text-based consultation",
                ConsultationType.EMAIL: "Detailed written consultation via email",
                ConsultationType.VOICE: "Voice-only consultation via phone"
            }.get(consult_type, "")
        })
    
    return ResponseModel(
        success=True,
        message="Consultation types retrieved",
        data={"types": types}
    )


@router.get("/astrologer/pending", response_model=ResponseModel)
async def get_pending_consultations(
    current_user: CurrentUser = Depends(resolve_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
) -> ResponseModel:
    """Get pending consultations for the current astrologer."""
    try:
        # Verify user is an astrologer
        from josi.models.astrologer_model import Astrologer
        astrologer_result = await db.execute(
            select(Astrologer).where(
                Astrologer.user_id == current_user.user_id,
                Astrologer.is_deleted == False
            )
        )
        astrologer = astrologer_result.scalar_one_or_none()
        
        if not astrologer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only astrologers can access this endpoint"
            )
        
        consultation_service = ConsultationService(db)
        consultations = await consultation_service.get_astrologer_consultations(
            astrologer_id=astrologer.astrologer_id,
            status_filter=ConsultationStatus.SCHEDULED,
            limit=limit,
            offset=offset
        )

        consultation_list = []
        for consultation in consultations:
            consultation_list.append(ConsultationResponse(
                consultation_id=consultation.consultation_id,
                user_id=consultation.user_id,
                astrologer_id=consultation.astrologer_id,
                chart_id=consultation.chart_id,
                consultation_type_id=consultation.consultation_type_id,
                consultation_type_name=consultation.consultation_type_name,
                status_id=consultation.status_id,
                status_name=consultation.status_name,
                user_questions=consultation.user_questions,
                focus_areas=consultation.focus_areas,
                scheduled_at=consultation.scheduled_at,
                duration_minutes=consultation.duration_minutes,
                total_amount=consultation.total_amount,
                currency=consultation.currency,
                payment_status_id=consultation.payment_status_id,
                payment_status_name=consultation.payment_status_name,
                ai_summary=consultation.ai_summary,
                created_at=consultation.created_at,
                completed_at=consultation.completed_at
            ))
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(consultation_list)} pending consultations",
            data={
                "consultations": consultation_list,
                "total": len(consultation_list),
                "limit": limit,
                "offset": offset
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get pending consultations",
            error=str(e),
            user_id=str(current_user.user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve consultations: {str(e)}"
        )