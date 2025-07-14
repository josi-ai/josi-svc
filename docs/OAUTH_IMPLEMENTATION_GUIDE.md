# Open Source OAuth Implementation Guide for Josi

This guide covers how to implement OAuth2/OpenID Connect authentication using open-source solutions, replacing or enhancing the current JWT-based authentication system.

## Current Authentication System

Josi currently uses:
- **JWT tokens** for user authentication
- **API keys** for programmatic access
- **Mock implementation** (not connected to a user database)

## Recommended Open Source OAuth Solutions

### 1. **Authlib** (Lightweight, Python-native)

Best for: Direct integration into FastAPI without external services.

#### Installation
```bash
poetry add authlib httpx
```

#### Implementation

```python
# src/josi/core/oauth_config.py
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from fastapi import HTTPException
from josi.core.config import settings

oauth = OAuth()

# Configure OAuth providers
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

oauth.register(
    name='github',
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'}
)
```

```python
# src/josi/api/v1/oauth.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from josi.core.oauth_config import oauth
from josi.core.security import create_access_token
from josi.core.database import get_session
from josi.models.user_model import User
from josi.api.response import ResponseModel

router = APIRouter(prefix="/api/v1/oauth", tags=["oauth"])

@router.get("/login/{provider}")
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth login flow."""
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    if provider not in ['google', 'github']:
        raise HTTPException(status_code=400, detail="Provider not supported")
    
    client = getattr(oauth, provider)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str, 
    request: Request,
    db: Session = Depends(get_session)
):
    """Handle OAuth callback."""
    try:
        client = getattr(oauth, provider)
        token = await client.authorize_access_token(request)
        
        # Get user info from provider
        if provider == 'google':
            user_info = token.get('userinfo')
            email = user_info.get('email')
            name = user_info.get('name')
            provider_id = user_info.get('sub')
        elif provider == 'github':
            resp = await client.get('user', token=token)
            user_info = resp.json()
            email = user_info.get('email')
            name = user_info.get('name') or user_info.get('login')
            provider_id = str(user_info.get('id'))
        
        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                oauth_provider=provider,
                oauth_provider_id=provider_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create JWT token
        access_token = create_access_token({
            "sub": str(user.user_id),
            "email": user.email,
            "organization_id": str(user.organization_id)
        })
        
        # Redirect to frontend with token
        frontend_url = settings.frontend_url or "http://localhost:3000"
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}"
        )
        
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. **FastAPI-Users** (Full-featured authentication)

Best for: Complete authentication system with user management.

#### Installation
```bash
poetry add "fastapi-users[sqlalchemy,oauth]"
```

#### Implementation

```python
# src/josi/core/fastapi_users_config.py
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.github import GitHubOAuth2

from josi.core.config import settings
from josi.models.user_model import User, UserCreate, UserUpdate
from josi.core.database import get_async_db

# OAuth clients
google_oauth_client = GoogleOAuth2(
    settings.google_client_id,
    settings.google_client_secret,
)

github_oauth_client = GitHubOAuth2(
    settings.github_client_id,
    settings.github_client_secret,
)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_oauth_register(
        self, user: User, request: Optional[Request] = None, provider: str = None
    ):
        print(f"User {user.id} has registered with {provider}.")

async def get_user_db(session: AsyncSession = Depends(get_async_db)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# JWT authentication backend
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
```

```python
# src/josi/api/v1/users.py
from fastapi import APIRouter
from josi.core.fastapi_users_config import (
    auth_backend,
    fastapi_users,
    google_oauth_client,
    github_oauth_client,
)

router = APIRouter()

# Include FastAPI Users routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        settings.secret_key,
        redirect_url=f"{settings.frontend_url}/auth/google/callback",
    ),
    prefix="/auth/google",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_oauth_router(
        github_oauth_client,
        auth_backend,
        settings.secret_key,
        redirect_url=f"{settings.frontend_url}/auth/github/callback",
    ),
    prefix="/auth/github",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)
```

### 3. **Keycloak** (Self-hosted identity provider)

Best for: Enterprise deployments with advanced features.

#### Docker Compose Setup

```yaml
# docker-compose.keycloak.yml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: keycloak
    ports:
      - "8080:8080"
    command: start-dev
    depends_on:
      - postgres
  
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: keycloak
    volumes:
      - keycloak_data:/var/lib/postgresql/data

volumes:
  keycloak_data:
```

#### Integration

```python
# src/josi/core/keycloak_auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt, JWTError
from typing import Optional
import httpx

from josi.core.config import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.keycloak_url}/auth/realms/{settings.keycloak_realm}/protocol/openid-connect/auth",
    tokenUrl=f"{settings.keycloak_url}/auth/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
)

async def get_keycloak_public_key():
    """Fetch Keycloak public key for token verification."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.keycloak_url}/auth/realms/{settings.keycloak_realm}"
        )
        return response.json()["public_key"]

async def verify_token(token: str = Depends(oauth2_scheme)):
    """Verify Keycloak JWT token."""
    try:
        public_key = await get_keycloak_public_key()
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.keycloak_client_id,
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

async def get_current_user(token_data: dict = Depends(verify_token)):
    """Extract user information from Keycloak token."""
    return {
        "id": token_data.get("sub"),
        "email": token_data.get("email"),
        "name": token_data.get("name"),
        "roles": token_data.get("realm_access", {}).get("roles", [])
    }
```

### 4. **Ory Kratos** (Modern identity infrastructure)

Best for: Cloud-native deployments with high security requirements.

#### Deployment

```yaml
# k8s/ory-kratos.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kratos-config
  namespace: josi
data:
  kratos.yml: |
    version: v0.11.1
    dsn: postgres://kratos:password@postgres:5432/kratos?sslmode=disable
    serve:
      public:
        base_url: https://api.josi.example.com/kratos/
        cors:
          enabled: true
      admin:
        base_url: http://kratos:4434/
    selfservice:
      default_browser_return_url: https://app.josi.example.com/
      flows:
        login:
          ui_url: https://app.josi.example.com/login
        registration:
          ui_url: https://app.josi.example.com/registration
    identity:
      default_schema_id: default
      schemas:
        - id: default
          url: file:///etc/config/identity.schema.json
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kratos
  namespace: josi
spec:
  replicas: 2
  selector:
    matchLabels:
      app: kratos
  template:
    metadata:
      labels:
        app: kratos
    spec:
      containers:
      - name: kratos
        image: oryd/kratos:v0.11.1
        ports:
        - containerPort: 4433
        - containerPort: 4434
        command: ["kratos"]
        args: ["serve", "--config", "/etc/config/kratos.yml"]
        volumeMounts:
        - name: kratos-config
          mountPath: /etc/config
      volumes:
      - name: kratos-config
        configMap:
          name: kratos-config
```

## Migration Strategy

### Step 1: Choose Your Solution

| Solution | Best For | Complexity | Features |
|----------|----------|------------|----------|
| **Authlib** | Simple OAuth integration | Low | Social login only |
| **FastAPI-Users** | Complete auth system | Medium | Full user management |
| **Keycloak** | Enterprise | High | Advanced IAM features |
| **Ory Kratos** | Cloud-native | High | API-first identity |

### Step 2: Update User Model

```python
# src/josi/models/user_model.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, nullable=False)
    name: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    
    # OAuth fields
    oauth_provider: Optional[str] = Field(default=None, nullable=True)
    oauth_provider_id: Optional[str] = Field(default=None, nullable=True)
    
    # Profile fields
    avatar_url: Optional[str] = Field(default=None, nullable=True)
    phone: Optional[str] = Field(default=None, nullable=True)
    
    # Multi-factor auth
    mfa_enabled: bool = Field(default=False)
    mfa_secret: Optional[str] = Field(default=None, nullable=True)

class User(UserBase, table=True):
    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.organization_id")
    hashed_password: Optional[str] = Field(default=None, nullable=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None, nullable=True)
    
    # Relationships
    organization: "Organization" = Relationship(back_populates="users")
    sessions: List["UserSession"] = Relationship(back_populates="user")
```

### Step 3: Environment Configuration

```bash
# .env
# OAuth Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Keycloak (if using)
KEYCLOAK_URL=https://keycloak.example.com
KEYCLOAK_REALM=josi
KEYCLOAK_CLIENT_ID=josi-api
KEYCLOAK_CLIENT_SECRET=your-keycloak-secret

# Frontend URLs
FRONTEND_URL=https://app.josi.example.com
API_URL=https://api.josi.example.com
```

### Step 4: Update Security Middleware

```python
# src/josi/core/auth_middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional

class AuthMiddleware(BaseHTTPMiddleware):
    """Unified authentication middleware supporting multiple auth methods."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in ["/docs", "/openapi.json", "/health", "/api/v1/oauth/login"]:
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        api_key = request.headers.get("X-API-Key")
        
        # Try JWT token first
        if auth_header and auth_header.startswith("Bearer "):
            request.state.auth_type = "jwt"
            request.state.token = auth_header.split(" ")[1]
        # Try API key
        elif api_key:
            request.state.auth_type = "api_key"
            request.state.api_key = api_key
        # OAuth session cookie
        elif request.cookies.get("session"):
            request.state.auth_type = "session"
            request.state.session_id = request.cookies.get("session")
        else:
            # No authentication provided
            if not request.url.path.startswith("/api/v1/oauth"):
                raise HTTPException(status_code=401, detail="Authentication required")
        
        response = await call_next(request)
        return response
```

## Frontend Integration

### React Example

```typescript
// AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  user: User | null;
  login: (provider: 'google' | 'github' | 'email') => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  
  const login = async (provider: string) => {
    if (provider === 'email') {
      // Handle email/password login
    } else {
      // Redirect to OAuth provider
      window.location.href = `${API_URL}/api/v1/oauth/login/${provider}`;
    }
  };
  
  const logout = async () => {
    await fetch(`${API_URL}/api/v1/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    setUser(null);
  };
  
  // Handle OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    
    if (token) {
      localStorage.setItem('access_token', token);
      // Fetch user profile
      fetchUserProfile();
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);
  
  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## Security Best Practices

1. **Token Storage**
   - Use httpOnly cookies for web apps
   - Secure storage for mobile apps
   - Never store tokens in localStorage for sensitive data

2. **PKCE Flow**
   - Use PKCE for public clients (SPAs, mobile apps)
   - Prevents authorization code interception

3. **Token Rotation**
   - Implement refresh token rotation
   - Short-lived access tokens (15-30 minutes)
   - Long-lived refresh tokens with rotation

4. **Multi-Factor Authentication**
   - Support TOTP (Google Authenticator)
   - WebAuthn for passwordless
   - SMS as fallback only

5. **Session Management**
   - Track active sessions
   - Allow users to revoke sessions
   - Implement "remember me" securely

## Testing OAuth

```python
# tests/test_oauth.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_google_oauth_flow(async_client: AsyncClient):
    """Test Google OAuth login flow."""
    # Mock Google OAuth response
    with patch('authlib.integrations.starlette_client.OAuth.google') as mock_google:
        mock_token = {
            'userinfo': {
                'email': 'test@example.com',
                'name': 'Test User',
                'sub': '12345'
            }
        }
        mock_google.authorize_access_token.return_value = mock_token
        
        # Test callback
        response = await async_client.get(
            "/api/v1/oauth/callback/google?code=test-code"
        )
        
        assert response.status_code == 302
        assert 'token=' in response.headers['location']
```

## Deployment Considerations

1. **Environment Variables**
   - Store OAuth secrets in Secret Manager
   - Use different credentials per environment

2. **Redirect URLs**
   - Configure allowed redirect URLs in OAuth providers
   - Use environment-specific URLs

3. **HTTPS Required**
   - OAuth requires HTTPS in production
   - Use proper SSL certificates

4. **Rate Limiting**
   - Implement rate limiting on auth endpoints
   - Prevent brute force attacks

5. **Monitoring**
   - Log authentication events
   - Monitor failed login attempts
   - Alert on suspicious activity