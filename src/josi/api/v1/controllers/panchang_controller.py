"""
Panchang and calendar-related controller - Clean Architecture.
"""
from fastapi import APIRouter, Query
from datetime import datetime
from typing import Optional

from josi.api.v1.dependencies import PanchangCalculatorDep, MuhurtaCalculatorDep
from josi.api.response import ResponseModel


router = APIRouter(prefix="/panchang", tags=["panchang"])


@router.get("/", response_model=ResponseModel)
async def get_panchang(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone: str,
    panchang_calculator: PanchangCalculatorDep
) -> ResponseModel:
    """
    Get Panchang (Hindu calendar) details for a specific date and location.
    
    Panchang is the Hindu calendar system that provides five key elements
    (panch = five, ang = limbs) essential for determining auspicious timing
    and understanding the quality of time.
    
    Args:
        date (datetime): Date and time for calculation (ISO format)
        latitude (float): Location latitude (-90 to 90)
        longitude (float): Location longitude (-180 to 180)
        timezone (str): Timezone name (e.g., "Asia/Kolkata", "America/New_York")
        panchang_calculator (PanchangCalculatorDep): Injected panchang calculator
    
    Returns:
        ResponseModel: Success response containing:
            - date: Calculation date
            - location: Coordinates and timezone
            - tithi: Lunar day (1-30) with details:
                - name: Sanskrit name (e.g., "Shukla Paksha Pratipada")
                - deity: Presiding deity
                - percentage: Completion percentage at given time
                - end_time: When tithi ends
            - nakshatra: Lunar mansion (1-27) with:
                - name: Sanskrit name (e.g., "Ashwini")
                - ruler: Planetary ruler
                - pada: Quarter (1-4)
                - percentage: Completion percentage
                - end_time: When nakshatra changes
            - yoga: Sun-Moon combination (1-27) with:
                - name: Sanskrit name
                - effect: Auspicious/inauspicious nature
                - end_time: When yoga changes
            - karana: Half of tithi (1-11) with:
                - name: Sanskrit name
                - type: Fixed or movable
                - end_time: When karana changes
            - rahu_kaal: Inauspicious period of the day
            - sunrise/sunset: Local sun timings
            - detailed_panchang: Complete calculations
            - auspicious_periods: Good times for activities
    
    Five Elements (Panchang):
        1. Tithi: Lunar day determining Moon's phase
        2. Vara: Weekday ruled by specific planet
        3. Nakshatra: Moon's position in 27 lunar mansions
        4. Yoga: Combined longitude of Sun and Moon
        5. Karana: Half of a tithi
    
    Example:
        GET /api/v1/panchang?date=2024-01-15T06:00:00&latitude=13.0827&longitude=80.2707&timezone=Asia/Kolkata
    """
    # Calculate panchang
    panchang_data = panchang_calculator.calculate_panchang(date, latitude, longitude, timezone)
    
    return ResponseModel(
        success=True,
        message="Panchang calculated successfully",
        data={
            "date": date.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude, "timezone": timezone},
            "tithi": panchang_data["tithi"]["name"],
            "nakshatra": panchang_data["nakshatra"]["name"],
            "yoga": panchang_data["yoga"]["name"],
            "karana": panchang_data["karana"]["name"],
            "detailed_panchang": panchang_data,
            "auspicious_periods": panchang_data.get("auspicious_periods", [])
        }
    )


@router.post("/muhurta", response_model=ResponseModel)
async def find_muhurta(
    purpose: str,  # marriage, business, travel, etc.
    start_date: datetime,
    end_date: datetime,
    latitude: float,
    longitude: float,
    timezone: str,
    max_results: int = Query(default=10, le=50),
    muhurta_calculator: MuhurtaCalculatorDep
) -> ResponseModel:
    """
    Find auspicious times (Muhurta) for specific activities.
    
    Muhurta is the Vedic system of electional astrology that identifies
    the most favorable times to begin important activities. Each muhurta
    is approximately 48 minutes long, with 30 muhurtas in a day.
    
    Args:
        purpose (str): Type of activity to find muhurta for
            Supported purposes:
            - "marriage": Wedding ceremonies
            - "business": Starting new ventures, signing contracts
            - "travel": Beginning journeys
            - "education": Starting studies, exams
            - "property": Buying property, moving homes
            - "medical": Surgery, starting treatment
            - "spiritual": Religious ceremonies, meditation
            - "general": Any auspicious activity
        start_date (datetime): Search period start (ISO format)
        end_date (datetime): Search period end (ISO format)
        latitude (float): Location latitude (-90 to 90)
        longitude (float): Location longitude (-180 to 180)
        timezone (str): Timezone name
        max_results (int): Maximum muhurtas to return (default: 10, max: 50)
        muhurta_calculator (MuhurtaCalculatorDep): Injected muhurta calculator
    
    Returns:
        ResponseModel: Success response containing:
            - purpose: Activity type searched for
            - location: Search location details
            - search_period: Date range searched
            - auspicious_times: List of muhurtas with:
                - start_time: Muhurta start (ISO format)
                - end_time: Muhurta end (ISO format)
                - quality: "Excellent", "Very Good", "Good"
                - nakshatra: Prevailing lunar mansion
                - tithi: Lunar day
                - yoga: Sun-Moon combination
                - special_factors: List of positive factors:
                    - Benefic planets in kendras
                    - Absence of malefic influences
                    - Special yogas present
                - avoid_factors: Any negative factors present
                - overall_score: Numerical rating (0-100)
            - total_found: Number of muhurtas found
    
    Muhurta Selection Criteria:
        - Avoids inauspicious tithis (4th, 9th, 14th)
        - Considers nakshatra qualities
        - Checks for Rahu Kaal and other negative periods
        - Evaluates planetary positions and aspects
        - Applies purpose-specific rules
    
    Example:
        POST /api/v1/panchang/muhurta
        {
            "purpose": "marriage",
            "start_date": "2024-02-01T00:00:00",
            "end_date": "2024-02-29T23:59:59",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata",
            "max_results": 20
        }
    """
    # Find muhurtas for the given purpose
    muhurtas = muhurta_calculator.find_muhurta(
        purpose=purpose,
        start_date=start_date,
        end_date=end_date,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        max_results=max_results
    )
    
    return ResponseModel(
        success=True,
        message=f"Found {len(muhurtas)} auspicious times for {purpose}",
        data={
            "purpose": purpose,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone
            },
            "search_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "auspicious_times": muhurtas,
            "total_found": len(muhurtas)
        }
    )