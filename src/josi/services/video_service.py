"""
Video consultation service using Twilio Video API.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import secrets

from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
import structlog

from josi.core.config import settings

logger = structlog.get_logger(__name__)


class VideoConsultationService:
    """Handle video consultations using Twilio Video."""
    
    def __init__(self):
        if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_api_key]):
            logger.warning("Twilio credentials not configured - video features will be disabled")
            self.client = None
            self.api_key_sid = None
            self.api_key_secret = None
        else:
            self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            self.api_key_sid = settings.twilio_api_key
            self.api_key_secret = settings.twilio_api_secret
    
    async def create_video_room(
        self, 
        consultation_id: str,
        duration_minutes: int = 60,
        enable_recording: bool = True
    ) -> Dict[str, str]:
        """Create a Twilio video room for consultation."""
        if not self.client:
            raise ValueError("Twilio not configured")
        
        try:
            room_name = f"consultation_{consultation_id}"
            
            # Create the video room
            room = self.client.video.rooms.create(
                unique_name=room_name,
                type='group',  # Supports up to 50 participants
                max_participants=2,  # Just user and astrologer
                record_participants_on_connect=enable_recording,
                status_callback=f"{settings.base_url}/api/v1/video/webhook",
                status_callback_method='POST'
            )
            
            logger.info(
                "Video room created",
                room_sid=room.sid,
                room_name=room_name,
                consultation_id=consultation_id
            )
            
            return {
                "room_sid": room.sid,
                "room_name": room_name,
                "status": room.status,
                "created_at": room.date_created.isoformat() if room.date_created else None
            }
            
        except Exception as e:
            logger.error(
                "Failed to create video room",
                error=str(e),
                consultation_id=consultation_id
            )
            raise
    
    def generate_access_token(
        self, 
        user_id: str, 
        room_name: str,
        user_role: str = "participant",
        expires_in_hours: int = 2
    ) -> str:
        """Generate access token for video room."""
        if not self.api_key_sid:
            raise ValueError("Twilio API key not configured")
        
        try:
            # Create access token
            token = AccessToken(
                settings.twilio_account_sid,
                self.api_key_sid,
                self.api_key_secret,
                identity=user_id,
                ttl=timedelta(hours=expires_in_hours)
            )
            
            # Add video grant
            video_grant = VideoGrant(room=room_name)
            token.add_grant(video_grant)
            
            access_token = token.to_jwt()
            
            logger.info(
                "Video access token generated",
                user_id=user_id,
                room_name=room_name,
                expires_in_hours=expires_in_hours
            )
            
            return access_token
            
        except Exception as e:
            logger.error(
                "Failed to generate access token",
                error=str(e),
                user_id=user_id,
                room_name=room_name
            )
            raise
    
    async def get_room_status(self, room_sid: str) -> Dict:
        """Get current status of a video room."""
        if not self.client:
            raise ValueError("Twilio not configured")
        
        try:
            room = self.client.video.rooms(room_sid).fetch()
            
            # Get participants
            participants = []
            for participant in self.client.video.rooms(room_sid).participants.list():
                participants.append({
                    "sid": participant.sid,
                    "identity": participant.identity,
                    "status": participant.status,
                    "start_time": participant.start_time.isoformat() if participant.start_time else None,
                    "end_time": participant.end_time.isoformat() if participant.end_time else None
                })
            
            return {
                "sid": room.sid,
                "unique_name": room.unique_name,
                "status": room.status,
                "type": room.type,
                "max_participants": room.max_participants,
                "participants": participants,
                "duration": room.duration,
                "created_at": room.date_created.isoformat() if room.date_created else None,
                "ended_at": room.end_time.isoformat() if room.end_time else None
            }
            
        except Exception as e:
            logger.error(
                "Failed to get room status",
                error=str(e),
                room_sid=room_sid
            )
            raise
    
    async def end_room(self, room_sid: str) -> bool:
        """End a video room."""
        if not self.client:
            raise ValueError("Twilio not configured")
        
        try:
            room = self.client.video.rooms(room_sid).update(status='completed')
            
            logger.info(
                "Video room ended",
                room_sid=room_sid,
                status=room.status
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to end video room",
                error=str(e),
                room_sid=room_sid
            )
            return False
    
    async def get_recordings(self, room_sid: str) -> List[Dict]:
        """Get recordings for a room."""
        if not self.client:
            raise ValueError("Twilio not configured")
        
        try:
            recordings = []
            for recording in self.client.video.recordings.list(room_sid=room_sid):
                recordings.append({
                    "sid": recording.sid,
                    "room_sid": recording.room_sid,
                    "status": recording.status,
                    "source_sid": recording.source_sid,
                    "size": recording.size,
                    "duration": recording.duration,
                    "container_format": recording.container_format,
                    "codec": recording.codec,
                    "grouping_sids": recording.grouping_sids,
                    "created_at": recording.date_created.isoformat() if recording.date_created else None,
                    "media_url": f"https://video.twilio.com/v1/Recordings/{recording.sid}/Media"
                })
            
            return recordings
            
        except Exception as e:
            logger.error(
                "Failed to get recordings",
                error=str(e),
                room_sid=room_sid
            )
            return []
    
    async def delete_recording(self, recording_sid: str) -> bool:
        """Delete a recording."""
        if not self.client:
            raise ValueError("Twilio not configured")
        
        try:
            self.client.video.recordings(recording_sid).delete()
            
            logger.info(
                "Video recording deleted",
                recording_sid=recording_sid
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to delete recording",
                error=str(e),
                recording_sid=recording_sid
            )
            return False
    
    def create_room_for_consultation(
        self,
        consultation_id: str,
        user_id: str,
        astrologer_id: str,
        duration_minutes: int = 60
    ) -> Dict[str, str]:
        """Create video room and generate tokens for consultation."""
        if not self.client:
            return {
                "error": "Video service not available",
                "user_token": None,
                "astrologer_token": None,
                "room_sid": None
            }
        
        try:
            # Create room
            room_info = self.create_video_room(consultation_id, duration_minutes)
            room_name = room_info["room_name"]
            
            # Generate tokens
            user_token = self.generate_access_token(
                user_id=f"user_{user_id}",
                room_name=room_name,
                user_role="participant"
            )
            
            astrologer_token = self.generate_access_token(
                user_id=f"astrologer_{astrologer_id}",
                room_name=room_name,
                user_role="moderator"
            )
            
            return {
                "room_sid": room_info["room_sid"],
                "room_name": room_name,
                "user_token": user_token,
                "astrologer_token": astrologer_token,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(
                "Failed to create consultation room",
                error=str(e),
                consultation_id=consultation_id
            )
            return {
                "error": str(e),
                "user_token": None,
                "astrologer_token": None,
                "room_sid": None
            }
    
    async def handle_webhook(self, webhook_data: Dict) -> Dict:
        """Handle Twilio webhook events."""
        try:
            event_type = webhook_data.get("StatusCallbackEvent")
            room_sid = webhook_data.get("RoomSid")
            room_name = webhook_data.get("RoomName")
            
            logger.info(
                "Video webhook received",
                event_type=event_type,
                room_sid=room_sid,
                room_name=room_name
            )
            
            # Handle different events
            if event_type == "room-created":
                return {"status": "room_created_acknowledged"}
            
            elif event_type == "room-ended":
                # Room has ended, potentially trigger cleanup
                return {"status": "room_ended_acknowledged"}
            
            elif event_type == "participant-connected":
                participant_identity = webhook_data.get("ParticipantIdentity")
                logger.info(
                    "Participant connected",
                    room_sid=room_sid,
                    participant=participant_identity
                )
                return {"status": "participant_connected_acknowledged"}
            
            elif event_type == "participant-disconnected":
                participant_identity = webhook_data.get("ParticipantIdentity")
                logger.info(
                    "Participant disconnected",
                    room_sid=room_sid,
                    participant=participant_identity
                )
                return {"status": "participant_disconnected_acknowledged"}
            
            elif event_type == "recording-started":
                logger.info("Recording started", room_sid=room_sid)
                return {"status": "recording_started_acknowledged"}
            
            elif event_type == "recording-completed":
                recording_sid = webhook_data.get("RecordingSid")
                logger.info(
                    "Recording completed",
                    room_sid=room_sid,
                    recording_sid=recording_sid
                )
                return {"status": "recording_completed_acknowledged"}
            
            else:
                logger.warning(
                    "Unknown webhook event",
                    event_type=event_type,
                    data=webhook_data
                )
                return {"status": "unknown_event"}
        
        except Exception as e:
            logger.error(
                "Failed to handle video webhook",
                error=str(e),
                webhook_data=webhook_data
            )
            return {"status": "error", "error": str(e)}