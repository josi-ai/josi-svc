"""Clerk auth provider implementation."""
from typing import Optional

import httpx
import structlog
from fastapi import HTTPException, status

from josi.auth.providers.base import AuthProvider
from josi.core.config import settings

logger = structlog.get_logger()


class ClerkProvider(AuthProvider):
    _jwks_client = None

    @property
    def provider_name(self) -> str:
        return "clerk"

    @staticmethod
    def _derive_jwks_url() -> str:
        """Derive JWKS URL from Clerk publishable key."""
        import base64
        pk = settings.clerk_publishable_key or ""
        encoded = pk.split("_", 2)[-1] if "_" in pk else ""
        try:
            domain = base64.b64decode(encoded + "==").decode().rstrip("$")
            return f"https://{domain}/.well-known/jwks.json"
        except Exception:
            logger.warning("Could not derive JWKS URL from publishable key, using fallback")
            return "https://api.clerk.com/.well-known/jwks.json"

    def _get_jwks_client(self):
        if ClerkProvider._jwks_client is None:
            from jwt import PyJWKClient
            ClerkProvider._jwks_client = PyJWKClient(self._derive_jwks_url())
        return ClerkProvider._jwks_client

    def validate_jwt(self, token: str) -> dict:
        import jwt as pyjwt

        try:
            signing_key = self._get_jwks_client().get_signing_key_from_jwt(token)
            claims = pyjwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
            return claims
        except Exception as e:
            logger.warning("Clerk JWT validation failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_user_info(self, provider_user_id: str) -> Optional[dict]:
        """Fetch user details from Clerk Backend API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.clerk.com/v1/users/{provider_user_id}",
                    headers={
                        "Authorization": f"Bearer {settings.clerk_secret_key}",
                    },
                )
                if response.status_code != 200:
                    logger.warning(
                        "Clerk API user lookup failed",
                        provider_user_id=provider_user_id,
                        status=response.status_code,
                    )
                    return None

                data = response.json()

                # Extract primary email
                emails = data.get("email_addresses", [])
                primary_email_id = data.get("primary_email_address_id")
                primary_email = ""
                for e in emails:
                    if e.get("id") == primary_email_id:
                        primary_email = e.get("email_address", "")
                        break
                if not primary_email and emails:
                    primary_email = emails[0].get("email_address", "")

                # Extract name
                first_name = data.get("first_name") or ""
                last_name = data.get("last_name") or ""
                full_name = f"{first_name} {last_name}".strip()
                if not full_name:
                    full_name = primary_email.split("@")[0] if primary_email else "User"

                # Extract phone
                phones = data.get("phone_numbers", [])
                primary_phone_id = data.get("primary_phone_number_id")
                primary_phone = None
                for p in phones:
                    if p.get("id") == primary_phone_id:
                        primary_phone = p.get("phone_number")
                        break

                return {
                    "email": primary_email,
                    "full_name": full_name,
                    "phone": primary_phone,
                }
        except Exception as e:
            logger.error("Clerk API call failed", error=str(e), provider_user_id=provider_user_id)
            return None

    async def set_user_metadata(self, provider_user_id: str, metadata: dict) -> bool:
        """Set publicMetadata on a Clerk user so subsequent JWTs carry josi_* claims."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"https://api.clerk.com/v1/users/{provider_user_id}",
                    headers={
                        "Authorization": f"Bearer {settings.clerk_secret_key}",
                        "Content-Type": "application/json",
                    },
                    json={"public_metadata": metadata},
                )
                if response.status_code != 200:
                    logger.error(
                        "Failed to set Clerk publicMetadata",
                        provider_user_id=provider_user_id,
                        status=response.status_code,
                        body=response.text,
                    )
                    return False
                return True
        except Exception as e:
            logger.error(
                "Clerk API call failed",
                error=str(e),
                provider_user_id=provider_user_id,
            )
            return False
