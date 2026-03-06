"""Descope client singleton — initialized once at startup."""
from descope import DescopeClient
from josi.core.config import settings


_client: DescopeClient | None = None


def get_descope_client() -> DescopeClient:
    global _client
    if _client is None:
        _client = DescopeClient(
            project_id=settings.descope_project_id,
            management_key=settings.descope_management_key,
        )
    return _client
