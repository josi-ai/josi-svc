"""
V1 API Dependencies - Clean architecture dependency injection.
"""
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from josi.db.async_db import get_async_db
from josi.models.organization_model import Organization
from josi.repositories.organization_repository import OrganizationRepository
from josi.repositories.person_repository import PersonRepository
from josi.models.person_model import Person
from josi.models.chart_model import AstrologyChart

# Services
from josi.services.person_service import PersonService
from josi.services.chart_service import ChartService
from josi.services.geocoding_service import GeocodingService
from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.panchang_service import PanchangCalculator
from josi.services.vedic.muhurta_service import MuhurtaCalculator
from josi.services.vedic.dasha_service import VimshottariDashaCalculator, YoginiDashaCalculator, CharaDashaCalculator
from josi.services.vedic.remedies_service import RemedyService
from josi.services.western.progressions_service import ProgressionCalculator
from josi.services.interpretation_engine_service import InterpretationEngine
from josi.services.vedic.ashtakoota_service import AshtakootaCalculator


async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> str:
    """Extract and validate API key from headers."""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required. Please provide X-API-Key header."
        )
    return x_api_key


async def get_current_organization(
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_async_db)
) -> Organization:
    """Get the current organization based on API key."""
    # For now, return a default organization
    # In production, validate API key and get associated organization
    org_repo = OrganizationRepository(db)
    
    # Try to get default organization
    organizations = await org_repo.get_multi(limit=1)
    if organizations:
        return organizations[0]
    
    # Create default organization if none exists
    org_data = {
        "organization_id": UUID("00000000-0000-0000-0000-000000000000"),
        "name": "Default Organization",
        "slug": "default-organization",
        "api_key": api_key,
        "is_active": True
    }
    
    default_org = await org_repo.create(org_data)
    await db.commit()
    
    return default_org


# Repository Dependencies (for services that need them)
async def get_person_repository(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    organization: Annotated[Organization, Depends(get_current_organization)]
) -> PersonRepository:
    """Get PersonRepository with dependencies."""
    return PersonRepository(Person, db, organization.organization_id)


# Service Dependencies - These encapsulate all database access
async def get_person_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    organization: Annotated[Organization, Depends(get_current_organization)]
) -> PersonService:
    """Get PersonService with all dependencies."""
    return PersonService(db, organization.organization_id)


async def get_chart_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    organization: Annotated[Organization, Depends(get_current_organization)]
) -> ChartService:
    """Get ChartService with all dependencies."""
    return ChartService(db, organization.organization_id)


async def get_geocoding_service() -> GeocodingService:
    """Get GeocodingService instance."""
    return GeocodingService()


async def get_astrology_calculator() -> AstrologyCalculator:
    """Get AstrologyCalculator instance."""
    return AstrologyCalculator()


async def get_panchang_calculator() -> PanchangCalculator:
    """Get PanchangCalculator instance."""
    return PanchangCalculator()


async def get_muhurta_calculator() -> MuhurtaCalculator:
    """Get MuhurtaCalculator instance."""
    return MuhurtaCalculator()


async def get_vimshottari_dasha_calculator() -> VimshottariDashaCalculator:
    """Get VimshottariDashaCalculator instance."""
    return VimshottariDashaCalculator()


async def get_yogini_dasha_calculator() -> YoginiDashaCalculator:
    """Get YoginiDashaCalculator instance."""
    return YoginiDashaCalculator()


async def get_chara_dasha_calculator() -> CharaDashaCalculator:
    """Get CharaDashaCalculator instance."""
    return CharaDashaCalculator()


async def get_remedy_service() -> RemedyService:
    """Get RemedyService instance."""
    return RemedyService()


async def get_progression_calculator() -> ProgressionCalculator:
    """Get ProgressionCalculator instance."""
    return ProgressionCalculator()


async def get_interpretation_engine() -> InterpretationEngine:
    """Get InterpretationEngine instance."""
    return InterpretationEngine()


async def get_ashtakoota_calculator() -> AshtakootaCalculator:
    """Get AshtakootaCalculator instance."""
    return AshtakootaCalculator()


# Type Aliases for cleaner dependency injection
PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]
ChartServiceDep = Annotated[ChartService, Depends(get_chart_service)]
PersonRepositoryDep = Annotated[PersonRepository, Depends(get_person_repository)]
OrganizationDep = Annotated[Organization, Depends(get_current_organization)]
GeocodingServiceDep = Annotated[GeocodingService, Depends(get_geocoding_service)]
AstrologyCalculatorDep = Annotated[AstrologyCalculator, Depends(get_astrology_calculator)]
PanchangCalculatorDep = Annotated[PanchangCalculator, Depends(get_panchang_calculator)]
MuhurtaCalculatorDep = Annotated[MuhurtaCalculator, Depends(get_muhurta_calculator)]
VimshottariDashaDep = Annotated[VimshottariDashaCalculator, Depends(get_vimshottari_dasha_calculator)]
YoginiDashaDep = Annotated[YoginiDashaCalculator, Depends(get_yogini_dasha_calculator)]
CharaDashaDep = Annotated[CharaDashaCalculator, Depends(get_chara_dasha_calculator)]
RemedyServiceDep = Annotated[RemedyService, Depends(get_remedy_service)]
ProgressionCalculatorDep = Annotated[ProgressionCalculator, Depends(get_progression_calculator)]
InterpretationEngineDep = Annotated[InterpretationEngine, Depends(get_interpretation_engine)]
AshtakootaCalculatorDep = Annotated[AshtakootaCalculator, Depends(get_ashtakoota_calculator)]