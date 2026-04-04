"""User service — business logic for user management and auth resolution."""
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import UUID

import structlog

from josi.auth.schemas import CurrentUser
from josi.auth.providers import get_auth_provider
from josi.models.user_model import User
from josi.repositories.user_repository import UserRepository
from josi.services.session_cache_service import invalidate_user

logger = structlog.get_logger()


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge *override* into *base*.

    - Dict values are merged recursively.
    - All other values in *override* replace those in *base*.
    - Keys present only in *base* are preserved.

    Returns a **new** dict (does not mutate *base*).
    """
    merged = dict(base)
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class UserService:
    """Business logic for users and auth resolution."""

    def __init__(self, current_user: Optional[CurrentUser] = None):
        self.current_user = current_user
        self.user_id = current_user.user_id if current_user else None
        self.email = current_user.email if current_user else None
        self.roles = current_user.roles if current_user else None
        self.user_repository = UserRepository(current_user=current_user)

    # --- Clerk publicMetadata sync ---

    def _build_metadata(self, user: User) -> dict:
        """Build the josi_* claims dict to store in Clerk publicMetadata."""
        return {
            "josi_user_id": str(user.user_id),
            "josi_email": user.email,
            "josi_full_name": user.full_name,
            "josi_auth_provider": user.auth_provider,
            "josi_subscription_tier": user.subscription_tier_name or "Free",
            "josi_subscription_tier_id": user.subscription_tier_id or 1,
            "josi_roles": user.roles,
            "josi_is_active": user.is_active,
            "josi_is_verified": user.is_verified,
        }

    async def sync_provider_metadata(self, user: User) -> None:
        """Push josi_* claims to the auth provider so they appear in future JWTs."""
        provider = get_auth_provider()
        metadata = self._build_metadata(user)
        success = await provider.set_user_metadata(user.auth_provider_id, metadata)
        if success:
            logger.info(
                "Synced provider metadata",
                user_id=str(user.user_id),
                auth_provider_id=user.auth_provider_id,
            )
        else:
            logger.warning(
                "Failed to sync provider metadata",
                user_id=str(user.user_id),
                auth_provider_id=user.auth_provider_id,
            )

    # --- User upsert (called by webhook) ---

    async def upsert_from_clerk(
        self,
        clerk_user_id: str,
        email: Optional[str],
        full_name: Optional[str],
        phone: Optional[str] = None,
    ) -> User:
        """Find-or-create a user from Clerk webhook data."""
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

        # Sync josi_* claims to Clerk publicMetadata so future JWTs carry them
        await self.sync_provider_metadata(user)

        await invalidate_user(clerk_user_id)
        return user

    # --- Ensure user exists (called from middleware on every auth) ---

    async def ensure_user_exists(
        self,
        user_id: UUID,
        auth_provider_id: str,
        email: str,
        full_name: str,
    ) -> None:
        """Ensure a user record exists in the DB for this user_id.

        Called on every authenticated request (behind a Redis flag so it only
        hits DB once per hour). Handles the case where JWT claims reference a
        user_id that doesn't exist in the DB (e.g., after a DB reset, or when
        the Clerk fast-path was used before the users table existed).
        """
        user = await self.user_repository.get_by_id(user_id)
        if user:
            return  # Already exists

        # Try by auth_provider_id (might exist with a different user_id)
        user = await self.user_repository.get_by_auth_provider_id(auth_provider_id)
        if user:
            return  # Exists under different ID — close enough

        # Create the user record
        logger.info(
            "Creating missing user record from JWT claims",
            user_id=str(user_id),
            email=email,
        )
        new_user = User(
            user_id=user_id,
            auth_provider_id=auth_provider_id,
            auth_provider="clerk",
            email=email or "unknown@josiam.com",
            full_name=full_name or "User",
            is_active=True,
            is_verified=bool(email),
            last_login=datetime.utcnow(),
        )
        await self.user_repository.create(new_user)

    # --- Default profile creation ---

    async def ensure_default_profile_exists(
        self, user_id: UUID, full_name: str, email: str
    ) -> None:
        """Ensure a default birth profile exists for this user."""
        from josi.models.person_model import Person
        from josi.db.async_db import get_async_session
        from sqlalchemy import select, and_

        async with get_async_session() as session:
            # Check if default profile already exists
            result = await session.execute(
                select(Person).where(
                    and_(
                        Person.user_id == user_id,
                        Person.is_default == True,
                        Person.is_deleted == False,
                    )
                )
            )
            existing = result.scalars().first()
            if existing:
                return

            # Create default profile
            person = Person(
                name=full_name or "My Profile",
                email=email,
                is_default=True,
                user_id=user_id,
            )
            session.add(person)
            await session.commit()
            logger.info(
                "Created default profile for user",
                user_id=str(user_id),
            )

    # --- Preferences ---

    async def get_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """Return preferences dict for the given user (empty dict if none set)."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return {}
        return user.preferences or {}

    async def update_preferences(
        self, user_id: UUID, incoming: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep-merge *incoming* into the user's existing preferences and persist.

        Returns the full merged preferences dict.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        existing = user.preferences or {}
        merged = _deep_merge(existing, incoming)
        user.preferences = merged
        user.updated_at = datetime.utcnow()
        await self.user_repository.update(user)
        logger.info(
            "Updated user preferences",
            user_id=str(user_id),
            keys=list(incoming.keys()),
        )
        return merged

    # --- Auth resolution (used by middleware) ---

    async def resolve_user_from_db(self, auth_provider_id: str, email: str) -> CurrentUser:
        """Look up user by auth_provider_id. If missing, fetch details from
        the auth provider API and create the user."""
        user = await self.user_repository.get_by_auth_provider_id(auth_provider_id)

        if not user:
            # Fetch real user info from auth provider (email isn't in JWT by default)
            provider = get_auth_provider()
            user_info = await provider.get_user_info(auth_provider_id)

            actual_email = (user_info or {}).get("email") or email
            actual_name = (user_info or {}).get("full_name") or (
                actual_email.split("@")[0] if actual_email else "User"
            )
            actual_phone = (user_info or {}).get("phone")

            # Check if a user already exists with this email (link accounts)
            if actual_email:
                user = await self.user_repository.get_by_email(actual_email)
                if user:
                    user.auth_provider_id = auth_provider_id
                    user.last_login = datetime.utcnow()
                    user = await self.user_repository.update(user)
                    logger.info("Linked existing user to auth provider", user_id=str(user.user_id))

            if not user:
                logger.info("Auto-creating user from auth provider", sub=auth_provider_id, email=actual_email)
                user = User(
                    auth_provider_id=auth_provider_id,
                    email=actual_email,
                    full_name=actual_name,
                    phone=actual_phone,
                    is_verified=bool(actual_email),
                    last_login=datetime.utcnow(),
                )
                user = await self.user_repository.create(user)

        # Sync josi_* claims to auth provider so future JWTs include josi_user_id
        await self.sync_provider_metadata(user)

        return CurrentUser(
            user_id=user.user_id,
            auth_provider_id=user.auth_provider_id,
            auth_provider=user.auth_provider,
            email=user.email,
            full_name=user.full_name,
            subscription_tier=user.subscription_tier_name or "Free",
            subscription_tier_id=user.subscription_tier_id,
            roles=user.roles,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
