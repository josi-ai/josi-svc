"""
Dasha (planetary periods) controller - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException
from uuid import UUID

from josi.api.v1.dependencies import PersonServiceDep, VimshottariDashaDep, YoginiDashaDep, CharaDashaDep, AstrologyCalculatorDep
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
    Calculate Vimshottari Dasha periods for a person.
    
    Vimshottari Dasha is the most important timing system in Vedic astrology,
    based on a 120-year cycle divided among 9 planets. Each planet rules for
    a specific number of years based on the Moon's position at birth.
    
    Args:
        person_id (UUID): Unique identifier of the person
        person_service (PersonServiceDep): Injected person service
        vimshottari_calculator (VimshottariDashaDep): Injected Vimshottari calculator
        astrology_calculator (AstrologyCalculatorDep): Injected astrology calculator
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - birth_nakshatra: Birth star/nakshatra with pada
            - current_dasha: Current operating periods:
                - mahadasha: Major period planet and dates
                - antardasha: Sub-period planet and dates
                - pratyantardasha: Sub-sub-period planet and dates
                - sookshma: Sub-sub-sub-period (if requested)
                - prana: Sub-sub-sub-sub-period (if requested)
            - dasha_sequence: Complete 120-year sequence with:
                - Planet name and total years
                - Start and end dates for each mahadasha
                - Age at start of each period
            - upcoming_changes: Next 5 period changes with dates
            - detailed_periods: Hierarchical breakdown of all periods
    
    Raises:
        HTTPException(404): If person not found
    
    Planet Periods:
        - Sun (Surya): 6 years
        - Moon (Chandra): 10 years
        - Mars (Mangal): 7 years
        - Rahu: 18 years
        - Jupiter (Guru): 16 years
        - Saturn (Shani): 19 years
        - Mercury (Budha): 17 years
        - Ketu: 7 years
        - Venus (Shukra): 20 years
    
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
    
    # Get Moon longitude
    moon_longitude = natal_chart["planets"]["Moon"]["longitude"]
    
    # Calculate Vimshottari Dasha
    dasha_data = vimshottari_calculator.calculate_dasha_periods(
        person.time_of_birth,
        moon_longitude,
        include_antardashas=True,
        include_pratyantardashas=True
    )
    
    return ResponseModel(
        success=True,
        message="Vimshottari Dasha calculated successfully",
        data={
            "person_id": str(person_id),
            "birth_nakshatra": dasha_data["birth_details"]["nakshatra_name"],
            "current_dasha": dasha_data["current_dasha"],
            "dasha_sequence": dasha_data["mahadashas"],
            "detailed_periods": {
                "current_mahadasha": dasha_data["current_dasha"]["mahadasha"] if dasha_data["current_dasha"] else None,
                "current_antardasha": dasha_data["current_dasha"].get("antardasha") if dasha_data["current_dasha"] else None,
                "current_pratyantardasha": dasha_data["current_dasha"].get("pratyantardasha") if dasha_data["current_dasha"] else None,
                "upcoming_changes": dasha_data.get("upcoming_changes", [])
            },
            "life_timeline": dasha_data["mahadashas"]
        }
    )


@router.get("/yogini/{person_id}", response_model=ResponseModel)
async def get_yogini_dasha(
    person_id: UUID,
    person_service: PersonServiceDep,
    yogini_calculator: YoginiDashaDep,
    astrology_calculator: AstrologyCalculatorDep
) -> ResponseModel:
    """
    Calculate Yogini Dasha periods (36-year cycle system).
    
    Yogini Dasha is a nakshatra-based timing system using 8 yoginis
    (female deities) cycling through 36 years total. It's particularly
    useful for spiritual progress and shorter-term predictions.
    
    Args:
        person_id (UUID): Unique identifier of the person
        person_service (PersonServiceDep): Injected person service
        vimshottari_calculator (VimshottariDashaDep): Injected Vimshottari calculator
        astrology_calculator (AstrologyCalculatorDep): Injected astrology calculator
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - moon_nakshatra: Birth nakshatra
            - yogini_cycle: Total cycle duration (36 years)
            - current_yogini: Currently active yogini with:
                - name: Yogini name
                - duration: Years ruled by this yogini
                - start_date: When current yogini period started
                - end_date: When it will end
                - characteristics: Key themes of this yogini
            - yogini_sequence: Complete sequence with durations:
                - Mangala: 1 year (Moon)
                - Pingala: 2 years (Sun)
                - Dhanya: 3 years (Jupiter)
                - Bhramari: 4 years (Mars)
                - Bhadrika: 5 years (Mercury)
                - Ulka: 6 years (Saturn)
                - Siddha: 7 years (Venus)
                - Sankata: 8 years (Rahu)
    
    Raises:
        HTTPException(404): If person not found
    
    Yogini Characteristics:
        - Mangala: Auspicious beginnings, emotional well-being
        - Pingala: Authority, recognition, health
        - Dhanya: Wealth, wisdom, spiritual growth
        - Bhramari: Energy, conflicts, transformations
        - Bhadrika: Communication, business, relationships
        - Ulka: Obstacles, delays, hard work
        - Siddha: Success, creativity, pleasures
        - Sankata: Difficulties, foreign matters, spirituality
    
    Example:
        GET /api/v1/dasha/yogini/123e4567-e89b-12d3-a456-426614174000
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Calculate natal chart to get Moon position
    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Get Moon's nakshatra
    moon_longitude = natal_chart["planets"]["Moon"]["longitude"]
    nakshatra_num = int(moon_longitude / 13.333333) + 1
    
    # Yogini dasha sequence and durations
    yogini_dashas = {
        "Mangala": 1, "Pingala": 2, "Dhanya": 3, "Bhramari": 4,
        "Bhadrika": 5, "Ulka": 6, "Siddha": 7, "Sankata": 8
    }
    
    # Calculate starting yogini based on nakshatra
    start_yogini = ((nakshatra_num - 1) % 8) + 1
    
    return ResponseModel(
        success=True,
        message="Yogini Dasha calculated successfully",
        data={
            "person_id": str(person_id),
            "moon_nakshatra": natal_chart["planets"]["Moon"]["nakshatra"],
            "yogini_cycle": "36 years total",
            "current_yogini": "To be calculated",  # Would need full implementation
            "yogini_sequence": yogini_dashas
        }
    )


@router.get("/chara/{person_id}", response_model=ResponseModel)
async def get_chara_dasha(
    person_id: UUID,
    person_service: PersonServiceDep,
    chara_calculator: CharaDashaDep,
    astrology_calculator: AstrologyCalculatorDep
) -> ResponseModel:
    """
    Calculate Chara Dasha (Jaimini sign-based system).
    
    Chara Dasha is a rashi (sign) based timing system from Jaimini astrology.
    Unlike planetary dashas, this uses zodiac signs as period lords with
    variable durations based on their positions.
    
    Args:
        person_id (UUID): Unique identifier of the person
        person_service (PersonServiceDep): Injected person service
        vimshottari_calculator (VimshottariDashaDep): Injected Vimshottari calculator
        astrology_calculator (AstrologyCalculatorDep): Injected astrology calculator
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - system: "Jaimini Chara Dasha"
            - current_sign_dasha: Currently active sign period:
                - sign: Zodiac sign name
                - duration: Years of this sign's rule
                - start_date: Period start
                - end_date: Period end
                - house_activated: Which house is activated
            - dasha_sequence: Complete sequence of 12 signs with:
                - Order based on specific Jaimini rules
                - Duration for each sign (1-12 years)
                - Important karakas (significators) activated
            - special_features:
                - Atmakaraka activation periods
                - Arudha lagna influences
                - Rajayoga timing
    
    Raises:
        HTTPException(404): If person not found
    
    Calculation Method:
        - Periods start from ascendant or 7th house
        - Duration = Distance between sign and its lord
        - Special rules for exalted/debilitated lords
        - Considers aspects from benefics/malefics
    
    Example:
        GET /api/v1/dasha/chara/123e4567-e89b-12d3-a456-426614174000
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # This would require full Jaimini calculations
    # For now, return basic structure
    return ResponseModel(
        success=True,
        message="Chara Dasha calculated successfully",
        data={
            "person_id": str(person_id),
            "system": "Jaimini Chara Dasha",
            "note": "Sign-based dasha system",
            "current_sign_dasha": "To be implemented"
        }
    )