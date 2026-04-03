"""User self-service endpoints — profile, usage, subscription info."""
from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException

from josi.api.response import ResponseModel
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


@router.get("/preferences", response_model=ResponseModel)
async def get_preferences(current_user: CurrentUserDep):
    """Get current user's preferences (widget layout, chart defaults, theme, etc.)."""
    user_service = UserService(current_user=current_user)
    preferences = await user_service.get_preferences(current_user.user_id)
    return ResponseModel(
        success=True,
        message="Preferences retrieved",
        data=preferences,
    )


@router.put("/preferences", response_model=ResponseModel)
async def update_preferences(
    current_user: CurrentUserDep,
    preferences: Dict[str, Any] = Body(...),
):
    """Update user preferences. Merges with existing preferences (not replace).

    Supports nested keys such as:
    - ``dashboard.widget_layout`` — array of widget positions
    - ``dashboard.active_widgets`` — list of enabled widget types
    - ``chart.default_tradition`` — "vedic" | "western" | "chinese"
    - ``chart.default_house_system`` — "whole_sign" | "placidus" etc.
    - ``chart.default_ayanamsa`` — "lahiri" | "raman" etc.
    - ``chart.default_format`` — "South Indian" | "North Indian" | "Western Wheel"
    - ``theme`` — "dark" | "light"
    """
    user_service = UserService(current_user=current_user)
    try:
        merged = await user_service.update_preferences(
            current_user.user_id, preferences
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return ResponseModel(
        success=True,
        message="Preferences updated",
        data=merged,
    )
