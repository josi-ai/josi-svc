"""Auth middleware — resolves CurrentUser from JWT or API key."""
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, Request, status

from josi.auth.schemas import CurrentUser
from josi.auth.providers import get_auth_provider
from josi.services.user_service import UserService
from josi.services.api_key_service import ApiKeyService
from josi.services.session_cache_service import get_cached_user, cache_user

import structlog

logger = structlog.get_logger()


def _build_current_user_from_claims(claims: dict) -> Optional[CurrentUser]:
    """Build CurrentUser from josi_* claims in the JWT. Returns None if claims are missing."""
    josi_user_id = claims.get("josi_user_id")
    if not josi_user_id:
        return None
    try:
        user_id = UUID(josi_user_id)
    except ValueError:
        return None
    return CurrentUser(
        user_id=user_id,
        auth_provider_id=claims.get("sub", ""),
        auth_provider=claims.get("josi_auth_provider", "clerk"),
        email=claims.get("josi_email", ""),
        full_name=claims.get("josi_full_name", ""),
        subscription_tier=claims.get("josi_subscription_tier", "Free"),
        subscription_tier_id=claims.get("josi_subscription_tier_id"),
        roles=claims.get("josi_roles", ["user"]),
        is_active=claims.get("josi_is_active", True),
        is_verified=claims.get("josi_is_verified", False),
    )


async def _ensure_user_exists_in_db(current_user: CurrentUser, claims: dict) -> None:
    """Ensure the user record exists in the DB.

    Uses a Redis flag to avoid hitting the DB on every request.
    If the flag is missing (first request after cache expiry, DB reset, etc.),
    does a DB upsert and sets the flag.
    """
    from josi.core.cache import cache_manager

    flag_key = f"josi:user_exists:{current_user.user_id}"

    # Check Redis flag first (sub-ms)
    try:
        client = cache_manager.redis_client
        if client:
            exists = await client.get(flag_key)
            if exists:
                return  # User verified to exist in DB
    except Exception:
        pass  # Redis down — fall through to DB check

    # DB upsert — find or create the user
    user_service = UserService()
    await user_service.ensure_user_exists(
        user_id=current_user.user_id,
        auth_provider_id=current_user.auth_provider_id,
        email=current_user.email,
        full_name=current_user.full_name,
    )

    # Set the flag in Redis (1 hour TTL)
    try:
        client = cache_manager.redis_client
        if client:
            await client.setex(flag_key, 3600, "1")
    except Exception:
        pass  # Non-fatal


# --- Main Resolver ---

async def resolve_current_user(request: Request) -> CurrentUser:
    """Resolve CurrentUser from either JWT or API key.

    JWT path:
      1. Redis session cache → return if hit
      2. Build CurrentUser from josi_* JWT claims (fast) OR resolve from DB (slow, first login)
      3. Ensure user record exists in DB (Redis-flagged, only hits DB once per hour)
      4. Cache in Redis for subsequent requests
    """
    auth_header: Optional[str] = request.headers.get("authorization")
    api_key_header: Optional[str] = request.headers.get("x-api-key")

    # Path 1: JWT (B2C)
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        provider = get_auth_provider()
        claims = provider.validate_jwt(token)
        auth_provider_id = claims.get("sub", "")

        # Step 1: Check Redis session cache
        cached = await get_cached_user(auth_provider_id)
        if cached:
            # Even with cache hit, ensure user exists in DB (Redis-flagged, cheap)
            await _ensure_user_exists_in_db(cached, claims)
            return cached

        # Step 2: Try fast path — build from JWT claims
        current_user = _build_current_user_from_claims(claims)

        if not current_user:
            # First login: josi_user_id not in JWT yet — resolve from DB
            user_service = UserService()
            current_user = await user_service.resolve_user_from_db(
                auth_provider_id=auth_provider_id,
                email=claims.get("email", ""),
            )

        # Step 3: Ensure user record exists in DB
        await _ensure_user_exists_in_db(current_user, claims)

        # Step 4: Cache for subsequent requests
        await cache_user(current_user)
        return current_user

    # Path 2: API Key (B2B)
    if api_key_header:
        api_key_service = ApiKeyService()
        result = await api_key_service.resolve_user_from_api_key(api_key_header)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key",
            )

        user, api_key = result
        return CurrentUser(
            user_id=user.user_id,
            auth_provider_id=user.auth_provider_id,
            auth_provider=user.auth_provider,
            email=user.email,
            full_name=user.full_name,
            subscription_tier=user.subscription_tier_name or "Free",
            subscription_tier_id=user.subscription_tier_id,
            roles=user.roles,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )

    # No auth provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide Authorization: Bearer <token> or X-API-Key header.",
    )
