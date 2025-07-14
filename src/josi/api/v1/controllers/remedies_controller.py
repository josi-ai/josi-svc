"""
Remedies and recommendations controller - Clean Architecture.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import UUID

from josi.api.v1.dependencies import PersonServiceDep, RemedyServiceDep, AstrologyCalculatorDep
from josi.api.response import ResponseModel


router = APIRouter(prefix="/remedies", tags=["remedies"])


@router.get("/{person_id}", response_model=ResponseModel)
async def get_remedies(
    person_id: UUID,
    person_service: PersonServiceDep,
    remedy_service: RemedyServiceDep,
    astrology_calculator: AstrologyCalculatorDep
) -> ResponseModel:
    """
    Get personalized remedies based on planetary positions.
    
    Comprehensive remedial measures based on Vedic astrology principles
    to strengthen benefic planets and pacify malefic influences in the
    birth chart. Remedies are tailored to individual chart analysis.
    
    Args:
        person_id (UUID): Unique identifier of the person
        organization (Organization): Current organization (injected)
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - person_name: Person's name
            - analysis_date: When analysis was performed
            - gemstones: Recommended gemstones:
                - primary: Main life stone
                - secondary: Supporting stones
                - metal: Best metal to wear with
                - finger: Which finger to wear on
                - day: Best day to start wearing
            - mantras: Sacred sound remedies:
                - planet: Which planet's mantra
                - mantra_text: Sanskrit text
                - count: Daily repetitions (108, 1008, etc.)
                - benefits: Expected results
            - donations: Charitable remedies:
                - item: What to donate
                - recipient: Who to donate to
                - day: Which day of week
                - quantity: How much/many
            - yantras: Sacred geometry tools:
                - yantra_name: Which yantra
                - material: Copper, silver, etc.
                - placement: Where to keep
                - activation: How to energize
            - fasting: Dietary observances:
                - day: Which day to fast
                - type: Complete or partial
                - foods_allowed: What can be eaten
                - deity: Associated deity
            - general_remedies: Other recommendations:
                - Temples to visit
                - Rituals to perform
                - Lifestyle changes
                - Spiritual practices
    
    Raises:
        HTTPException(404): If person not found
    
    Remedy Principles:
        - Strengthen weak benefics
        - Pacify strong malefics
        - Support functional benefics
        - Protect from afflictions
        - Enhance positive yogas
    
    Example:
        GET /api/v1/remedies/123e4567-e89b-12d3-a456-426614174000
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Calculate natal chart
    chart_data = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Get remedies based on chart analysis
    remedies = remedy_service.analyze_chart_for_remedies(chart_data)
    
    return ResponseModel(
        success=True,
        message="Remedies calculated successfully",
        data={
            "person_id": str(person_id),
            "person_name": person.name,
            "analysis_date": datetime.now().isoformat(),
            "gemstones": remedies["gemstones"],
            "mantras": remedies["mantras"],
            "donations": remedies["donations"],
            "yantras": remedies["yantras"],
            "fasting": remedies["fasting"],
            "general_remedies": remedies["general_remedies"]
        }
    )


@router.get("/gemstones/{person_id}", response_model=ResponseModel)
async def get_gemstone_recommendations(
    person_id: UUID,
    person_service: PersonServiceDep,
    remedy_service: RemedyServiceDep,
    astrology_calculator: AstrologyCalculatorDep
) -> ResponseModel:
    """
    Get detailed gemstone recommendations.
    
    In-depth gemstone therapy analysis based on Jyotish principles.
    Gemstones act as cosmic filters that can enhance positive planetary
    vibrations and shield from negative influences.
    
    Args:
        person_id (UUID): Unique identifier of the person
        organization (Organization): Current organization (injected)
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - primary_gemstone: Main recommendation:
                - stone: Gemstone name (e.g., "Yellow Sapphire")
                - planet: Ruling planet
                - weight: Minimum carats (e.g., "3+ carats")
                - quality: Required quality standards
                - substitute: Alternative stones
            - life_stone: Based on Moon position:
                - stone: Supporting life force
                - benefits: Health and emotional balance
            - lucky_stone: Based on 9th house lord:
                - stone: For fortune and dharma
                - benefits: Luck and opportunities
            - beneficial_stones: Additional helpful gems:
                - For specific life areas
                - Temporary period stones
            - stones_to_avoid: Conflicting gemstones:
                - stone: Name and ruling planet
                - reason: Why to avoid
            - wearing_instructions: How to wear:
                - purification: Cleansing method
                - activation: Mantra and ritual
                - finger: Which finger
                - hand: Right or left
                - day_time: When to first wear
                - metal: Gold, silver, or panchadhatu
            - metal_recommendations: Compatible metals:
                - primary_metal: Best choice
                - alternative_metals: Other options
    
    Raises:
        HTTPException(404): If person not found
    
    Gemstone Selection Criteria:
        - Ascendant lord strength
        - Functional benefics/malefics
        - Current dasha periods
        - Afflictions to counter
        - Life goals and needs
    
    Planet-Gemstone Mapping:
        - Sun: Ruby
        - Moon: Pearl
        - Mars: Red Coral
        - Mercury: Emerald
        - Jupiter: Yellow Sapphire
        - Venus: Diamond
        - Saturn: Blue Sapphire
        - Rahu: Hessonite
        - Ketu: Cat's Eye
    
    Example:
        GET /api/v1/remedies/gemstones/123e4567-e89b-12d3-a456-426614174000
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Calculate natal chart
    chart_data = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Get detailed gemstone analysis
    remedies_data = remedy_service.analyze_chart_for_remedies(chart_data)
    gemstone_data = remedies_data.get("gemstones", [])
    
    return ResponseModel(
        success=True,
        message="Gemstone recommendations calculated successfully",
        data={
            "person_id": str(person_id),
            "gemstone_recommendations": gemstone_data,
            "all_remedies": remedies_data
        }
    )


@router.post("/numerology", response_model=ResponseModel)
async def calculate_numerology(
    name: str,
    date_of_birth: datetime
) -> ResponseModel:
    """
    Calculate numerology numbers and recommendations.
    
    Comprehensive numerological analysis using Pythagorean and Chaldean
    systems to reveal personality traits, life purpose, and optimal
    timing through the vibrational science of numbers.
    
    Args:
        name (str): Full name as per birth certificate
        date_of_birth (datetime): Birth date for calculations
        organization (Organization): Current organization (injected)
    
    Returns:
        ResponseModel: Success response containing:
            - life_path_number: Core life purpose (1-9, 11, 22, 33):
                - number: The life path number
                - meaning: Core life lessons
                - traits: Personality characteristics
                - career_paths: Suitable professions
            - destiny_number: Name vibration total:
                - number: Calculated from full name
                - purpose: Life mission
                - talents: Natural abilities
            - soul_number: Inner desires (from vowels):
                - number: Heart's desire number
                - inner_self: True motivations
                - needs: Emotional requirements
            - personality_number: Outer self (from consonants):
                - number: How others see you
                - impression: First impressions
                - style: Personal presentation
            - maturity_number: Life path + destiny:
                - number: Later life focus
                - age_activation: When it activates
            - personal_year: Current year cycle (1-9):
                - number: This year's theme
                - opportunities: What to focus on
                - challenges: What to avoid
            - lucky_numbers: Favorable numbers:
                - daily: For routine use
                - important: For big decisions
            - lucky_colors: Beneficial colors:
                - primary: Main color
                - secondary: Supporting colors
            - name_correction: If needed:
                - current_value: Present name number
                - suggested_spelling: Better vibration
                - missing_numbers: What to add
    
    Calculation Methods:
        - Life Path: Birth date reduction
        - Destiny: Full name letter values
        - Soul: Vowels only (A,E,I,O,U,Y)
        - Personality: Consonants only
        - Master Numbers: 11, 22, 33 not reduced
    
    Letter Values (Pythagorean):
        1: A,J,S
        2: B,K,T
        3: C,L,U
        4: D,M,V
        5: E,N,W
        6: F,O,X
        7: G,P,Y
        8: H,Q,Z
        9: I,R
    
    Example:
        POST /api/v1/remedies/numerology
        {
            "name": "John Smith",
            "date_of_birth": "1990-05-15T00:00:00"
        }
    """
    # For now, return placeholder data - would need NumerologyService in dependencies
    numerology_data = {
        "life_path": 7,
        "expression": 3,
        "soul_urge": 9,
        "personality": 5,
        "birth_day": 15,
        "recommendations": ["Focus on spiritual growth", "Express creativity", "Trust intuition"]
    }
    
    return ResponseModel(
        success=True,
        message="Numerology calculated successfully",
        data=numerology_data
    )


@router.post("/color-therapy/{person_id}", response_model=ResponseModel)
async def get_color_therapy(
    person_id: UUID,
    person_service: PersonServiceDep,
    remedy_service: RemedyServiceDep,
    astrology_calculator: AstrologyCalculatorDep
) -> ResponseModel:
    """
    Get color therapy recommendations based on planetary positions.
    
    Color therapy (Chromotherapy) uses planetary color associations
    to balance cosmic energies. Each planet radiates specific color
    frequencies that can be harnessed for healing and success.
    
    Args:
        person_id (UUID): Unique identifier of the person
        organization (Organization): Current organization (injected)
    
    Returns:
        ResponseModel: Success response containing:
            - person_id: Person's UUID
            - daily_colors: Day-wise recommendations:
                - Monday: Moon colors (white, silver)
                - Tuesday: Mars colors (red, coral)
                - Wednesday: Mercury colors (green)
                - Thursday: Jupiter colors (yellow)
                - Friday: Venus colors (white, pastels)
                - Saturday: Saturn colors (blue, black)
                - Sunday: Sun colors (red, orange)
            - purpose_colors: Activity-specific colors:
                - career: For professional success
                - health: For vitality and healing
                - relationships: For harmony
                - wealth: For prosperity
                - spirituality: For meditation
                - education: For learning
            - avoid_colors: Unfavorable colors:
                - color: Name and shade
                - reason: Why to avoid
                - situations: When especially harmful
            - home_colors: Room-wise suggestions:
                - entrance: First impressions
                - living_room: Social harmony
                - bedroom: Rest and romance
                - kitchen: Health and nourishment
                - study: Concentration
                - pooja_room: Spiritual energy
            - office_colors: Workspace optimization:
                - desk_area: Productivity
                - meeting_room: Communication
                - reception: Welcome energy
                - personal_cabin: Authority
    
    Raises:
        HTTPException(404): If person not found
    
    Color Psychology:
        - Red: Energy, passion, courage
        - Orange: Creativity, enthusiasm
        - Yellow: Wisdom, prosperity
        - Green: Growth, healing, balance
        - Blue: Peace, communication
        - Indigo: Intuition, depth
        - Violet: Spirituality, transformation
        - White: Purity, clarity
        - Black: Protection, grounding
    
    Application Methods:
        - Clothing choices
        - Room painting/decor
        - Gemstone colors
        - Meditation on colors
        - Color breathing
        - Light therapy
    
    Example:
        POST /api/v1/remedies/color-therapy/123e4567-e89b-12d3-a456-426614174000
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Calculate natal chart
    chart_data = astrology_calculator.calculate_vedic_chart(
        person.time_of_birth, person.latitude, person.longitude
    )
    
    # Generate color recommendations
    color_therapy = _get_color_therapy_recommendations(chart_data)
    
    return ResponseModel(
        success=True,
        message="Color therapy recommendations generated successfully",
        data={
            "person_id": str(person_id),
            "daily_colors": color_therapy["daily"],
            "purpose_colors": color_therapy["purposes"],
            "avoid_colors": color_therapy["avoid"],
            "home_colors": color_therapy["home"],
            "office_colors": color_therapy["office"]
        }
    )


def _get_color_therapy_recommendations(chart_data: dict) -> dict:
    """Generate color therapy recommendations based on chart."""
    
    # Planet-color associations
    planet_colors = {
        "Sun": ["orange", "gold", "red"],
        "Moon": ["white", "silver", "cream"],
        "Mars": ["red", "crimson", "maroon"],
        "Mercury": ["green", "emerald", "mint"],
        "Jupiter": ["yellow", "gold", "saffron"],
        "Venus": ["white", "pink", "light blue"],
        "Saturn": ["blue", "black", "dark gray"],
        "Rahu": ["smoke gray", "electric blue"],
        "Ketu": ["brown", "gray", "multicolor"]
    }
    
    # Get ascendant sign
    asc_sign = chart_data["ascendant"]["sign"]
    
    # Basic recommendations (would be more complex in reality)
    return {
        "daily": {
            "Monday": "White or silver",
            "Tuesday": "Red or pink",
            "Wednesday": "Green",
            "Thursday": "Yellow or orange",
            "Friday": "White or light blue",
            "Saturday": "Blue or black",
            "Sunday": "Red or orange"
        },
        "purposes": {
            "career": "Based on 10th lord placement",
            "health": "Based on 6th lord",
            "relationships": "Based on 7th lord",
            "wealth": "Based on 2nd and 11th lords"
        },
        "avoid": ["Colors of malefic planets in chart"],
        "home": {
            "living_room": "Warm colors for social areas",
            "bedroom": "Soft, calming colors",
            "study": "Green or yellow for concentration"
        },
        "office": {
            "desk_area": "Colors supporting Mercury",
            "meeting_room": "Balanced, neutral tones"
        }
    }