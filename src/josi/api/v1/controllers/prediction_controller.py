"""
Prediction controller — daily, weekly, monthly, quarterly, half-yearly, and yearly.

All endpoints return predictions structured around 10 life categories with
scores, summaries, advice, and caution.  The shared scoring logic lives in
`josi.services.prediction_engine`.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from uuid import UUID

from josi.api.v1.dependencies import PersonServiceDep, AstrologyCalculatorDep, VimshottariDashaDep
from josi.api.response import ResponseModel
from josi.services.prediction_engine import (
    score_all_categories,
    overall_score_and_summary,
    get_current_dasha_lord,
    identify_sign_changes,
    aggregate_transit_charts,
)

router = APIRouter(prefix="/predictions", tags=["predictions"])


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _natal_and_transit(
    calculator,
    person,
    transit_dt: datetime,
):
    """Compute natal chart + single transit chart and extract the dasha lord."""
    natal_chart = calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude,
    )
    transit_chart = calculator.calculate_vedic_chart(
        transit_dt, person.latitude, person.longitude,
    )
    dasha_lord = get_current_dasha_lord(natal_chart)
    return natal_chart, transit_chart, dasha_lord


def _daily_auspicious_times(prediction_date: datetime) -> List[str]:
    """Return simplified favorable hora windows for a given date."""
    weekday = prediction_date.weekday()
    times = {
        0: ["6:00-7:30 AM", "12:00-1:30 PM"],
        1: ["7:30-9:00 AM", "3:00-4:30 PM"],
        2: ["9:00-10:30 AM", "4:30-6:00 PM"],
        3: ["6:00-7:30 AM", "1:30-3:00 PM"],
        4: ["7:30-9:00 AM", "12:00-1:30 PM"],
        5: ["9:00-10:30 AM", "3:00-4:30 PM"],
        6: ["10:30 AM-12:00 PM", "4:30-6:00 PM"],
    }
    return times.get(weekday, ["Dawn", "Noon"])


def _daily_caution_periods(categories: List[Dict]) -> List[str]:
    """Collect caution strings from low-scoring categories."""
    cautions: List[str] = []
    for cat in categories:
        if cat["score"] <= 3 and cat["caution"]:
            cautions.append(f"{cat['name']}: {cat['caution']}")
    return cautions


def _build_response(
    timeframe: str,
    period_start: str,
    period_end: str,
    categories: List[Dict],
    *,
    sign_changes: Optional[List[Dict]] = None,
    auspicious_times: Optional[List[str]] = None,
    caution_periods: Optional[List[str]] = None,
    extra: Optional[Dict] = None,
) -> Dict:
    """Assemble the standard prediction response dict."""
    overall, summary = overall_score_and_summary(categories)
    result: Dict = {
        "timeframe": timeframe,
        "period": {"start": period_start, "end": period_end},
        "overall_score": overall,
        "overall_summary": summary,
        "categories": categories,
    }
    if sign_changes is not None:
        result["sign_changes"] = sign_changes
    if auspicious_times is not None:
        result["auspicious_times"] = auspicious_times
    if caution_periods is not None:
        result["caution_periods"] = caution_periods
    if extra:
        result.update(extra)
    return result


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/daily/{person_id}", response_model=ResponseModel)
async def get_daily_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    date: Optional[datetime] = None,
) -> ResponseModel:
    """
    Get daily predictions for a person.

    Calculates the Moon transit relative to the natal chart and scores
    10 life categories.  Includes auspicious times and caution periods.

    Args:
        person_id: UUID of the person.
        date: Prediction date (ISO 8601). Defaults to today.
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    prediction_date = date or datetime.now()

    natal_chart, transit_chart, dasha_lord = _natal_and_transit(
        astrology_calculator, person, prediction_date,
    )

    categories = score_all_categories(natal_chart, transit_chart, dasha_lord)
    auspicious = _daily_auspicious_times(prediction_date)
    cautions = _daily_caution_periods(categories)

    date_str = prediction_date.strftime("%Y-%m-%d")

    data = _build_response(
        timeframe="daily",
        period_start=date_str,
        period_end=date_str,
        categories=categories,
        auspicious_times=auspicious,
        caution_periods=cautions,
        extra={
            "person_id": str(person_id),
            "moon_sign": natal_chart["planets"]["Moon"]["sign"],
            "ascendant_sign": natal_chart["ascendant"]["sign"],
            "current_moon_transit": transit_chart["planets"]["Moon"]["sign"],
        },
    )

    return ResponseModel(
        success=True,
        message="Daily predictions generated successfully",
        data=data,
    )


@router.get("/weekly/{person_id}", response_model=ResponseModel)
async def get_weekly_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    week_start: Optional[str] = Query(
        None,
        description="Start date of the week (YYYY-MM-DD). Defaults to the coming Monday.",
    ),
) -> ResponseModel:
    """
    Get weekly predictions for a person.

    Aggregates daily Moon transits across 7 days and identifies planet
    sign changes during the week.  Returns 10 life categories.

    Args:
        person_id: UUID of the person.
        week_start: First day of the 7-day window (YYYY-MM-DD).
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    if week_start:
        try:
            start_date = datetime.strptime(week_start, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="week_start must be YYYY-MM-DD")
    else:
        today = datetime.now()
        # Default to the coming Monday (or today if already Monday)
        days_ahead = (7 - today.weekday()) % 7
        start_date = today + timedelta(days=days_ahead) if days_ahead else today
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = start_date + timedelta(days=6)

    # Natal chart
    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude,
    )
    dasha_lord = get_current_dasha_lord(natal_chart)

    # Sample transits: one per day of the week (noon)
    sample_dates = [
        (start_date + timedelta(days=d)).replace(hour=12)
        for d in range(7)
    ]
    merged_transit = aggregate_transit_charts(
        astrology_calculator, sample_dates, person.latitude, person.longitude,
    )

    categories = score_all_categories(natal_chart, merged_transit, dasha_lord)

    # Identify sign changes during the week
    sign_changes = identify_sign_changes(
        astrology_calculator, start_date, end_date,
        person.latitude, person.longitude,
    )

    data = _build_response(
        timeframe="weekly",
        period_start=start_date.strftime("%Y-%m-%d"),
        period_end=end_date.strftime("%Y-%m-%d"),
        categories=categories,
        sign_changes=sign_changes,
        extra={"person_id": str(person_id)},
    )

    return ResponseModel(
        success=True,
        message="Weekly predictions generated successfully",
        data=data,
    )


@router.get("/monthly/{person_id}", response_model=ResponseModel)
async def get_monthly_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year"),
) -> ResponseModel:
    """
    Get monthly predictions for a person.

    Samples transits at several points during the month and scores
    10 life categories.  Includes sign changes for the period.

    Args:
        person_id: UUID of the person.
        month: Month number (1-12). Defaults to current month.
        year: Year. Defaults to current year.
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    now = datetime.now()
    month = month or now.month
    year = year or now.year

    start_date = datetime(year, month, 1)
    # Last day of month
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude,
    )
    dasha_lord = get_current_dasha_lord(natal_chart)

    # Sample 4 points in the month (roughly weekly)
    sample_dates = [
        datetime(year, month, d, 12) for d in [1, 8, 15, 22]
    ]
    merged_transit = aggregate_transit_charts(
        astrology_calculator, sample_dates, person.latitude, person.longitude,
    )

    categories = score_all_categories(natal_chart, merged_transit, dasha_lord)
    sign_changes = identify_sign_changes(
        astrology_calculator, start_date, end_date,
        person.latitude, person.longitude,
    )

    data = _build_response(
        timeframe="monthly",
        period_start=start_date.strftime("%Y-%m-%d"),
        period_end=end_date.strftime("%Y-%m-%d"),
        categories=categories,
        sign_changes=sign_changes,
        extra={"person_id": str(person_id), "month": month, "year": year},
    )

    return ResponseModel(
        success=True,
        message="Monthly predictions generated successfully",
        data=data,
    )


@router.get("/quarterly/{person_id}", response_model=ResponseModel)
async def get_quarterly_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    dasha_calculator: VimshottariDashaDep,
    quarter: int = Query(..., ge=1, le=4, description="Quarter (1-4)"),
    year: Optional[int] = Query(None, description="Year"),
) -> ResponseModel:
    """
    Get quarterly predictions for a person.

    Analyzes Saturn, Jupiter, and Rahu movements during the quarter and
    factors in the running dasha period.  Returns 10 life categories.

    Args:
        person_id: UUID of the person.
        quarter: Quarter number (1-4).
        year: Year. Defaults to current year.
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    year = year or datetime.now().year

    quarter_months = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}
    start_month, end_month = quarter_months[quarter]
    start_date = datetime(year, start_month, 1)
    if end_month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, end_month + 1, 1) - timedelta(days=1)

    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude,
    )

    # Use VimshottariDashaCalculator for precise dasha data
    moon_longitude = natal_chart["planets"]["Moon"]["longitude"]
    dasha_data = dasha_calculator.calculate_dasha_periods(
        person.time_of_birth, moon_longitude, include_antardashas=True,
    )
    dasha_lord: Optional[str] = None
    if dasha_data and dasha_data.get("current_dasha"):
        md = dasha_data["current_dasha"].get("mahadasha")
        if md:
            dasha_lord = md.get("planet")

    # Sample slow-planet transits at start, mid, and end of quarter
    mid_date = start_date + (end_date - start_date) / 2
    sample_dates = [
        start_date.replace(hour=12),
        mid_date.replace(hour=12),
        end_date.replace(hour=12),
    ]
    merged_transit = aggregate_transit_charts(
        astrology_calculator, sample_dates, person.latitude, person.longitude,
    )

    categories = score_all_categories(natal_chart, merged_transit, dasha_lord)

    # Track sign changes for the heavy-hitters
    slow_planets = ["Saturn", "Jupiter", "Rahu", "Ketu"]
    sign_changes = identify_sign_changes(
        astrology_calculator, start_date, end_date,
        person.latitude, person.longitude,
        planets=slow_planets,
    )

    data = _build_response(
        timeframe="quarterly",
        period_start=start_date.strftime("%Y-%m-%d"),
        period_end=end_date.strftime("%Y-%m-%d"),
        categories=categories,
        sign_changes=sign_changes,
        extra={
            "person_id": str(person_id),
            "quarter": quarter,
            "year": year,
            "dasha_lord": dasha_lord,
        },
    )

    return ResponseModel(
        success=True,
        message="Quarterly predictions generated successfully",
        data=data,
    )


@router.get("/half-yearly/{person_id}", response_model=ResponseModel)
async def get_half_yearly_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    dasha_calculator: VimshottariDashaDep,
    half: int = Query(..., ge=1, le=2, description="Half of the year (1 or 2)"),
    year: Optional[int] = Query(None, description="Year"),
) -> ResponseModel:
    """
    Get half-yearly predictions for a person.

    Examines major planetary period shifts in the 6-month window by
    combining transit and dasha analysis.  Returns 10 life categories.

    Args:
        person_id: UUID of the person.
        half: 1 for Jan-Jun, 2 for Jul-Dec.
        year: Year. Defaults to current year.
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    year = year or datetime.now().year

    if half == 1:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 6, 30)
    else:
        start_date = datetime(year, 7, 1)
        end_date = datetime(year, 12, 31)

    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude,
    )

    # Dasha from VimshottariDashaCalculator
    moon_longitude = natal_chart["planets"]["Moon"]["longitude"]
    dasha_data = dasha_calculator.calculate_dasha_periods(
        person.time_of_birth, moon_longitude, include_antardashas=True,
    )
    dasha_lord: Optional[str] = None
    antardasha_lord: Optional[str] = None
    if dasha_data and dasha_data.get("current_dasha"):
        md = dasha_data["current_dasha"].get("mahadasha")
        if md:
            dasha_lord = md.get("planet")
        ad = dasha_data["current_dasha"].get("antardasha")
        if ad:
            antardasha_lord = ad.get("planet")

    # Sample 6 points (one per month)
    sample_dates = []
    for m_offset in range(6):
        m = (start_date.month + m_offset - 1) % 12 + 1
        y = start_date.year + (start_date.month + m_offset - 1) // 12
        sample_dates.append(datetime(y, m, 15, 12))
    merged_transit = aggregate_transit_charts(
        astrology_calculator, sample_dates, person.latitude, person.longitude,
    )

    categories = score_all_categories(natal_chart, merged_transit, dasha_lord)

    sign_changes = identify_sign_changes(
        astrology_calculator, start_date, end_date,
        person.latitude, person.longitude,
    )

    data = _build_response(
        timeframe="half-yearly",
        period_start=start_date.strftime("%Y-%m-%d"),
        period_end=end_date.strftime("%Y-%m-%d"),
        categories=categories,
        sign_changes=sign_changes,
        extra={
            "person_id": str(person_id),
            "half": half,
            "year": year,
            "dasha_lord": dasha_lord,
            "antardasha_lord": antardasha_lord,
        },
    )

    return ResponseModel(
        success=True,
        message="Half-yearly predictions generated successfully",
        data=data,
    )


@router.get("/yearly/{person_id}", response_model=ResponseModel)
async def get_yearly_predictions(
    person_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    dasha_calculator: VimshottariDashaDep,
    year: Optional[int] = Query(None, description="Year"),
) -> ResponseModel:
    """
    Get yearly predictions for a person.

    Uses a full-year transit aggregate and dasha analysis to score
    10 life categories.  Includes sign changes and dasha context.

    Args:
        person_id: UUID of the person.
        year: Prediction year. Defaults to current year.
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    year = year or datetime.now().year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    natal_chart = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude,
    )

    # Dasha
    moon_longitude = natal_chart["planets"]["Moon"]["longitude"]
    dasha_data = dasha_calculator.calculate_dasha_periods(
        person.time_of_birth, moon_longitude, include_antardashas=True,
    )
    dasha_lord: Optional[str] = None
    antardasha_lord: Optional[str] = None
    if dasha_data and dasha_data.get("current_dasha"):
        md = dasha_data["current_dasha"].get("mahadasha")
        if md:
            dasha_lord = md.get("planet")
        ad = dasha_data["current_dasha"].get("antardasha")
        if ad:
            antardasha_lord = ad.get("planet")

    # Sample 12 months
    sample_dates = [datetime(year, m, 15, 12) for m in range(1, 13)]
    merged_transit = aggregate_transit_charts(
        astrology_calculator, sample_dates, person.latitude, person.longitude,
    )

    categories = score_all_categories(natal_chart, merged_transit, dasha_lord)

    sign_changes = identify_sign_changes(
        astrology_calculator, start_date, end_date,
        person.latitude, person.longitude,
    )

    data = _build_response(
        timeframe="yearly",
        period_start=start_date.strftime("%Y-%m-%d"),
        period_end=end_date.strftime("%Y-%m-%d"),
        categories=categories,
        sign_changes=sign_changes,
        extra={
            "person_id": str(person_id),
            "year": year,
            "dasha_lord": dasha_lord,
            "antardasha_lord": antardasha_lord,
        },
    )

    return ResponseModel(
        success=True,
        message="Yearly predictions generated successfully",
        data=data,
    )
