"""
Organization GraphQL schema.
"""
import strawberry
from strawberry.types import Info
from typing import List, Optional
from uuid import UUID

from josi.graphql.base import PaginationWindow, get_pagination_window, get_selected_fields
from josi.models import (
    OrganizationSchema,
    OrganizationCreateInput,
    OrganizationUpdateInput
)


@strawberry.type
class OrganizationQuery:
    @strawberry.field
    async def organizations(
        self,
        info: Info,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0
    ) -> List[OrganizationSchema]:
        """Get all organizations."""
        organizations = await info.context.organization_service.list_organizations(
            limit=limit,
            offset=offset,
            selected_fields=get_selected_fields(info)
        )
        return [OrganizationSchema.from_orm(org) for org in organizations]
    
    @strawberry.field
    async def organization(self, info: Info, organization_id: UUID) -> Optional[OrganizationSchema]:
        """Get organization by ID."""
        org = await info.context.organization_service.get_organization(
            organization_id=organization_id,
            selected_fields=get_selected_fields(info)
        )
        return OrganizationSchema.from_orm(org) if org else None
    
    @strawberry.field
    async def current_organization(self, info: Info) -> Optional[OrganizationSchema]:
        """Get the current user's organization."""
        if info.context.user_organization:
            org = await info.context.organization_service.get_organization(
                organization_id=info.context.user_organization.organization_id,
                selected_fields=get_selected_fields(info)
            )
            return OrganizationSchema.from_orm(org) if org else None
        return None


@strawberry.type
class OrganizationMutation:
    @strawberry.field
    async def create_organization(
        self,
        info: Info,
        organization: OrganizationCreateInput
    ) -> OrganizationSchema:
        """Create a new organization."""
        org_data = organization.to_pydantic()
        new_org = await info.context.organization_service.create_organization(org_data)
        return OrganizationSchema.from_orm(new_org)
    
    @strawberry.field
    async def update_organization(
        self,
        info: Info,
        organization_id: UUID,
        organization: OrganizationUpdateInput
    ) -> OrganizationSchema:
        """Update an organization."""
        org_data = organization.to_pydantic()
        updated_org = await info.context.organization_service.update_organization(
            organization_id=organization_id,
            organization_data=org_data,
            updated_fields=get_updated_fields(info)
        )
        return OrganizationSchema.from_orm(updated_org)
    
    @strawberry.field
    async def delete_organization(self, info: Info, organization_id: UUID) -> bool:
        """Delete an organization."""
        return await info.context.organization_service.delete_organization(organization_id)