"""Clerk webhook and auth-sync controllers — I/O validation only.

Business logic lives in UserService. These controllers handle:
- Request parsing, header validation, webhook signature verification
- Delegating to UserService for user upsert and Clerk metadata sync
"""
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from typing import Optional

from josi.core.config import settings
from josi.auth.providers import get_auth_provider
from josi.services.user_service import UserService
from josi.services.session_cache_service import invalidate_user

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/webhooks/clerk", tags=["webhooks"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


# --- Response schemas ---

class ClerkWebhookResponse(BaseModel):
    success: bool
    josi_user_id: Optional[str] = None


class SyncClaimsResponse(BaseModel):
    success: bool
    josi_user_id: Optional[str] = None
    synced: bool = False


# --- Webhook signature verification ---

def verify_clerk_webhook(request: Request, body: bytes) -> bool:
    """Verify Clerk webhook via Svix HMAC signature."""
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

    secret = settings.clerk_webhook_secret
    if secret.startswith("whsec_"):
        secret = secret[6:]
    secret_bytes = base64.b64decode(secret)

    to_sign = f"{svix_id}.{svix_timestamp}.".encode() + body
    expected_signature = base64.b64encode(
        hmac.new(secret_bytes, to_sign, hashlib.sha256).digest()
    ).decode()

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


# --- Webhook payload parsing ---

def _extract_clerk_user_fields(user_data: dict) -> dict:
    """Parse Clerk webhook payload into flat user fields."""
    email_addresses = user_data.get("email_addresses", [])
    primary_email_id = user_data.get("primary_email_address_id")
    primary_email = next(
        (e["email_address"] for e in email_addresses if e.get("id") == primary_email_id),
        email_addresses[0]["email_address"] if email_addresses else None,
    )

    phone_numbers = user_data.get("phone_numbers", [])
    primary_phone_id = user_data.get("primary_phone_number_id")
    primary_phone = next(
        (p["phone_number"] for p in phone_numbers if p.get("id") == primary_phone_id),
        phone_numbers[0]["phone_number"] if phone_numbers else None,
    )

    first_name = user_data.get("first_name") or ""
    last_name = user_data.get("last_name") or ""
    full_name = f"{first_name} {last_name}".strip()
    if not full_name:
        full_name = primary_email.split("@")[0] if primary_email else "User"

    return {
        "clerk_user_id": user_data.get("id"),
        "email": primary_email,
        "full_name": full_name,
        "phone": primary_phone,
    }


# --- Endpoints ---

@router.post("/user")
async def clerk_user_webhook(request: Request):
    """Called by Clerk on user.created and user.updated events."""
    body = await request.body()
    verify_clerk_webhook(request, body)

    payload = await request.json()
    event_type = payload.get("type")

    if event_type not in ("user.created", "user.updated"):
        return ClerkWebhookResponse(success=True)

    user_data = payload.get("data", {})
    fields = _extract_clerk_user_fields(user_data)

    if not fields["clerk_user_id"]:
        logger.warning("Clerk webhook missing user id", event_type=event_type)
        return ClerkWebhookResponse(success=False)

    logger.info("Clerk webhook received", event_type=event_type, clerk_user_id=fields["clerk_user_id"], email=fields["email"])

    user_service = UserService()
    user = await user_service.upsert_from_clerk(
        clerk_user_id=fields["clerk_user_id"],
        email=fields["email"],
        full_name=fields["full_name"],
        phone=fields["phone"],
    )

    return ClerkWebhookResponse(success=True, josi_user_id=str(user.user_id))


@auth_router.post("/sync-claims", response_model=SyncClaimsResponse)
async def sync_claims(request: Request):
    """Called by the client after first sign-in to ensure publicMetadata is set."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
        )

    token = auth_header[7:]
    provider = get_auth_provider()
    claims = provider.validate_jwt(token)

    clerk_user_id = claims.get("sub", "")
    email = claims.get("email", "")
    name = claims.get("name", "")

    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing sub claim in JWT",
        )

    logger.info("Sync-claims requested", clerk_user_id=clerk_user_id, email=email)

    user_service = UserService()
    user = await user_service.upsert_from_clerk(
        clerk_user_id=clerk_user_id,
        email=email,
        full_name=name,
    )

    return SyncClaimsResponse(
        success=True,
        josi_user_id=str(user.user_id),
        synced=True,
    )


@auth_router.post("/logout")
async def logout(request: Request):
    """Invalidate the user's session cache on logout."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
        )

    token = auth_header[7:]
    provider = get_auth_provider()
    claims = provider.validate_jwt(token)
    auth_provider_id = claims.get("sub", "")

    if auth_provider_id:
        await invalidate_user(auth_provider_id)

    return {"success": True}
