"""
Consultation service for booking and managing astrologer consultations.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError

from josi.models.consultation_model import (
    Consultation, 
    ConsultationMessage,
    ConsultationRequest,
    ConsultationUpdate,
    AstrologerResponse,
    ConsultationStatus,
    PaymentStatus
)
from josi.models.astrologer_model import Astrologer
from josi.models.user_model import User
from josi.services.video_service import VideoConsultationService
from josi.services.ai.interpretation_service import AIInterpretationService
from josi.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class ConsultationService:
    """Handle consultation booking and management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.video_service = VideoConsultationService()
        self.ai_service = AIInterpretationService()
    
    async def book_consultation(
        self,
        user_id: UUID,
        consultation_request: ConsultationRequest
    ) -> Consultation:
        """Book a new consultation with an astrologer."""
        try:
            # Validate astrologer exists and is available
            astrologer = await self._get_astrologer(consultation_request.astrologer_id)
            if not astrologer:
                raise ValueError("Astrologer not found")
            
            if not astrologer.is_active or astrologer.verification_status != "verified":
                raise ValueError("Astrologer is not available")
            
            # Check astrologer's availability
            if consultation_request.preferred_times:
                available_slot = await self._find_available_slot(
                    astrologer.astrologer_id,
                    consultation_request.preferred_times
                )
                if not available_slot:
                    raise ValueError("No available slots found")
            else:
                available_slot = None
            
            # Calculate total amount
            total_amount = self._calculate_consultation_cost(
                astrologer.hourly_rate,
                consultation_request.duration_minutes
            )
            
            # Create consultation record
            consultation_data = {
                "user_id": user_id,
                "astrologer_id": consultation_request.astrologer_id,
                "chart_id": consultation_request.chart_id,
                "type": consultation_request.type,
                "user_questions": consultation_request.user_questions,
                "focus_areas": consultation_request.focus_areas,
                "special_requests": consultation_request.special_requests,
                "duration_minutes": consultation_request.duration_minutes,
                "timezone": consultation_request.timezone,
                "total_amount": total_amount,
                "currency": astrologer.currency,
                "scheduled_at": available_slot
            }
            
            consultation = Consultation(**consultation_data)
            self.db.add(consultation)
            await self.db.flush()  # Get the ID
            
            # Create video room if it's a video consultation
            if consultation_request.type == "video" and available_slot:
                try:
                    video_details = self.video_service.create_room_for_consultation(
                        str(consultation.consultation_id),
                        str(user_id),
                        str(consultation_request.astrologer_id),
                        consultation_request.duration_minutes
                    )
                    
                    if video_details.get("room_sid"):
                        consultation.video_room_id = video_details["room_sid"]
                        consultation.video_access_token = video_details.get("user_token")
                
                except Exception as e:
                    logger.warning(
                        "Failed to create video room",
                        error=str(e),
                        consultation_id=str(consultation.consultation_id)
                    )
            
            # Generate AI-suggested questions based on chart
            try:
                ai_questions = await self._generate_ai_questions(consultation_request.chart_id)
                consultation.ai_generated_questions = ai_questions
            except Exception as e:
                logger.warning(
                    "Failed to generate AI questions",
                    error=str(e),
                    consultation_id=str(consultation.consultation_id)
                )
            
            await self.db.commit()
            await self.db.refresh(consultation)
            
            # TODO: Send notification to astrologer
            # TODO: Create payment intent
            
            logger.info(
                "Consultation booked",
                consultation_id=str(consultation.consultation_id),
                user_id=str(user_id),
                astrologer_id=str(consultation_request.astrologer_id),
                type=consultation_request.type.value
            )
            
            return consultation
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to book consultation",
                error=str(e),
                user_id=str(user_id),
                astrologer_id=str(consultation_request.astrologer_id)
            )
            raise
    
    async def process_astrologer_response(
        self,
        consultation_id: UUID,
        astrologer_id: UUID,
        response: AstrologerResponse
    ) -> Consultation:
        """Process astrologer's response to a consultation."""
        try:
            # Get consultation
            consultation = await self._get_consultation(consultation_id)
            if not consultation:
                raise ValueError("Consultation not found")
            
            if consultation.astrologer_id != astrologer_id:
                raise ValueError("Unauthorized to respond to this consultation")
            
            if consultation.status != ConsultationStatus.SCHEDULED:
                raise ValueError("Consultation is not in a state to receive responses")
            
            # Update consultation with astrologer's response
            consultation.interpretation = response.interpretation
            consultation.recommendations = response.recommendations
            consultation.follow_up_suggestions = response.follow_up_suggestions
            consultation.astrologer_notes = response.astrologer_notes
            consultation.status = ConsultationStatus.COMPLETED
            consultation.completed_at = datetime.utcnow()
            
            # Generate AI summary of the consultation
            try:
                ai_summary = await self._generate_consultation_summary(consultation)
                consultation.ai_summary = ai_summary["summary"]
                consultation.ai_key_points = ai_summary["key_points"]
            except Exception as e:
                logger.warning(
                    "Failed to generate AI summary",
                    error=str(e),
                    consultation_id=str(consultation_id)
                )
            
            # Update astrologer stats
            await self._update_astrologer_stats(astrologer_id)
            
            await self.db.commit()
            await self.db.refresh(consultation)
            
            # TODO: Send notification to user
            # TODO: Release payment to astrologer
            
            logger.info(
                "Astrologer response processed",
                consultation_id=str(consultation_id),
                astrologer_id=str(astrologer_id)
            )
            
            return consultation
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to process astrologer response",
                error=str(e),
                consultation_id=str(consultation_id),
                astrologer_id=str(astrologer_id)
            )
            raise
    
    async def send_message(
        self,
        consultation_id: UUID,
        sender_id: UUID,
        content: str,
        message_type: str = "text",
        attachment_url: Optional[str] = None
    ) -> ConsultationMessage:
        """Send a message in a consultation."""
        try:
            # Verify user has access to this consultation
            consultation = await self._get_consultation(consultation_id)
            if not consultation:
                raise ValueError("Consultation not found")
            
            if sender_id not in [consultation.user_id, consultation.astrologer_id]:
                raise ValueError("Unauthorized to send message to this consultation")
            
            message = ConsultationMessage(
                consultation_id=consultation_id,
                sender_id=sender_id,
                content=content,
                message_type=message_type,
                attachment_url=attachment_url
            )
            
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)
            
            # TODO: Send real-time notification via WebSocket
            
            return message
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to send message",
                error=str(e),
                consultation_id=str(consultation_id),
                sender_id=str(sender_id)
            )
            raise
    
    async def get_user_consultations(
        self,
        user_id: UUID,
        status_filter: Optional[ConsultationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Consultation]:
        """Get consultations for a user."""
        query = select(Consultation).where(
            Consultation.user_id == user_id,
            Consultation.is_deleted == False
        )
        
        if status_filter:
            query = query.where(Consultation.status == status_filter)
        
        query = query.order_by(Consultation.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_astrologer_consultations(
        self,
        astrologer_id: UUID,
        status_filter: Optional[ConsultationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Consultation]:
        """Get consultations for an astrologer."""
        query = select(Consultation).where(
            Consultation.astrologer_id == astrologer_id,
            Consultation.is_deleted == False
        )
        
        if status_filter:
            query = query.where(Consultation.status == status_filter)
        
        query = query.order_by(Consultation.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def cancel_consultation(
        self,
        consultation_id: UUID,
        user_id: UUID,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel a consultation."""
        try:
            consultation = await self._get_consultation(consultation_id)
            if not consultation:
                raise ValueError("Consultation not found")
            
            if consultation.user_id != user_id:
                raise ValueError("Unauthorized to cancel this consultation")
            
            if not consultation.can_be_cancelled():
                raise ValueError("Consultation cannot be cancelled at this time")
            
            consultation.status = ConsultationStatus.CANCELLED
            consultation.updated_at = datetime.utcnow()
            
            # End video room if exists
            if consultation.video_room_id:
                try:
                    await self.video_service.end_room(consultation.video_room_id)
                except Exception as e:
                    logger.warning(
                        "Failed to end video room",
                        error=str(e),
                        room_id=consultation.video_room_id
                    )
            
            await self.db.commit()
            
            # TODO: Process refund
            # TODO: Send notifications
            
            logger.info(
                "Consultation cancelled",
                consultation_id=str(consultation_id),
                user_id=str(user_id)
            )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to cancel consultation",
                error=str(e),
                consultation_id=str(consultation_id),
                user_id=str(user_id)
            )
            return False
    
    # Helper methods
    
    async def _get_astrologer(self, astrologer_id: UUID) -> Optional[Astrologer]:
        """Get astrologer by ID."""
        result = await self.db.execute(
            select(Astrologer).where(
                Astrologer.astrologer_id == astrologer_id,
                Astrologer.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def _get_consultation(self, consultation_id: UUID) -> Optional[Consultation]:
        """Get consultation by ID."""
        result = await self.db.execute(
            select(Consultation).where(
                Consultation.consultation_id == consultation_id,
                Consultation.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def _find_available_slot(
        self,
        astrologer_id: UUID,
        preferred_times: List[datetime]
    ) -> Optional[datetime]:
        """Find an available time slot for the astrologer."""
        # TODO: Implement proper availability checking
        # For now, return the first preferred time if it's in the future
        for time_slot in preferred_times:
            if time_slot > datetime.utcnow():
                # Check if astrologer has any conflicts
                conflicts = await self.db.execute(
                    select(Consultation).where(
                        Consultation.astrologer_id == astrologer_id,
                        Consultation.scheduled_at.between(
                            time_slot - timedelta(hours=1),
                            time_slot + timedelta(hours=1)
                        ),
                        Consultation.status.in_([
                            ConsultationStatus.SCHEDULED,
                            ConsultationStatus.IN_PROGRESS
                        ])
                    )
                )
                
                if not conflicts.scalar_one_or_none():
                    return time_slot
        
        return None
    
    def _calculate_consultation_cost(self, hourly_rate: float, duration_minutes: int) -> float:
        """Calculate consultation cost."""
        hours = duration_minutes / 60
        return round(hourly_rate * hours, 2)
    
    async def _generate_ai_questions(self, chart_id: UUID) -> List[str]:
        """Generate AI-suggested questions for the consultation."""
        try:
            # Get chart data
            from josi.services.chart_service import ChartService
            chart_service = ChartService(self.db, organization_id=None)
            chart = await chart_service.get_chart(chart_id)
            
            if not chart:
                return []
            
            # Generate questions using AI
            questions = await self.ai_service.generate_neural_pathway_questions(
                chart_data=chart.chart_data,
                previous_responses=[],
                focus_area="consultation_preparation"
            )
            
            return [q.get("question", "") for q in questions[:5]]
            
        except Exception as e:
            logger.warning(
                "Failed to generate AI questions",
                error=str(e),
                chart_id=str(chart_id)
            )
            return []
    
    async def _generate_consultation_summary(self, consultation: Consultation) -> Dict:
        """Generate AI summary of consultation."""
        try:
            summary_prompt = f"""
            Summarize this astrological consultation:
            
            User Questions: {', '.join(consultation.user_questions)}
            Focus Areas: {', '.join(consultation.focus_areas)}
            Astrologer's Interpretation: {consultation.interpretation}
            Recommendations: {', '.join(consultation.recommendations or [])}
            
            Provide:
            1. A concise summary (2-3 sentences)
            2. Key insights (3-5 bullet points)
            """
            
            if self.ai_service.openai_client:
                response = await self.ai_service.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert at summarizing astrological consultations."},
                        {"role": "user", "content": summary_prompt}
                    ],
                    temperature=0.3
                )
                
                summary_text = response.choices[0].message.content
                
                # Simple parsing - in production, use structured output
                lines = summary_text.split('\n')
                summary = lines[0] if lines else "Consultation completed successfully."
                key_points = [line.strip('- ') for line in lines[1:] if line.strip().startswith('-')]
                
                return {
                    "summary": summary,
                    "key_points": key_points[:5]
                }
            
        except Exception as e:
            logger.warning(
                "Failed to generate consultation summary",
                error=str(e),
                consultation_id=str(consultation.consultation_id)
            )
        
        return {
            "summary": "Consultation completed successfully.",
            "key_points": ["Chart analysis provided", "Recommendations given"]
        }
    
    async def _update_astrologer_stats(self, astrologer_id: UUID):
        """Update astrologer performance statistics."""
        try:
            # Get astrologer
            astrologer = await self._get_astrologer(astrologer_id)
            if not astrologer:
                return
            
            # Count completed consultations
            completed_count = await self.db.execute(
                select(func.count(Consultation.consultation_id)).where(
                    Consultation.astrologer_id == astrologer_id,
                    Consultation.status == ConsultationStatus.COMPLETED,
                    Consultation.is_deleted == False
                )
            )
            
            total_completed = completed_count.scalar_one()
            
            # Update stats
            astrologer.total_consultations = total_completed
            astrologer.last_active = datetime.utcnow()
            
            await self.db.commit()
            
        except Exception as e:
            logger.warning(
                "Failed to update astrologer stats",
                error=str(e),
                astrologer_id=str(astrologer_id)
            )