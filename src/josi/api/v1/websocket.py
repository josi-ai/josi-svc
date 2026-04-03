"""
WebSocket endpoints for real-time features.
"""
from fastapi import WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
from datetime import datetime

from josi.db.async_db import get_async_db as get_db
from josi.services.realtime_service import (
    realtime_manager,
    verify_websocket_token,
    handle_websocket_message
)
import structlog

logger = structlog.get_logger(__name__)


async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...),
    connection_type: str = Query(default="general"),
    db: AsyncSession = Depends(get_db)
):
    """Main WebSocket endpoint for real-time communication."""
    
    # Verify authentication
    user = await verify_websocket_token(token, db)
    if not user or str(user.user_id) != user_id:
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    # Establish connection
    await realtime_manager.connect(websocket, user_id, connection_type)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue
            
            # Handle ping specifically
            if message_data.get("type") == "ping":
                await realtime_manager.handle_ping(websocket)
                continue
            
            # Handle other message types
            await handle_websocket_message(user_id, message_data)
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", user_id=user_id)
    
    except Exception as e:
        logger.error(
            "WebSocket error",
            error=str(e),
            user_id=user_id
        )
    
    finally:
        await realtime_manager.disconnect(websocket, user_id)


async def consultation_websocket_endpoint(
    websocket: WebSocket,
    consultation_id: str,
    user_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint specifically for consultation rooms."""
    
    # Verify authentication
    user = await verify_websocket_token(token, db)
    if not user or str(user.user_id) != user_id:
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    # Verify access to consultation
    from josi.services.consultation_service import ConsultationService
    consultation_service = ConsultationService(db)
    consultation = await consultation_service._get_consultation(consultation_id)
    
    if not consultation:
        await websocket.close(code=4004, reason="Consultation not found")
        return
    
    # Check if user has access (either the client or the astrologer)
    has_access = consultation.user_id == user.user_id
    
    if not has_access:
        # Check if user is the astrologer
        from josi.models.astrologer_model import Astrologer
        from sqlalchemy import select
        
        astrologer_result = await db.execute(
            select(Astrologer).where(
                Astrologer.user_id == user.user_id,
                Astrologer.astrologer_id == consultation.astrologer_id,
                Astrologer.is_deleted == False
            )
        )
        has_access = astrologer_result.scalar_one_or_none() is not None
    
    if not has_access:
        await websocket.close(code=4003, reason="Access denied")
        return
    
    # Establish connection
    await realtime_manager.connect(websocket, user_id, "consultation")
    await realtime_manager.join_consultation_room(websocket, consultation_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue
            
            message_type = message_data.get("type")
            
            if message_type == "ping":
                await realtime_manager.handle_ping(websocket)
            
            elif message_type == "consultation_message":
                # Send message to all participants
                await realtime_manager.send_consultation_message(
                    consultation_id=consultation_id,
                    message_data=message_data.get("data", {}),
                    sender_id=user_id
                )
                
                # Also store in database
                content = message_data.get("data", {}).get("content", "")
                if content:
                    await consultation_service.send_message(
                        consultation_id=consultation_id,
                        sender_id=user.user_id,
                        content=content,
                        message_type=message_data.get("data", {}).get("message_type", "text")
                    )
            
            elif message_type == "typing_indicator":
                # Broadcast typing indicator to other participants
                await realtime_manager.broadcast_to_room(
                    f"consultation:{consultation_id}",
                    {
                        "type": "typing_indicator",
                        "sender_id": user_id,
                        "is_typing": message_data.get("is_typing", False),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude=websocket
                )
            
            else:
                await handle_websocket_message(user_id, message_data)
    
    except WebSocketDisconnect:
        logger.info("Consultation WebSocket disconnected", user_id=user_id, consultation_id=consultation_id)
    
    except Exception as e:
        logger.error(
            "Consultation WebSocket error",
            error=str(e),
            user_id=user_id,
            consultation_id=consultation_id
        )
    
    finally:
        await realtime_manager.leave_consultation_room(websocket, consultation_id)
        await realtime_manager.disconnect(websocket, user_id)


async def video_webhook_endpoint(webhook_data: dict):
    """Handle Twilio video webhooks and broadcast updates."""
    try:
        room_name = webhook_data.get("RoomName", "")
        event_type = webhook_data.get("StatusCallbackEvent", "")
        
        # Extract consultation ID from room name
        if room_name.startswith("consultation_"):
            consultation_id = room_name.replace("consultation_", "")
            
            # Broadcast video event to consultation participants
            await realtime_manager.broadcast_consultation_update(
                consultation_id=consultation_id,
                update_data={
                    "video_event": event_type,
                    "room_status": webhook_data.get("RoomStatus"),
                    "participant_identity": webhook_data.get("ParticipantIdentity"),
                    "webhook_data": webhook_data
                }
            )
        
        return {"status": "acknowledged"}
    
    except Exception as e:
        logger.error("Failed to handle video webhook", error=str(e), webhook_data=webhook_data)
        return {"status": "error", "error": str(e)}