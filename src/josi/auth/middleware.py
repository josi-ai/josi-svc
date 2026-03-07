"""Auth middleware — resolves CurrentUser from JWT or API key."""
import hashlib
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from josi.auth.schemas import CurrentUser
from josi.core.config import settings
from josi.db.async_db import get_async_db
from josi.models.api_key_model import ApiKey
from josi.models.user_model import User

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


def extract_user_from_claims(claims: dict) -> CurrentUser:
    """Extract CurrentUser from JWT claims — works for both providers.

    Clerk injects custom claims via publicMetadata → JWT template:
      - josi_user_id, josi_subscription_tier, josi_subscription_tier_id,
        josi_roles, josi_is_active, josi_is_verified

    If josi_user_id is missing (first login before webhook sets publicMetadata),
    returns None so the caller can fall back to DB lookup.
    """
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
        email=claims.get("email", ""),
        subscription_tier=claims.get("josi_subscription_tier", "Free"),
        subscription_tier_id=claims.get("josi_subscription_tier_id"),
        roles=claims.get("josi_roles", ["user"]),
        is_active=claims.get("josi_is_active", True),
        is_verified=claims.get("josi_is_verified", False),
    )


async def resolve_user_from_db(auth_provider_id: str, email: str, db: AsyncSession) -> CurrentUser:
    """Fall back to DB lookup when JWT doesn't have josi_* claims yet.

    Handles the first login before the webhook sets publicMetadata.
    """
    result = await db.execute(
        select(User).where(
            and_(User.clerk_id == auth_provider_id, User.is_deleted == False)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.info("User not yet provisioned, creating from JWT", sub=auth_provider_id, email=email)
        user = User(
            clerk_id=auth_provider_id,
            email=email,
            full_name=email.split("@")[0] if email else "User",
            last_login=datetime.utcnow(),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        await db.commit()

    return CurrentUser(
        user_id=user.user_id,
        auth_provider_id=user.clerk_id,
        email=user.email,
        subscription_tier=user.subscription_tier_name or "Free",
        subscription_tier_id=user.subscription_tier_id,
        roles=user.roles,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


# --- API Key Resolution (provider-agnostic) ---

async def resolve_api_key_user(
    api_key_raw: str, db: AsyncSession
) -> User:
    """Look up API key in DB, return associated User."""
    key_hash = hashlib.sha256(api_key_raw.encode()).hexdigest()

    result = await db.execute(
        select(ApiKey).where(
            and_(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True,
            )
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if api_key.expires_at:
        if api_key.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
            )

    api_key.last_used_at = datetime.utcnow()
    await db.flush()

    user_result = await db.execute(
        select(User).where(
            and_(User.user_id == api_key.user_id, User.is_deleted == False)
        )
    )
    user = user_result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    return user


# --- Main Resolver ---

async def resolve_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> CurrentUser:
    """Resolve CurrentUser from either JWT or API key.

    Checks Authorization header first, then X-API-Key.
    Checks Authorization header first, then X-API-Key.
    """
    auth_header: Optional[str] = request.headers.get("authorization")
    api_key_header: Optional[str] = request.headers.get("x-api-key")

    # Path 1: JWT (B2C)
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        claims = validate_jwt(token)

        # Try extracting from custom claims first (fast path)
        current_user = extract_user_from_claims(claims)
        if current_user:
            return current_user

        # Fall back to DB lookup (first login before webhook sets claims)
        return await resolve_user_from_db(
            auth_provider_id=claims.get("sub", ""),
            email=claims.get("email", ""),
            db=db,
        )

    # Path 2: API Key (B2B)
    if api_key_header:
        user = await resolve_api_key_user(api_key_header, db)
        return CurrentUser(
            user_id=user.user_id,
            auth_provider_id=user.clerk_id,
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
