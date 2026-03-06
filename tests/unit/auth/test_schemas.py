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
