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
