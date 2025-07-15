# Josi AI & Marketplace Implementation Plan

## Executive Summary

This plan outlines the implementation of AI-powered interpretations, human astrologer marketplace, real-time features, and user management capabilities on top of the existing Josi astrology calculation backend.

## Current State vs. Target State

### ✅ Already Implemented
- FastAPI backend with async/await
- Multiple astrology systems (Vedic, Western, Chinese, etc.)
- PostgreSQL with SQLModel
- GraphQL and REST APIs
- Docker containerization
- Redis caching
- OAuth2 foundation (Google, GitHub)
- Comprehensive test suite

### 🎯 New Features to Implement
1. **AI Integration** - GPT-4/Claude for personalized interpretations
2. **Astrologer Marketplace** - Connect users with human astrologers
3. **Real-time Features** - WebSockets, live updates, video calls
4. **User Management** - Full authentication, subscriptions, payments
5. **Advanced Astrology** - Muhurta, Pariharam, enhanced compatibility
6. **Frontend PWA** - React-based progressive web app
7. **Mobile Apps** - iOS/Android deployment

## Phase 1: Foundation (Weeks 1-4)

### 1.1 Enhanced User Management System

#### Database Models
```python
# src/josi/models/user_model.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID, uuid4
import enum

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    EXPLORER = "explorer"
    MYSTIC = "mystic"
    MASTER = "master"

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = Field(default=None)
    hashed_password: Optional[str] = Field(default=None)
    
    # Profile
    full_name: str
    avatar_url: Optional[str] = Field(default=None)
    date_of_birth: Optional[datetime] = Field(default=None)
    birth_location: Optional[Dict] = Field(default=None, sa_column=JSON)
    
    # Subscription
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE)
    subscription_end_date: Optional[datetime] = Field(default=None)
    stripe_customer_id: Optional[str] = Field(default=None)
    
    # Settings
    preferences: Dict = Field(default_factory=dict, sa_column=JSON)
    notification_settings: Dict = Field(default_factory=dict, sa_column=JSON)
    
    # OAuth
    oauth_providers: List[str] = Field(default_factory=list, sa_column=JSON)
    
    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    consultations: List["Consultation"] = Relationship(back_populates="user")
    saved_charts: List["SavedChart"] = Relationship(back_populates="user")
    quiz_responses: List["QuizResponse"] = Relationship(back_populates="user")
```

#### Authentication Service
```python
# src/josi/services/auth_service.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    
    async def register_user(self, user_data: UserCreate) -> User:
        # Check if user exists
        # Hash password
        # Create user with free tier
        # Send verification email
        pass
    
    async def login(self, email: str, password: str) -> Dict:
        # Verify credentials
        # Create tokens
        # Update last_login
        pass
```

### 1.2 AI Integration Layer

#### AI Service Architecture
```python
# src/josi/services/ai/interpretation_service.py
from openai import AsyncOpenAI
import anthropic
from typing import Dict, List, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class AIInterpretationService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.openai_api_key)
        self.anthropic = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.qdrant = QdrantClient(url=settings.qdrant_url)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    async def generate_interpretation(
        self,
        chart_data: Dict,
        question: str,
        user_context: Optional[Dict] = None,
        style: str = "balanced"  # balanced, psychological, spiritual, practical
    ) -> Dict:
        """Generate AI-powered chart interpretation"""
        
        # 1. Search similar charts in vector DB
        similar_interpretations = await self._search_similar_interpretations(
            chart_data, question
        )
        
        # 2. Build context-aware prompt
        prompt = self._build_interpretation_prompt(
            chart_data=chart_data,
            question=question,
            user_context=user_context,
            similar_interpretations=similar_interpretations,
            style=style
        )
        
        # 3. Generate interpretation
        if settings.ai_provider == "openai":
            response = await self._generate_openai_response(prompt)
        else:
            response = await self._generate_anthropic_response(prompt)
        
        # 4. Store in vector DB for future reference
        await self._store_interpretation(chart_data, question, response)
        
        return {
            "interpretation": response,
            "confidence": self._calculate_confidence(response, similar_interpretations),
            "sources": self._extract_sources(similar_interpretations),
            "follow_up_questions": await self._generate_follow_up_questions(
                chart_data, question, response
            )
        }
    
    async def generate_neural_pathway_questions(
        self,
        chart_data: Dict,
        previous_responses: List[Dict],
        focus_area: Optional[str] = None
    ) -> List[Dict]:
        """Generate psychological self-awareness questions"""
        
        # Analyze chart for psychological indicators
        psych_indicators = self._extract_psychological_indicators(chart_data)
        
        # Review previous responses for patterns
        response_patterns = self._analyze_response_patterns(previous_responses)
        
        # Generate novel questions
        questions = await self._generate_questions(
            psych_indicators, 
            response_patterns,
            focus_area
        )
        
        return questions
```

#### Vector Database Schema
```python
# src/josi/services/ai/vector_store.py
from qdrant_client.models import Distance, VectorParams, PointStruct
import hashlib

class AstrologyVectorStore:
    def __init__(self):
        self.collection_name = "astrology_interpretations"
        self._init_collection()
        
    def _init_collection(self):
        self.qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
    
    async def add_interpretation(
        self,
        chart_data: Dict,
        question: str,
        interpretation: str,
        metadata: Dict
    ):
        # Create unique ID
        chart_hash = hashlib.md5(json.dumps(chart_data, sort_keys=True).encode()).hexdigest()
        point_id = f"{chart_hash}_{hashlib.md5(question.encode()).hexdigest()}"
        
        # Encode text
        embedding = self.encoder.encode(f"{question} {interpretation}")
        
        # Store in Qdrant
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "chart_data": chart_data,
                        "question": question,
                        "interpretation": interpretation,
                        "metadata": metadata,
                        "created_at": datetime.utcnow().isoformat()
                    }
                )
            ]
        )
```

## Phase 2: Astrologer Marketplace (Weeks 5-8)

### 2.1 Astrologer Management

#### Database Models
```python
# src/josi/models/astrologer_model.py
class AstrologerSpecialization(str, enum.Enum):
    VEDIC = "vedic"
    WESTERN = "western"
    CHINESE = "chinese"
    MEDICAL = "medical"
    KARMIC = "karmic"
    RELATIONSHIP = "relationship"
    CAREER = "career"

class Astrologer(SQLModel, table=True):
    __tablename__ = "astrologers"
    
    astrologer_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.user_id", unique=True)
    
    # Professional Info
    professional_name: str
    bio: str
    years_experience: int
    certifications: List[Dict] = Field(default_factory=list, sa_column=JSON)
    specializations: List[str] = Field(default_factory=list, sa_column=JSON)
    languages: List[str] = Field(default_factory=list, sa_column=JSON)
    
    # Availability
    timezone: str
    availability_schedule: Dict = Field(default_factory=dict, sa_column=JSON)
    consultation_types: List[str] = Field(default_factory=list, sa_column=JSON)
    
    # Pricing
    hourly_rate: float
    currency: str = "USD"
    accepts_sliding_scale: bool = Field(default=False)
    
    # Performance
    rating: float = Field(default=0.0)
    total_consultations: int = Field(default=0)
    response_time_hours: float = Field(default=24.0)
    
    # Status
    verification_status: str = Field(default="pending")
    is_active: bool = Field(default=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    consultations: List["Consultation"] = Relationship(back_populates="astrologer")
    reviews: List["AstrologerReview"] = Relationship(back_populates="astrologer")

class Consultation(SQLModel, table=True):
    __tablename__ = "consultations"
    
    consultation_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.user_id")
    astrologer_id: UUID = Field(foreign_key="astrologers.astrologer_id")
    chart_id: UUID = Field(foreign_key="astrology_chart.chart_id")
    
    # Consultation Details
    type: str  # "video", "chat", "email"
    status: str = Field(default="pending")  # pending, scheduled, in_progress, completed
    
    # Questions & Responses
    user_questions: List[str] = Field(default_factory=list, sa_column=JSON)
    focus_areas: List[str] = Field(default_factory=list, sa_column=JSON)
    astrologer_notes: Optional[str] = Field(default=None)
    interpretation: Optional[Dict] = Field(default=None, sa_column=JSON)
    
    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)
    duration_minutes: int = Field(default=60)
    
    # Video Call
    video_room_id: Optional[str] = Field(default=None)
    video_access_token: Optional[str] = Field(default=None)
    recording_url: Optional[str] = Field(default=None)
    
    # AI Enhancement
    ai_summary: Optional[str] = Field(default=None)
    ai_key_points: List[str] = Field(default_factory=list, sa_column=JSON)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    user: User = Relationship(back_populates="consultations")
    astrologer: Astrologer = Relationship(back_populates="consultations")
```

### 2.2 Consultation Workflow

#### Booking Service
```python
# src/josi/services/consultation_service.py
class ConsultationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.video_service = VideoConsultationService()
        self.notification_service = NotificationService()
        self.payment_service = PaymentService()
        
    async def book_consultation(
        self,
        user_id: UUID,
        astrologer_id: UUID,
        consultation_request: ConsultationRequest
    ) -> Consultation:
        # 1. Check astrologer availability
        available = await self._check_availability(
            astrologer_id, 
            consultation_request.preferred_times
        )
        
        # 2. Process payment
        payment = await self.payment_service.process_consultation_payment(
            user_id=user_id,
            astrologer_id=astrologer_id,
            amount=consultation_request.calculate_total(),
            type=consultation_request.type
        )
        
        # 3. Create consultation record
        consultation = Consultation(
            user_id=user_id,
            astrologer_id=astrologer_id,
            chart_id=consultation_request.chart_id,
            type=consultation_request.type,
            scheduled_at=available.slot,
            duration_minutes=consultation_request.duration,
            user_questions=consultation_request.questions,
            focus_areas=consultation_request.focus_areas
        )
        
        # 4. If video consultation, create room
        if consultation_request.type == "video":
            video_details = await self.video_service.create_video_room(
                consultation.consultation_id
            )
            consultation.video_room_id = video_details["room_id"]
        
        # 5. Send notifications
        await self._send_booking_notifications(consultation)
        
        self.db.add(consultation)
        await self.db.commit()
        
        return consultation
    
    async def process_astrologer_response(
        self,
        consultation_id: UUID,
        response: AstrologerResponse
    ):
        consultation = await self.get_consultation(consultation_id)
        
        # 1. Store astrologer's interpretation
        consultation.interpretation = response.interpretation
        consultation.astrologer_notes = response.notes
        
        # 2. Generate AI summary
        ai_summary = await self.ai_service.summarize_consultation(
            consultation.user_questions,
            response.interpretation,
            consultation.chart_data
        )
        
        consultation.ai_summary = ai_summary["summary"]
        consultation.ai_key_points = ai_summary["key_points"]
        
        # 3. Update status
        consultation.status = "completed"
        consultation.completed_at = datetime.utcnow()
        
        # 4. Notify user
        await self.notification_service.send_consultation_ready(
            consultation.user_id,
            consultation_id
        )
        
        await self.db.commit()
```

## Phase 3: Real-time Features (Weeks 9-10)

### 3.1 WebSocket Implementation

```python
# src/josi/services/realtime_service.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

class RealtimeConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_subscriptions: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Send initial data
        await self.send_initial_data(websocket, user_id)
        
    async def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id].discard(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]
            
    async def subscribe_to_transits(self, user_id: str, chart_id: str):
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        self.user_subscriptions[user_id].add(f"transits:{chart_id}")
        
    async def broadcast_transit_update(self, chart_id: str, transit_data: Dict):
        subscription_key = f"transits:{chart_id}"
        
        for user_id, subscriptions in self.user_subscriptions.items():
            if subscription_key in subscriptions:
                await self.send_to_user(user_id, {
                    "type": "transit_update",
                    "chart_id": chart_id,
                    "data": transit_data
                })
                
    async def send_to_user(self, user_id: str, message: Dict):
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.active_connections[user_id].discard(ws)

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: str,
    token: str = Query(...)
):
    # Verify token
    user = await verify_websocket_token(token)
    if not user or str(user.user_id) != user_id:
        await websocket.close()
        return
        
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(user_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
```

### 3.2 Transit Monitoring Service

```python
# src/josi/services/transit_monitor.py
class TransitMonitorService:
    def __init__(self):
        self.active_monitors: Dict[str, asyncio.Task] = {}
        
    async def start_monitoring(self, user_id: str, chart_id: str):
        """Start monitoring transits for a user's chart"""
        monitor_key = f"{user_id}:{chart_id}"
        
        if monitor_key in self.active_monitors:
            return
            
        task = asyncio.create_task(
            self._monitor_transits(user_id, chart_id)
        )
        self.active_monitors[monitor_key] = task
        
    async def _monitor_transits(self, user_id: str, chart_id: str):
        """Background task to monitor transits"""
        chart = await self.get_chart(chart_id)
        
        while True:
            try:
                # Calculate current transits
                current_transits = await self.calculate_current_transits(chart)
                
                # Check for significant changes
                significant_changes = await self._check_significant_changes(
                    chart_id, current_transits
                )
                
                if significant_changes:
                    # Send real-time update
                    await realtime_manager.broadcast_transit_update(
                        chart_id, significant_changes
                    )
                    
                    # Send push notification if enabled
                    await self.notification_service.send_transit_alert(
                        user_id, significant_changes
                    )
                
                # Wait before next check (5 minutes for active monitoring)
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Transit monitoring error: {e}")
                await asyncio.sleep(60)
```

## Phase 4: Advanced Astrology Features (Weeks 11-12)

### 4.1 Muhurta Calculator

```python
# src/josi/services/vedic/muhurta_service.py
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class MuhurtaService:
    def __init__(self):
        self.ephemeris = SwissEphemeris()
        self.panchang_service = PanchangService()
        
    async def find_muhurta(
        self,
        activity_type: str,
        start_date: datetime,
        end_date: datetime,
        location: Dict,
        user_chart: Optional[Dict] = None
    ) -> List[MuhurtaWindow]:
        """Find auspicious time windows for activities"""
        
        muhurta_windows = []
        current = start_date
        
        while current <= end_date:
            # Calculate panchang for the day
            panchang = await self.panchang_service.calculate(
                current, location
            )
            
            # Get activity-specific rules
            rules = self._get_muhurta_rules(activity_type)
            
            # Check each muhurta (48 minutes) of the day
            for muhurta_num in range(30):  # 30 muhurtas in a day
                muhurta_start = current + timedelta(minutes=48 * muhurta_num)
                
                # Evaluate muhurta quality
                quality = await self._evaluate_muhurta(
                    muhurta_start,
                    location,
                    panchang,
                    rules,
                    user_chart
                )
                
                if quality.is_auspicious:
                    muhurta_windows.append(MuhurtaWindow(
                        start_time=muhurta_start,
                        end_time=muhurta_start + timedelta(minutes=48),
                        quality_score=quality.score,
                        factors=quality.factors,
                        warnings=quality.warnings
                    ))
            
            current += timedelta(days=1)
            
        # Sort by quality score
        muhurta_windows.sort(key=lambda x: x.quality_score, reverse=True)
        return muhurta_windows
        
    def _get_muhurta_rules(self, activity_type: str) -> MuhurtaRules:
        """Get rules for specific activities"""
        rules_db = {
            "marriage": {
                "avoid_nakshatras": ["Bharani", "Krittika", "Ashlesha"],
                "avoid_tithis": [4, 9, 14],  # Chaturthi, Navami, Chaturdashi
                "preferred_days": ["Monday", "Wednesday", "Thursday", "Friday"],
                "avoid_months": ["Ashada", "Bhadrapada", "Pausha"],
                "check_venus": True,
                "check_jupiter": True
            },
            "business": {
                "avoid_nakshatras": ["Krittika", "Magha", "Moola"],
                "preferred_tithis": [2, 3, 5, 7, 10, 11, 13],
                "preferred_days": ["Wednesday", "Thursday", "Friday"],
                "check_mercury": True,
                "avoid_retrograde": ["Mercury", "Venus"]
            },
            "travel": {
                "avoid_nakshatras": ["Bharani", "Krittika", "Ashlesha", "Magha"],
                "avoid_days": ["Tuesday", "Saturday"],
                "check_moon": True,
                "avoid_void_of_course": True
            }
        }
        return MuhurtaRules(rules_db.get(activity_type, {}))
```

### 4.2 Pariharam (Remedies) System

```python
# src/josi/models/remedy_model.py
class RemedyType(str, enum.Enum):
    MANTRA = "mantra"
    GEMSTONE = "gemstone"
    YANTRA = "yantra"
    RITUAL = "ritual"
    CHARITY = "charity"
    FASTING = "fasting"
    PILGRIMAGE = "pilgrimage"

class Remedy(SQLModel, table=True):
    __tablename__ = "remedies"
    
    remedy_id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    type: RemedyType
    tradition: str  # "vedic", "western", etc.
    
    # Association
    planet: Optional[str] = Field(default=None)
    dosha_type: Optional[str] = Field(default=None)
    affliction_type: Optional[str] = Field(default=None)
    
    # Details (multi-language)
    description: Dict = Field(default_factory=dict, sa_column=JSON)
    instructions: Dict = Field(default_factory=dict, sa_column=JSON)
    benefits: List[str] = Field(default_factory=list, sa_column=JSON)
    precautions: List[str] = Field(default_factory=list, sa_column=JSON)
    
    # Effectiveness
    effectiveness_rating: float = Field(default=0.0)
    user_ratings_count: int = Field(default=0)
    scientific_basis: Optional[str] = Field(default=None)
    
    # Media
    mantra_audio_url: Optional[str] = Field(default=None)
    instruction_video_url: Optional[str] = Field(default=None)
    yantra_image_url: Optional[str] = Field(default=None)

# src/josi/services/remedy_service.py
class RemedyRecommendationService:
    async def analyze_and_recommend(
        self,
        chart_id: UUID,
        concern_areas: List[str],
        tradition_preference: Optional[str] = None
    ) -> List[RemedyRecommendation]:
        """Analyze chart and recommend remedies"""
        
        # 1. Get chart and analyze afflictions
        chart = await self.get_chart(chart_id)
        afflictions = await self._analyze_afflictions(chart)
        
        # 2. Identify doshas
        doshas = await self._identify_doshas(chart)
        
        # 3. Map concerns to planetary influences
        planetary_influences = self._map_concerns_to_planets(
            concern_areas, chart
        )
        
        # 4. Query remedy database
        remedies = await self._find_matching_remedies(
            afflictions=afflictions,
            doshas=doshas,
            planetary_influences=planetary_influences,
            tradition=tradition_preference
        )
        
        # 5. Rank remedies by effectiveness and relevance
        ranked_remedies = self._rank_remedies(
            remedies, chart, concern_areas
        )
        
        # 6. Add personalization
        recommendations = []
        for remedy in ranked_remedies[:10]:  # Top 10
            recommendation = RemedyRecommendation(
                remedy=remedy,
                relevance_score=self._calculate_relevance(remedy, chart),
                personalized_instructions=await self._personalize_instructions(
                    remedy, chart
                ),
                expected_timeline=self._estimate_timeline(remedy, afflictions)
            )
            recommendations.append(recommendation)
            
        return recommendations
```

## Phase 5: Frontend Development (Weeks 11-12)

### 5.1 React PWA Structure

```typescript
// Frontend structure
josi-web/
├── src/
│   ├── components/
│   │   ├── charts/
│   │   │   ├── BirthChartVisualization.tsx
│   │   │   ├── TransitOverlay.tsx
│   │   │   └── ChartControls.tsx
│   │   ├── ai/
│   │   │   ├── InterpretationChat.tsx
│   │   │   ├── NeuralPathwayQuiz.tsx
│   │   │   └── AIInsightCards.tsx
│   │   ├── marketplace/
│   │   │   ├── AstrologerGrid.tsx
│   │   │   ├── ConsultationBooking.tsx
│   │   │   └── VideoCallInterface.tsx
│   │   └── muhurta/
│   │       ├── MuhurtaCalendar.tsx
│   │       └── ActivitySelector.tsx
│   ├── hooks/
│   │   ├── useRealtimeUpdates.ts
│   │   ├── useAIInterpretation.ts
│   │   └── useConsultation.ts
│   ├── services/
│   │   ├── api/
│   │   ├── websocket/
│   │   └── notifications/
│   └── store/
│       ├── authSlice.ts
│       ├── chartSlice.ts
│       └── marketplaceSlice.ts
```

### 5.2 Key React Components

```typescript
// src/components/ai/InterpretationChat.tsx
import React, { useState, useEffect } from 'react';
import { useAIInterpretation } from '@/hooks/useAIInterpretation';
import { ChartData } from '@/types';

export const InterpretationChat: React.FC<{ chart: ChartData }> = ({ chart }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const { interpret, isLoading } = useAIInterpretation();
  
  const handleQuestionSubmit = async (question: string) => {
    const newMessage = { role: 'user', content: question };
    setMessages([...messages, newMessage]);
    
    const interpretation = await interpret({
      chart,
      question,
      context: messages,
      style: userPreferences.interpretationStyle
    });
    
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: interpretation.text,
      sources: interpretation.sources,
      confidence: interpretation.confidence
    }]);
  };
  
  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />
      <QuestionInput onSubmit={handleQuestionSubmit} isLoading={isLoading} />
      <SuggestedQuestions chart={chart} onSelect={handleQuestionSubmit} />
    </div>
  );
};
```

## Phase 6: Deployment & Monitoring

### 6.1 Infrastructure Updates

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Existing services...
  
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
      
  redis-pubsub:
    image: redis:7-alpine
    command: redis-server --port 6380
    ports:
      - "6380:6380"
      
  video-server:
    build: ./video-service
    environment:
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
    ports:
      - "3002:3002"
      
volumes:
  qdrant_data:
```

### 6.2 Monitoring & Analytics

```python
# src/josi/services/analytics_service.py
from prometheus_client import Counter, Histogram, Gauge
import sentry_sdk

# Metrics
ai_interpretation_counter = Counter(
    'ai_interpretations_total',
    'Total AI interpretations generated',
    ['model', 'style']
)

consultation_duration = Histogram(
    'consultation_duration_seconds',
    'Consultation duration in seconds',
    ['type', 'astrologer_id']
)

active_websocket_connections = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

class AnalyticsService:
    async def track_interpretation(self, user_id: str, chart_id: str, details: Dict):
        # Prometheus metrics
        ai_interpretation_counter.labels(
            model=details['model'],
            style=details['style']
        ).inc()
        
        # Analytics database
        await self.db.analytics_events.insert_one({
            'event': 'ai_interpretation',
            'user_id': user_id,
            'chart_id': chart_id,
            'details': details,
            'timestamp': datetime.utcnow()
        })
        
        # Segment/Amplitude tracking
        analytics.track(user_id, 'AI Interpretation Generated', details)
```

## Implementation Timeline

### Month 1: Core Infrastructure
- **Week 1-2**: User authentication, subscription system
- **Week 3**: AI service integration (GPT-4/Claude)
- **Week 4**: Vector database setup and knowledge base

### Month 2: Marketplace & Real-time
- **Week 5-6**: Astrologer portal and booking system
- **Week 7**: WebSocket implementation
- **Week 8**: Video consultation integration

### Month 3: Advanced Features & Launch
- **Week 9**: Muhurta calculator
- **Week 10**: Remedy recommendation system
- **Week 11**: Frontend PWA development
- **Week 12**: Testing, deployment, and launch

## Budget Estimate

### Monthly Costs
- **AI API (GPT-4)**: $500-2000 (based on usage)
- **Vector Database (Qdrant Cloud)**: $50-200
- **Video API (Twilio)**: $100-500
- **Additional Infrastructure**: $200-500

### Development Resources
- **Backend Developer**: 3 months
- **Frontend Developer**: 2 months
- **UI/UX Designer**: 1 month
- **QA Engineer**: 1 month

## Success Metrics

1. **User Engagement**
   - Daily active users
   - AI interpretations per user
   - Consultation bookings

2. **Revenue**
   - Subscription conversions
   - Consultation revenue
   - Average revenue per user

3. **Quality**
   - AI interpretation ratings
   - Astrologer ratings
   - User satisfaction scores

4. **Technical**
   - API response times
   - WebSocket connection stability
   - AI response accuracy

This implementation plan builds upon your excellent foundation and adds the AI, marketplace, and user-facing features needed to realize your vision of a comprehensive astrology platform.