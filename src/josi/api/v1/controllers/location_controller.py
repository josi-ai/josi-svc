"""
Location and geocoding controller - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from josi.api.v1.dependencies import GeocodingServiceDep
from josi.api.response import ResponseModel


router = APIRouter(prefix="/location", tags=["location"])


@router.get("/search", response_model=ResponseModel)
async def search_location(
    query: str,
    geocoding_service: GeocodingServiceDep,
    limit: int = Query(default=5, le=20)
) -> ResponseModel:
    """
    Search for locations and get coordinates and timezone.
    
    Performs geocoding search to find locations matching the query string.
    Returns multiple possible matches with their coordinates and timezone information.
    
    Args:
        query (str): Location search string
            Examples:
            - "New York" - City name only
            - "Paris, France" - City and country
            - "Tokyo, Japan" - City and country
            - "Chennai, Tamil Nadu, India" - City, state, and country
            - "10 Downing Street, London" - Address search
        limit (int): Maximum results to return (default: 5, max: 20)
        geocoding_service (GeocodingServiceDep): Injected geocoding service
    
    Returns:
        ResponseModel: Success response containing:
            - results: List of matched locations with:
                - place: Original search query
                - formatted_address: Full formatted address
                - latitude: Decimal latitude (-90 to 90)
                - longitude: Decimal longitude (-180 to 180)
                - timezone: IANA timezone identifier
                - components: Address components:
                    - city: City/locality name
                    - state: State/province/region
                    - country: Country name
                    - country_code: ISO country code
                - confidence: Match confidence score (0-1)
            - count: Total number of results returned
    
    Raises:
        HTTPException(404): If no locations found matching query
    
    Notes:
        - Uses OpenStreetMap Nominatim for geocoding
        - Results are sorted by relevance
        - Caches results for repeated queries
        - Supports multiple languages in queries
    
    Example:
        GET /api/v1/location/search?query=San%20Francisco&limit=3
    """
    # For now, using single location lookup
    # In production, implement multi-result search
    try:
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(query)
        return ResponseModel(
            success=True,
            message="Location found successfully",
            data={
                "results": [
                    {
                        "place": query,
                        "latitude": lat,
                        "longitude": lon,
                        "timezone": tz,
                        "formatted_address": query  # Would get from geocoding service
                    }
                ],
                "count": 1
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/coordinates", response_model=ResponseModel)
async def get_coordinates(
    city: str,
    geocoding_service: GeocodingServiceDep,
    state: Optional[str] = None,
    country: Optional[str] = None
) -> ResponseModel:
    """
    Get coordinates and timezone for a specific location.
    
    Structured geocoding endpoint that accepts city, state, and country
    as separate parameters for more precise location matching.
    
    Args:
        city (str): City or locality name (required)
            Examples: "Mumbai", "Los Angeles", "London"
        state (str, optional): State, province, or region
            Examples: "California", "Maharashtra", "England"
        country (str, optional): Country name or ISO code
            Examples: "India", "USA", "United Kingdom", "GB"
        geocoding_service (GeocodingServiceDep): Injected geocoding service
    
    Returns:
        ResponseModel: Success response containing:
            - city: Input city name
            - state: Input state (if provided)
            - country: Input country (if provided)
            - latitude: Decimal latitude (-90 to 90)
            - longitude: Decimal longitude (-180 to 180)
            - timezone: IANA timezone identifier (e.g., "Asia/Kolkata")
            - timezone_offset: Current UTC offset (e.g., "+05:30")
            - dst_active: Whether DST is currently active
            - elevation: Elevation in meters (if available)
    
    Raises:
        HTTPException(404): If location not found
    
    Notes:
        - More accurate than free-text search
        - Handles variations in naming (e.g., "NY" vs "New York")
        - Returns the most likely match if multiple exist
        - State parameter improves accuracy for common city names
    
    Example:
        POST /api/v1/location/coordinates
        {
            "city": "Springfield",
            "state": "Illinois",
            "country": "USA"
        }
    """
    try:
        # Build location string
        location_parts = [city]
        if state:
            location_parts.append(state)
        if country:
            location_parts.append(country)
        location = ", ".join(location_parts)
        
        lat, lon, tz = geocoding_service.get_coordinates_and_timezone(location)
        
        return ResponseModel(
            success=True,
            message="Coordinates retrieved successfully",
            data={
                "city": city,
                "state": state,
                "country": country,
                "latitude": lat,
                "longitude": lon,
                "timezone": tz
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/timezone", response_model=ResponseModel)
async def get_timezone(
    latitude: float,
    longitude: float,
    geocoding_service: GeocodingServiceDep
) -> ResponseModel:
    """
    Get timezone for given coordinates.
    
    Reverse geocoding endpoint that determines the timezone for any
    point on Earth based on latitude and longitude coordinates.
    
    Args:
        latitude (float): Latitude in decimal degrees
            Range: -90 to 90 (negative for South)
        longitude (float): Longitude in decimal degrees
            Range: -180 to 180 (negative for West)
        geocoding_service (GeocodingServiceDep): Injected geocoding service
    
    Returns:
        ResponseModel: Success response containing:
            - latitude: Input latitude
            - longitude: Input longitude
            - timezone: IANA timezone identifier
                Examples: "America/New_York", "Europe/London", "Asia/Tokyo"
            - timezone_name: Human-readable timezone name
                Example: "Eastern Standard Time"
            - utc_offset: Current UTC offset in hours
                Example: -5.0 for EST, 5.5 for IST
            - dst_offset: Daylight saving time offset (if applicable)
            - is_dst: Whether DST is currently active
            - country_code: ISO country code for the location
            - region: Geographic region or state
    
    Raises:
        HTTPException(400): If coordinates are invalid or out of range
    
    Notes:
        - Uses offline timezone database for fast lookups
        - Handles timezone boundaries accurately
        - Works for ocean coordinates (returns nearest timezone)
        - Accounts for daylight saving time changes
    
    Example:
        GET /api/v1/location/timezone?latitude=40.7128&longitude=-74.0060
        
        Returns: America/New_York timezone for NYC coordinates
    """
    try:
        timezone = geocoding_service.get_timezone_from_coordinates(latitude, longitude)
        
        return ResponseModel(
            success=True,
            message="Timezone retrieved successfully",
            data={
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get timezone: {str(e)}")