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
