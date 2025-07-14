"""
Compatibility and matching controller - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException
from uuid import UUID

from josi.api.v1.dependencies import PersonServiceDep, AshtakootaCalculatorDep, AstrologyCalculatorDep
from josi.api.response import ResponseModel


router = APIRouter(prefix="/compatibility", tags=["compatibility"])


@router.post("/calculate", response_model=ResponseModel)
async def calculate_compatibility(
    person1_id: UUID,
    person2_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep,
    ashtakoota_calculator: AshtakootaCalculatorDep
) -> ResponseModel:
    """
    Calculate compatibility between two people using Vedic Ashtakoota method.
    
    The Ashtakoota (8-fold) matching system is the traditional Vedic method
    for assessing marriage compatibility. It evaluates 8 different factors
    (gunas) based on the Moon's position in both charts.
    
    Args:
        person1_id (UUID): First person's unique identifier
        person2_id (UUID): Second person's unique identifier
        organization (Organization): Current organization (injected)
    
    Returns:
        ResponseModel: Success response containing:
            - person1: First person's details (id, name)
            - person2: Second person's details (id, name)
            - total_score: Combined score out of 36 points
            - max_score: Maximum possible score (36)
            - compatibility_percentage: Score as percentage
            - gunas: Individual scores for 8 factors:
                1. Varna (4 pts): Spiritual compatibility
                2. Vashya (2 pts): Dominance and control
                3. Tara (3 pts): Birth star compatibility
                4. Yoni (4 pts): Sexual compatibility
                5. Graha Maitri (5 pts): Mental compatibility
                6. Gana (6 pts): Temperament compatibility
                7. Bhakoot (7 pts): Love and emotional plane
                8. Nadi (8 pts): Genetic compatibility
            - manglik_status: Mars dosha analysis:
                - person1: Boolean manglik status
                - person2: Boolean manglik status
                - manglik_match: Whether both match
            - recommendations: Compatibility interpretation:
                - 0-18: Not recommended
                - 18-24: Average match
                - 24-32: Good match
                - 32-36: Excellent match
            - detailed_analysis: Factor-wise detailed insights
    
    Raises:
        HTTPException(404): If either person not found
    
    Manglik Dosha:
        Occurs when Mars is in 1st, 4th, 7th, 8th, or 12th house.
        Can cause marital discord if only one partner has it.
    
    Example:
        POST /api/v1/compatibility/calculate
        {
            "person1_id": "123e4567-e89b-12d3-a456-426614174000",
            "person2_id": "987fcdeb-51d2-43a1-b890-123456789012"
        }
    """
    # Fetch both persons' data
    person1 = await person_service.get_person(person1_id)
    person2 = await person_service.get_person(person2_id)
    
    if not person1 or not person2:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Calculate charts for both persons
    chart1 = astrology_calculator.calculate_vedic_chart(
        person1.time_of_birth, person1.latitude, person1.longitude
    )
    chart2 = astrology_calculator.calculate_vedic_chart(
        person2.time_of_birth, person2.latitude, person2.longitude
    )
    
    # Get Moon longitudes
    moon1_long = chart1["planets"]["Moon"]["longitude"]
    moon2_long = chart2["planets"]["Moon"]["longitude"]
    
    # Calculate Ashtakoota compatibility
    compatibility = ashtakoota_calculator.calculate_compatibility(moon1_long, moon2_long)
    
    # Check Manglik status
    manglik1 = ashtakoota_calculator.check_manglik_dosha(chart1["planets"], chart1["houses"])
    manglik2 = ashtakoota_calculator.check_manglik_dosha(chart2["planets"], chart2["houses"])
    
    return ResponseModel(
        success=True,
        message="Ashtakoota compatibility calculated successfully",
        data={
            "person1": {"id": str(person1_id), "name": person1.name},
            "person2": {"id": str(person2_id), "name": person2.name},
            "total_score": compatibility["ashtakoota_points"]["total_points"],
            "max_score": compatibility["ashtakoota_points"]["max_points"],
            "compatibility_percentage": compatibility["ashtakoota_points"]["percentage"],
            "gunas": compatibility["guna_analysis"],
            "manglik_status": {
                "person1": manglik1["is_manglik"],
                "person2": manglik2["is_manglik"],
                "manglik_match": manglik1["is_manglik"] == manglik2["is_manglik"]
            },
            "recommendations": compatibility["recommendations"],
            "detailed_analysis": compatibility["overall_assessment"],
            "doshas": compatibility["doshas"],
            "compatibility_level": compatibility["compatibility_level"]
        }
    )


@router.post("/synastry", response_model=ResponseModel)
async def calculate_synastry(
    person1_id: UUID,
    person2_id: UUID,
    person_service: PersonServiceDep,
    astrology_calculator: AstrologyCalculatorDep
) -> ResponseModel:
    """
    Calculate Western synastry compatibility between two people.
    
    Synastry is the Western astrological method of relationship analysis
    that compares two birth charts by overlaying them to see how the
    planets interact and influence each other.
    
    Args:
        person1_id (UUID): First person's unique identifier
        person2_id (UUID): Second person's unique identifier
        organization (Organization): Current organization (injected)
    
    Returns:
        ResponseModel: Success response containing:
            - person1: First person's details (id, name)
            - person2: Second person's details (id, name)
            - aspects: Inter-chart planetary aspects:
                - planet1: Planet from first chart
                - aspect: Type (conjunction, trine, square, etc.)
                - planet2: Planet from second chart
                - orb: Exactness in degrees
                - influence: "Harmonious", "Challenging", "Neutral"
                - interpretation: Aspect meaning
            - house_overlays: Where person2's planets fall in person1's houses:
                - planet: Person2's planet
                - house: Person1's house number
                - interpretation: What this placement means
            - composite_points: Midpoint composite chart data:
                - sun: Composite Sun sign and degree
                - moon: Composite Moon sign and degree
                - ascendant: Composite Ascendant
                - interpretation: Relationship identity
            - compatibility_themes: Major relationship themes:
                - Communication style
                - Emotional connection
                - Physical attraction
                - Long-term potential
                - Growth areas
            - relationship_dynamics: Detailed analysis:
                - strengths: Positive aspects
                - challenges: Difficult aspects
                - karmic_connections: Nodal contacts
                - soul_mate_indicators: Special configurations
    
    Raises:
        HTTPException(404): If either person not found
    
    Key Aspects Analyzed:
        - Conjunctions (0°): Blending of energies
        - Trines (120°): Natural harmony
        - Squares (90°): Dynamic tension
        - Oppositions (180°): Polarity and attraction
        - Sextiles (60°): Opportunities
    
    Special Points:
        - Sun-Moon contacts: Basic compatibility
        - Venus-Mars contacts: Romance and attraction
        - Mercury contacts: Communication
        - Saturn contacts: Commitment and karma
        - Node contacts: Destiny and growth
    
    Example:
        POST /api/v1/compatibility/synastry
        {
            "person1_id": "123e4567-e89b-12d3-a456-426614174000",
            "person2_id": "987fcdeb-51d2-43a1-b890-123456789012"
        }
    """
    # Fetch both persons' data
    person1 = await person_service.get_person(person1_id)
    person2 = await person_service.get_person(person2_id)
    
    if not person1 or not person2:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Calculate Western charts
    chart1 = astrology_calculator.calculate_western_chart(
        person1.time_of_birth, person1.latitude, person1.longitude
    )
    chart2 = astrology_calculator.calculate_western_chart(
        person2.time_of_birth, person2.latitude, person2.longitude
    )
    
    # Calculate synastry aspects
    synastry_data = astrology_calculator.calculate_synastry(chart1, chart2)
    
    return ResponseModel(
        success=True,
        message="Synastry analysis calculated successfully",
        data={
            "person1": {"id": str(person1_id), "name": person1.name},
            "person2": {"id": str(person2_id), "name": person2.name},
            "aspects": synastry_data["aspects"],
            "house_overlays": synastry_data["house_overlays"],
            "composite_points": synastry_data["composite_points"],
            "compatibility_themes": synastry_data["themes"],
            "relationship_dynamics": synastry_data["dynamics"]
        }
    )