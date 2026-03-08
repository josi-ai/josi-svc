"""User service — business logic for user management and auth provider sync."""
from typing import Optional
from datetime import datetime
from uuid import UUID

import structlog

from josi.auth.schemas import CurrentUser
from josi.auth.providers import get_auth_provider
from josi.models.user_model import User
from josi.repositories.user_repository import UserRepository
from josi.services.session_cache_service import invalidate_user

logger = structlog.get_logger()


class UserService:
    """Business logic for users, provider metadata sync, and auth resolution."""

    def __init__(self, current_user: Optional[CurrentUser] = None):
        self.current_user = current_user
        self.user_id = current_user.user_id if current_user else None
        self.email = current_user.email if current_user else None
        self.roles = current_user.roles if current_user else None
        self.user_repository = UserRepository(current_user=current_user)

    # --- Auth provider metadata sync ---

    async def sync_provider_metadata(self, provider_user_id: str, metadata: dict) -> bool:
        provider = get_auth_provider()
        return await provider.set_user_metadata(provider_user_id, metadata)

    def _build_metadata(self, user: User) -> dict:
        return {
            "josi_user_id": str(user.user_id),
            "josi_subscription_tier_id": user.subscription_tier_id or 1,
            "josi_subscription_tier": user.subscription_tier_name or "Free",
            "josi_roles": user.roles,
            "josi_is_active": user.is_active,
            "josi_is_verified": user.is_verified,
        }

    # --- User upsert (shared by webhook + sync-claims) ---

    async def upsert_from_clerk(
        self,
        clerk_user_id: str,
        email: Optional[str],
        full_name: Optional[str],
        phone: Optional[str] = None,
    ) -> User:
        """Find-or-create a user from Clerk data and sync publicMetadata."""
        user = await self.user_repository.get_by_auth_provider_id(clerk_user_id)

        if not user and email:
            user = await self.user_repository.get_by_email(email)
            if user:
                user.auth_provider_id = clerk_user_id
                logger.info(
                    "Linked existing user to auth provider",
                    user_id=str(user.user_id),
                    clerk_user_id=clerk_user_id,
                )

        if user:
            user.last_login = datetime.utcnow()
            if email and user.email != email:
                user.email = email
            if phone and user.phone != phone:
                user.phone = phone
            if full_name and user.full_name != full_name:
                user.full_name = full_name
            user = await self.user_repository.update(user)
        else:
            user = User(
                auth_provider_id=clerk_user_id,
                email=email or "",
                full_name=full_name or (email.split("@")[0] if email else "User"),
                phone=phone,
                is_verified=bool(email),
                last_login=datetime.utcnow(),
            )
            user = await self.user_repository.create(user)
            logger.info("New user created", user_id=str(user.user_id), email=user.email)

        await self.sync_provider_metadata(clerk_user_id, self._build_metadata(user))
        await invalidate_user(clerk_user_id)
        return user

    # --- Auth resolution (used by middleware) ---

    def extract_user_from_claims(self, claims: dict) -> Optional[CurrentUser]:
        """Extract CurrentUser from JWT custom claims (fast path).

        Returns None if josi_user_id is missing (first login before webhook).
        """
        josi_user_id = claims.get("josi_user_id")
        if not josi_user_id:
            return None

        try:
            user_id = UUID(josi_user_id)
        except ValueError:
            return None

        return CurrentUser(
            user_id=user_id,
            auth_provider_id=claims.get("sub", ""),
            email=claims.get("email", ""),
            subscription_tier=claims.get("josi_subscription_tier", "Free"),
            subscription_tier_id=claims.get("josi_subscription_tier_id"),
            roles=claims.get("josi_roles", ["user"]),
            is_active=claims.get("josi_is_active", True),
            is_verified=claims.get("josi_is_verified", False),
        )

    async def resolve_user_from_db(self, auth_provider_id: str, email: str) -> CurrentUser:
        """Fallback: look up user by auth_provider_id, create if missing."""
        user = await self.user_repository.get_by_auth_provider_id(auth_provider_id)

        if not user:
            logger.info("User not yet provisioned, creating from JWT", sub=auth_provider_id, email=email)
            user = User(
                auth_provider_id=auth_provider_id,
                email=email,
                full_name=email.split("@")[0] if email else "User",
                last_login=datetime.utcnow(),
            )
            user = await self.user_repository.create(user)

        return CurrentUser(
            user_id=user.user_id,
            auth_provider_id=user.auth_provider_id,
            email=user.email,
            subscription_tier=user.subscription_tier_name or "Free",
            subscription_tier_id=user.subscription_tier_id,
            roles=user.roles,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
