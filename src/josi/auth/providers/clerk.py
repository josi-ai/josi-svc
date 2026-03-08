"""Clerk auth provider implementation."""
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
        # publishable key format: pk_test_<base64-encoded-domain>
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

    async def set_user_metadata(self, provider_user_id: str, metadata: dict) -> bool:
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
            logger.error("Clerk API call failed", error=str(e), provider_user_id=provider_user_id)
            return False
