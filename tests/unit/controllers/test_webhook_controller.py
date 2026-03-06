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
