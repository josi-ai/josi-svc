"""Abstract auth provider interface for pluggable JWT validation."""
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Optional


class AuthProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    def validate_jwt(self, token: str) -> dict: ...

    @abstractmethod
    async def get_user_info(self, provider_user_id: str) -> Optional[dict]:
        """Fetch user details (email, full_name, phone) from the auth provider.

        Returns dict with keys: email, full_name, phone. Or None on failure.
        """
        ...

    @abstractmethod
    async def set_user_metadata(self, provider_user_id: str, metadata: dict) -> bool:
        """Set public metadata on the auth provider user (e.g. Clerk publicMetadata).

        Returns True on success, False on failure.
        """
        ...


@lru_cache()
def get_auth_provider() -> AuthProvider:
    from josi.core.config import settings

    name = settings.auth_provider_name
    if name == "clerk":
        from josi.auth.providers.clerk import ClerkProvider
        return ClerkProvider()
    raise ValueError(f"Unknown auth provider: {name}")
