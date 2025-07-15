"""
Authentication API endpoints.
"""
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from josi.core.database import get_db
from josi.services.auth_service import AuthService, get_current_active_user
from josi.models.user_model import UserCreate, UserResponse, User, UserLogin
from josi.api.response import ResponseModel
# from cache.cache_invalidation import CacheInvalidator  # TODO: Implement proper cache invalidation

router = APIRouter(tags=["Authentication"], prefix="/auth")


@router.post("/register", response_model=ResponseModel)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Register a new user."""
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(user_data)
        
        # Clear any cached data
        # await CacheInvalidator.invalidate_user_cache(str(user.user_id))  # TODO: Implement
        
        return ResponseModel(
            success=True,
            message="Registration successful",
            data={
                "user": UserResponse(
                    user_id=user.user_id,
                    email=user.email,
                    full_name=user.full_name,
                    phone=user.phone,
                    avatar_url=user.avatar_url,
                    subscription_tier=user.subscription_tier,
                    subscription_end_date=user.subscription_end_date,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    created_at=user.created_at,
                    preferences=user.preferences,
                    notification_settings=user.notification_settings
                )
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=ResponseModel)
async def login(
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Login with email and password."""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.login(credentials)
        
        # Set refresh token as httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,  # Use HTTPS in production
            samesite="lax",
            max_age=30 * 24 * 60 * 60  # 30 days
        )
        
        return ResponseModel(
            success=True,
            message="Login successful",
            data={
                "access_token": tokens["access_token"],
                "token_type": tokens["token_type"]
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/token", response_model=Dict[str, str])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """OAuth2 compatible token endpoint."""
    auth_service = AuthService(db)
    credentials = UserLogin(email=form_data.username, password=form_data.password)
    tokens = await auth_service.login(credentials)
    return {
        "access_token": tokens["access_token"],
        "token_type": tokens["token_type"]
    }


@router.post("/refresh", response_model=ResponseModel)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Refresh access token using refresh token."""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.refresh_access_token(refresh_token)
        
        return ResponseModel(
            success=True,
            message="Token refreshed successfully",
            data=tokens
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout", response_model=ResponseModel)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user)
) -> ResponseModel:
    """Logout current user."""
    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token")
    
    # TODO: Add token to blacklist if implementing token revocation
    
    # Clear user cache
    # await CacheInvalidator.invalidate_user_cache(str(current_user.user_id))  # TODO: Implement
    
    return ResponseModel(
        success=True,
        message="Logged out successfully",
        data=None
    )


@router.get("/me", response_model=ResponseModel)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> ResponseModel:
    """Get current user information."""
    return ResponseModel(
        success=True,
        message="User information retrieved",
        data={
            "user": UserResponse(
                user_id=current_user.user_id,
                email=current_user.email,
                full_name=current_user.full_name,
                phone=current_user.phone,
                avatar_url=current_user.avatar_url,
                subscription_tier=current_user.subscription_tier,
                subscription_end_date=current_user.subscription_end_date,
                is_active=current_user.is_active,
                is_verified=current_user.is_verified,
                created_at=current_user.created_at,
                preferences=current_user.preferences,
                notification_settings=current_user.notification_settings
            )
        }
    )


@router.post("/verify-email/{token}", response_model=ResponseModel)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Verify user email with token."""
    # TODO: Implement email verification
    return ResponseModel(
        success=True,
        message="Email verification not yet implemented",
        data=None
    )


@router.post("/forgot-password", response_model=ResponseModel)
async def forgot_password(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """Request password reset."""
    # TODO: Implement password reset flow
    return ResponseModel(
        success=True,
        message="Password reset not yet implemented",
        data=None
    )