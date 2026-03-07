"""Auth schemas shared across services."""
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class CurrentUser(BaseModel):
    """Resolved user context — same shape regardless of auth provider or path."""
    user_id: UUID
    auth_provider_id: str  # Descope user ID or Clerk user ID
    email: str
    subscription_tier: str
    subscription_tier_id: Optional[int] = None
    roles: List[str]
    is_active: bool = True
    is_verified: bool = False

    def has_role(self, role: str) -> bool:
        return role in self.roles
