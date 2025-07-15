"""
Authentication service with JWT and OAuth support.
"""
from typing import Optional, Dict, Union
from datetime import datetime, timedelta
from uuid import UUID
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from josi.core.config import settings
from josi.models.user_model import User, UserCreate, UserLogin, SubscriptionTier
from josi.core.database import get_db
import structlog

logger = structlog.get_logger(__name__)

# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30


class AuthService:
    """Handle authentication and authorization."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def create_access_token(
        self, 
        data: Dict[str, Union[str, UUID]], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        
        # Convert UUID to string for JWT encoding
        for key, value in to_encode.items():
            if isinstance(value, UUID):
                to_encode[key] = str(value)
        
        return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    
    def create_refresh_token(self, data: Dict[str, Union[str, UUID]]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # JWT ID for revocation tracking
        })
        
        # Convert UUID to string for JWT encoding
        for key, value in to_encode.items():
            if isinstance(value, UUID):
                to_encode[key] = str(value)
        
        return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password or ""):
            return None
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(
                User.email == email,
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(
                User.user_id == user_id,
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        try:
            # Check if user exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create user
            user_dict = user_data.model_dump(exclude_unset=True)
            
            # Hash password if provided
            if user_data.password:
                user_dict["hashed_password"] = self.get_password_hash(user_data.password)
                del user_dict["password"]
            
            # Handle OAuth registration
            if user_data.oauth_provider and user_data.oauth_id:
                user_dict["oauth_providers"] = [user_data.oauth_provider]
                if user_data.oauth_provider == "google":
                    user_dict["google_id"] = user_data.oauth_id
                elif user_data.oauth_provider == "github":
                    user_dict["github_id"] = user_data.oauth_id
                user_dict["is_verified"] = True  # OAuth users are pre-verified
            
            # Create user instance
            user = User(**user_dict)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(
                "User registered",
                user_id=str(user.user_id),
                email=user.email,
                oauth_provider=user_data.oauth_provider
            )
            
            # TODO: Send verification email if not OAuth user
            
            return user
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error("Database error during registration", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
    
    async def login(self, credentials: UserLogin) -> Dict[str, str]:
        """Login user and return tokens."""
        user = await self.authenticate_user(credentials.email, credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        # Create tokens
        access_token = self.create_access_token(
            data={"sub": user.user_id, "email": user.email}
        )
        refresh_token = self.create_refresh_token(
            data={"sub": user.user_id}
        )
        
        logger.info("User logged in", user_id=str(user.user_id), email=user.email)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Create new access token from refresh token."""
        try:
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[ALGORITHM])
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = UUID(payload.get("sub"))
            user = await self.get_user_by_id(user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Create new access token
            access_token = self.create_access_token(
                data={"sub": user.user_id, "email": user.email}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def verify_token(self, token: str) -> User:
        """Verify JWT token and return user."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise credentials_exception
                
        except JWTError:
            raise credentials_exception
        
        user = await self.get_user_by_id(UUID(user_id))
        if user is None:
            raise credentials_exception
            
        return user
    
    async def oauth_login_or_register(
        self,
        email: str,
        full_name: str,
        provider: str,
        provider_id: str,
        avatar_url: Optional[str] = None
    ) -> Dict[str, str]:
        """Handle OAuth login or registration."""
        # Check if user exists
        user = await self.get_user_by_email(email)
        
        if user:
            # Update OAuth info if needed
            if provider not in user.oauth_providers:
                user.oauth_providers.append(provider)
                if provider == "google":
                    user.google_id = provider_id
                elif provider == "github":
                    user.github_id = provider_id
            
            # Update last login
            user.last_login = datetime.utcnow()
            await self.db.commit()
        else:
            # Register new user
            user_data = UserCreate(
                email=email,
                full_name=full_name,
                oauth_provider=provider,
                oauth_id=provider_id
            )
            user = await self.register_user(user_data)
            
            # Update avatar if provided
            if avatar_url:
                user.avatar_url = avatar_url
                await self.db.commit()
        
        # Create tokens
        access_token = self.create_access_token(
            data={"sub": user.user_id, "email": user.email}
        )
        refresh_token = self.create_refresh_token(
            data={"sub": user.user_id}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


# Dependency to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    auth_service = AuthService(db)
    return await auth_service.verify_token(token)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user