"""
Improved dependency injection for clean architecture.
"""
from typing import Annotated
from fastapi import Depends
from uuid import UUID

from josi.models.organization_model import Organization
from josi.services.person_service import PersonService
from josi.services.chart_service import ChartService
from josi.db.async_db import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_organization(api_key: str) -> Organization:
    """Get organization from API key."""
    # Implementation here
    pass


async def get_person_service(
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[AsyncSession, Depends(get_async_db)]
) -> PersonService:
    """Inject PersonService with all its dependencies."""
    return PersonService(db, organization.organization_id)


async def get_chart_service(
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[AsyncSession, Depends(get_async_db)]
) -> ChartService:
    """Inject ChartService with all its dependencies."""
    return ChartService(db, organization.organization_id)


# Type aliases for cleaner code
PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]
ChartServiceDep = Annotated[ChartService, Depends(get_chart_service)]
OrganizationDep = Annotated[Organization, Depends(get_current_organization)]