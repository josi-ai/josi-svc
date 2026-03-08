"""User self-service endpoints — profile, usage, subscription info."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException

from josi.auth.middleware import resolve_current_user
from josi.auth.schemas import CurrentUser
from josi.models.user_model import UserResponse, UserUpdate
from josi.models.user_usage_model import UserUsageResponse
from josi.services.user_service import UserService
from josi.services.usage_service import UsageService

router = APIRouter(prefix="/me", tags=["me"])
CurrentUserDep = Annotated[CurrentUser, Depends(resolve_current_user)]


@router.get("", response_model=UserResponse)
async def get_my_profile(current_user: CurrentUserDep):
    user_service = UserService(current_user=current_user)
    user = await user_service.user_repository.get_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("", response_model=UserResponse)
async def update_my_profile(body: UserUpdate, current_user: CurrentUserDep):
    user_service = UserService(current_user=current_user)
    user = await user_service.user_repository.get_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    user = await user_service.user_repository.update(user)
    return user


@router.get("/usage", response_model=UserUsageResponse)
async def get_my_usage(current_user: CurrentUserDep, period: Optional[str] = None):
    usage_service = UsageService(current_user=current_user)
    return await usage_service.get_usage(current_user.user_id, period)


@router.get("/subscription")
async def get_my_subscription(current_user: CurrentUserDep):
    user_service = UserService(current_user=current_user)
    user = await user_service.user_repository.get_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "subscription_tier_id": user.subscription_tier_id,
        "subscription_tier_name": user.subscription_tier_name,
        "subscription_end_date": user.subscription_end_date,
        "is_active": user.is_subscription_active(),
        "has_premium": user.has_premium_features(),
        "limits": user.get_tier_limits(),
    }
