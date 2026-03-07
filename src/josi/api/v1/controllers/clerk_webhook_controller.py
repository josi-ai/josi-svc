"""Clerk webhook endpoints — called by Clerk on user events.

Flow:
1. User signs up/in via Clerk
2. Clerk sends user.created/user.updated webhook here
3. We upsert the user in our DB
4. We call Clerk API to set publicMetadata with josi_* fields
5. Clerk reads publicMetadata into session token via the JWT template
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
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

router = APIRouter(prefix="/webhooks/clerk", tags=["webhooks"])


class ClerkWebhookResponse(BaseModel):
    success: bool
    josi_user_id: Optional[str] = None


def verify_clerk_webhook(request: Request, body: bytes) -> bool:
    """Verify Clerk webhook via Svix HMAC signature.

    Clerk uses Svix for webhook delivery. The signing secret is base64-encoded
    after stripping the 'whsec_' prefix.
    """
    import base64
    import hashlib
    import hmac
    import time

    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    if not all([svix_id, svix_timestamp, svix_signature]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook verification headers",
        )

    if not settings.clerk_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Webhook secret not configured",
        )

    # Check timestamp is within 5 minutes to prevent replay attacks
    try:
        ts = int(svix_timestamp)
        if abs(time.time() - ts) > 300:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Webhook timestamp too old",
            )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook timestamp",
        )

    # Decode the signing secret (strip 'whsec_' prefix, base64 decode)
    secret = settings.clerk_webhook_secret
    if secret.startswith("whsec_"):
        secret = secret[6:]
    secret_bytes = base64.b64decode(secret)

    # Build the signature payload: "{svix_id}.{svix_timestamp}.{body}"
    to_sign = f"{svix_id}.{svix_timestamp}.".encode() + body
    expected_signature = base64.b64encode(
        hmac.new(secret_bytes, to_sign, hashlib.sha256).digest()
    ).decode()

    # Svix-Signature header can have multiple signatures: "v1,sig1 v1,sig2"
    signatures = svix_signature.split(" ")
    for sig in signatures:
        parts = sig.split(",", 1)
        if len(parts) == 2 and parts[0] == "v1":
            if hmac.compare_digest(parts[1], expected_signature):
                return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid webhook signature",
    )


async def set_clerk_public_metadata(clerk_user_id: str, metadata: dict) -> bool:
    """Call Clerk API to set publicMetadata on a user.

    This is what feeds the session token custom claims template.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://api.clerk.com/v1/users/{clerk_user_id}",
                headers={
                    "Authorization": f"Bearer {settings.clerk_secret_key}",
                    "Content-Type": "application/json",
                },
                json={"public_metadata": metadata},
            )
            if response.status_code != 200:
                logger.error(
                    "Failed to set Clerk publicMetadata",
                    clerk_user_id=clerk_user_id,
                    status=response.status_code,
                    body=response.text,
                )
                return False
            return True
    except Exception as e:
        logger.error("Clerk API call failed", error=str(e), clerk_user_id=clerk_user_id)
        return False


@router.post("/user")
async def clerk_user_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """Called by Clerk on user.created and user.updated events.

    Upserts the user in our DB, then sets publicMetadata on the Clerk user
    so the session token contains our custom claims.
    """
    body = await request.body()
    verify_clerk_webhook(request, body)

    payload = await request.json()
    event_type = payload.get("type")
    user_data = payload.get("data", {})

    if event_type not in ("user.created", "user.updated"):
        return ClerkWebhookResponse(success=True)

    clerk_user_id = user_data.get("id")
    if not clerk_user_id:
        logger.warning("Clerk webhook missing user id", event=event_type)
        return ClerkWebhookResponse(success=False)

    # Extract email from Clerk's email_addresses array
    email_addresses = user_data.get("email_addresses", [])
    primary_email_id = user_data.get("primary_email_address_id")
    primary_email = next(
        (e["email_address"] for e in email_addresses if e.get("id") == primary_email_id),
        email_addresses[0]["email_address"] if email_addresses else None,
    )

    # Extract phone
    phone_numbers = user_data.get("phone_numbers", [])
    primary_phone_id = user_data.get("primary_phone_number_id")
    primary_phone = next(
        (p["phone_number"] for p in phone_numbers if p.get("id") == primary_phone_id),
        phone_numbers[0]["phone_number"] if phone_numbers else None,
    )

    # Build name
    first_name = user_data.get("first_name") or ""
    last_name = user_data.get("last_name") or ""
    full_name = f"{first_name} {last_name}".strip()
    if not full_name:
        full_name = primary_email.split("@")[0] if primary_email else "User"

    logger.info("Clerk webhook received", event=event_type, clerk_user_id=clerk_user_id, email=primary_email)

    # Look up existing user
    result = await db.execute(
        select(User).where(User.descope_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.last_login = datetime.utcnow()
        if primary_email and user.email != primary_email:
            user.email = primary_email
        if primary_phone and user.phone != primary_phone:
            user.phone = primary_phone
        if full_name and user.full_name != full_name:
            user.full_name = full_name
        await db.flush()
        await db.commit()

        logger.info("Existing user updated via Clerk", user_id=str(user.user_id))

        # Set publicMetadata so Clerk session token has our claims
        await set_clerk_public_metadata(clerk_user_id, {
            "josi_user_id": str(user.user_id),
            "josi_subscription_tier_id": user.subscription_tier_id or 1,
            "josi_subscription_tier": user.subscription_tier_name or "Free",
            "josi_roles": user.roles,
            "josi_is_active": user.is_active,
            "josi_is_verified": user.is_verified,
        })

        return ClerkWebhookResponse(success=True, josi_user_id=str(user.user_id))

    # New user
    new_user = User(
        descope_id=clerk_user_id,
        email=primary_email or "",
        full_name=full_name,
        phone=primary_phone,
        is_verified=bool(primary_email),
        last_login=datetime.utcnow(),
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    await db.commit()

    logger.info("New user created via Clerk", user_id=str(new_user.user_id), email=new_user.email)

    # Set publicMetadata so Clerk session token has our claims
    await set_clerk_public_metadata(clerk_user_id, {
        "josi_user_id": str(new_user.user_id),
        "josi_subscription_tier_id": new_user.subscription_tier_id or 1,
        "josi_subscription_tier": new_user.subscription_tier_name or "Free",
        "josi_roles": new_user.roles,
        "josi_is_active": new_user.is_active,
        "josi_is_verified": new_user.is_verified,
    })

    return ClerkWebhookResponse(success=True, josi_user_id=str(new_user.user_id))
