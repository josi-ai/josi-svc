"""
Chart service - handles all astrological chart calculations and interpretations.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import math
from josi.core.json_serializer import dumps as json_dumps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from josi.repositories.person_repository import ChartRepository
from josi.models.person_model import Person
from josi.models.chart_model import AstrologyChart, ChartInterpretation, PlanetPosition
from josi.enums.astrology_system_enum import AstrologySystemEnum as AstrologySystem
from josi.enums.house_system_enum import HouseSystemEnum as HouseSystem
from josi.enums.ayanamsa_enum import AyanamsaEnum as Ayanamsa

# Import all calculation services
from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.panchang_service import PanchangCalculator
from josi.services.vedic.ashtakoota_service import AshtakootaCalculator
from josi.services.vedic.dasha_service import VimshottariDashaCalculator
from josi.services.chinese.bazi_calculator_service import BaZiCalculator
from josi.services.western.progressions_service import ProgressionCalculator
from josi.services.interpretation_engine_service import InterpretationEngine


class ChartService:
    """Service for chart calculations and management."""
    
    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.chart_repo = ChartRepository(AstrologyChart, db, user_id)
        
        # Initialize calculators
        self.astrology_calculator = AstrologyCalculator()
        self.panchang_calculator = PanchangCalculator()
        self.ashtakoota_calculator = AshtakootaCalculator()
        self.dasha_calculator = VimshottariDashaCalculator()
        self.bazi_calculator = BaZiCalculator()
        self.progression_calculator = ProgressionCalculator()
        self.interpretation_engine = InterpretationEngine()
    
    async def calculate_charts(
        self,
        person: Person,
        systems: List[AstrologySystem],
        house_system: HouseSystem = HouseSystem.PLACIDUS,
        ayanamsa: Ayanamsa = Ayanamsa.LAHIRI,
        include_interpretations: bool = False
    ) -> List[AstrologyChart]:
        """Calculate multiple chart types for a person."""
        charts = []
        
        for system in systems:
            # Calculate chart based on system
            if system == AstrologySystem.VEDIC:
                chart_data = await self._calculate_vedic_chart(
                    person, house_system, ayanamsa
                )
            elif system == AstrologySystem.WESTERN:
                chart_data = await self._calculate_western_chart(
                    person, house_system
                )
            elif system == AstrologySystem.CHINESE:
                chart_data = await self._calculate_chinese_chart(person)
            elif system == AstrologySystem.HELLENISTIC:
                chart_data = await self._calculate_hellenistic_chart(
                    person, house_system
                )
            else:
                # Default to Western for other systems
                chart_data = await self._calculate_western_chart(
                    person, house_system
                )
                chart_data["system"] = system.name.lower()
            
            # Create chart record - serialize JSON fields using custom serializer
            import json
            from josi.core.json_serializer import custom_json_serializer
            
            chart_dict = {
                "person_id": person.person_id,
                "chart_type": system.name.lower(),
                "house_system": house_system.name.lower(),
                "ayanamsa": ayanamsa.name.lower() if system == AstrologySystem.VEDIC else None,
                "chart_data": json.loads(json.dumps(chart_data, default=custom_json_serializer)),
                "calculated_at": datetime.utcnow(),
                "calculation_version": "2.0",
                "planet_positions": json.loads(json.dumps(chart_data.get("planets", {}), default=custom_json_serializer)),
                "house_cusps": chart_data.get("houses", []),
                "aspects": json.loads(json.dumps(self._calculate_aspects(chart_data), default=custom_json_serializer))
            }
            
            chart = await self.chart_repo.create(chart_dict)
            
            # Save planet positions as separate records
            await self._save_planet_positions(chart.chart_id, chart_data)
            
            # Generate interpretations if requested
            if include_interpretations:
                await self._generate_interpretations(chart)
            
            charts.append(chart)
        
        await self.db.commit()
        return charts
    
    async def _calculate_vedic_chart(
        self,
        person: Person,
        house_system: HouseSystem,
        ayanamsa: Ayanamsa
    ) -> Dict[str, Any]:
        """Calculate Vedic astrology chart."""
        # Set ayanamsa
        self.astrology_calculator.set_ayanamsa(ayanamsa.name.lower())
        
        # Calculate base chart with timezone
        chart_data = self.astrology_calculator.calculate_vedic_chart(
            person.time_of_birth,
            float(person.latitude),
            float(person.longitude),
            person.timezone
        )
        
        # Add panchang
        panchang = self.panchang_calculator.calculate_panchang(
            person.time_of_birth,
            float(person.latitude),
            float(person.longitude),
            person.timezone
        )
        chart_data["panchang"] = panchang
        
        # Add dasha
        moon_long = chart_data["planets"]["Moon"]["longitude"]
        dasha = self.dasha_calculator.calculate_dasha_periods(
            person.time_of_birth,
            moon_long,
            include_antardashas=True
        )
        chart_data["dasha"] = dasha
        
        # Add divisional charts info
        chart_data["divisional_charts_available"] = [
            "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", 
            "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
        ]
        
        return chart_data
    
    async def _calculate_western_chart(
        self,
        person: Person,
        house_system: HouseSystem
    ) -> Dict[str, Any]:
        """Calculate Western astrology chart."""
        # Calculate tropical chart
        chart_data = self.astrology_calculator.calculate_western_chart(
            person.time_of_birth,
            float(person.latitude),
            float(person.longitude)
        )
        
        # Add optional progressions and return info
        try:
            current_progressions = self.progression_calculator.calculate_secondary_progressions(
                person.time_of_birth,
                datetime.now(),
                float(person.latitude),
                float(person.longitude)
            )
            chart_data["current_progressions"] = current_progressions
        except Exception as e:
            # Log but don't fail the natal chart
            chart_data["current_progressions"] = None
            chart_data["progressions_error"] = str(e)
        
        # Solar return is optional - only calculate if reasonable
        try:
            birth_year = person.time_of_birth.year
            current_year = datetime.now().year
            age = current_year - birth_year
            
            # Only calculate if person would be alive (reasonable age limit)
            if 0 <= age <= 120:
                solar_return = self.progression_calculator.calculate_solar_return(
                    person.time_of_birth,
                    current_year,
                    float(person.latitude),
                    float(person.longitude)
                )
                chart_data["current_solar_return"] = solar_return
            else:
                chart_data["current_solar_return"] = None
                chart_data["solar_return_note"] = f"Age {age} out of range for solar return"
        except Exception as e:
            # Log but don't fail the natal chart
            chart_data["current_solar_return"] = None
            chart_data["solar_return_error"] = str(e)
        
        return chart_data
    
    async def _calculate_chinese_chart(self, person: Person) -> Dict[str, Any]:
        """Calculate Chinese astrology chart (BaZi/Four Pillars)."""
        return self.bazi_calculator.calculate_bazi(
            person.time_of_birth,
            float(person.latitude),
            float(person.longitude),
            person.timezone
        )
    
    async def _calculate_hellenistic_chart(
        self,
        person: Person,
        house_system: HouseSystem
    ) -> Dict[str, Any]:
        """Calculate Hellenistic astrology chart."""
        # Start with Western chart as base
        chart_data = await self._calculate_western_chart(person, house_system)
        
        # Add Hellenistic-specific calculations
        chart_data["sect"] = self._determine_sect(chart_data)
        chart_data["lots"] = self._calculate_lots(chart_data)
        chart_data["time_lords"] = self._calculate_time_lords(
            person.time_of_birth, chart_data
        )
        chart_data["zodiacal_releasing"] = self._calculate_zodiacal_releasing(
            person.time_of_birth, chart_data
        )
        
        return chart_data
    
    def _calculate_aspects(self, chart_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate planetary aspects."""
        aspects = []
        planets = chart_data.get("planets", {})
        
        # Major aspects with orbs
        aspect_orbs = {
            0: ("conjunction", 8),
            60: ("sextile", 6),
            90: ("square", 8),
            120: ("trine", 8),
            180: ("opposition", 8)
        }
        
        planet_names = list(planets.keys())
        
        for i, planet1 in enumerate(planet_names):
            for j in range(i + 1, len(planet_names)):
                planet2 = planet_names[j]
                
                long1 = planets[planet1]["longitude"]
                long2 = planets[planet2]["longitude"]
                
                # Calculate shortest angular distance
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for aspects
                for angle, (aspect_name, orb) in aspect_orbs.items():
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "aspect": aspect_name,
                            "angle": angle,
                            "orb": round(abs(diff - angle), 2),
                            "applying": self._is_applying_aspect(
                                planets[planet1], planets[planet2], diff
                            )
                        })
                        break
        
        return aspects
    
    def _is_applying_aspect(
        self,
        planet1: Dict,
        planet2: Dict,
        current_distance: float
    ) -> bool:
        """Determine if aspect is applying or separating."""
        # Simplified - check if faster planet is moving toward exact aspect
        speed1 = planet1.get("speed", 0)
        speed2 = planet2.get("speed", 0)
        
        if abs(speed1) > abs(speed2):
            # Planet1 is faster
            return speed1 > 0 if planet1["longitude"] < planet2["longitude"] else speed1 < 0
        else:
            # Planet2 is faster
            return speed2 < 0 if planet2["longitude"] < planet1["longitude"] else speed2 > 0
    
    async def _save_planet_positions(
        self,
        chart_id: UUID,
        chart_data: Dict[str, Any]
    ) -> None:
        """Save individual planet positions to database."""
        planets = chart_data.get("planets", {})
        
        for planet_name, planet_data in planets.items():
            position_dict = {
                "chart_id": chart_id,
                "user_id": self.user_id,
                "planet_name": planet_name,
                "longitude": planet_data["longitude"],
                "latitude": planet_data.get("latitude", 0),
                "distance": planet_data.get("distance"),
                "speed": planet_data.get("speed", 0),
                "sign": planet_data.get("sign", ""),
                "sign_degree": planet_data["longitude"] % 30,
                "house": planet_data.get("house", 1),
                "house_degree": self._calculate_house_degree(
                    planet_data["longitude"], 
                    planet_data.get("house", 1), 
                    chart_data.get("houses", [])
                ),
                "nakshatra": planet_data.get("nakshatra"),
                "nakshatra_pada": planet_data.get("pada"),
                "dignity": self._calculate_dignity(planet_name, planet_data.get("sign", "")),
                "is_retrograde": planet_data.get("speed", 0) < 0,
                "is_combust": self._is_combust(planet_name, planets.get("Sun", {})),
                "is_deleted": False  # Explicitly set to avoid SQLModel issues
            }
            
            position = PlanetPosition(**position_dict)
            self.db.add(position)
    
    def _calculate_dignity(self, planet: str, sign: str) -> str:
        """Calculate planetary dignity."""
        # Simplified dignity calculation
        dignities = {
            "Sun": {"exalted": "Aries", "own": "Leo", "debilitated": "Libra"},
            "Moon": {"exalted": "Taurus", "own": "Cancer", "debilitated": "Scorpio"},
            "Mars": {"exalted": "Capricorn", "own": ["Aries", "Scorpio"], "debilitated": "Cancer"},
            "Mercury": {"exalted": "Virgo", "own": ["Gemini", "Virgo"], "debilitated": "Pisces"},
            "Jupiter": {"exalted": "Cancer", "own": ["Sagittarius", "Pisces"], "debilitated": "Capricorn"},
            "Venus": {"exalted": "Pisces", "own": ["Taurus", "Libra"], "debilitated": "Virgo"},
            "Saturn": {"exalted": "Libra", "own": ["Capricorn", "Aquarius"], "debilitated": "Aries"}
        }
        
        planet_dignity = dignities.get(planet, {})
        
        if sign == planet_dignity.get("exalted"):
            return "exalted"
        elif sign == planet_dignity.get("debilitated"):
            return "debilitated"
        elif sign in (planet_dignity.get("own", []) if isinstance(planet_dignity.get("own"), list) else [planet_dignity.get("own")]):
            return "own_sign"
        else:
            return "neutral"
    
    def _is_combust(self, planet: str, sun_data: Dict) -> bool:
        """Check if planet is combust (too close to Sun)."""
        if planet == "Sun" or not sun_data:
            return False
        
        # Combustion orbs in degrees
        combustion_orbs = {
            "Moon": 12,
            "Mars": 17,
            "Mercury": 14,
            "Jupiter": 11,
            "Venus": 10,
            "Saturn": 15
        }
        
        # Get planet data from the current context
        # This method is called during planet position saving,
        # so we need to check the sun_data parameter
        if "longitude" not in sun_data:
            return False
            
        # For now, return False as we need planet longitude
        # which should be passed differently
        return False
    
    def _calculate_house_degree(self, longitude: float, house_num: int, houses: List[float]) -> Optional[float]:
        """Calculate degree position within a house."""
        if not houses or house_num < 1 or house_num > 12:
            return None
            
        # Get house cusps
        house_start = houses[house_num - 1]
        house_end = houses[house_num % 12]
        
        # Handle houses that cross 0°
        if house_start > house_end:
            # House crosses 0° Aries
            if longitude >= house_start:
                house_size = (360 - house_start) + house_end
                position_in_house = longitude - house_start
            else:
                house_size = (360 - house_start) + house_end
                position_in_house = (360 - house_start) + longitude
        else:
            # Normal house
            house_size = house_end - house_start
            position_in_house = longitude - house_start
        
        # Calculate percentage through house
        if house_size > 0:
            return round((position_in_house / house_size) * 30, 2)
        
        return None
    
    async def _generate_interpretations(self, chart: AstrologyChart) -> None:
        """Generate interpretations for a chart."""
        interpretations = self.interpretation_engine.generate_interpretations(
            chart.chart_data,
            chart.chart_type
        )
        
        for interp_type, interp_data in interpretations.items():
            interp_dict = {
                "chart_id": chart.chart_id,
                "user_id": self.user_id,
                "interpretation_type": interp_type,
                "language": "en",
                "title": interp_data.get("title", ""),
                "summary": interp_data.get("summary", ""),
                "detailed_text": interp_data.get("details", {}),
                "interpreter_version": "1.0",
                "confidence_score": interp_data.get("confidence", 0.8)
            }

            interpretation = ChartInterpretation(**interp_dict)
            self.db.add(interpretation)

    def _determine_sect(self, chart_data: Dict) -> str:
        """Determine if chart is diurnal or nocturnal (Hellenistic)."""
        sun = chart_data.get("planets", {}).get("Sun", {})
        asc = chart_data.get("ascendant", {}).get("longitude", 0)
        
        # Check if Sun is above horizon (in houses 7-12)
        sun_house = sun.get("house", 1)
        return "Day" if 7 <= sun_house <= 12 else "Night"
    
    def _calculate_lots(self, chart_data: Dict) -> Dict[str, Any]:
        """Calculate Hellenistic lots."""
        planets = chart_data.get("planets", {})
        asc = chart_data.get("ascendant", {}).get("longitude", 0)
        
        sun_long = planets.get("Sun", {}).get("longitude", 0)
        moon_long = planets.get("Moon", {}).get("longitude", 0)
        
        # Lot of Fortune
        if self._determine_sect(chart_data) == "Day":
            fortune = (asc + moon_long - sun_long) % 360
        else:
            fortune = (asc + sun_long - moon_long) % 360
        
        # Lot of Spirit (reverse of Fortune)
        if self._determine_sect(chart_data) == "Day":
            spirit = (asc + sun_long - moon_long) % 360
        else:
            spirit = (asc + moon_long - sun_long) % 360
        
        return {
            "fortune": {
                "longitude": fortune,
                "sign": self._get_sign_from_longitude(fortune),
                "house": self._get_house_from_longitude(fortune, chart_data.get("houses", []))
            },
            "spirit": {
                "longitude": spirit,
                "sign": self._get_sign_from_longitude(spirit),
                "house": self._get_house_from_longitude(spirit, chart_data.get("houses", []))
            }
        }
    
    def _calculate_time_lords(self, birth_time: datetime, chart_data: Dict) -> Dict:
        """Calculate Hellenistic time lord periods."""
        # Simplified - implement full calculations
        return {
            "annual_profection": self._calculate_profection_year(birth_time),
            "zodiacal_releasing": "Not yet implemented"
        }
    
    def _calculate_zodiacal_releasing(self, birth_time: datetime, chart_data: Dict) -> Dict:
        """Calculate Zodiacal Releasing periods."""
        # This is a complex calculation - simplified version
        lots = self._calculate_lots(chart_data)
        fortune_sign = lots["fortune"]["sign"]
        
        return {
            "from_fortune": {
                "current_period": fortune_sign,
                "level": "L1",
                "started": birth_time,
                "description": "Major life direction period"
            }
        }
    
    def _calculate_profection_year(self, birth_time: datetime) -> Dict:
        """Calculate annual profection."""
        age = (datetime.now() - birth_time).days / 365.25
        profection_house = int(age % 12) + 1
        
        return {
            "age": int(age),
            "house": profection_house,
            "sign": self._get_sign_from_house(profection_house),
            "lord": self._get_house_lord(profection_house)
        }
    
    def _get_sign_from_longitude(self, longitude: float) -> str:
        """Get zodiac sign from longitude."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[int(longitude / 30)]
    
    def _get_house_from_longitude(self, longitude: float, houses: List[float]) -> int:
        """Get house number from longitude."""
        if not houses:
            return 1
        
        for i in range(12):
            house_start = houses[i]
            house_end = houses[(i + 1) % 12]
            
            if house_start <= longitude < house_end:
                return i + 1
            elif house_start > house_end:  # Crosses 0°
                if longitude >= house_start or longitude < house_end:
                    return i + 1
        
        return 1
    
    def _get_sign_from_house(self, house: int) -> str:
        """Get sign from house number (simplified)."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[(house - 1) % 12]
    
    def _get_house_lord(self, house: int) -> str:
        """Get planetary lord of house/sign."""
        lords = [
            "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
            "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
        ]
        return lords[(house - 1) % 12]
    
    async def get_chart(self, chart_id: UUID) -> Optional[AstrologyChart]:
        """Get a specific chart."""
        return await self.chart_repo.get(chart_id)
    
    async def get_person_charts(
        self,
        person_id: UUID,
        chart_type: Optional[str] = None
    ) -> List[AstrologyChart]:
        """Get all charts for a person."""
        return await self.chart_repo.get_person_charts(person_id, chart_type)
    
    async def generate_interpretations(
        self,
        chart_id: UUID,
        interpretation_types: List[str],
        language: str = "en"
    ) -> List[ChartInterpretation]:
        """Generate specific interpretations for a chart."""
        chart = await self.get_chart(chart_id)
        if not chart:
            raise ValueError("Chart not found")
        
        interpretations = []
        
        for interp_type in interpretation_types:
            interp_data = self.interpretation_engine.generate_interpretation(
                chart.chart_data,
                chart.chart_type,
                interp_type,
                language
            )
            
            interp_dict = {
                "chart_id": chart_id,
                "user_id": self.user_id,
                "interpretation_type": interp_type,
                "language": language,
                "title": interp_data.get("title", ""),
                "summary": interp_data.get("summary", ""),
                "detailed_text": interp_data.get("details", {}),
                "interpreter_version": "1.0",
                "confidence_score": interp_data.get("confidence", 0.8)
            }
            
            interpretation = ChartInterpretation(**interp_dict)
            self.db.add(interpretation)
            interpretations.append(interpretation)
        
        await self.db.commit()
        return interpretations
    
    async def get_all_charts(
        self,
        limit: int = 100,
        offset: int = 0,
        chart_type: Optional[str] = None,
        selected_fields: Optional[List[str]] = None
    ) -> List[AstrologyChart]:
        """Get all charts with optional filtering."""
        from sqlalchemy import select
        query = select(AstrologyChart).where(AstrologyChart.is_deleted == False)
        
        if self.user_id:
            query = query.where(AstrologyChart.user_id == self.user_id)

        if chart_type:
            query = query.where(AstrologyChart.chart_type == chart_type)

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_person_charts_count(
        self,
        person_id: UUID,
        chart_type: Optional[str] = None
    ) -> int:
        """Get count of charts for a person."""
        from sqlalchemy import select, func
        query = select(func.count(AstrologyChart.chart_id)).where(
            AstrologyChart.person_id == person_id,
            AstrologyChart.is_deleted == False
        )
        
        if self.user_id:
            query = query.where(AstrologyChart.user_id == self.user_id)

        if chart_type:
            query = query.where(AstrologyChart.chart_type == chart_type)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_chart_interpretations(
        self,
        chart_id: UUID,
        selected_fields: Optional[List[str]] = None
    ) -> List[ChartInterpretation]:
        """Get all interpretations for a chart."""
        from sqlalchemy import select
        query = select(ChartInterpretation).where(
            ChartInterpretation.chart_id == chart_id,
            ChartInterpretation.is_deleted == False
        )
        
        if self.user_id:
            query = query.where(ChartInterpretation.user_id == self.user_id)

        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def calculate_charts_for_person(
        self,
        person_id: UUID,
        chart_types: List[str],
        house_system: str = "placidus",
        ayanamsa: Optional[str] = None,
        include_interpretations: bool = False
    ) -> List[AstrologyChart]:
        """Calculate charts for a person by ID."""
        # Get person first
        from josi.repositories.person_repository import PersonRepository
        person_repo = PersonRepository(Person, self.db, self.user_id)
        person = await person_repo.get(person_id)
        
        if not person:
            raise ValueError(f"Person {person_id} not found")
        
        # Convert chart types to enum values
        systems = [AstrologySystem.lookup(ct) for ct in chart_types]
        systems = [s for s in systems if s is not None]
        hs = HouseSystem.lookup(house_system) or HouseSystem.PLACIDUS
        ay = Ayanamsa.lookup(ayanamsa) if ayanamsa else Ayanamsa.LAHIRI
        
        return await self.calculate_charts(
            person=person,
            systems=systems,
            house_system=hs,
            ayanamsa=ay,
            include_interpretations=include_interpretations
        )
    
    async def delete_chart(self, chart_id: UUID) -> bool:
        """Soft delete a chart."""
        chart = await self.get_chart(chart_id)
        if chart:
            chart.is_deleted = True
            chart.deleted_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False
    
    async def restore_chart(self, chart_id: UUID) -> Optional[AstrologyChart]:
        """Restore a soft-deleted chart."""
        from sqlalchemy import select
        query = select(AstrologyChart).where(AstrologyChart.chart_id == chart_id)
        
        if self.user_id:
            query = query.where(AstrologyChart.user_id == self.user_id)

        result = await self.db.execute(query)
        chart = result.scalar_one_or_none()

        if chart and chart.is_deleted:
            chart.is_deleted = False
            chart.deleted_at = None
            await self.db.commit()
            await self.db.refresh(chart)
            return chart
        return None