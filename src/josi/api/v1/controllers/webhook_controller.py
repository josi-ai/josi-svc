"""Descope webhook endpoints — called by Descope Connector during auth flows."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from josi.core.config import settings
from josi.db.async_db import get_async_db
from josi.models.user_model import User
from josi.auth.descope_client import get_descope_client

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/webhooks/descope", tags=["webhooks"])


class DescopeLoginRequest(BaseModel):
    """Payload from Descope Connector."""
    sub: str
    email: str


class DescopeLoginResponse(BaseModel):
    """Claims to inject into the JWT."""
    josi_user_id: str
    josi_subscription_tier: str
    josi_roles: list[str]


def verify_webhook_secret(webhook_secret: str, expected_secret: str) -> bool:
    """Verify the shared secret from Descope Connector."""
    if not webhook_secret or webhook_secret != expected_secret:
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

    # Look up existing user
    result = await db.execute(
        select(User).where(User.descope_id == payload.sub)
    )
    user = result.scalar_one_or_none()

    if user:
        # Existing user — update last_login
        user.last_login = datetime.utcnow()
        await db.flush()
        await db.commit()

        logger.info("Existing user login", user_id=str(user.user_id), email=user.email)

        return DescopeLoginResponse(
            josi_user_id=str(user.user_id),
            josi_subscription_tier=user.subscription_tier.value,
            josi_roles=user.roles,
        )

    # New user — fetch details from Descope Management API
    descope_client = get_descope_client()
    try:
        user_resp = descope_client.mgmt.user.load_by_user_id(payload.sub)
        descope_user = user_resp["user"]
    except Exception as e:
        logger.error("Failed to fetch user from Descope", error=str(e), sub=payload.sub)
        descope_user = {}

    # Create local user
    new_user = User(
        descope_id=payload.sub,
        email=payload.email,
        full_name=descope_user.get("name", payload.email.split("@")[0]),
        phone=descope_user.get("phone"),
        is_verified=descope_user.get("verifiedEmail", False),
        last_login=datetime.utcnow(),
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    await db.commit()

    logger.info("New user created", user_id=str(new_user.user_id), email=new_user.email)

    return DescopeLoginResponse(
        josi_user_id=str(new_user.user_id),
        josi_subscription_tier=new_user.subscription_tier.value,
        josi_roles=new_user.roles,
    )
