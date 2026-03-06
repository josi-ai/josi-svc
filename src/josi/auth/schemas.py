"""Auth schemas shared across services."""
from pydantic import BaseModel
from typing import List
from uuid import UUID


class CurrentUser(BaseModel):
    """Resolved user context — same shape regardless of auth path (JWT or API key)."""
    user_id: UUID
    descope_id: str
    email: str
    subscription_tier: str
    roles: List[str]

    def has_role(self, role: str) -> bool:
        return role in self.roles
