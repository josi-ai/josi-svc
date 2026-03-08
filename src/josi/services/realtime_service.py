"""
Real-time WebSocket service for live updates and notifications.
"""
from typing import Dict, Set, List, Optional, Any
import asyncio
import json
from datetime import datetime
import uuid

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from josi.auth.providers import get_auth_provider
from josi.models.user_model import User

logger = structlog.get_logger(__name__)


class RealtimeConnectionManager:
    """Manage WebSocket connections for real-time features."""
    
    def __init__(self):
        # Active connections: user_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # User subscriptions: user_id -> set of subscription topics
        self.user_subscriptions: Dict[str, Set[str]] = {}
        
        # Room-based connections (for consultations)
        self.room_connections: Dict[str, Set[WebSocket]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        user_id: str,
        connection_type: str = "general"
    ):
        """Accept a new WebSocket connection."""
        try:
            await websocket.accept()
            
            # Add to active connections
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            
            # Store connection metadata
            self.connection_metadata[websocket] = {
                "user_id": user_id,
                "connection_type": connection_type,
                "connected_at": datetime.utcnow(),
                "last_ping": datetime.utcnow()
            }
            
            # Send initial connection confirmation
            await self.send_to_connection(websocket, {
                "type": "connection_established",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "connection_id": str(uuid.uuid4())
            })
            
            # Send any queued messages or initial data
            await self.send_initial_data(websocket, user_id)
            
            logger.info(
                "WebSocket connection established",
                user_id=user_id,
                connection_type=connection_type
            )
            
        except Exception as e:
            logger.error(
                "Failed to establish WebSocket connection",
                error=str(e),
                user_id=user_id
            )
            await websocket.close()
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket disconnection."""
        try:
            # Remove from active connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from room connections
            for room_id, connections in self.room_connections.items():
                connections.discard(websocket)
            
            # Clean up metadata
            metadata = self.connection_metadata.pop(websocket, {})
            
            logger.info(
                "WebSocket connection closed",
                user_id=user_id,
                connection_duration=str(datetime.utcnow() - metadata.get("connected_at", datetime.utcnow()))
            )
            
        except Exception as e:
            logger.error(
                "Error during WebSocket disconnection",
                error=str(e),
                user_id=user_id
            )
    
    async def subscribe_to_transits(self, user_id: str, chart_id: str):
        """Subscribe user to transit updates for a specific chart."""
        subscription_key = f"transits:{chart_id}"
        
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        
        self.user_subscriptions[user_id].add(subscription_key)
        
        # Notify user of subscription
        await self.send_to_user(user_id, {
            "type": "subscription_confirmed",
            "topic": "transits",
            "chart_id": chart_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(
            "User subscribed to transits",
            user_id=user_id,
            chart_id=chart_id
        )
    
    async def subscribe_to_consultation(self, user_id: str, consultation_id: str):
        """Subscribe user to consultation updates."""
        subscription_key = f"consultation:{consultation_id}"
        
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        
        self.user_subscriptions[user_id].add(subscription_key)
        
        # Also join consultation room
        room_id = f"consultation:{consultation_id}"
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        
        # Add all user's connections to the room
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                self.room_connections[room_id].add(websocket)
        
        logger.info(
            "User subscribed to consultation",
            user_id=user_id,
            consultation_id=consultation_id
        )
    
    async def join_consultation_room(self, websocket: WebSocket, consultation_id: str):
        """Join a specific consultation room."""
        room_id = f"consultation:{consultation_id}"
        
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        
        self.room_connections[room_id].add(websocket)
        
        # Notify room of new participant
        await self.broadcast_to_room(room_id, {
            "type": "participant_joined",
            "consultation_id": consultation_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude=websocket)
    
    async def leave_consultation_room(self, websocket: WebSocket, consultation_id: str):
        """Leave a consultation room."""
        room_id = f"consultation:{consultation_id}"
        
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(websocket)
            
            # Notify room of participant leaving
            await self.broadcast_to_room(room_id, {
                "type": "participant_left",
                "consultation_id": consultation_id,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def broadcast_transit_update(self, chart_id: str, transit_data: Dict):
        """Broadcast transit updates to subscribed users."""
        subscription_key = f"transits:{chart_id}"
        
        message = {
            "type": "transit_update",
            "chart_id": chart_id,
            "data": transit_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all subscribed users
        for user_id, subscriptions in self.user_subscriptions.items():
            if subscription_key in subscriptions:
                await self.send_to_user(user_id, message)
        
        logger.info(
            "Transit update broadcasted",
            chart_id=chart_id,
            subscriber_count=sum(
                1 for subs in self.user_subscriptions.values() 
                if subscription_key in subs
            )
        )
    
    async def broadcast_consultation_update(
        self, 
        consultation_id: str, 
        update_data: Dict,
        exclude_user: Optional[str] = None
    ):
        """Broadcast consultation updates to participants."""
        room_id = f"consultation:{consultation_id}"
        
        message = {
            "type": "consultation_update",
            "consultation_id": consultation_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to room
        await self.broadcast_to_room(room_id, message)
        
        # Also send to subscribed users not in room
        subscription_key = f"consultation:{consultation_id}"
        for user_id, subscriptions in self.user_subscriptions.items():
            if subscription_key in subscriptions and user_id != exclude_user:
                await self.send_to_user(user_id, message)
    
    async def send_consultation_message(
        self,
        consultation_id: str,
        message_data: Dict,
        sender_id: str
    ):
        """Send a message to consultation participants."""
        room_id = f"consultation:{consultation_id}"
        
        message = {
            "type": "consultation_message",
            "consultation_id": consultation_id,
            "sender_id": sender_id,
            "data": message_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_room(room_id, message)
    
    async def send_notification(self, user_id: str, notification: Dict):
        """Send a notification to a specific user."""
        message = {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_to_user(user_id, message)
    
    async def send_to_user(self, user_id: str, message: Dict):
        """Send message to all connections of a specific user."""
        if user_id in self.active_connections:
            disconnected_connections = set()
            
            for websocket in self.active_connections[user_id]:
                try:
                    await self.send_to_connection(websocket, message)
                except Exception as e:
                    logger.warning(
                        "Failed to send message to connection",
                        error=str(e),
                        user_id=user_id
                    )
                    disconnected_connections.add(websocket)
            
            # Clean up disconnected connections
            for websocket in disconnected_connections:
                await self.disconnect(websocket, user_id)
    
    async def send_to_connection(self, websocket: WebSocket, message: Dict):
        """Send message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
            
            # Update last ping time
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["last_ping"] = datetime.utcnow()
                
        except Exception as e:
            logger.warning(
                "Failed to send WebSocket message",
                error=str(e),
                message_type=message.get("type")
            )
            raise
    
    async def broadcast_to_room(
        self, 
        room_id: str, 
        message: Dict, 
        exclude: Optional[WebSocket] = None
    ):
        """Broadcast message to all connections in a room."""
        if room_id not in self.room_connections:
            return
        
        disconnected_connections = set()
        
        for websocket in self.room_connections[room_id]:
            if websocket == exclude:
                continue
                
            try:
                await self.send_to_connection(websocket, message)
            except Exception as e:
                logger.warning(
                    "Failed to send message to room connection",
                    error=str(e),
                    room_id=room_id
                )
                disconnected_connections.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected_connections:
            self.room_connections[room_id].discard(websocket)
    
    async def send_initial_data(self, websocket: WebSocket, user_id: str):
        """Send initial data when user connects."""
        try:
            # Send user's active subscriptions
            subscriptions = self.user_subscriptions.get(user_id, set())
            
            await self.send_to_connection(websocket, {
                "type": "initial_data",
                "subscriptions": list(subscriptions),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.warning(
                "Failed to send initial data",
                error=str(e),
                user_id=user_id
            )
    
    async def handle_ping(self, websocket: WebSocket):
        """Handle ping/pong for connection health."""
        try:
            await self.send_to_connection(websocket, {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.warning("Failed to handle ping", error=str(e))
    
    async def cleanup_stale_connections(self):
        """Periodic cleanup of stale connections."""
        stale_connections = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        for websocket, metadata in self.connection_metadata.items():
            if metadata.get("last_ping", datetime.utcnow()) < cutoff_time:
                stale_connections.append((websocket, metadata["user_id"]))
        
        for websocket, user_id in stale_connections:
            logger.info("Cleaning up stale connection", user_id=user_id)
            await self.disconnect(websocket, user_id)
    
    def get_connection_stats(self) -> Dict:
        """Get current connection statistics."""
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        
        return {
            "total_connections": total_connections,
            "active_users": len(self.active_connections),
            "total_subscriptions": sum(len(subs) for subs in self.user_subscriptions.values()),
            "active_rooms": len(self.room_connections),
            "room_participants": sum(len(connections) for connections in self.room_connections.values())
        }


# Global connection manager instance
realtime_manager = RealtimeConnectionManager()


async def verify_websocket_token(token: str, db: AsyncSession) -> Optional[User]:
    """Verify WebSocket authentication token via auth provider JWT."""
    try:
        from sqlalchemy import select, and_
        provider = get_auth_provider()
        claims = provider.validate_jwt(token)
        result = await db.execute(
            select(User).where(
                and_(User.auth_provider_id == claims["sub"], User.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.warning("WebSocket token verification failed", error=str(e))
        return None


async def handle_websocket_message(user_id: str, message_data: Dict):
    """Handle incoming WebSocket messages."""
    try:
        message_type = message_data.get("type")
        
        if message_type == "ping":
            # Ping will be handled by the endpoint
            pass
        
        elif message_type == "subscribe_transits":
            chart_id = message_data.get("chart_id")
            if chart_id:
                await realtime_manager.subscribe_to_transits(user_id, chart_id)
        
        elif message_type == "subscribe_consultation":
            consultation_id = message_data.get("consultation_id")
            if consultation_id:
                await realtime_manager.subscribe_to_consultation(user_id, consultation_id)
        
        elif message_type == "join_consultation_room":
            consultation_id = message_data.get("consultation_id")
            # This would need the websocket instance, handled at endpoint level
            pass
        
        else:
            logger.warning(
                "Unknown WebSocket message type",
                message_type=message_type,
                user_id=user_id
            )
    
    except Exception as e:
        logger.error(
            "Failed to handle WebSocket message",
            error=str(e),
            user_id=user_id,
            message_data=message_data
        )


# Background task for cleanup
async def websocket_cleanup_task():
    """Background task to clean up stale connections."""
    while True:
        try:
            await realtime_manager.cleanup_stale_connections()
            await asyncio.sleep(60)  # Run every minute
        except Exception as e:
            logger.error("WebSocket cleanup task error", error=str(e))
            await asyncio.sleep(60)