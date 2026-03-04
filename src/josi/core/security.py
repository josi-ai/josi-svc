"""
Production-ready security middleware and authentication
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib
import time
import asyncio
from functools import wraps
import structlog

from josi.core.config import settings

logger = structlog.get_logger()


class SecurityManager:
    """Enterprise-grade security manager"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security = HTTPBearer(auto_error=False)
        self.rate_limit_storage = {}  # In production, use Redis
        
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire, "type": "access", "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    async def verify_token(self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
            
            # Check token expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
            
        except JWTError as e:
            logger.warning("Invalid token", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    async def get_current_user(self, token_data: Dict = Depends(verify_token)) -> Dict[str, Any]:
        """Get current authenticated user"""
        return {
            "user_id": token_data.get("sub"),
            "organization_id": token_data.get("org_id", "default"),
            "permissions": token_data.get("permissions", []),
            "tier": token_data.get("tier", "basic")
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)


class RateLimiter:
    """Advanced rate limiting with different tiers"""
    
    def __init__(self):
        self.storage = {}  # In production, use Redis
        self.rate_limits = {
            "basic": {"requests_per_minute": 60, "calculations_per_hour": 100},
            "premium": {"requests_per_minute": 300, "calculations_per_hour": 1000},
            "enterprise": {"requests_per_minute": 1000, "calculations_per_hour": 10000}
        }
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP or user ID)"""
        # Try to get from auth first
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                return f"user:{payload.get('sub', 'unknown')}"
            except:
                pass
        
        # Fallback to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        return f"ip:{request.client.host}"
    
    def _get_user_tier(self, request: Request) -> str:
        """Determine user tier for rate limiting"""
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                return payload.get("tier", "basic")
            except:
                pass
        return "basic"
    
    async def check_rate_limit(self, request: Request, endpoint_type: str = "general") -> bool:
        """Check if request is within rate limits"""
        client_id = self._get_client_id(request)
        tier = self._get_user_tier(request)
        current_minute = int(time.time() // 60)
        
        # Get rate limits for tier
        limits = self.rate_limits.get(tier, self.rate_limits["basic"])
        
        # Create storage key
        key = f"{client_id}:{endpoint_type}:{current_minute}"
        
        # Increment counter
        if key not in self.storage:
            self.storage[key] = 0
        self.storage[key] += 1
        
        # Clean old entries (simple cleanup)
        if len(self.storage) > 10000:  # Prevent memory bloat
            old_keys = [k for k in self.storage.keys() if int(k.split(':')[-1]) < current_minute - 5]
            for old_key in old_keys:
                del self.storage[old_key]
        
        # Check limit
        limit_key = "calculations_per_hour" if endpoint_type == "calculation" else "requests_per_minute"
        if endpoint_type == "calculation":
            # For calculations, check hourly limit
            current_hour = int(time.time() // 3600)
            hour_key = f"{client_id}:calculation_hour:{current_hour}"
            if hour_key not in self.storage:
                self.storage[hour_key] = 0
            self.storage[hour_key] += 1
            return self.storage[hour_key] <= limits["calculations_per_hour"]
        else:
            # For general requests, check per minute
            return self.storage[key] <= limits["requests_per_minute"]
    
    def rate_limit(self, endpoint_type: str = "general"):
        """Decorator for rate limiting endpoints"""
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                if not await self.check_rate_limit(request, endpoint_type):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded for {endpoint_type}. Upgrade your plan for higher limits.",
                        headers={"Retry-After": "60"}
                    )
                return await func(request, *args, **kwargs)
            return wrapper
        return decorator


class SecurityMiddleware:
    """Security middleware for headers and validation"""
    
    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
    
    # Relaxed CSP for docs pages that need CDN resources and inline scripts
    DOCS_CSP = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' https://cdn.jsdelivr.net"
    )
    DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}

    async def add_security_headers(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)

        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value

        # Relax CSP for Swagger UI / ReDoc pages
        if request.url.path in self.DOCS_PATHS:
            response.headers["Content-Security-Policy"] = self.DOCS_CSP

        # Add request ID for tracing
        import uuid
        response.headers["X-Request-ID"] = str(uuid.uuid4())

        return response


# Global instances
security_manager = SecurityManager()
rate_limiter = RateLimiter()
security_middleware = SecurityMiddleware()

# Dependencies for use in controllers
SecurityDep = Depends(security_manager.get_current_user)


def require_authentication():
    """Dependency that requires authentication"""
    return Depends(security_manager.get_current_user)


def require_permissions(required_permissions: List[str]):
    """Dependency that requires specific permissions"""
    def permission_checker(current_user: Dict = SecurityDep):
        user_permissions = current_user.get("permissions", [])
        if not any(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return Depends(permission_checker)


# Input validation utilities
def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    
    # Remove potentially dangerous characters
    import re
    cleaned = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', value.strip())
    
    if len(cleaned) > max_length:
        raise ValueError(f"String too long (max {max_length} characters)")
    
    return cleaned


def validate_uuid(value: str) -> str:
    """Validate UUID format"""
    import uuid
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValueError("Invalid UUID format")


def validate_coordinates(latitude: float, longitude: float) -> tuple:
    """Validate geographic coordinates"""
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")
    return latitude, longitude


# Standalone functions for backward compatibility
_security_manager = SecurityManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token (standalone function)"""
    return _security_manager.create_access_token(data, expires_delta)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)