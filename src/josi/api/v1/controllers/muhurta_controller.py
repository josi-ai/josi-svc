"""
Muhurta (Auspicious Time) calculator API controller.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from josi.core.database import get_db
from josi.api.v1.dependencies import get_current_organization
from josi.models.organization_model import Organization
from josi.services.vedic.muhurta_service import MuhurtaCalculator
from josi.api.response import ResponseModel
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/muhurta", tags=["Muhurta"])


class MuhurtaRequest(BaseModel):
    """Request schema for finding auspicious times."""
    purpose: str = Field(..., description="Purpose/activity type")
    start_date: datetime = Field(..., description="Start of search period")
    end_date: datetime = Field(..., description="End of search period")
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    timezone: str = Field(..., description="Location timezone")
    max_results: Optional[int] = Field(default=10, ge=1, le=50, description="Maximum results")


class RahuKaalRequest(BaseModel):
    """Request schema for Rahu Kaal calculation."""
    date: datetime = Field(..., description="Date for calculation")
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    timezone: str = Field(..., description="Location timezone")


class MonthlyCalendarRequest(BaseModel):
    """Request schema for monthly auspicious calendar."""
    year: int = Field(..., ge=1900, le=2100, description="Year")
    month: int = Field(..., ge=1, le=12, description="Month")
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    timezone: str = Field(..., description="Location timezone")


@router.post("/find-muhurta")
async def find_muhurta(
    request: MuhurtaRequest,
    db: AsyncSession = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Find auspicious times (Muhurta) for specific activities.
    
    Supports activities like:
    - marriage
    - business
    - travel
    - education
    - medical
    - property
    """
    try:
        calculator = MuhurtaCalculator()
        
        # Validate date range
        if request.end_date <= request.start_date:
            raise HTTPException(
                status_code=400,
                detail="End date must be after start date"
            )
        
        # Validate activity type
        valid_activities = ["marriage", "business", "travel", "education", "medical", "property"]
        if request.purpose.lower() not in valid_activities:
            logger.warning(
                "Using general business rules for unknown activity",
                purpose=request.purpose,
                valid_activities=valid_activities
            )
        
        # Calculate muhurtas
        muhurtas = calculator.find_muhurta(
            purpose=request.purpose,
            start_date=request.start_date,
            end_date=request.end_date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone,
            max_results=request.max_results
        )
        
        logger.info(
            "Muhurta calculation completed",
            purpose=request.purpose,
            organization_id=str(organization.organization_id),
            result_count=len(muhurtas)
        )
        
        return ResponseModel(
            success=True,
            message="Auspicious times calculated successfully",
            data={
                "muhurtas": muhurtas,
                "search_criteria": {
                    "purpose": request.purpose,
                    "date_range": f"{request.start_date.date()} to {request.end_date.date()}",
                    "location": f"{request.latitude}, {request.longitude}",
                    "timezone": request.timezone
                },
                "total_found": len(muhurtas)
            }
        )
    
    except Exception as e:
        logger.error(
            "Failed to calculate muhurta",
            error=str(e),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate auspicious times: {str(e)}"
        )


@router.post("/rahu-kaal")
async def calculate_rahu_kaal(
    request: RahuKaalRequest,
    db: AsyncSession = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Calculate Rahu Kaal (inauspicious time) for a specific date and location.
    
    Rahu Kaal is considered inauspicious for starting new ventures.
    """
    try:
        calculator = MuhurtaCalculator()
        
        rahu_kaal_data = calculator.calculate_rahu_kaal(
            date=request.date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )
        
        logger.info(
            "Rahu Kaal calculation completed",
            date=request.date.date(),
            organization_id=str(organization.organization_id)
        )
        
        return ResponseModel(
            success=True,
            message="Rahu Kaal calculated successfully",
            data=rahu_kaal_data
        )
    
    except Exception as e:
        logger.error(
            "Failed to calculate Rahu Kaal",
            error=str(e),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate Rahu Kaal: {str(e)}"
        )


@router.post("/monthly-calendar")
async def get_monthly_calendar(
    request: MonthlyCalendarRequest,
    db: AsyncSession = Depends(get_db),
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Get auspicious dates calendar for an entire month.
    
    Returns daily panchang information and auspicious classifications.
    """
    try:
        calculator = MuhurtaCalculator()
        
        calendar_data = calculator.get_monthly_calendar(
            year=request.year,
            month=request.month,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )
        
        # Calculate statistics
        auspicious_count = sum(1 for day in calendar_data if day["is_auspicious"])
        
        logger.info(
            "Monthly calendar generated",
            year=request.year,
            month=request.month,
            organization_id=str(organization.organization_id),
            auspicious_days=auspicious_count
        )
        
        return ResponseModel(
            success=True,
            message="Monthly calendar generated successfully",
            data={
                "calendar": calendar_data,
                "month_info": {
                    "year": request.year,
                    "month": request.month,
                    "total_days": len(calendar_data),
                    "auspicious_days": auspicious_count,
                    "location": f"{request.latitude}, {request.longitude}",
                    "timezone": request.timezone
                }
            }
        )
    
    except Exception as e:
        logger.error(
            "Failed to generate monthly calendar",
            error=str(e),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate monthly calendar: {str(e)}"
        )


@router.get("/activities")
async def get_supported_activities(
    organization: Organization = Depends(get_current_organization)
) -> ResponseModel:
    """
    Get list of supported activities for Muhurta calculation.
    """
    activities = [
        {
            "name": "marriage",
            "description": "Wedding ceremonies and marriage-related events",
            "considerations": ["Favorable tithis", "Auspicious nakshatras", "Avoid malefic periods"]
        },
        {
            "name": "business",
            "description": "Starting new business ventures or important business activities",
            "considerations": ["Prosperity-enhancing periods", "Jupiter's favorable influence"]
        },
        {
            "name": "travel",
            "description": "Beginning journeys or travel-related activities",
            "considerations": ["Safe travel periods", "Favorable directions"]
        },
        {
            "name": "education",
            "description": "Starting studies, exams, or educational activities",
            "considerations": ["Mercury's favorable periods", "Wisdom-enhancing times"]
        },
        {
            "name": "medical",
            "description": "Medical procedures, surgeries, or health-related activities",
            "considerations": ["Healing-favorable periods", "Avoid malefic influences"]
        },
        {
            "name": "property",
            "description": "Property purchase, real estate, or construction activities",
            "considerations": ["Stability-enhancing periods", "Avoid property-related doshas"]
        }
    ]
    
    return ResponseModel(
        success=True,
        message="Supported activities retrieved successfully",
        data={
            "activities": activities,
            "note": "Custom activities will use general business rules"
        }
    )


@router.get("/best-times-today")
async def get_best_times_today(
    latitude: float = Query(..., ge=-90, le=90, description="Location latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Location longitude"),
    timezone: str = Query(..., description="Location timezone"),
    db: AsyncSession = Depends(get_db),
    organization: Organization = Depends(get_current_organization),
    purpose: str = Query(default="general", description="Activity purpose")
) -> ResponseModel:
    """
    Get best times for today for quick reference.
    """
    try:
        calculator = MuhurtaCalculator()
        today = datetime.now()
        tomorrow = today.replace(hour=23, minute=59, second=59)
        
        # Find muhurtas for today
        muhurtas = calculator.find_muhurta(
            purpose=purpose,
            start_date=today,
            end_date=tomorrow,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            max_results=5
        )
        
        # Calculate Rahu Kaal for today
        rahu_kaal = calculator.calculate_rahu_kaal(
            date=today,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )
        
        return ResponseModel(
            success=True,
            message="Today's auspicious times calculated",
            data={
                "date": today.date().isoformat(),
                "best_times": muhurtas,
                "rahu_kaal": rahu_kaal["rahu_kaal"],
                "general_advice": "Start important activities during auspicious times and avoid Rahu Kaal"
            }
        )
    
    except Exception as e:
        logger.error(
            "Failed to get today's best times",
            error=str(e),
            organization_id=str(organization.organization_id)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get today's auspicious times: {str(e)}"
        )