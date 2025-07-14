"""
V1 API module - consolidated REST API endpoints.
"""
from fastapi import APIRouter

from josi.api.v1.controllers.chart_controller import router as chart_router
from josi.api.v1.controllers.person_controller import router as person_router
from josi.api.v1.controllers.panchang_controller import router as panchang_router
from josi.api.v1.controllers.compatibility_controller import router as compatibility_router
from josi.api.v1.controllers.transit_controller import router as transit_router
from josi.api.v1.controllers.dasha_controller import router as dasha_router
from josi.api.v1.controllers.prediction_controller import router as prediction_router
from josi.api.v1.controllers.remedies_controller import router as remedies_router
from josi.api.v1.controllers.location_controller import router as location_router
from josi.api.v1.health import router as health_router
from josi.api.v1.oauth import router as oauth_router


# Create main v1 router
v1_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
v1_router.include_router(person_router)
v1_router.include_router(chart_router)
v1_router.include_router(panchang_router)
v1_router.include_router(compatibility_router)
v1_router.include_router(transit_router)
v1_router.include_router(dasha_router)
v1_router.include_router(prediction_router)
v1_router.include_router(remedies_router)
v1_router.include_router(location_router)
v1_router.include_router(health_router)
v1_router.include_router(oauth_router)


__all__ = ["v1_router"]