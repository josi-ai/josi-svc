"""V1 API module — consolidated REST API endpoints."""
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
from josi.api.v1.controllers.ai_controller import router as ai_router
from josi.api.v1.controllers.astrologer_controller import router as astrologer_router
from josi.api.v1.controllers.consultation_controller import router as consultation_router
from josi.api.v1.controllers.muhurta_controller import router as muhurta_router
from josi.api.v1.controllers.remedy_controller import router as remedy_router
from josi.api.v1.controllers.webhook_controller import router as webhook_router
from josi.api.v1.controllers.api_key_controller import router as api_key_router
from josi.api.v1.health import router as health_router

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
v1_router.include_router(ai_router)
v1_router.include_router(astrologer_router)
v1_router.include_router(consultation_router)
v1_router.include_router(muhurta_router)
v1_router.include_router(remedy_router)
v1_router.include_router(health_router)
v1_router.include_router(webhook_router)
v1_router.include_router(api_key_router)

__all__ = ["v1_router"]
