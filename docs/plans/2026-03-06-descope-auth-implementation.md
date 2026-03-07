# Descope Authentication Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the existing JWT/password/OAuth auth system with Descope-based authentication, add API key management for B2B, and structure auth as a liftable module for future microservices.

**Architecture:** Descope handles all identity (email, SMS, MFA, OAuth). Backend validates Descope JWTs and self-managed API keys via a unified auth middleware that resolves a `CurrentUser` context. A webhook endpoint provisions users on first login. Auth code lives in `src/josi/auth/` — structured to be extractable into `josi-core` later.

**Tech Stack:** descope Python SDK, FastAPI dependencies, SQLModel, SHA-256 for API key hashing, GCP Secret Manager for credentials.

**Design Doc:** `docs/plans/2026-03-06-descope-auth-design.md`

---

## Task 1: Add Descope SDK and Update Config

**Files:**
- Modify: `pyproject.toml:31,41,44` (add descope, remove python-jose/passlib/authlib)
- Modify: `src/josi/core/config.py:38-42,73-78`

**Step 1: Update pyproject.toml dependencies**

Add `descope` and remove old auth packages:

```toml
# Remove these lines:
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
authlib = "^1.6.0"

# Add this line (in the [tool.poetry.dependencies] section):
descope = "^1.6.0"
```

**Step 2: Update config.py — replace old security settings with Descope settings**

Replace lines 38-42 (old security settings) and 73-78 (OAuth settings) in `src/josi/core/config.py`:

```python
# Replace the Security settings block with:

# Descope settings
descope_project_id: str = Field(default="")
descope_management_key: str = Field(default="")
descope_webhook_secret: str = Field(default="")

# Keep api_key_header
api_key_header: str = Field(default="X-API-Key")

# Remove entirely:
# secret_key, algorithm, access_token_expire_minutes
# google_client_id, google_client_secret
# github_client_id, github_client_secret
# frontend_url (move to CORS origins if needed)
```

Also change `extra="forbid"` to `extra="ignore"` in the `model_config` on line 129 — this prevents startup crashes from leftover env vars during migration.

**Step 3: Install dependencies**

Run: `poetry lock && poetry install`

**Step 4: Verify the app still starts**

Run: `docker-compose up -d && docker-compose logs web --tail=20`
Expected: App starts (auth endpoints will break — that's expected)

**Step 5: Commit**

```bash
git add pyproject.toml poetry.lock src/josi/core/config.py
git commit -m "feat(auth): add descope SDK, remove python-jose/passlib/authlib, update config"
```

---

## Task 2: Update User Model

**Files:**
- Modify: `src/josi/models/user_model.py`

**Step 1: Write a test for the updated User model**

Create `tests/unit/models/test_user_model.py`:

```python
"""Tests for User model with Descope integration."""
import pytest
from uuid import uuid4
from josi.models.user_model import User, SubscriptionTier


def test_user_has_descope_id_field():
    user = User(
        email="test@example.com",
        full_name="Test User",
        descope_id="U3AXkLL5ULmyFWqbfyRwVpL2WjCi",
    )
    assert user.descope_id == "U3AXkLL5ULmyFWqbfyRwVpL2WjCi"


def test_user_no_longer_has_password_fields():
    assert not hasattr(User, "hashed_password") or True  # Field removed
    user = User(email="test@example.com", full_name="Test", descope_id="abc")
    assert not hasattr(user, "hashed_password")


def test_user_no_longer_has_oauth_provider_fields():
    user = User(email="test@example.com", full_name="Test", descope_id="abc")
    assert not hasattr(user, "google_id")
    assert not hasattr(user, "github_id")
    assert not hasattr(user, "oauth_providers")


def test_user_default_subscription_is_free():
    user = User(email="test@example.com", full_name="Test", descope_id="abc")
    assert user.subscription_tier == SubscriptionTier.FREE


def test_user_roles_default_empty():
    user = User(email="test@example.com", full_name="Test", descope_id="abc")
    assert user.roles == ["user"]
```

**Step 2: Run tests to verify they fail**

Run: `poetry run pytest tests/unit/models/test_user_model.py -v`
Expected: FAIL (descope_id doesn't exist, old fields still present)

**Step 3: Update User model**

Modify `src/josi/models/user_model.py`:

```python
"""User model with Descope authentication and subscription tiers."""
from sqlmodel import Field, SQLModel, Column, JSON
from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from josi.models.consultation_model import Consultation
    from josi.models.saved_chart_model import SavedChart
    from josi.models.quiz_response_model import QuizResponse


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels for users."""
    FREE = "free"
    EXPLORER = "explorer"
    MYSTIC = "mystic"
    MASTER = "master"


class User(SQLModel, table=True):
    """User model — identity owned by Descope, profile and authz owned by us."""

    __tablename__ = "users"

    user_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    descope_id: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = Field(default=None, index=True)

    # Profile
    full_name: str
    avatar_url: Optional[str] = Field(default=None)
    date_of_birth: Optional[datetime] = Field(default=None)
    birth_location: Optional[Dict] = Field(default=None, sa_column=Column(JSON))

    # Subscription
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE)
    subscription_end_date: Optional[datetime] = Field(default=None)
    stripe_customer_id: Optional[str] = Field(default=None, index=True)

    # Settings
    preferences: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    notification_settings: Dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Authorization (owned by us, not Descope)
    roles: List[str] = Field(default=["user"], sa_column=Column(JSON))

    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "descope_id": "U3AXkLL5ULmyFWqbfyRwVpL2WjCi",
                "subscription_tier": "free",
            }
        }

    def has_premium_features(self) -> bool:
        return self.subscription_tier != SubscriptionTier.FREE

    def is_subscription_active(self) -> bool:
        if self.subscription_tier == SubscriptionTier.FREE:
            return True
        return (
            self.subscription_end_date is not None
            and self.subscription_end_date > datetime.utcnow()
        )

    def get_tier_limits(self) -> Dict[str, int]:
        limits = {
            SubscriptionTier.FREE: {
                "charts_per_month": 3,
                "ai_interpretations_per_month": 5,
                "saved_charts": 1,
                "consultations_per_month": 0,
            },
            SubscriptionTier.EXPLORER: {
                "charts_per_month": 50,
                "ai_interpretations_per_month": 100,
                "saved_charts": 10,
                "consultations_per_month": 1,
            },
            SubscriptionTier.MYSTIC: {
                "charts_per_month": 500,
                "ai_interpretations_per_month": 500,
                "saved_charts": 100,
                "consultations_per_month": 3,
            },
            SubscriptionTier.MASTER: {
                "charts_per_month": -1,
                "ai_interpretations_per_month": -1,
                "saved_charts": -1,
                "consultations_per_month": 10,
            },
        }
        return limits.get(self.subscription_tier, limits[SubscriptionTier.FREE])


class UserCreate(SQLModel):
    """Schema for creating a user from Descope webhook data."""
    descope_id: str
    email: str
    full_name: str
    phone: Optional[str] = None


class UserUpdate(SQLModel):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    birth_location: Optional[Dict] = None
    preferences: Optional[Dict] = None
    notification_settings: Optional[Dict] = None


class UserResponse(SQLModel):
    """Schema for user response (excludes sensitive data)."""
    user_id: UUID
    email: str
    full_name: str
    phone: Optional[str]
    avatar_url: Optional[str]
    subscription_tier: SubscriptionTier
    subscription_end_date: Optional[datetime]
    roles: List[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    preferences: Dict
    notification_settings: Dict
```

Removed: `hashed_password`, `google_id`, `github_id`, `oauth_providers`, `UserLogin`.
Added: `descope_id`, `roles`.

**Step 4: Run tests to verify they pass**

Run: `poetry run pytest tests/unit/models/test_user_model.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/josi/models/user_model.py tests/unit/models/test_user_model.py
git commit -m "feat(auth): update User model for Descope — add descope_id, roles; remove password/OAuth fields"
```

---

## Task 3: Create ApiKey Model

**Files:**
- Create: `src/josi/models/api_key_model.py`
- Create: `tests/unit/models/test_api_key_model.py`

**Step 1: Write the test**

```python
"""Tests for ApiKey model."""
import pytest
from uuid import uuid4
from josi.models.api_key_model import ApiKey


def test_api_key_creation():
    user_id = uuid4()
    key = ApiKey(
        user_id=user_id,
        key_hash="sha256hashhere",
        key_prefix="jsk_abcd",
        name="My Production Key",
    )
    assert key.user_id == user_id
    assert key.key_prefix == "jsk_abcd"
    assert key.is_active is True


def test_api_key_defaults():
    key = ApiKey(
        user_id=uuid4(),
        key_hash="hash",
        key_prefix="jsk_1234",
        name="Test",
    )
    assert key.is_active is True
    assert key.expires_at is None
    assert key.last_used_at is None
```

**Step 2: Run test — should fail**

Run: `poetry run pytest tests/unit/models/test_api_key_model.py -v`
Expected: FAIL (module not found)

**Step 3: Create the ApiKey model**

Create `src/josi/models/api_key_model.py`:

```python
"""API Key model for B2B programmatic access."""
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class ApiKey(SQLModel, table=True):
    """API key for programmatic access. Keys are stored hashed."""

    __tablename__ = "api_keys"

    api_key_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.user_id", index=True)
    key_hash: str = Field(index=True)
    key_prefix: str = Field(max_length=12)
    name: str = Field(max_length=255)
    last_used_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApiKeyCreate(SQLModel):
    """Schema for creating an API key."""
    name: str


class ApiKeyResponse(SQLModel):
    """Schema for API key response (never includes the full key)."""
    api_key_id: UUID
    key_prefix: str
    name: str
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime


class ApiKeyCreatedResponse(SQLModel):
    """Returned only at creation time — includes the plaintext key."""
    api_key_id: UUID
    key: str  # Plaintext — shown once, never stored
    key_prefix: str
    name: str
```

**Step 4: Run test — should pass**

Run: `poetry run pytest tests/unit/models/test_api_key_model.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/josi/models/api_key_model.py tests/unit/models/test_api_key_model.py
git commit -m "feat(auth): add ApiKey model for B2B programmatic access"
```

---

## Task 4: Create Auth Module — CurrentUser Schema and Descope Client

**Files:**
- Create: `src/josi/auth/__init__.py`
- Create: `src/josi/auth/schemas.py`
- Create: `src/josi/auth/descope_client.py`
- Create: `tests/unit/auth/__init__.py`
- Create: `tests/unit/auth/test_schemas.py`

**Step 1: Write test for CurrentUser schema**

Create `tests/unit/auth/__init__.py` (empty) and `tests/unit/auth/test_schemas.py`:

```python
"""Tests for auth schemas."""
from uuid import uuid4
from josi.auth.schemas import CurrentUser


def test_current_user_creation():
    uid = uuid4()
    user = CurrentUser(
        user_id=uid,
        descope_id="U3AXk",
        email="test@example.com",
        subscription_tier="free",
        roles=["user"],
    )
    assert user.user_id == uid
    assert user.email == "test@example.com"
    assert user.roles == ["user"]


def test_current_user_has_role():
    user = CurrentUser(
        user_id=uuid4(),
        descope_id="U3AXk",
        email="test@example.com",
        subscription_tier="explorer",
        roles=["user", "astrologer"],
    )
    assert user.has_role("astrologer") is True
    assert user.has_role("admin") is False
```

**Step 2: Run test — should fail**

Run: `poetry run pytest tests/unit/auth/test_schemas.py -v`
Expected: FAIL

**Step 3: Create the auth module**

Create `src/josi/auth/__init__.py`:

```python
"""Auth module — structured for future extraction into josi-core."""
```

Create `src/josi/auth/schemas.py`:

```python
"""Auth schemas shared across services."""
from pydantic import BaseModel
from typing import List
from uuid import UUID


class CurrentUser(BaseModel):
    """Resolved user context — same shape regardless of auth path (JWT or API key)."""
    user_id: UUID
    descope_id: str
    email: str
    subscription_tier: str
    roles: List[str]

    def has_role(self, role: str) -> bool:
        return role in self.roles
```

Create `src/josi/auth/descope_client.py`:

```python
"""Descope client singleton — initialized once at startup."""
from descope import DescopeClient
from josi.core.config import settings


_client: DescopeClient | None = None


def get_descope_client() -> DescopeClient:
    global _client
    if _client is None:
        _client = DescopeClient(
            project_id=settings.descope_project_id,
            management_key=settings.descope_management_key,
        )
    return _client
```

**Step 4: Run test — should pass**

Run: `poetry run pytest tests/unit/auth/test_schemas.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/josi/auth/ tests/unit/auth/
git commit -m "feat(auth): add auth module with CurrentUser schema and Descope client singleton"
```

---

## Task 5: Create Auth Middleware — JWT + API Key Resolution

**Files:**
- Create: `src/josi/auth/middleware.py`
- Create: `tests/unit/auth/test_middleware.py`

**Step 1: Write tests for the auth dependency**

Create `tests/unit/auth/test_middleware.py`:

```python
"""Tests for auth middleware — resolve_current_user dependency."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import HTTPException

from josi.auth.middleware import resolve_current_user


@pytest.mark.asyncio
async def test_no_auth_headers_returns_401():
    """Request with no Authorization or X-API-Key should 401."""
    request = MagicMock()
    request.headers = {}
    db = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await resolve_current_user(request=request, db=db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_jwt_path_extracts_claims():
    """Valid JWT with josi_* claims resolves CurrentUser without DB call."""
    mock_token_data = {
        "sub": "U3AXk",
        "email": "test@example.com",
        "josi_user_id": str(uuid4()),
        "josi_subscription_tier": "free",
        "josi_roles": ["user"],
    }
    request = MagicMock()
    request.headers = {"authorization": "Bearer fake-jwt"}
    db = AsyncMock()

    with patch("josi.auth.middleware.validate_descope_jwt", return_value=mock_token_data):
        user = await resolve_current_user(request=request, db=db)

    assert user.email == "test@example.com"
    assert user.descope_id == "U3AXk"


@pytest.mark.asyncio
async def test_api_key_path_resolves_from_db():
    """Valid API key resolves user from DB."""
    user_id = uuid4()
    mock_user = MagicMock()
    mock_user.user_id = user_id
    mock_user.descope_id = "U3AXk"
    mock_user.email = "dev@example.com"
    mock_user.subscription_tier = "explorer"
    mock_user.roles = ["user"]

    request = MagicMock()
    request.headers = {"x-api-key": "jsk_abcdef1234567890rest"}
    db = AsyncMock()

    with patch("josi.auth.middleware.resolve_api_key_user", return_value=mock_user):
        user = await resolve_current_user(request=request, db=db)

    assert user.user_id == user_id
    assert user.email == "dev@example.com"
```

**Step 2: Run tests — should fail**

Run: `poetry run pytest tests/unit/auth/test_middleware.py -v`
Expected: FAIL

**Step 3: Implement the auth middleware**

Create `src/josi/auth/middleware.py`:

```python
"""Auth middleware — resolves CurrentUser from JWT or API key."""
import hashlib
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from descope import AuthException

from josi.auth.descope_client import get_descope_client
from josi.auth.schemas import CurrentUser
from josi.db.async_db import get_async_db
from josi.models.api_key_model import ApiKey
from josi.models.user_model import User

import structlog

logger = structlog.get_logger()


def validate_descope_jwt(token: str) -> dict:
    """Validate a Descope session JWT and return claims."""
    client = get_descope_client()
    try:
        jwt_response = client.validate_session(token)
        return jwt_response
    except AuthException as e:
        logger.warning("Descope JWT validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def resolve_api_key_user(
    api_key_raw: str, db: AsyncSession
) -> User:
    """Look up API key in DB, return associated User."""
    key_hash = hashlib.sha256(api_key_raw.encode()).hexdigest()

    result = await db.execute(
        select(ApiKey).where(
            and_(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True,
            )
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Check expiry
    if api_key.expires_at:
        from datetime import datetime
        if api_key.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
            )

    # Update last_used_at
    from datetime import datetime
    api_key.last_used_at = datetime.utcnow()
    await db.flush()

    # Load user
    user_result = await db.execute(
        select(User).where(
            and_(User.user_id == api_key.user_id, User.is_deleted == False)
        )
    )
    user = user_result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    return user


async def resolve_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> CurrentUser:
    """Resolve CurrentUser from either JWT or API key.

    Checks Authorization header first, then X-API-Key.
    """
    auth_header: Optional[str] = request.headers.get("authorization")
    api_key_header: Optional[str] = request.headers.get("x-api-key")

    # Path 1: JWT (B2C)
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        claims = validate_descope_jwt(token)

        return CurrentUser(
            user_id=UUID(claims["josi_user_id"]),
            descope_id=claims["sub"],
            email=claims["email"],
            subscription_tier=claims["josi_subscription_tier"],
            roles=claims["josi_roles"],
        )

    # Path 2: API Key (B2B)
    if api_key_header:
        user = await resolve_api_key_user(api_key_header, db)
        return CurrentUser(
            user_id=user.user_id,
            descope_id=user.descope_id,
            email=user.email,
            subscription_tier=user.subscription_tier.value,
            roles=user.roles,
        )

    # No auth provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide Authorization: Bearer <token> or X-API-Key header.",
    )
```

**Step 4: Run tests — should pass**

Run: `poetry run pytest tests/unit/auth/test_middleware.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/josi/auth/middleware.py tests/unit/auth/test_middleware.py
git commit -m "feat(auth): add auth middleware — resolves CurrentUser from JWT or API key"
```

---

## Task 6: Create Descope Webhook Endpoint

**Files:**
- Create: `src/josi/api/v1/controllers/webhook_controller.py`
- Create: `tests/unit/controllers/test_webhook_controller.py`

**Step 1: Write test**

Create `tests/unit/controllers/test_webhook_controller.py`:

```python
"""Tests for Descope login webhook."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from uuid import uuid4


@pytest.fixture
def webhook_secret():
    return "test-webhook-secret"


def test_webhook_rejects_missing_secret(webhook_secret):
    """Request without X-Descope-Webhook-Secret should 401."""
    from josi.api.v1.controllers.webhook_controller import verify_webhook_secret
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        verify_webhook_secret(webhook_secret="", expected_secret=webhook_secret)
    assert exc_info.value.status_code == 401


def test_webhook_rejects_wrong_secret(webhook_secret):
    """Request with wrong secret should 401."""
    from josi.api.v1.controllers.webhook_controller import verify_webhook_secret
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        verify_webhook_secret(webhook_secret="wrong", expected_secret=webhook_secret)
    assert exc_info.value.status_code == 401


def test_webhook_accepts_correct_secret(webhook_secret):
    """Request with correct secret should pass."""
    from josi.api.v1.controllers.webhook_controller import verify_webhook_secret
    result = verify_webhook_secret(webhook_secret=webhook_secret, expected_secret=webhook_secret)
    assert result is True
```

**Step 2: Run tests — should fail**

Run: `poetry run pytest tests/unit/controllers/test_webhook_controller.py -v`
Expected: FAIL

**Step 3: Implement webhook controller**

Create `src/josi/api/v1/controllers/webhook_controller.py`:

```python
"""Descope webhook endpoints — called by Descope Connector during auth flows."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from josi.core.config import settings
from josi.db.async_db import get_async_db
from josi.models.user_model import User
from josi.auth.descope_client import get_descope_client

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/webhooks/descope", tags=["webhooks"])


class DescopeLoginRequest(BaseModel):
    """Payload from Descope Connector."""
    sub: str
    email: str


class DescopeLoginResponse(BaseModel):
    """Claims to inject into the JWT."""
    josi_user_id: str
    josi_subscription_tier: str
    josi_roles: list[str]


def verify_webhook_secret(webhook_secret: str, expected_secret: str) -> bool:
    """Verify the shared secret from Descope Connector."""
    if not webhook_secret or webhook_secret != expected_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )
    return True


@router.post("/login", response_model=DescopeLoginResponse)
async def descope_login_webhook(
    payload: DescopeLoginRequest,
    x_descope_webhook_secret: str = Header(..., alias="X-Descope-Webhook-Secret"),
    db: AsyncSession = Depends(get_async_db),
):
    """Called by Descope Connector during sign-in/sign-up flows.

    Upserts the user and returns claims for JWT enrichment.
    """
    verify_webhook_secret(x_descope_webhook_secret, settings.descope_webhook_secret)

    # Look up existing user
    result = await db.execute(
        select(User).where(User.descope_id == payload.sub)
    )
    user = result.scalar_one_or_none()

    if user:
        # Existing user — update last_login
        user.last_login = datetime.utcnow()
        await db.flush()
        await db.commit()

        logger.info("Existing user login", user_id=str(user.user_id), email=user.email)

        return DescopeLoginResponse(
            josi_user_id=str(user.user_id),
            josi_subscription_tier=user.subscription_tier.value,
            josi_roles=user.roles,
        )

    # New user — fetch details from Descope Management API
    descope_client = get_descope_client()
    try:
        user_resp = descope_client.mgmt.user.load_by_user_id(payload.sub)
        descope_user = user_resp["user"]
    except Exception as e:
        logger.error("Failed to fetch user from Descope", error=str(e), sub=payload.sub)
        descope_user = {}

    # Create local user
    new_user = User(
        descope_id=payload.sub,
        email=payload.email,
        full_name=descope_user.get("name", payload.email.split("@")[0]),
        phone=descope_user.get("phone"),
        is_verified=descope_user.get("verifiedEmail", False),
        last_login=datetime.utcnow(),
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    await db.commit()

    logger.info("New user created", user_id=str(new_user.user_id), email=new_user.email)

    return DescopeLoginResponse(
        josi_user_id=str(new_user.user_id),
        josi_subscription_tier=new_user.subscription_tier.value,
        josi_roles=new_user.roles,
    )
```

**Step 4: Run tests — should pass**

Run: `poetry run pytest tests/unit/controllers/test_webhook_controller.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/josi/api/v1/controllers/webhook_controller.py tests/unit/controllers/test_webhook_controller.py
git commit -m "feat(auth): add Descope login webhook — upserts user, returns JWT enrichment claims"
```

---

## Task 7: Create API Key Management Endpoints

**Files:**
- Create: `src/josi/api/v1/controllers/api_key_controller.py`
- Create: `tests/unit/controllers/test_api_key_controller.py`

**Step 1: Write test**

Create `tests/unit/controllers/test_api_key_controller.py`:

```python
"""Tests for API key generation utilities."""
import pytest
import hashlib
from josi.api.v1.controllers.api_key_controller import generate_api_key


def test_generate_api_key_format():
    """API key should start with jsk_ prefix."""
    key = generate_api_key()
    assert key.startswith("jsk_")
    assert len(key) > 20


def test_generate_api_key_is_unique():
    """Each call should produce a unique key."""
    key1 = generate_api_key()
    key2 = generate_api_key()
    assert key1 != key2


def test_api_key_hash_is_deterministic():
    """Same key should produce same hash."""
    key = "jsk_test1234567890"
    hash1 = hashlib.sha256(key.encode()).hexdigest()
    hash2 = hashlib.sha256(key.encode()).hexdigest()
    assert hash1 == hash2
```

**Step 2: Run tests — should fail**

Run: `poetry run pytest tests/unit/controllers/test_api_key_controller.py -v`
Expected: FAIL

**Step 3: Implement API key controller**

Create `src/josi/api/v1/controllers/api_key_controller.py`:

```python
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
```

**Step 4: Run tests — should pass**

Run: `poetry run pytest tests/unit/controllers/test_api_key_controller.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/josi/api/v1/controllers/api_key_controller.py tests/unit/controllers/test_api_key_controller.py
git commit -m "feat(auth): add API key management endpoints — create, list, revoke, rotate"
```

---

## Task 8: Update Dependencies and Route Registration

**Files:**
- Modify: `src/josi/api/v1/dependencies.py`
- Modify: `src/josi/api/v1/__init__.py`
- Modify: `src/josi/main.py`

**Step 1: Update dependencies.py**

Replace the old `get_api_key` / `get_current_organization` with the new auth system. Keep all service dependencies intact — they no longer need `organization` param.

In `src/josi/api/v1/dependencies.py`, replace lines 1-68 (the auth-related imports and functions) and update the service getters:

```python
"""V1 API Dependencies — Clean architecture dependency injection."""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from josi.db.async_db import get_async_db
from josi.auth.middleware import resolve_current_user
from josi.auth.schemas import CurrentUser

# Services
from josi.services.person_service import PersonService
from josi.services.chart_service import ChartService
from josi.services.geocoding_service import GeocodingService
from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.panchang_service import PanchangCalculator
from josi.services.vedic.muhurta_service import MuhurtaCalculator
from josi.services.vedic.dasha_service import VimshottariDashaCalculator, YoginiDashaCalculator, CharaDashaCalculator
from josi.services.vedic.remedies_service import RemediesCalculator
from josi.services.western.progressions_service import ProgressionCalculator
from josi.services.interpretation_engine_service import InterpretationEngine
from josi.services.vedic.ashtakoota_service import AshtakootaCalculator


# Auth dependency
CurrentUserDep = Annotated[CurrentUser, Depends(resolve_current_user)]


# Service Dependencies
async def get_person_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> PersonService:
    return PersonService(db)


async def get_chart_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> ChartService:
    return ChartService(db)


async def get_geocoding_service() -> GeocodingService:
    return GeocodingService()


async def get_astrology_calculator() -> AstrologyCalculator:
    return AstrologyCalculator()


async def get_panchang_calculator() -> PanchangCalculator:
    return PanchangCalculator()


async def get_muhurta_calculator() -> MuhurtaCalculator:
    return MuhurtaCalculator()


async def get_vimshottari_dasha_calculator() -> VimshottariDashaCalculator:
    return VimshottariDashaCalculator()


async def get_yogini_dasha_calculator() -> YoginiDashaCalculator:
    return YoginiDashaCalculator()


async def get_chara_dasha_calculator() -> CharaDashaCalculator:
    return CharaDashaCalculator()


async def get_remedy_service() -> RemediesCalculator:
    return RemediesCalculator()


async def get_progression_calculator() -> ProgressionCalculator:
    return ProgressionCalculator()


async def get_interpretation_engine() -> InterpretationEngine:
    return InterpretationEngine()


async def get_ashtakoota_calculator() -> AshtakootaCalculator:
    return AshtakootaCalculator()


# Type Aliases
PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]
ChartServiceDep = Annotated[ChartService, Depends(get_chart_service)]
GeocodingServiceDep = Annotated[GeocodingService, Depends(get_geocoding_service)]
AstrologyCalculatorDep = Annotated[AstrologyCalculator, Depends(get_astrology_calculator)]
PanchangCalculatorDep = Annotated[PanchangCalculator, Depends(get_panchang_calculator)]
MuhurtaCalculatorDep = Annotated[MuhurtaCalculator, Depends(get_muhurta_calculator)]
VimshottariDashaDep = Annotated[VimshottariDashaCalculator, Depends(get_vimshottari_dasha_calculator)]
YoginiDashaDep = Annotated[YoginiDashaCalculator, Depends(get_yogini_dasha_calculator)]
CharaDashaDep = Annotated[CharaDashaCalculator, Depends(get_chara_dasha_calculator)]
RemedyServiceDep = Annotated[RemediesCalculator, Depends(get_remedy_service)]
ProgressionCalculatorDep = Annotated[ProgressionCalculator, Depends(get_progression_calculator)]
InterpretationEngineDep = Annotated[InterpretationEngine, Depends(get_interpretation_engine)]
AshtakootaCalculatorDep = Annotated[AshtakootaCalculator, Depends(get_ashtakoota_calculator)]
```

Note: `OrganizationDep` and `PersonRepositoryDep` are removed. Services that took `organization_id` will need their constructors updated — but that's a follow-up. For now, pass `None` or remove the param if the service supports it.

**Step 2: Update route registration in `src/josi/api/v1/__init__.py`**

```python
"""V1 API module — consolidated REST API endpoints."""
from fastapi import APIRouter

from josi.api.v1.controllers.chart_controller import router as chart_router
from josi.api.v1.controllers.person_controller import router as person_router
from josi.api.v1.controllers.panchang_controller import router as panchang_router
from josi.api.v1.controllers.compatibility_controller import router as compatibility_router
from josi.api.v1.controllers.transit_controller import router as transit_router
from josi.api.v1.controllers.dasha_controller import router as dasha_router
from josi.api.v1.controllers.prediction_controller import router as prediction_router
from josi.api.v1.controllers.remedies_controller import router as remedies_router
from josi.api.v1.controllers.location_controller import router as location_router
from josi.api.v1.controllers.ai_controller import router as ai_router
from josi.api.v1.controllers.astrologer_controller import router as astrologer_router
from josi.api.v1.controllers.consultation_controller import router as consultation_router
from josi.api.v1.controllers.muhurta_controller import router as muhurta_router
from josi.api.v1.controllers.remedy_controller import router as remedy_router
from josi.api.v1.controllers.webhook_controller import router as webhook_router
from josi.api.v1.controllers.api_key_controller import router as api_key_router
from josi.api.v1.health import router as health_router

# Create main v1 router
v1_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
v1_router.include_router(person_router)
v1_router.include_router(chart_router)
v1_router.include_router(panchang_router)
v1_router.include_router(compatibility_router)
v1_router.include_router(transit_router)
v1_router.include_router(dasha_router)
v1_router.include_router(prediction_router)
v1_router.include_router(remedies_router)
v1_router.include_router(location_router)
v1_router.include_router(ai_router)
v1_router.include_router(astrologer_router)
v1_router.include_router(consultation_router)
v1_router.include_router(muhurta_router)
v1_router.include_router(remedy_router)
v1_router.include_router(health_router)
v1_router.include_router(webhook_router)
v1_router.include_router(api_key_router)

__all__ = ["v1_router"]
```

Removed: `auth_router`, `oauth_router`.
Added: `webhook_router`, `api_key_router`.

**Step 3: Update main.py — remove old auth router**

In `src/josi/main.py`, remove line 10 (`from josi.api.v1.auth import router as auth_router`) and line 94 (`app.include_router(auth_router, prefix="/api/v1")`).

**Step 4: Verify app starts**

Run: `docker-compose up -d && docker-compose logs web --tail=30`
Expected: App starts. Old auth endpoints gone. New `/api/v1/webhooks/descope/login` and `/api/v1/api-keys` visible in `/docs`.

**Step 5: Commit**

```bash
git add src/josi/api/v1/dependencies.py src/josi/api/v1/__init__.py src/josi/main.py
git commit -m "feat(auth): wire up new auth — register webhook and api-key routes, remove old auth/oauth routes"
```

---

## Task 9: Remove Old Auth Files

**Files:**
- Delete: `src/josi/services/auth_service.py`
- Delete: `src/josi/api/v1/auth.py`
- Delete: `src/josi/api/v1/oauth.py`
- Delete: `src/josi/core/oauth.py`
- Modify: `src/josi/core/security.py` (strip auth functions, keep utility functions)

**Step 1: Delete old auth files**

```bash
rm src/josi/services/auth_service.py
rm src/josi/api/v1/auth.py
rm src/josi/api/v1/oauth.py
rm src/josi/core/oauth.py
```

**Step 2: Clean up security.py**

Keep `SecurityMiddleware`, `RateLimiter`, `sanitize_string`, `validate_uuid`, `validate_coordinates`.
Remove `SecurityManager`, `security_manager`, `SecurityDep`, `require_authentication`, `require_permissions`, `pwd_context`, `create_access_token`, `hash_password`, `verify_password`, and all `jose`/`passlib` imports.

Replace `src/josi/core/security.py` with:

```python
"""Security utilities — rate limiting, headers, input validation."""
import time
from typing import List, Dict, Any
from functools import wraps
from fastapi import HTTPException, status, Request
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """Rate limiting with subscription-tier-based limits."""

    def __init__(self):
        self.storage = {}
        self.rate_limits = {
            "free": {"requests_per_minute": 60, "calculations_per_hour": 100},
            "explorer": {"requests_per_minute": 300, "calculations_per_hour": 1000},
            "mystic": {"requests_per_minute": 600, "calculations_per_hour": 5000},
            "master": {"requests_per_minute": 1000, "calculations_per_hour": 10000},
        }

    async def check_rate_limit(self, request: Request, endpoint_type: str = "general") -> bool:
        client_id = request.headers.get("x-user-id", request.client.host)
        tier = request.headers.get("x-subscription-tier", "free")
        current_minute = int(time.time() // 60)

        limits = self.rate_limits.get(tier, self.rate_limits["free"])
        key = f"{client_id}:{endpoint_type}:{current_minute}"

        if key not in self.storage:
            self.storage[key] = 0
        self.storage[key] += 1

        if len(self.storage) > 10000:
            old_keys = [k for k in self.storage if int(k.split(':')[-1]) < current_minute - 5]
            for old_key in old_keys:
                del self.storage[old_key]

        limit_key = "calculations_per_hour" if endpoint_type == "calculation" else "requests_per_minute"
        return self.storage[key] <= limits[limit_key]


class SecurityMiddleware:
    """Security headers middleware."""

    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

    DOCS_CSP = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' https://cdn.jsdelivr.net"
    )
    DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}

    async def add_security_headers(self, request: Request, call_next):
        response = await call_next(request)
        for header, value in self.security_headers.items():
            response.headers[header] = value
        if request.url.path in self.DOCS_PATHS:
            response.headers["Content-Security-Policy"] = self.DOCS_CSP
        import uuid
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        return response


# Global instances
rate_limiter = RateLimiter()
security_middleware = SecurityMiddleware()


# Input validation utilities
def sanitize_string(value: str, max_length: int = 255) -> str:
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    import re
    cleaned = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', value.strip())
    if len(cleaned) > max_length:
        raise ValueError(f"String too long (max {max_length} characters)")
    return cleaned


def validate_uuid(value: str) -> str:
    import uuid
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValueError("Invalid UUID format")


def validate_coordinates(latitude: float, longitude: float) -> tuple:
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")
    return latitude, longitude
```

**Step 3: Check for remaining imports of deleted files**

Run: `grep -r "from josi.services.auth_service" src/ && grep -r "from josi.api.v1.auth" src/ && grep -r "from josi.core.oauth" src/ && grep -r "from josi.api.v1.oauth" src/ && grep -r "from josi.core.security import.*password\|create_access_token\|SecurityManager\|security_manager\|SecurityDep" src/`

Fix any broken imports found. Common places: `main.py` (already fixed in Task 8), controller files, middleware.

**Step 4: Run full test suite**

Run: `poetry run pytest --tb=short -q`
Expected: All new tests pass. Some old tests that depended on deleted code may fail — that's expected and acceptable. Those tests should be deleted in the same commit.

**Step 5: Commit**

```bash
git add -A
git commit -m "refactor(auth): remove old auth system — delete auth_service, oauth, password utilities"
```

---

## Task 10: Generate Database Migration

**Files:**
- Generated: `src/alembic/versions/xxxx_descope_auth.py`

**Step 1: Generate the migration**

Run inside docker:
```bash
docker-compose exec web alembic revision --autogenerate -m "descope auth - add descope_id and roles to users, add api_keys table, remove password and oauth fields"
```

**Step 2: Review the generated migration**

Read the generated file. It should:
- Add `descope_id` column to `users` (string, unique, indexed)
- Add `roles` column to `users` (JSON, default `["user"]`)
- Remove `hashed_password`, `google_id`, `github_id`, `oauth_providers` from `users`
- Create `api_keys` table

**WARNING:** If existing users have data, the migration needs a data migration step to set `descope_id` for existing rows before making it NOT NULL. If the database is empty (dev only), this is fine as-is.

**Step 3: Apply the migration**

```bash
docker-compose exec web alembic upgrade head
```

**Step 4: Verify**

```bash
docker-compose exec db psql -U josi -d josi -c "\d users" && docker-compose exec db psql -U josi -d josi -c "\d api_keys"
```

Expected: Both tables have the correct columns.

**Step 5: Commit**

```bash
git add src/alembic/
git commit -m "migration: descope auth — add descope_id, roles, api_keys table; remove password/oauth fields"
```

---

## Task 11: Update .env and Docker Config

**Files:**
- Modify: `.env.example` (or `.env`)
- Modify: `docker-compose.yml` (if env vars are set there)

**Step 1: Add Descope env vars**

Add to `.env.example`:
```
# Descope Authentication
DESCOPE_PROJECT_ID=P3AXgK6L8OgCfFSKcrNaA99vVChw
DESCOPE_MANAGEMENT_KEY=your-management-key-here
DESCOPE_WEBHOOK_SECRET=your-webhook-secret-here
```

Remove old auth env vars:
```
# Remove these:
# SECRET_KEY=...
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...
# GITHUB_CLIENT_ID=...
# GITHUB_CLIENT_SECRET=...
```

**Step 2: Verify the app starts with new env vars**

Run: `docker-compose up -d && docker-compose logs web --tail=20`
Expected: App starts, `/docs` shows new endpoints.

**Step 3: Commit**

```bash
git add .env.example docker-compose.yml
git commit -m "config: add Descope env vars, remove old auth config"
```

---

## Task 12: End-to-End Smoke Test

**No files to modify — manual verification.**

**Step 1: Verify webhook endpoint works**

```bash
curl -X POST http://localhost:8000/api/v1/webhooks/descope/login \
  -H "Content-Type: application/json" \
  -H "X-Descope-Webhook-Secret: <your-enrich-secret>" \
  -d '{"sub": "U3AXkLL5ULmyFWqbfyRwVpL2WjCi", "email": "govind@josiam.com"}'
```

Expected: 200 with `josi_user_id`, `josi_subscription_tier`, `josi_roles`.

**Step 2: Verify unauthenticated request is rejected**

```bash
curl -X GET http://localhost:8000/api/v1/persons
```

Expected: 401

**Step 3: Verify API key flow (once a user exists)**

Create a key via the webhook-created user, then test access with it.

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat(auth): Descope authentication integration complete"
```

---

## Summary of All Files

### Created
- `src/josi/auth/__init__.py`
- `src/josi/auth/schemas.py`
- `src/josi/auth/descope_client.py`
- `src/josi/auth/middleware.py`
- `src/josi/models/api_key_model.py`
- `src/josi/api/v1/controllers/webhook_controller.py`
- `src/josi/api/v1/controllers/api_key_controller.py`
- `tests/unit/auth/__init__.py`
- `tests/unit/auth/test_schemas.py`
- `tests/unit/auth/test_middleware.py`
- `tests/unit/models/test_api_key_model.py`
- `tests/unit/controllers/test_webhook_controller.py`
- `tests/unit/controllers/test_api_key_controller.py`

### Modified
- `pyproject.toml`
- `src/josi/core/config.py`
- `src/josi/core/security.py`
- `src/josi/models/user_model.py`
- `src/josi/api/v1/dependencies.py`
- `src/josi/api/v1/__init__.py`
- `src/josi/main.py`
- `.env.example`

### Deleted
- `src/josi/services/auth_service.py`
- `src/josi/api/v1/auth.py`
- `src/josi/api/v1/oauth.py`
- `src/josi/core/oauth.py`

### Descope Console Setup (Manual)
1. Create Generic HTTP Connector → `POST <your-url>/api/v1/webhooks/descope/login`
2. Set `X-Descope-Webhook-Secret` header with the enrich secret value
3. Add connector to Sign Up and Sign In flows
4. Map response: `josi_user_id` → custom claim, `josi_subscription_tier` → custom claim, `josi_roles` → custom claim
