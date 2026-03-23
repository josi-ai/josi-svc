"""V1 API Dependencies — Clean architecture dependency injection."""
from typing import Annotated
from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from josi.db.async_db import get_async_db
from josi.auth.middleware import resolve_current_user
from josi.auth.schemas import CurrentUser

# Services
from josi.services.person_service import PersonService
from josi.services.chart_service import ChartService
from josi.services.geocoding_service import GeocodingService
from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.panchang_service import PanchangCalculator
from josi.services.vedic.muhurta_service import MuhurtaCalculator
from josi.services.vedic.dasha_service import VimshottariDashaCalculator, YoginiDashaCalculator, CharaDashaCalculator
from josi.services.vedic.remedies_service import RemediesCalculator
from josi.services.western.progressions_service import ProgressionCalculator
from josi.services.interpretation_engine_service import InterpretationEngine
from josi.services.vedic.ashtakoota_service import AshtakootaCalculator

# Auth dependency
CurrentUserDep = Annotated[CurrentUser, Depends(resolve_current_user)]


# Service Dependencies
async def get_person_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: CurrentUserDep,
) -> PersonService:
    return PersonService(db, current_user.user_id)


async def get_chart_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: CurrentUserDep,
) -> ChartService:
    return ChartService(db, current_user.user_id)


async def get_geocoding_service() -> GeocodingService:
    return GeocodingService()


async def get_astrology_calculator() -> AstrologyCalculator:
    return AstrologyCalculator()


async def get_panchang_calculator() -> PanchangCalculator:
    return PanchangCalculator()


async def get_muhurta_calculator() -> MuhurtaCalculator:
    return MuhurtaCalculator()


async def get_vimshottari_dasha_calculator() -> VimshottariDashaCalculator:
    return VimshottariDashaCalculator()


async def get_yogini_dasha_calculator() -> YoginiDashaCalculator:
    return YoginiDashaCalculator()


async def get_chara_dasha_calculator() -> CharaDashaCalculator:
    return CharaDashaCalculator()


async def get_remedy_service() -> RemediesCalculator:
    return RemediesCalculator()


async def get_progression_calculator() -> ProgressionCalculator:
    return ProgressionCalculator()


async def get_interpretation_engine() -> InterpretationEngine:
    return InterpretationEngine()


async def get_ashtakoota_calculator() -> AshtakootaCalculator:
    return AshtakootaCalculator()


# Type Aliases
PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]
ChartServiceDep = Annotated[ChartService, Depends(get_chart_service)]
GeocodingServiceDep = Annotated[GeocodingService, Depends(get_geocoding_service)]
AstrologyCalculatorDep = Annotated[AstrologyCalculator, Depends(get_astrology_calculator)]
PanchangCalculatorDep = Annotated[PanchangCalculator, Depends(get_panchang_calculator)]
MuhurtaCalculatorDep = Annotated[MuhurtaCalculator, Depends(get_muhurta_calculator)]
VimshottariDashaDep = Annotated[VimshottariDashaCalculator, Depends(get_vimshottari_dasha_calculator)]
YoginiDashaDep = Annotated[YoginiDashaCalculator, Depends(get_yogini_dasha_calculator)]
CharaDashaDep = Annotated[CharaDashaCalculator, Depends(get_chara_dasha_calculator)]
RemedyServiceDep = Annotated[RemediesCalculator, Depends(get_remedy_service)]
ProgressionCalculatorDep = Annotated[ProgressionCalculator, Depends(get_progression_calculator)]
InterpretationEngineDep = Annotated[InterpretationEngine, Depends(get_interpretation_engine)]
AshtakootaCalculatorDep = Annotated[AshtakootaCalculator, Depends(get_ashtakoota_calculator)]
