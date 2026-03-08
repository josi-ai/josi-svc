"""API key management controllers — I/O validation only."""
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from josi.auth.middleware import resolve_current_user
from josi.auth.schemas import CurrentUser
from josi.models.api_key_model import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyCreatedResponse,
)
from josi.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

CurrentUserDep = Annotated[CurrentUser, Depends(resolve_current_user)]


@router.post("", response_model=ApiKeyCreatedResponse, status_code=201)
async def create_api_key(body: ApiKeyCreate, current_user: CurrentUserDep):
    """Create a new API key. The plaintext key is returned ONCE."""
    service = ApiKeyService(current_user=current_user)
    api_key, raw_key = await service.create_key(current_user.user_id, body.name)

    return ApiKeyCreatedResponse(
        api_key_id=api_key.api_key_id,
        key=raw_key,
        key_prefix=api_key.key_prefix,
        name=api_key.name,
    )


@router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(current_user: CurrentUserDep):
    """List all API keys for the current user (masked)."""
    service = ApiKeyService(current_user=current_user)
    keys = await service.list_keys(current_user.user_id)

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
async def revoke_api_key(key_id: UUID, current_user: CurrentUserDep):
    """Revoke an API key."""
    service = ApiKeyService(current_user=current_user)
    api_key = await service.revoke_key(key_id, current_user.user_id)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")


@router.post("/{key_id}/rotate", response_model=ApiKeyCreatedResponse)
async def rotate_api_key(key_id: UUID, current_user: CurrentUserDep):
    """Rotate an API key — revokes old, creates new with same name."""
    service = ApiKeyService(current_user=current_user)
    result = await service.rotate_key(key_id, current_user.user_id)

    if not result:
        raise HTTPException(status_code=404, detail="API key not found")

    new_key, raw_key = result
    return ApiKeyCreatedResponse(
        api_key_id=new_key.api_key_id,
        key=raw_key,
        key_prefix=new_key.key_prefix,
        name=new_key.name,
    )
