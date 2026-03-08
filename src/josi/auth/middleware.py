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


def extract_user_from_claims(claims: dict) -> Optional[CurrentUser]:
    """Fast path: build CurrentUser directly from josi_* claims baked into JWT."""
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


# --- Main Resolver ---

async def resolve_current_user(request: Request) -> CurrentUser:
    """Resolve CurrentUser from either JWT or API key.

    Checks Authorization header first, then X-API-Key.
    JWT path: claims fast-path → Redis cache → DB fallback.
    """
    auth_header: Optional[str] = request.headers.get("authorization")
    api_key_header: Optional[str] = request.headers.get("x-api-key")

    # Path 1: JWT (B2C)
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        provider = get_auth_provider()
        claims = provider.validate_jwt(token)

        # Fast path: read josi_* claims from JWT (publicMetadata baked in by Clerk)
        current_user = extract_user_from_claims(claims)
        if current_user:
            return current_user

        # First login: josi_user_id not in JWT yet
        auth_provider_id = claims.get("sub", "")

        # Check Redis cache
        cached = await get_cached_user(auth_provider_id)
        if cached:
            return cached

        # DB fallback — resolve or auto-create user
        user_service = UserService()
        current_user = await user_service.resolve_user_from_db(
            auth_provider_id=auth_provider_id,
            email=claims.get("email", ""),
        )
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
