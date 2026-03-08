"""Redis-backed session cache for sub-millisecond CurrentUser resolution."""
import json
from typing import Optional

import structlog

from josi.auth.schemas import CurrentUser
from josi.core.cache import cache_manager

logger = structlog.get_logger()

SESSION_TTL = 900  # 15 minutes


def _cache_key(auth_provider_id: str) -> str:
    return f"josi:user_session:{auth_provider_id}"


async def get_cached_user(auth_provider_id: str) -> Optional[CurrentUser]:
    try:
        client = cache_manager.redis_client
        if not client:
            return None
        raw = await client.get(_cache_key(auth_provider_id))
        if not raw:
            return None
        data = json.loads(raw)
        return CurrentUser.model_validate(data)
    except Exception as e:
        logger.debug("Session cache miss", auth_provider_id=auth_provider_id, error=str(e))
        return None


async def cache_user(user: CurrentUser) -> None:
    try:
        client = cache_manager.redis_client
        if not client:
            return
        payload = json.dumps(user.model_dump(mode="json"))
        await client.setex(_cache_key(user.auth_provider_id), SESSION_TTL, payload)
    except Exception as e:
        logger.warning("Session cache set failed", error=str(e))


async def invalidate_user(auth_provider_id: str) -> None:
    try:
        client = cache_manager.redis_client
        if not client:
            return
        await client.delete(_cache_key(auth_provider_id))
    except Exception as e:
        logger.warning("Session cache invalidation failed", error=str(e))


async def invalidate_user_by_id(user_id: str) -> None:
    try:
        await cache_manager.delete(f"josi:user_session:*")
    except Exception as e:
        logger.warning("Session cache bulk invalidation failed", error=str(e))
