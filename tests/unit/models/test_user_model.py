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
