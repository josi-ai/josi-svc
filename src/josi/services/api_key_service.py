"""API key service — business logic for key management and auth resolution."""
import hashlib
import secrets
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from josi.auth.schemas import CurrentUser
from josi.models.api_key_model import ApiKey
from josi.models.user_model import User
from josi.repositories.api_key_repository import ApiKeyRepository
from josi.repositories.user_repository import UserRepository


class ApiKeyService:
    """Business logic for API key CRUD and auth resolution."""

    def __init__(self, current_user: Optional[CurrentUser] = None):
        self.current_user = current_user
        self.user_id = current_user.user_id if current_user else None
        self.key_repo = ApiKeyRepository(current_user=current_user)
        self.user_repo = UserRepository(current_user=current_user)

    @staticmethod
    def generate_raw_key() -> str:
        return f"jsk_{secrets.token_urlsafe(32)}"

    async def create_key(self, user_id: UUID, name: str) -> tuple[ApiKey, str]:
        """Create a new API key. Returns (api_key, raw_key_plaintext)."""
        raw_key = self.generate_raw_key()
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:12]

        api_key = ApiKey(
            user_id=user_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
        )
        api_key = await self.key_repo.create(api_key)
        return api_key, raw_key

    async def list_keys(self, user_id: UUID) -> List[ApiKey]:
        return await self.key_repo.list_active_by_user(user_id)

    async def revoke_key(self, key_id: UUID, user_id: UUID) -> Optional[ApiKey]:
        """Revoke a key. Returns the key if found, None otherwise."""
        api_key = await self.key_repo.get_by_id_and_user(key_id, user_id)
        if not api_key:
            return None
        api_key.is_active = False
        api_key.updated_at = datetime.utcnow()
        api_key = await self.key_repo.update(api_key)
        return api_key

    async def rotate_key(self, key_id: UUID, user_id: UUID) -> Optional[tuple[ApiKey, str]]:
        """Rotate a key: revoke old, create new with same name."""
        old_key = await self.key_repo.get_by_id_and_user(key_id, user_id, active_only=True)
        if not old_key:
            return None

        old_key.is_active = False
        old_key.updated_at = datetime.utcnow()
        await self.key_repo.update(old_key)

        new_key, raw_key = await self.create_key(user_id, old_key.name)
        return new_key, raw_key

    # --- Auth resolution (used by middleware) ---

    async def resolve_user_from_api_key(self, raw_key: str) -> Optional[tuple[User, ApiKey]]:
        """Look up an API key, validate it, return the associated user."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = await self.key_repo.get_by_hash(key_hash)
        if not api_key:
            return None

        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None

        api_key.last_used_at = datetime.utcnow()
        await self.key_repo.update(api_key)

        user = await self.user_repo.get_by_id(api_key.user_id)
        if not user or not user.is_active:
            return None

        return user, api_key
