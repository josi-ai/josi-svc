"""Usage tracking service with Redis counters + DB persistence."""
from typing import Optional
from datetime import datetime
from uuid import UUID

import structlog

from josi.auth.schemas import CurrentUser
from josi.core.cache import cache_manager
from josi.models.user_usage_model import UserUsageResponse
from josi.repositories.usage_repository import UsageRepository
from josi.repositories.user_repository import UserRepository

logger = structlog.get_logger()

TRACKED_FIELDS = [
    "charts_calculated",
    "ai_interpretations_used",
    "consultations_booked",
    "saved_charts_count",
]
USAGE_TTL = 86400  # 24 hours


def _redis_key(user_id: UUID, period: str, field: str) -> str:
    return f"josi:usage:{user_id}:{period}:{field}"


def _current_period() -> str:
    return datetime.utcnow().strftime("%Y-%m")


class UsageService:
    def __init__(self, current_user: Optional[CurrentUser] = None):
        self.current_user = current_user
        self.usage_repo = UsageRepository(current_user=current_user)
        self.user_repo = UserRepository(current_user=current_user)

    async def increment(self, user_id: UUID, field: str, amount: int = 1) -> None:
        if field not in TRACKED_FIELDS:
            raise ValueError(f"Invalid usage field: {field}")

        period = _current_period()
        client = cache_manager.redis_client

        if client:
            try:
                key = _redis_key(user_id, period, field)
                await client.incrby(key, amount)
                await client.expire(key, USAGE_TTL)
                return
            except Exception as e:
                logger.warning("Redis increment failed, falling back to DB", error=str(e))

        await self.usage_repo.increment(user_id, field, amount)

    async def get_usage(self, user_id: UUID, period: Optional[str] = None) -> UserUsageResponse:
        period = period or _current_period()
        counts = {}
        client = cache_manager.redis_client

        # Try Redis first
        if client:
            try:
                for field in TRACKED_FIELDS:
                    val = await client.get(_redis_key(user_id, period, field))
                    counts[field] = int(val) if val else None
            except Exception:
                counts = {}

        # If any field missing from Redis, fall back to DB
        if not all(v is not None for v in counts.values()):
            usage = await self.usage_repo.get_or_create(user_id, period)
            for field in TRACKED_FIELDS:
                if counts.get(field) is None:
                    counts[field] = getattr(usage, field, 0)

        # Get tier limits from user
        user = await self.user_repo.get_by_id(user_id)
        limits = user.get_tier_limits() if user else {}

        return UserUsageResponse(
            period=period,
            charts_calculated=counts.get("charts_calculated", 0),
            ai_interpretations_used=counts.get("ai_interpretations_used", 0),
            consultations_booked=counts.get("consultations_booked", 0),
            saved_charts_count=counts.get("saved_charts_count", 0),
            limits=limits,
        )

    async def sync_to_db(self, user_id: UUID, period: Optional[str] = None) -> None:
        """Flush Redis counters to DB."""
        period = period or _current_period()
        client = cache_manager.redis_client
        if not client:
            return

        usage = await self.usage_repo.get_or_create(user_id, period)

        for field in TRACKED_FIELDS:
            try:
                val = await client.get(_redis_key(user_id, period, field))
                if val is not None:
                    setattr(usage, field, int(val))
            except Exception:
                continue

        usage.updated_at = datetime.utcnow()
        from josi.db.async_db import get_async_session
        async with get_async_session() as session:
            await session.merge(usage)
            await session.flush()
