"""
Dasha (planetary periods) controller - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException
from uuid import UUID

from josi.api.v1.dependencies import PersonServiceDep, VimshottariDashaDep, AstrologyCalculatorDep
from josi.api.response import ResponseModel


router = APIRouter(prefix="/dasha", tags=["dasha"])


@router.get("/vimshottari/{person_id}", response_model=ResponseModel)
async def get_vimshottari_dasha(
    person_id: UUID,
    person_service: PersonServiceDep,
    vimshottari_calculator: VimshottariDashaDep,
    astrology_calculator: AstrologyCalculatorDep
) -> ResponseModel:
    """
    Calculate Vimshottari Dasha (120-year cycle planetary periods).
    
    Vimshottari is the most widely used dasha system in Vedic astrology,
    based on the Moon's position at birth. It divides life into planetary
    periods totaling 120 years, with each planet ruling for a specific duration.
    
    Args:
        person_id (UUID): Unique identifier of the person
        person_service (PersonServiceDep): Injected person service
        vimshottari_calculator (VimshottariDashaDep): Injected Vimshottari calculator
        astrology_calculator (AstrologyCalculatorDep): Injected astrology calculator
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - moon_nakshatra: Birth nakshatra (lunar mansion)
            - current_dasha: Currently active periods:
                - mahadasha: Major period planet and duration
                - antardasha: Sub-period planet and duration
                - pratyantardasha: Sub-sub-period details
                - start_date: When current period began
                - end_date: When current period ends
            - upcoming_changes: Next 5 period changes:
                - date: When change occurs
                - type: Which level changes (MD/AD/PD)
                - from_planet: Current ruler
                - to_planet: New ruler
                - significance: General effects
            - life_timeline: Complete mahadasha sequence from birth
    
    Raises:
        HTTPException(404): If person not found
    
    Dasha Durations:
        - Sun: 6 years
        - Moon: 10 years
        - Mars: 7 years
        - Rahu: 18 years
        - Jupiter: 16 years
        - Saturn: 19 years
        - Mercury: 17 years
        - Ketu: 7 years
        - Venus: 20 years
        Total: 120 years
    
    Example:
        GET /api/v1/dasha/vimshottari/123e4567-e89b-12d3-a456-426614174000
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Calculate natal chart to get Moon position
    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Calculate Vimshottari dasha
    dasha_data = vimshottari_calculator.calculate_mahadasha(
        natal_chart["planets"]["Moon"]["longitude"],
        person.time_of_birth
    )
    
    return ResponseModel(
        success=True,
        message="Vimshottari Dasha calculated successfully",
        data={
            "person_id": str(person_id),
            "moon_nakshatra": natal_chart["planets"]["Moon"]["nakshatra"],
            "current_dasha": {
                "mahadasha": dasha_data["current_mahadasha"],
                "antardasha": dasha_data["current_antardasha"],
                "pratyantardasha": dasha_data.get("current_pratyantardasha"),
                "start_date": dasha_data["current_start_date"],
                "end_date": dasha_data["current_end_date"]
            },
            "upcoming_changes": dasha_data.get("upcoming_changes", []),
            "life_timeline": dasha_data["mahadashas"]
        }
    )


# TODO: Implement YoginiDashaCalculator and CharaDashaCalculator
# The following endpoints are commented out until these calculators are implemented

# @router.get("/yogini/{person_id}", response_model=ResponseModel)
# async def get_yogini_dasha(...)

# @router.get("/chara/{person_id}", response_model=ResponseModel)  
# async def get_chara_dasha(...)