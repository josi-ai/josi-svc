from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from josi.repositories.base_repository import BaseRepository
from josi.models.organization_model import Organization


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for Organization operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)
    
    async def get_by_api_key(self, api_key: str) -> Optional[Organization]:
        """Get organization by API key."""
        query = select(Organization).where(Organization.api_key == api_key)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        query = select(Organization).where(Organization.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()