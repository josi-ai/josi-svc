"""Auth middleware — resolves CurrentUser from JWT or API key."""
import hashlib
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from descope import AuthException

from josi.auth.descope_client import get_descope_client
from josi.auth.schemas import CurrentUser
from josi.db.async_db import get_async_db
from josi.models.api_key_model import ApiKey
from josi.models.user_model import User

import structlog

logger = structlog.get_logger()


def validate_descope_jwt(token: str) -> dict:
    """Validate a Descope session JWT and return claims."""
    client = get_descope_client()
    try:
        jwt_response = client.validate_session(token)
        return jwt_response
    except AuthException as e:
        logger.warning("Descope JWT validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )


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

    # Check expiry
    if api_key.expires_at:
        from datetime import datetime
        if api_key.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
            )

    # Update last_used_at
    from datetime import datetime
    api_key.last_used_at = datetime.utcnow()
    await db.flush()

    # Load user
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


async def resolve_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> CurrentUser:
    """Resolve CurrentUser from either JWT or API key.

    Checks Authorization header first, then X-API-Key.
    """
    auth_header: Optional[str] = request.headers.get("authorization")
    api_key_header: Optional[str] = request.headers.get("x-api-key")

    # Path 1: JWT (B2C)
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        claims = validate_descope_jwt(token)

        return CurrentUser(
            user_id=UUID(claims["josi_user_id"]),
            descope_id=claims["sub"],
            email=claims["email"],
            subscription_tier=claims["josi_subscription_tier"],
            roles=claims["josi_roles"],
        )

    # Path 2: API Key (B2B)
    if api_key_header:
        user = await resolve_api_key_user(api_key_header, db)
        return CurrentUser(
            user_id=user.user_id,
            descope_id=user.descope_id,
            email=user.email,
            subscription_tier=user.subscription_tier.value if hasattr(user.subscription_tier, 'value') else user.subscription_tier,
            roles=user.roles,
        )

    # No auth provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide Authorization: Bearer <token> or X-API-Key header.",
    )
