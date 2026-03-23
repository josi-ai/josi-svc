"""
Improved dependency injection for clean architecture.
"""
from typing import Annotated
from fastapi import Depends
from uuid import UUID

from josi.auth.middleware import resolve_current_user
from josi.auth.schemas import CurrentUser
from josi.services.person_service import PersonService
from josi.services.chart_service import ChartService
from josi.db.async_db import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

CurrentUserDep = Annotated[CurrentUser, Depends(resolve_current_user)]


async def get_person_service(
    current_user: CurrentUserDep,
    db: Annotated[AsyncSession, Depends(get_async_db)]
) -> PersonService:
    """Inject PersonService with all its dependencies."""
    return PersonService(db, current_user.user_id)


async def get_chart_service(
    current_user: CurrentUserDep,
    db: Annotated[AsyncSession, Depends(get_async_db)]
) -> ChartService:
    """Inject ChartService with all its dependencies."""
    return ChartService(db, current_user.user_id)


# Type aliases for cleaner code
PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]
ChartServiceDep = Annotated[ChartService, Depends(get_chart_service)]