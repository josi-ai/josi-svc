"""Clerk auth provider implementation."""
import httpx
import structlog
from fastapi import HTTPException, status

from josi.auth.providers.base import AuthProvider
from josi.core.config import settings

logger = structlog.get_logger()


class ClerkProvider(AuthProvider):
    @property
    def provider_name(self) -> str:
        return "clerk"

    def validate_jwt(self, token: str) -> dict:
        import jwt as pyjwt
        from jwt import PyJWKClient

        try:
            jwks_url = "https://api.clerk.com/.well-known/jwks.json"
            jwks_client = PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
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
