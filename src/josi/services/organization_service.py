"""
Organization service - handles business logic for organization management.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from josi.models.organization_model import Organization
from josi.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    """Service for organization-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # Organization doesn't have a tenant filter since it's the top level
        self.repo = OrganizationRepository(Organization, db, None)
    
    async def get_organization(
        self,
        organization_id: UUID,
        selected_fields: Optional[List[str]] = None
    ) -> Optional[Organization]:
        """Get organization by ID."""
        return await self.repo.get(organization_id)
    
    async def list_organizations(
        self,
        skip: int = 0,
        limit: int = 100,
        offset: Optional[int] = None,
        selected_fields: Optional[List[str]] = None
    ) -> List[Organization]:
        """List all organizations."""
        # Use offset if provided, otherwise use skip
        actual_offset = offset if offset is not None else skip
        return await self.repo.list(skip=actual_offset, limit=limit)
    
    async def create_organization(self, organization_data: Organization) -> Organization:
        """Create a new organization."""
        return await self.repo.create(organization_data)
    
    async def update_organization(
        self,
        organization_id: UUID,
        organization_data: Organization,
        updated_fields: Optional[List[str]] = None
    ) -> Optional[Organization]:
        """Update an organization."""
        org = await self.repo.get(organization_id)
        if not org:
            return None
        
        # Update fields
        update_dict = organization_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(org, field, value)
        
        await self.db.commit()
        await self.db.refresh(org)
        return org
    
    async def delete_organization(self, organization_id: UUID) -> bool:
        """Soft delete an organization."""
        return await self.repo.delete(organization_id)