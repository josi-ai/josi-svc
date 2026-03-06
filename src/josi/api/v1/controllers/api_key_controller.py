"""API key management endpoints."""
import hashlib
import secrets
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from josi.auth.middleware import resolve_current_user
from josi.auth.schemas import CurrentUser
from josi.db.async_db import get_async_db
from josi.models.api_key_model import (
    ApiKey,
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyCreatedResponse,
)

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

CurrentUserDep = Annotated[CurrentUser, Depends(resolve_current_user)]


def generate_api_key() -> str:
    """Generate a new API key with jsk_ prefix."""
    return f"jsk_{secrets.token_urlsafe(32)}"


@router.post("", response_model=ApiKeyCreatedResponse, status_code=201)
async def create_api_key(
    body: ApiKeyCreate,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new API key. The plaintext key is returned ONCE."""
    raw_key = generate_api_key()
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12]

    api_key = ApiKey(
        user_id=current_user.user_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=body.name,
    )
    db.add(api_key)
    await db.flush()
    await db.refresh(api_key)
    await db.commit()

    return ApiKeyCreatedResponse(
        api_key_id=api_key.api_key_id,
        key=raw_key,
        key_prefix=key_prefix,
        name=api_key.name,
    )


@router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_async_db),
):
    """List all API keys for the current user (masked)."""
    result = await db.execute(
        select(ApiKey).where(
            and_(
                ApiKey.user_id == current_user.user_id,
                ApiKey.is_active == True,
            )
        )
    )
    keys = result.scalars().all()
    return [
        ApiKeyResponse(
            api_key_id=k.api_key_id,
            key_prefix=k.key_prefix,
            name=k.name,
            is_active=k.is_active,
            last_used_at=k.last_used_at,
            expires_at=k.expires_at,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.delete("/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: UUID,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_async_db),
):
    """Revoke an API key."""
    result = await db.execute(
        select(ApiKey).where(
            and_(
                ApiKey.api_key_id == key_id,
                ApiKey.user_id == current_user.user_id,
            )
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    api_key.updated_at = datetime.utcnow()
    await db.flush()
    await db.commit()


@router.post("/{key_id}/rotate", response_model=ApiKeyCreatedResponse)
async def rotate_api_key(
    key_id: UUID,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_async_db),
):
    """Rotate an API key — revokes old, creates new with same name."""
    result = await db.execute(
        select(ApiKey).where(
            and_(
                ApiKey.api_key_id == key_id,
                ApiKey.user_id == current_user.user_id,
                ApiKey.is_active == True,
            )
        )
    )
    old_key = result.scalar_one_or_none()

    if not old_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Revoke old key
    old_key.is_active = False
    old_key.updated_at = datetime.utcnow()

    # Create new key with same name
    raw_key = generate_api_key()
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12]

    new_key = ApiKey(
        user_id=current_user.user_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=old_key.name,
    )
    db.add(new_key)
    await db.flush()
    await db.refresh(new_key)
    await db.commit()

    return ApiKeyCreatedResponse(
        api_key_id=new_key.api_key_id,
        key=raw_key,
        key_prefix=key_prefix,
        name=new_key.name,
    )
