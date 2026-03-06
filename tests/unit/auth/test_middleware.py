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
