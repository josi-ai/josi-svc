"""
GraphQL context with service instances.
"""
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from logging import getLogger

from strawberry.fastapi import BaseContext

from josi.core.config import Settings, settings
from josi.db.async_db import get_async_db
from josi.models.organization_model import Organization

# Import services
from josi.services.person_service import PersonService
from josi.services.chart_service import ChartService
from josi.services.organization_service import OrganizationService

log = getLogger("uvicorn")


class UserOrganization:
    """User organization context."""
    def __init__(self, organization: Organization, user_id: Optional[UUID] = None):
        self.organization_id = organization.organization_id
        self.organization_name = organization.name
        self.user_id = user_id
        self.user_name = None  # Would come from auth
        self.entity_access = None  # Would come from permissions
        self.user_roles = []  # Would come from auth


class ServiceContext(BaseContext):
    """GraphQL context with all services."""
    
    def __init__(
        self,
        db: AsyncSession,
        user_organization: Optional[UserOrganization] = None
    ):
        self.settings = settings
        self.db = db
        self.user_organization = user_organization
        
        # Get user_id from context
        uid = user_organization.user_id if user_organization else None

        # Initialize services
        self.person_service = PersonService(db=db, user_id=uid)
        self.chart_service = ChartService(db=db, user_id=uid)
        self.organization_service = OrganizationService(db=db)


async def get_context(request: Request, db: AsyncSession = Depends(get_async_db)):
    """Get GraphQL context for request."""
    # settings already imported
    
    # In production, get organization from auth headers
    # For now, create default organization
    default_org = Organization(
        organization_id=UUID("00000000-0000-0000-0000-000000000000"),
        name="Default Organization",
        api_key="default-key",
        is_active=True
    )
    
    # Create user organization context
    user_organization = UserOrganization(
        organization=default_org,
        user_id=None  # Would come from auth
    )
    
    # Skip organization check for GraphQL introspection
    skip_organization_required_check = False
    if request.url.path.endswith('/graphql') and request.method == 'GET':
        skip_organization_required_check = True
    
    if (user_organization is None or user_organization.organization_id is None) and settings.enable_authorization and not skip_organization_required_check:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="User organization not found in request headers",
        )
    
    log.info(f"User Organization: {user_organization.organization_id}")
    
    context = ServiceContext(
        db=db,
        user_organization=user_organization,
    )
    
    return context