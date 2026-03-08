"""User service — business logic for user management and auth resolution."""
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
    """Business logic for users and auth resolution."""

    def __init__(self, current_user: Optional[CurrentUser] = None):
        self.current_user = current_user
        self.user_id = current_user.user_id if current_user else None
        self.email = current_user.email if current_user else None
        self.roles = current_user.roles if current_user else None
        self.user_repository = UserRepository(current_user=current_user)

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

        await invalidate_user(clerk_user_id)
        return user

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
