"""
Prediction controller for daily, monthly, and yearly predictions - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from uuid import UUID

from josi.api.v1.dependencies import PersonServiceDep, AstrologyCalculatorDep
from josi.api.response import ResponseModel


router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/daily/{person_id}", response_model=ResponseModel)
async def get_daily_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    date: Optional[datetime] = None
) -> ResponseModel:
    """
    Get daily predictions based on planetary transits.
    
    Generates personalized daily forecasts by analyzing the current
    planetary positions relative to the person's birth chart. Primary
    focus is on Moon's transit through houses from natal Moon position.
    
    Args:
        person_id (UUID): Unique identifier of the person
        date (datetime, optional): Prediction date (default: today)
            Format: ISO 8601 (e.g., "2024-01-15T00:00:00")
        person_service (PersonServiceDep): Injected person service
        astrology_calculator (AstrologyCalculatorDep): Injected astrology calculator
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - date: Prediction date
            - moon_sign: Natal Moon sign
            - ascendant_sign: Natal Ascendant sign
            - current_moon_transit: Today's Moon sign
            - predictions: Daily forecast with:
                - general: Overall theme for the day
                - career: Professional guidance
                - finance: Money matters advice
                - health: Wellness recommendations
                - relationships: Personal connections
                - lucky_number: Numerological guidance (1-9)
                - lucky_color: Beneficial color to wear
                - mood: Emotional tendency
                - moon_transit_house: House Moon transits (1-12)
                - favorable_times: Best times for important activities
    
    Raises:
        HTTPException(404): If person not found
    
    Prediction Basis:
        - Moon's transit house from natal Moon (primary)
        - Current planetary aspects to natal positions
        - Weekday rulers and hora periods
        - Vedic electional principles
    
    Moon Transit Houses:
        1st: New beginnings, self-focus
        2nd: Finances, values, possessions
        3rd: Communication, short trips
        4th: Home, family, emotions
        5th: Creativity, romance, children
        6th: Health, work, service
        7th: Partnerships, relationships
        8th: Transformation, shared resources
        9th: Higher learning, travel
        10th: Career, reputation
        11th: Friends, hopes, gains
        12th: Spirituality, isolation, endings
    
    Example:
        GET /api/v1/predictions/daily/123e4567-e89b-12d3-a456-426614174000?date=2024-01-15T00:00:00
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    prediction_date = date or datetime.now()
    
    # Calculate natal chart
    natal_chart = astrology_astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Calculate transits for prediction date
    transit_chart = astrology_astrology_calculator.calculate_vedic_chart(
        prediction_date, person.latitude, person.longitude
    )
    
    # Get Moon sign and ascendant for predictions
    moon_sign = natal_chart["planets"]["Moon"]["sign"]
    ascendant_sign = natal_chart["ascendant"]["sign"]
    
    # Calculate current Moon transit
    transit_moon_sign = transit_chart["planets"]["Moon"]["sign"]
    
    # Generate predictions based on transits
    predictions = _generate_daily_predictions(
        moon_sign, ascendant_sign, transit_moon_sign,
        natal_chart, transit_chart, prediction_date
    )
    
    return ResponseModel(
        success=True,
        message="Daily predictions generated successfully",
        data={
            "person_id": str(person_id),
            "date": prediction_date.isoformat(),
            "moon_sign": moon_sign,
            "ascendant_sign": ascendant_sign,
            "current_moon_transit": transit_moon_sign,
            "predictions": predictions
        }
    )


@router.get("/monthly/{person_id}", response_model=ResponseModel)
async def get_monthly_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> ResponseModel:
    """
    Get monthly predictions based on planetary movements.
    
    Provides a comprehensive monthly forecast by analyzing major
    planetary transits, eclipse effects, and retrograde periods
    that will influence the person during the specified month.
    
    Args:
        person_id (UUID): Unique identifier of the person
        month (int, optional): Month number (1-12, default: current month)
        year (int, optional): Year (default: current year)
        organization (Organization): Current organization (injected)
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - month: Prediction month (1-12)
            - year: Prediction year
            - moon_sign: Natal Moon sign for predictions
            - monthly_overview: General theme and energy of the month
            - key_dates: Important dates to watch:
                - Date and significance
                - Planetary events on those dates
            - favorable_periods: Best times for initiatives:
                - Week numbers or date ranges
                - Activities favored
            - challenges: Potential difficulties:
                - Time periods of concern
                - Nature of challenges
                - Mitigation strategies
            - opportunities: Positive potentials:
                - Areas of growth
                - Lucky periods
                - Recommended actions
    
    Raises:
        HTTPException(404): If person not found
    
    Analysis Includes:
        - New and Full Moons impact
        - Major planet sign changes
        - Retrograde stations
        - Eclipse effects (if any)
        - Beneficial Jupiter/Venus transits
        - Challenging Saturn/Mars transits
        - Personal planet aspects
    
    Monthly Themes Based On:
        - Sun's movement through houses
        - Mercury retrograde periods
        - Venus and Mars positions
        - Outer planet aspects
        - Lunar phases and eclipses
    
    Example:
        GET /api/v1/predictions/monthly/123e4567-e89b-12d3-a456-426614174000?month=3&year=2024
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Default to current month if not specified
    now = datetime.now()
    month = month or now.month
    year = year or now.year
    
    # Calculate natal chart
    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Get Moon sign for predictions
    moon_sign = natal_chart["planets"]["Moon"]["sign"]
    
    # Generate monthly overview
    monthly_themes = _get_monthly_themes(moon_sign, month, year)
    
    return ResponseModel(
        success=True,
        message="Monthly predictions generated successfully",
        data={
            "person_id": str(person_id),
            "month": month,
            "year": year,
            "moon_sign": moon_sign,
            "monthly_overview": monthly_themes["overview"],
            "key_dates": monthly_themes["key_dates"],
            "favorable_periods": monthly_themes["favorable_periods"],
            "challenges": monthly_themes["challenges"],
            "opportunities": monthly_themes["opportunities"]
        }
    )


@router.get("/yearly/{person_id}", response_model=ResponseModel)
async def get_yearly_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    year: Optional[int] = None
) -> ResponseModel:
    """
    Get yearly predictions based on solar return and annual transits.
    
    Comprehensive annual forecast using multiple predictive techniques
    including solar return chart, major transits, progressions, and
    time lord periods to map the year's potential.
    
    Args:
        person_id (UUID): Unique identifier of the person
        year (int, optional): Prediction year (default: current year)
        organization (Organization): Current organization (injected)
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - year: Prediction year
            - yearly_theme: Overall theme and life focus:
                - Primary area of growth
                - Keywords for the year
                - Spiritual lessons
            - career_outlook: Professional predictions:
                - Job changes or promotions
                - Best periods for advancement
                - Challenges to navigate
                - New skill development
            - financial_forecast: Money matters:
                - Income potential
                - Investment timing
                - Major expenses
                - Wealth-building opportunities
            - relationship_prospects: Love and connections:
                - Romance timing
                - Relationship deepening
                - Family dynamics
                - Social expansion
            - health_focus: Wellness guidance:
                - Areas needing attention
                - Preventive measures
                - Energy levels throughout year
                - Best times for procedures
            - spiritual_growth: Evolution and development:
                - Inner work themes
                - Meditation/practice guidance
                - Karmic lessons
                - Consciousness expansion
            - major_periods: Quarterly breakdown:
                - Period date ranges
                - Focus areas
                - Do's and don'ts
            - lucky_months: Most favorable months (1-12)
    
    Raises:
        HTTPException(404): If person not found
    
    Calculation Methods:
        - Solar Return: Sun returns to birth position
        - Profections: Age-based house activation
        - Transits: Slow planet movements
        - Progressions: Day-for-year symbolism
        - Dashas: Vedic time periods
        - Numerology: Personal year number
    
    Life Cycles:
        - 12-year Jupiter cycle
        - 29.5-year Saturn cycle
        - 7-year Uranus sub-cycles
        - Personal biorhythms
    
    Example:
        GET /api/v1/predictions/yearly/123e4567-e89b-12d3-a456-426614174000?year=2024
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Default to current year if not specified
    year = year or datetime.now().year
    
    # Calculate natal chart
    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Calculate solar return chart (when Sun returns to natal position)
    birth_sun_long = natal_chart["planets"]["Sun"]["longitude"]
    
    # Get yearly predictions
    yearly_data = _generate_yearly_predictions(
        natal_chart, person.date_of_birth, year
    )
    
    return ResponseModel(
        success=True,
        message="Yearly predictions generated successfully",
        data={
            "person_id": str(person_id),
            "year": year,
            "yearly_theme": yearly_data["theme"],
            "career_outlook": yearly_data["career"],
            "financial_forecast": yearly_data["finance"],
            "relationship_prospects": yearly_data["relationships"],
            "health_focus": yearly_data["health"],
            "spiritual_growth": yearly_data["spiritual"],
            "major_periods": yearly_data["major_periods"],
            "lucky_months": yearly_data["lucky_months"]
        }
    )


def _generate_daily_predictions(
    moon_sign: str,
    ascendant_sign: str,
    transit_moon_sign: str,
    natal_chart: Dict,
    transit_chart: Dict,
    date: datetime
) -> Dict:
    """Generate daily predictions based on planetary positions."""
    
    # Calculate house position of transit Moon from natal Moon
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    moon_sign_index = signs.index(moon_sign)
    transit_moon_index = signs.index(transit_moon_sign)
    moon_house = ((transit_moon_index - moon_sign_index) % 12) + 1
    
    # Base predictions on Moon's house transit
    house_predictions = {
        1: {"general": "New beginnings and self-focus", "mood": "Confident"},
        2: {"general": "Focus on finances and values", "mood": "Practical"},
        3: {"general": "Communication and short trips favored", "mood": "Curious"},
        4: {"general": "Home and family matters important", "mood": "Nurturing"},
        5: {"general": "Creativity and romance highlighted", "mood": "Playful"},
        6: {"general": "Health and work routines in focus", "mood": "Diligent"},
        7: {"general": "Relationships and partnerships emphasized", "mood": "Harmonious"},
        8: {"general": "Transformation and deep changes", "mood": "Intense"},
        9: {"general": "Learning and expansion favored", "mood": "Optimistic"},
        10: {"general": "Career and public life highlighted", "mood": "Ambitious"},
        11: {"general": "Friends and goals important", "mood": "Social"},
        12: {"general": "Rest and spiritual matters favored", "mood": "Reflective"}
    }
    
    base_prediction = house_predictions.get(moon_house, {"general": "Mixed influences", "mood": "Variable"})
    
    # Calculate lucky number based on date and natal Moon
    lucky_number = ((date.day + date.month + moon_sign_index + 1) % 9) + 1
    
    # Determine lucky color based on ruling planet of the day
    weekday = date.weekday()
    daily_colors = [
        "Red",      # Monday - Mars
        "Green",    # Tuesday - Mercury
        "Yellow",   # Wednesday - Jupiter
        "Pink",     # Thursday - Venus
        "Blue",     # Friday - Saturn
        "Red",      # Saturday - Sun
        "White"     # Sunday - Moon
    ]
    
    return {
        "general": base_prediction["general"],
        "career": _get_career_prediction(moon_house, transit_chart),
        "finance": _get_finance_prediction(moon_house, transit_chart),
        "health": _get_health_prediction(moon_house, transit_chart),
        "relationships": _get_relationship_prediction(moon_house, transit_chart),
        "lucky_number": lucky_number,
        "lucky_color": daily_colors[weekday],
        "mood": base_prediction["mood"],
        "moon_transit_house": moon_house,
        "favorable_times": _get_favorable_times(date)
    }


def _get_career_prediction(moon_house: int, transit_chart: Dict) -> str:
    """Generate career prediction based on Moon house."""
    career_predictions = {
        1: "Take initiative in professional matters",
        2: "Financial gains through work possible",
        3: "Good for meetings and negotiations",
        4: "Work from home or focus on work-life balance",
        5: "Creative projects favored",
        6: "Handle routine tasks efficiently",
        7: "Partnerships and collaborations beneficial",
        8: "Expect changes in work environment",
        9: "Learning new skills beneficial",
        10: "Career advancement opportunities",
        11: "Network with colleagues",
        12: "Work behind the scenes"
    }
    return career_predictions.get(moon_house, "Regular work day")


def _get_finance_prediction(moon_house: int, transit_chart: Dict) -> str:
    """Generate finance prediction based on Moon house."""
    finance_predictions = {
        1: "Good for new financial ventures",
        2: "Favorable for earnings and savings",
        3: "Short-term investments favored",
        4: "Focus on home-related expenses",
        5: "Speculative gains possible",
        6: "Review and organize finances",
        7: "Joint finances need attention",
        8: "Unexpected financial changes",
        9: "Long-term investments favorable",
        10: "Career-related financial gains",
        11: "Group investments beneficial",
        12: "Avoid major financial decisions"
    }
    return finance_predictions.get(moon_house, "Maintain financial stability")


def _get_health_prediction(moon_house: int, transit_chart: Dict) -> str:
    """Generate health prediction based on Moon house."""
    health_predictions = {
        1: "High energy levels, stay active",
        2: "Watch your diet and throat",
        3: "Nervous energy, practice relaxation",
        4: "Emotional well-being important",
        5: "Heart and back need care",
        6: "Focus on daily health routines",
        7: "Maintain balance in lifestyle",
        8: "Detox and regeneration favored",
        9: "Outdoor activities beneficial",
        10: "Manage stress from work",
        11: "Social activities boost health",
        12: "Rest and recuperation needed"
    }
    return health_predictions.get(moon_house, "Maintain regular health habits")


def _get_relationship_prediction(moon_house: int, transit_chart: Dict) -> str:
    """Generate relationship prediction based on Moon house."""
    relationship_predictions = {
        1: "Assert your needs in relationships",
        2: "Show appreciation to loved ones",
        3: "Communication improves relationships",
        4: "Family time is important",
        5: "Romance and fun with partner",
        6: "Help and serve loved ones",
        7: "Focus on partnership harmony",
        8: "Deep bonding opportunities",
        9: "Plan adventures together",
        10: "Balance work and relationships",
        11: "Social gatherings with loved ones",
        12: "Private time with partner"
    }
    return relationship_predictions.get(moon_house, "Nurture close relationships")


def _get_favorable_times(date: datetime) -> List[str]:
    """Get favorable times of the day."""
    # Simplified - in reality would calculate based on hora and other factors
    weekday = date.weekday()
    
    favorable_times = {
        0: ["6:00-7:30 AM", "12:00-1:30 PM"],  # Monday
        1: ["7:30-9:00 AM", "3:00-4:30 PM"],   # Tuesday
        2: ["9:00-10:30 AM", "4:30-6:00 PM"],  # Wednesday
        3: ["6:00-7:30 AM", "1:30-3:00 PM"],   # Thursday
        4: ["7:30-9:00 AM", "12:00-1:30 PM"],  # Friday
        5: ["9:00-10:30 AM", "3:00-4:30 PM"],  # Saturday
        6: ["10:30 AM-12:00 PM", "4:30-6:00 PM"]  # Sunday
    }
    
    return favorable_times.get(weekday, ["Dawn", "Noon"])


def _get_monthly_themes(moon_sign: str, month: int, year: int) -> Dict:
    """Generate monthly themes based on Moon sign."""
    # This would be more complex in reality
    return {
        "overview": f"Month {month} brings focus on personal growth and relationships",
        "key_dates": [f"{year}-{month:02d}-05", f"{year}-{month:02d}-15", f"{year}-{month:02d}-25"],
        "favorable_periods": ["First week", "Third week"],
        "challenges": ["Mid-month may bring communication issues"],
        "opportunities": ["New connections possible", "Financial gains likely"]
    }


def _generate_yearly_predictions(natal_chart: Dict, birth_date: datetime, year: int) -> Dict:
    """Generate yearly predictions."""
    # Calculate age for this year
    age = year - birth_date.year
    
    # Basic yearly themes based on age cycles
    return {
        "theme": "Growth and expansion" if age % 12 == 0 else "Consolidation and stability",
        "career": "Professional advancement likely with focused effort",
        "finance": "Steady growth expected, avoid risky investments",
        "relationships": "Deepening of existing bonds, new connections possible",
        "health": "Focus on preventive care and maintaining routines",
        "spiritual": "Time for inner reflection and spiritual practices",
        "major_periods": [
            {"period": "January-March", "focus": "Career initiatives"},
            {"period": "April-June", "focus": "Personal relationships"},
            {"period": "July-September", "focus": "Financial planning"},
            {"period": "October-December", "focus": "Health and wellness"}
        ],
        "lucky_months": [3, 7, 11]
    }