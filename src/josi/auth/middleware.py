"""Auth middleware — resolves CurrentUser from JWT or API key."""
from typing import Optional

from fastapi import HTTPException, Request, status

from josi.auth.schemas import CurrentUser
from josi.services.user_service import UserService
from josi.services.api_key_service import ApiKeyService

import structlog

logger = structlog.get_logger()


# --- JWT Validation ---

def validate_jwt(token: str) -> dict:
    """Validate a Clerk session JWT and return claims."""
    import jwt as pyjwt
    from jwt import PyJWKClient

    try:
        jwks_url = "https://api.clerk.com/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return claims
    except Exception as e:
        logger.warning("Clerk JWT validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Main Resolver ---

async def resolve_current_user(request: Request) -> CurrentUser:
    """Resolve CurrentUser from either JWT or API key.

    Checks Authorization header first, then X-API-Key.
    """
    auth_header: Optional[str] = request.headers.get("authorization")
    api_key_header: Optional[str] = request.headers.get("x-api-key")

    # Path 1: JWT (B2C)
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        claims = validate_jwt(token)

        user_service = UserService()

        # Try extracting from custom claims first (fast path)
        current_user = user_service.extract_user_from_claims(claims)
        if current_user:
            return current_user

        # Fall back to DB lookup (first login before webhook sets claims)
        return await user_service.resolve_user_from_db(
            auth_provider_id=claims.get("sub", ""),
            email=claims.get("email", ""),
        )

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
            email=user.email,
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
