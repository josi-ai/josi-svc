"""Descope webhook endpoints — called by Descope Connector during auth flows."""
import hmac
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from josi.core.config import settings
from josi.db.async_db import get_async_db
from josi.models.user_model import User
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/webhooks/descope", tags=["webhooks"])


class DescopeLoginRequest(BaseModel):
    """Full Descope user object from Connector.

    Accepts the entire {{user}} object — we extract what we need.
    Uses model_config extra="allow" so new Descope fields don't break us.
    """
    model_config = {"extra": "allow"}

    userId: str  # Descope user ID (maps to our descope_id)
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


class DescopeLoginResponse(BaseModel):
    """Claims to inject into the JWT."""
    josi_user_id: str
    josi_subscription_tier_id: int
    josi_subscription_tier: str
    josi_roles: list[str]
    josi_is_active: bool
    josi_is_verified: bool


def verify_webhook_secret(webhook_secret: str, expected_secret: str) -> bool:
    """Verify the shared secret from Descope Connector.

    Uses constant-time comparison to prevent timing attacks.
    """
    if not webhook_secret or not expected_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )
    if not hmac.compare_digest(webhook_secret, expected_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )
    return True


@router.post("/login", response_model=DescopeLoginResponse)
async def descope_login_webhook(
    payload: DescopeLoginRequest,
    x_descope_webhook_secret: str = Header(..., alias="X-Descope-Webhook-Secret"),
    db: AsyncSession = Depends(get_async_db),
):
    """Called by Descope Connector during sign-in/sign-up flows.

    Upserts the user and returns claims for JWT enrichment.
    """
    verify_webhook_secret(x_descope_webhook_secret, settings.descope_webhook_secret)

    logger.info("Descope webhook received", user_id=payload.userId, email=payload.email)

    # Look up existing user
    result = await db.execute(
        select(User).where(User.descope_id == payload.userId)
    )
    user = result.scalar_one_or_none()

    if user:
        # Existing user — update last_login and any changed fields
        user.last_login = datetime.utcnow()
        if payload.email and user.email != payload.email:
            user.email = payload.email
        if payload.phone and user.phone != payload.phone:
            user.phone = payload.phone
        if payload.name and user.full_name != payload.name:
            user.full_name = payload.name
        await db.flush()
        await db.commit()

        logger.info("Existing user login", user_id=str(user.user_id), email=user.email)

        return DescopeLoginResponse(
            josi_user_id=str(user.user_id),
            josi_subscription_tier_id=user.subscription_tier_id or 1,
            josi_subscription_tier=user.subscription_tier_name or "Free",
            josi_roles=user.roles,
            josi_is_active=user.is_active,
            josi_is_verified=user.is_verified,
        )

    # New user — all data comes from the payload, no Management API call needed
    email = payload.email or ""
    new_user = User(
        descope_id=payload.userId,
        email=email,
        full_name=payload.name or email.split("@")[0],
        phone=payload.phone,
        is_verified=False,
        last_login=datetime.utcnow(),
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    await db.commit()

    logger.info("New user created", user_id=str(new_user.user_id), email=new_user.email)

    return DescopeLoginResponse(
        josi_user_id=str(new_user.user_id),
        josi_subscription_tier_id=new_user.subscription_tier_id or 1,
        josi_subscription_tier=new_user.subscription_tier_name or "Free",
        josi_roles=new_user.roles,
        josi_is_active=new_user.is_active,
        josi_is_verified=new_user.is_verified,
    )
