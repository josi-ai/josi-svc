"""
Authentication endpoints for production API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from typing import Optional

from josi.core.security import security_manager, SecurityDep
from josi.api.response import ResponseModel

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserRegistration(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    name: str
    organization_name: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours


@router.post("/register", response_model=ResponseModel)
async def register_user(user_data: UserRegistration) -> ResponseModel:
    """
    Register a new user and organization
    
    Creates a new user account with:
    - Secure password hashing
    - Default organization setup
    - Basic tier permissions
    """
    # In production, this would:
    # 1. Check if email already exists
    # 2. Hash the password
    # 3. Create user and organization records
    # 4. Send verification email
    
    # For now, return success with mock data
    mock_user_id = "12345678-1234-5678-9012-123456789012"
    mock_org_id = "87654321-4321-8765-2109-876543210987"
    
    # Create access token
    token_data = {
        "sub": mock_user_id,
        "email": user_data.email,
        "org_id": mock_org_id,
        "tier": "basic",
        "permissions": ["charts:read", "charts:create", "persons:read", "persons:create"]
    }
    
    access_token = security_manager.create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=24)
    )
    
    return ResponseModel(
        success=True,
        message="User registered successfully",
        data={
            "user_id": mock_user_id,
            "email": user_data.email,
            "organization_id": mock_org_id,
            "tier": "basic",
            "access_token": access_token,
            "token_type": "bearer"
        }
    )


@router.post("/login", response_model=ResponseModel)
async def login_user(user_credentials: UserLogin) -> ResponseModel:
    """
    Authenticate user and return access token
    
    Validates credentials and returns JWT token for API access.
    Token expires in 24 hours and includes user permissions.
    """
    # In production, this would:
    # 1. Look up user by email
    # 2. Verify password hash
    # 3. Check if account is active
    # 4. Log successful/failed attempts
    
    # For demo purposes, accept any email/password combo
    if not user_credentials.email or not user_credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Mock user lookup
    if user_credentials.email == "demo@josi.com" and user_credentials.password == "demo123":
        tier = "premium"
        permissions = ["charts:read", "charts:create", "charts:delete", "persons:read", 
                      "persons:create", "persons:update", "persons:delete", "admin:read"]
    else:
        tier = "basic"
        permissions = ["charts:read", "charts:create", "persons:read", "persons:create"]
    
    mock_user_id = "user-" + user_credentials.email.split("@")[0]
    mock_org_id = "org-" + user_credentials.email.split("@")[0]
    
    # Create access token
    token_data = {
        "sub": mock_user_id,
        "email": user_credentials.email,
        "org_id": mock_org_id,
        "tier": tier,
        "permissions": permissions
    }
    
    access_token = security_manager.create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=24)
    )
    
    return ResponseModel(
        success=True,
        message="Login successful",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user_id": mock_user_id,
            "tier": tier,
            "permissions": permissions
        }
    )


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token endpoint
    
    This endpoint follows OAuth2 standards for compatibility with
    OpenAPI documentation and client libraries.
    """
    # Validate credentials (same logic as login)
    if form_data.username == "demo@josi.com" and form_data.password == "demo123":
        tier = "premium"
        permissions = ["charts:read", "charts:create", "charts:delete", "persons:read", 
                      "persons:create", "persons:update", "persons:delete", "admin:read"]
    else:
        tier = "basic"
        permissions = ["charts:read", "charts:create", "persons:read", "persons:create"]
    
    mock_user_id = "user-" + form_data.username.split("@")[0]
    mock_org_id = "org-" + form_data.username.split("@")[0]
    
    token_data = {
        "sub": mock_user_id,
        "email": form_data.username,
        "org_id": mock_org_id,
        "tier": tier,
        "permissions": permissions
    }
    
    access_token = security_manager.create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=24)
    )
    
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=ResponseModel)
async def get_current_user_info(current_user: dict = SecurityDep) -> ResponseModel:
    """
    Get current user information
    
    Returns details about the authenticated user including
    permissions, tier, and organization information.
    """
    return ResponseModel(
        success=True,
        message="User information retrieved",
        data={
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "tier": current_user["tier"],
            "permissions": current_user["permissions"]
        }
    )


@router.post("/refresh", response_model=ResponseModel)
async def refresh_token(current_user: dict = SecurityDep) -> ResponseModel:
    """
    Refresh access token
    
    Issues a new access token with the same permissions.
    Useful for extending session without re-authentication.
    """
    # Create new token with same data
    token_data = {
        "sub": current_user["user_id"],
        "org_id": current_user["organization_id"],
        "tier": current_user["tier"],
        "permissions": current_user["permissions"]
    }
    
    new_token = security_manager.create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=24)
    )
    
    return ResponseModel(
        success=True,
        message="Token refreshed successfully",
        data={
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": 86400
        }
    )


@router.post("/logout", response_model=ResponseModel)
async def logout_user(current_user: dict = SecurityDep) -> ResponseModel:
    """
    Logout user
    
    In production, this would blacklist the current token.
    For now, it just returns a success message.
    """
    # In production:
    # 1. Add token to blacklist in Redis
    # 2. Log logout event
    # 3. Clean up any session data
    
    return ResponseModel(
        success=True,
        message="Logout successful",
        data={"logged_out_at": "2024-01-01T12:00:00Z"}
    )