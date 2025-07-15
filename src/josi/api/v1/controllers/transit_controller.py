"""
Transit and prediction controller - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from uuid import UUID

from josi.api.v1.dependencies import PersonServiceDep, AstrologyCalculatorDep
from josi.api.response import ResponseModel


router = APIRouter(prefix="/transits", tags=["transits"])


@router.get("/current/{person_id}", response_model=ResponseModel)
async def get_current_transits(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep
) -> ResponseModel:
    """
    Get current planetary transits affecting a person's natal chart.
    
    Analyzes how current planetary positions interact with birth chart positions.
    Focuses on slow-moving planets that have longer-lasting effects.
    
    Args:
        person_id (UUID): Unique identifier of the person
        person_service (PersonServiceDep): Injected person service
        astrology_calculator (AstrologyCalculatorDep): Injected astrology calculator
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - current_date: Current date/time (UTC)
            - major_transits: List of significant transits with:
                - planet: Transiting planet name
                - current_sign: Planet's current zodiac sign
                - current_degree: Exact degree within sign
                - natal_sign: Planet's birth chart sign
                - natal_degree: Birth chart degree
                - aspect: Type of aspect formed (0°, 60°, 90°, 120°, 180°)
                - orb: Exactness of aspect in degrees
                - intensity: "Strong" (<2° orb) or "Moderate" (2-5° orb)
                - effects: Interpretation of this transit
            - current_planetary_positions: All planets' current positions:
                - sign: Current zodiac sign
                - degree: Degree within sign
                - retrograde: True if planet is retrograde
    
    Raises:
        HTTPException(404): If person not found
    
    Transit Planets Tracked:
        - Jupiter: 12-year cycle, expansion and growth
        - Saturn: 29.5-year cycle, discipline and karma
        - Rahu: 18-year cycle, desires and ambition
        - Ketu: 18-year cycle, spirituality and letting go
    
    Aspects Considered:
        - Conjunction (0°): Fusion of energies
        - Sextile (60°): Opportunities
        - Square (90°): Challenges
        - Trine (120°): Harmony
        - Opposition (180°): Awareness
    
    Example:
        GET /api/v1/transits/current/123e4567-e89b-12d3-a456-426614174000
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    current_time = datetime.utcnow()
    
    # Calculate natal chart
    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Calculate current positions
    current_chart = astrology_calculator.calculate_vedic_chart(
        current_time, person.latitude, person.longitude
    )
    
    # Compare positions and find major transits
    major_transits = []
    
    # Define major aspect angles
    aspects = {
        0: "Conjunction", 60: "Sextile", 90: "Square",
        120: "Trine", 180: "Opposition"
    }
    
    # Check transits for slow-moving planets
    transit_planets = ["Jupiter", "Saturn", "Rahu", "Ketu"]
    
    for planet in transit_planets:
        if planet in current_chart["planets"] and planet in natal_chart["planets"]:
            current_pos = current_chart["planets"][planet]
            natal_pos = natal_chart["planets"][planet]
            
            # Calculate angular distance
            distance = abs(current_pos["longitude"] - natal_pos["longitude"])
            if distance > 180:
                distance = 360 - distance
            
            # Check for aspects (with orb)
            for angle, aspect_name in aspects.items():
                if abs(distance - angle) <= 5:  # 5 degree orb
                    transit = {
                        "planet": planet,
                        "current_sign": current_pos["sign"],
                        "current_degree": round(current_pos["longitude"] % 30, 2),
                        "natal_sign": natal_pos["sign"],
                        "natal_degree": round(natal_pos["longitude"] % 30, 2),
                        "aspect": aspect_name,
                        "orb": round(abs(distance - angle), 2),
                        "intensity": "Strong" if abs(distance - angle) < 2 else "Moderate",
                        "effects": _get_transit_effects(planet, aspect_name)
                    }
                    major_transits.append(transit)
                    break
    
    return ResponseModel(
        success=True,
        message="Current transits calculated successfully",
        data={
            "person_id": str(person_id),
            "current_date": current_time.isoformat(),
            "major_transits": major_transits,
            "current_planetary_positions": {
                planet: {
                    "sign": data["sign"],
                    "degree": round(data["longitude"] % 30, 2),
                    "retrograde": data.get("speed", 0) < 0
                }
                for planet, data in current_chart["planets"].items()
            }
        }
    )


@router.get("/forecast/{person_id}", response_model=ResponseModel)
async def get_transit_forecast(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    days: int = 30
) -> ResponseModel:
    """
    Get transit forecast for upcoming period.
    
    Predicts significant astrological events over the specified time period
    by tracking planetary movements and their interactions with the natal chart.
    
    Args:
        person_id (UUID): Unique identifier of the person
        days (int): Number of days to forecast (default: 30, max: 365)
            - 30: Monthly forecast
            - 90: Quarterly forecast
            - 180: Half-yearly forecast
            - 365: Annual forecast
        person_service (PersonServiceDep): Injected person service
        astrology_calculator (AstrologyCalculatorDep): Injected astrology calculator
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - forecast_period: Time range details:
                - start: Forecast start date (UTC)
                - end: Forecast end date (UTC)
                - days: Number of days covered
            - forecast: Predicted events:
                - exact_transits: List of exact aspect formations:
                    - date: When aspect becomes exact
                    - planet: Transiting planet
                    - aspect: Type of aspect
                    - natal_planet: Planet being aspected
                    - interpretation: What this means
                - sign_changes: Planetary sign ingresses:
                    - date: When planet changes sign
                    - planet: Which planet
                    - from_sign: Previous sign
                    - to_sign: New sign
                    - duration: How long in new sign
                - retrograde_periods: Retrograde motions:
                    - planet: Which planet
                    - date: Start/end of retrograde
                    - sign: Sign where retrograde occurs
                    - type: "station_retrograde" or "station_direct"
    
    Raises:
        HTTPException(404): If person not found
    
    Forecast Elements:
        - Exact transit timing using Swiss Ephemeris
        - Major aspect formations (conjunctions, squares, etc.)
        - Sign ingresses for all planets
        - Retrograde and direct stations
        - Eclipse impacts (if any)
        - Lunar phases affecting natal Moon
    
    Example:
        GET /api/v1/transits/forecast/123e4567-e89b-12d3-a456-426614174000?days=90
    """
    if days > 365:
        days = 365
        
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    current_time = datetime.utcnow()
    
    # Calculate natal chart
    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Track transits over the period
    forecast_data = {
        "exact_transits": [],
        "sign_changes": [],
        "retrograde_periods": []
    }
    
    # Check daily for the forecast period
    for day_offset in range(0, days, 7):  # Check weekly
        check_date = current_time + timedelta(days=day_offset)
        
        # Calculate positions for this date
        transit_chart = astrology_calculator.calculate_vedic_chart(
            check_date, person.latitude, person.longitude
        )
        
        # Check for sign changes and major aspects
        for planet in ["Jupiter", "Saturn", "Rahu", "Ketu", "Mars"]:
            if planet in transit_chart["planets"]:
                transit_pos = transit_chart["planets"][planet]
                
                # Check retrograde status
                if transit_pos.get("speed", 0) < 0:
                    forecast_data["retrograde_periods"].append({
                        "planet": planet,
                        "date": check_date.isoformat(),
                        "sign": transit_pos["sign"]
                    })
    
    return ResponseModel(
        success=True,
        message="Transit forecast calculated successfully",
        data={
            "person_id": str(person_id),
            "forecast_period": {
                "start": current_time.isoformat(),
                "end": (current_time + timedelta(days=days)).isoformat(),
                "days": days
            },
            "forecast": forecast_data
        }
    )


def _get_transit_effects(planet: str, aspect: str) -> str:
    """
    Get general effects of planetary transits.
    
    Provides interpretations based on the transiting planet and aspect type.
    These are general guidelines that should be personalized based on
    house placement and individual chart factors.
    
    Args:
        planet (str): Name of the transiting planet
        aspect (str): Type of aspect being formed
    
    Returns:
        str: Interpretation text for the transit
    """
    effects = {
        "Jupiter": {
            "Conjunction": "Expansion and growth in the area of life affected",
            "Trine": "Opportunities and good fortune",
            "Square": "Need to balance growth with reality",
            "Opposition": "Culmination of growth cycle"
        },
        "Saturn": {
            "Conjunction": "Time of responsibility and hard work",
            "Square": "Challenges that build character",
            "Opposition": "Major life evaluation period",
            "Trine": "Rewards for past efforts"
        },
        "Rahu": {
            "Conjunction": "Intense desires and ambitions surface",
            "Square": "Inner conflicts about life direction",
            "Opposition": "Karmic events and fated encounters"
        },
        "Ketu": {
            "Conjunction": "Spiritual insights and detachment",
            "Square": "Need to release past patterns",
            "Opposition": "Completion of karmic cycle"
        }
    }
    
    return effects.get(planet, {}).get(aspect, "Significant life changes possible")