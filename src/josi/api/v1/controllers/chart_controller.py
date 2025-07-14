"""
Chart calculation and management controller - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from josi.api.v1.dependencies import ChartServiceDep, PersonServiceDep
from josi.api.response import ResponseModel
from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa

router = APIRouter(prefix="/charts", tags=["charts"])


@router.post("/calculate", response_model=ResponseModel)
async def calculate_chart(
    person_id: UUID,
    systems: str = Query(default="vedic,western", description="Comma-separated list of systems"),
    house_system: HouseSystem = Query(default=HouseSystem.PLACIDUS),
    ayanamsa: Ayanamsa = Query(default=Ayanamsa.LAHIRI),
    include_interpretations: bool = Query(default=False),
    chart_service: ChartServiceDep,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Calculate astrological charts for a person.
    
    Generates natal charts for specified astrological systems (Vedic, Western, etc.)
    with customizable house systems and ayanamsa settings. Can optionally include
    AI-generated interpretations.
    
    Args:
        person_id (UUID): Person's unique identifier
        systems (str): Comma-separated list of systems (vedic,western,chinese,hellenistic,mayan,celtic)
        house_system (HouseSystem): House calculation system
            - PLACIDUS: Most common in Western astrology
            - WHOLE_SIGN: Traditional, used in Vedic
            - KOCH: Popular in Europe
            - EQUAL: Simple equal houses
            - PORPHYRIUS: Trisects quadrants
            - REGIOMONTANUS: Medieval system
            - CAMPANUS: Space-based division
            - ALCABITUS: Time-based houses
            - MORINUS: Equatorial houses
            - TOPOCENTRIC: Location-specific
        ayanamsa (Ayanamsa): Ayanamsa for Vedic calculations
            - LAHIRI: Official Indian government
            - KRISHNAMURTI: KP system
            - RAMAN: B.V. Raman's ayanamsa
            - FAGAN_BRADLEY: Western sidereal
            - TRUE_CITRA: Spica at 180°
            - TRUE_REVATI: Revati at 359°50'
            - YUKTESHWAR: Sri Yukteshwar's
        include_interpretations (bool): Include AI interpretations
        chart_service (ChartServiceDep): Injected chart service
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with chart data
            - success (bool): True if successful
            - message (str): Success message
            - data (List[AstrologyChart]): List of calculated charts
    
    Raises:
        HTTPException(404): If person not found
        HTTPException(400): If invalid parameters
        HTTPException(500): If calculation fails
    
    Example:
        POST /api/v1/charts/calculate?person_id=123e4567&systems=vedic,western
    """
    # Parse systems
    systems_list = [s.strip() for s in systems.split(",") if s.strip()]
    try:
        astrology_systems = [AstrologySystem(system) for system in systems_list]
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid astrology system. Valid options: {[s.value for s in AstrologySystem]}"
        )
    
    # Get person
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id {person_id} not found")
    
    try:
        charts = await chart_service.calculate_charts(
            person=person,
            systems=astrology_systems,
            house_system=house_system,
            ayanamsa=ayanamsa,
            include_interpretations=include_interpretations
        )
        
        return ResponseModel(
            success=True,
            message=f"Successfully calculated {len(charts)} charts",
            data=charts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate charts: {str(e)}")


@router.get("/person/{person_id}", response_model=ResponseModel)
async def get_person_charts(
    person_id: UUID,
    system: Optional[AstrologySystem] = None,
    chart_type: Optional[str] = None,
    chart_service: ChartServiceDep
) -> ResponseModel:
    """
    Get all charts for a person.
    
    Retrieves all previously calculated charts for a person,
    optionally filtered by system or chart type.
    
    Args:
        person_id (UUID): Person's unique identifier
        system (AstrologySystem, optional): Filter by astrology system
        chart_type (str, optional): Filter by chart type (natal, transit, etc.)
        chart_service (ChartServiceDep): Injected chart service
    
    Returns:
        ResponseModel: Success response with list of charts
            - success (bool): True if successful
            - message (str): Success message with count
            - data (List[AstrologyChart]): List of chart objects
    
    Example:
        GET /api/v1/charts/person/123e4567?system=vedic
    """
    charts = await chart_service.get_person_charts(person_id, system, chart_type)
    
    return ResponseModel(
        success=True,
        message=f"Found {len(charts)} charts",
        data=charts
    )


@router.get("/{chart_id}", response_model=ResponseModel)
async def get_chart(
    chart_id: UUID,
    include_interpretations: bool = Query(default=False),
    chart_service: ChartServiceDep
) -> ResponseModel:
    """
    Get a specific chart by ID.
    
    Retrieves detailed chart data including planetary positions,
    house cusps, and optionally interpretations.
    
    Args:
        chart_id (UUID): Chart's unique identifier
        include_interpretations (bool): Include interpretations if available
        chart_service (ChartServiceDep): Injected chart service
    
    Returns:
        ResponseModel: Success response with chart data
            - success (bool): True if successful
            - message (str): Success message
            - data (AstrologyChart): Chart object with full details
    
    Raises:
        HTTPException(404): If chart not found
    
    Example:
        GET /api/v1/charts/456e7890?include_interpretations=true
    """
    chart = await chart_service.get_chart_by_id(chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail=f"Chart with id {chart_id} not found")
    
    if include_interpretations:
        # Load interpretations if requested
        interpretations = await chart_service.get_chart_interpretations(chart_id)
        chart.interpretations = interpretations
    
    return ResponseModel(
        success=True,
        message="Chart retrieved successfully",
        data=chart
    )


@router.delete("/{chart_id}", response_model=ResponseModel)
async def delete_chart(
    chart_id: UUID,
    chart_service: ChartServiceDep
) -> ResponseModel:
    """
    Delete a chart (soft delete).
    
    Marks a chart as deleted. The chart data remains in the database
    but is excluded from normal queries.
    
    Args:
        chart_id (UUID): Chart's unique identifier
        chart_service (ChartServiceDep): Injected chart service
    
    Returns:
        ResponseModel: Success response
            - success (bool): True if successful
            - message (str): Success message
            - data (dict): Contains deleted chart_id
    
    Raises:
        HTTPException(404): If chart not found
    
    Example:
        DELETE /api/v1/charts/456e7890
    """
    success = await chart_service.delete_chart(chart_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Chart with id {chart_id} not found")
    
    return ResponseModel(
        success=True,
        message="Chart deleted successfully",
        data={"chart_id": str(chart_id)}
    )


@router.get("/divisional/{person_id}", response_model=ResponseModel)
async def calculate_divisional_chart(
    person_id: UUID,
    division: int = Query(..., ge=1, le=300, description="Division number (D1-D300)"),
    ayanamsa: Ayanamsa = Query(default=Ayanamsa.LAHIRI),
    chart_service: ChartServiceDep,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Calculate Vedic divisional chart (Varga).
    
    Generates specific divisional charts used in Vedic astrology for
    detailed analysis of life areas. Common divisions include:
    - D1 (Rasi): Birth chart
    - D2 (Hora): Wealth
    - D3 (Drekkana): Siblings
    - D4 (Chaturthamsa): Property
    - D7 (Saptamsa): Children
    - D9 (Navamsa): Marriage/Dharma
    - D10 (Dasamsa): Career
    - D12 (Dvadasamsa): Parents
    - D16 (Shodasamsa): Vehicles/Comforts
    - D20 (Vimsamsa): Spiritual progress
    - D24 (Chaturvimsamsa): Education
    - D27 (Bhamsa): Strengths/Weaknesses
    - D30 (Trimsamsa): Misfortunes
    - D40 (Khavedamsa): Auspicious effects
    - D45 (Akshavedamsa): General well-being
    - D60 (Shashtyamsa): Past karma
    
    Args:
        person_id (UUID): Person's unique identifier
        division (int): Division number (1-300)
        ayanamsa (Ayanamsa): Ayanamsa system for calculations
        chart_service (ChartServiceDep): Injected chart service
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with divisional chart
            - success (bool): True if successful
            - message (str): Success message
            - data (dict): Divisional chart data
    
    Raises:
        HTTPException(404): If person not found
        HTTPException(400): If invalid division
        HTTPException(500): If calculation fails
    
    Example:
        GET /api/v1/charts/divisional/123e4567?division=9
    """
    # Get person
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id {person_id} not found")
    
    try:
        divisional_chart = await chart_service.calculate_divisional_chart(
            person=person,
            division=division,
            ayanamsa=ayanamsa
        )
        
        return ResponseModel(
            success=True,
            message=f"Successfully calculated D{division} divisional chart",
            data=divisional_chart
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate divisional chart: {str(e)}")


@router.post("/transit", response_model=ResponseModel)
async def calculate_transit_chart(
    person_id: UUID,
    transit_date: Optional[str] = None,
    systems: str = Query(default="vedic,western"),
    include_aspects: bool = Query(default=True),
    chart_service: ChartServiceDep,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Calculate current planetary transits for a person.
    
    Shows current planetary positions overlaid on the natal chart
    to analyze current influences and timing.
    
    Args:
        person_id (UUID): Person's unique identifier
        transit_date (str, optional): Date for transits (ISO format), defaults to now
        systems (str): Comma-separated list of systems
        include_aspects (bool): Include transit-to-natal aspects
        chart_service (ChartServiceDep): Injected chart service
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with transit data
            - success (bool): True if successful
            - message (str): Success message
            - data (dict): Transit chart with aspects
    
    Example:
        POST /api/v1/charts/transit?person_id=123e4567&transit_date=2024-01-01
    """
    # Get person
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id {person_id} not found")
    
    # Parse systems
    systems_list = [s.strip() for s in systems.split(",") if s.strip()]
    try:
        astrology_systems = [AstrologySystem(system) for system in systems_list]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid astrology system")
    
    try:
        transit_charts = await chart_service.calculate_transit_charts(
            person=person,
            transit_date=transit_date,
            systems=astrology_systems,
            include_aspects=include_aspects
        )
        
        return ResponseModel(
            success=True,
            message="Transit charts calculated successfully",
            data=transit_charts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate transits: {str(e)}")


@router.post("/synastry", response_model=ResponseModel)
async def calculate_synastry(
    person1_id: UUID,
    person2_id: UUID,
    include_composite: bool = Query(default=True),
    chart_service: ChartServiceDep,
    person_service: PersonServiceDep
) -> ResponseModel:
    """
    Calculate synastry (relationship compatibility) between two people.
    
    Analyzes inter-aspects between two charts to determine relationship
    dynamics, compatibility, and karmic connections.
    
    Args:
        person1_id (UUID): First person's ID
        person2_id (UUID): Second person's ID
        include_composite (bool): Include composite chart
        chart_service (ChartServiceDep): Injected chart service
        person_service (PersonServiceDep): Injected person service
    
    Returns:
        ResponseModel: Success response with synastry analysis
            - success (bool): True if successful
            - message (str): Success message
            - data (dict): Synastry data with aspects and analysis
    
    Example:
        POST /api/v1/charts/synastry?person1_id=123&person2_id=456
    """
    # Get both persons
    person1 = await person_service.get_person(person1_id)
    person2 = await person_service.get_person(person2_id)
    
    if not person1 or not person2:
        raise HTTPException(status_code=404, detail="One or both persons not found")
    
    try:
        synastry_data = await chart_service.calculate_synastry(
            person1=person1,
            person2=person2,
            include_composite=include_composite
        )
        
        return ResponseModel(
            success=True,
            message="Synastry analysis completed successfully",
            data=synastry_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate synastry: {str(e)}")