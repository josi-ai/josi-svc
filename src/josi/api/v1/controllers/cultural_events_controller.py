"""
Cultural Events Calendar controller — returns festivals filtered by ethnicity and date.
"""
from typing import Optional

from fastapi import APIRouter, Query

from josi.api.response import ResponseModel
from josi.services.cultural_events_service import CulturalEventsService

router = APIRouter(prefix="/events", tags=["Cultural Events"])


@router.get("/cultural", response_model=ResponseModel)
async def get_cultural_events(
    ethnicity: Optional[str] = Query(
        None,
        description="Comma-separated ethnicity tags, e.g. 'Tamil Hindu,Buddhist'",
    ),
    year: int = Query(2026, description="Calendar year (only 2026 supported currently)"),
    month: Optional[int] = Query(
        None, ge=1, le=12, description="Month number (1-12)"
    ),
) -> ResponseModel:
    """
    Get cultural and religious events filtered by ethnicity tags and date.

    Query parameters:
        - **ethnicity**: Comma-separated list of ethnicity tags.
          Available tags: Tamil Hindu, North Indian Hindu, Bengali Hindu,
          Buddhist, Sikh, Jain, Muslim, Christian.
        - **year**: Calendar year (default 2026, only year with data).
        - **month**: Optional month filter (1-12).

    If no ethnicity filter is provided, all events for the given month/year
    are returned.

    Example:
        GET /api/v1/events/cultural?ethnicity=Tamil%20Hindu,Buddhist&year=2026&month=1
    """
    ethnicity_list = (
        [tag.strip() for tag in ethnicity.split(",") if tag.strip()]
        if ethnicity
        else None
    )

    service = CulturalEventsService()
    events = service.get_events(
        ethnicity=ethnicity_list,
        year=year,
        month=month,
    )

    return ResponseModel(
        success=True,
        message=f"Found {len(events)} cultural events",
        data={
            "events": events,
            "total": len(events),
            "filters": {
                "ethnicity": ethnicity_list,
                "year": year,
                "month": month,
            },
        },
    )
