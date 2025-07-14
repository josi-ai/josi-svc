"""
Western astrology progressions and return charts calculator.
Implements secondary progressions, solar arc directions, and return charts.
"""
import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math


class ProgressionCalculator:
    """Calculate various progression and return charts for Western astrology."""
    
    def __init__(self):
        swe.set_ephe_path('')
    
    def calculate_secondary_progressions(
        self,
        birth_datetime: datetime,
        target_datetime: datetime,
        birth_latitude: float,
        birth_longitude: float
    ) -> Dict:
        """
        Calculate secondary progressions (day-for-a-year).
        
        Args:
            birth_datetime: Native's birth date and time
            target_datetime: Date to calculate progressions for
            birth_latitude: Birth latitude
            birth_longitude: Birth longitude
        
        Returns:
            Progressed chart data
        """
        # Calculate days between birth and target
        days_lived = (target_datetime - birth_datetime).days
        years_lived = days_lived / 365.25
        
        # Progressed date = birth + years_lived days
        progressed_datetime = birth_datetime + timedelta(days=years_lived)
        
        # Calculate progressed chart
        prog_jd = self._datetime_to_julian(progressed_datetime)
        
        # Calculate progressed planets
        progressed_planets = {}
        planets = [
            ("Sun", swe.SUN),
            ("Moon", swe.MOON),
            ("Mercury", swe.MERCURY),
            ("Venus", swe.VENUS),
            ("Mars", swe.MARS),
            ("Jupiter", swe.JUPITER),
            ("Saturn", swe.SATURN),
            ("Uranus", swe.URANUS),
            ("Neptune", swe.NEPTUNE),
            ("Pluto", swe.PLUTO)
        ]
        
        for planet_name, planet_id in planets:
            xx, ret = swe.calc_ut(prog_jd, planet_id)
            
            progressed_planets[planet_name] = {
                "longitude": xx[0],
                "latitude": xx[1],
                "distance": xx[2],
                "speed": xx[3],
                "sign": self._get_sign(xx[0]),
                "degree_in_sign": xx[0] % 30
            }
        
        # Calculate progressed angles
        houses, ascmc = swe.houses(prog_jd, birth_latitude, birth_longitude, b'P')
        
        # Calculate progressed Moon phase
        prog_sun = progressed_planets["Sun"]["longitude"]
        prog_moon = progressed_planets["Moon"]["longitude"]
        moon_phase = self._calculate_moon_phase(prog_sun, prog_moon)
        
        # Important progressed aspects to natal
        natal_jd = self._datetime_to_julian(birth_datetime)
        important_aspects = self._calculate_progressed_aspects(
            progressed_planets, natal_jd, birth_latitude, birth_longitude
        )
        
        return {
            "calculation_date": target_datetime.isoformat(),
            "years_progressed": round(years_lived, 2),
            "progressed_date": progressed_datetime.isoformat(),
            "progressed_planets": progressed_planets,
            "progressed_angles": {
                "ASC": houses[0],
                "MC": ascmc[1],
                "DC": (houses[0] + 180) % 360,
                "IC": (ascmc[1] + 180) % 360
            },
            "progressed_moon_phase": moon_phase,
            "important_aspects": important_aspects,
            "current_progressions": self._interpret_current_progressions(
                progressed_planets, important_aspects
            )
        }
    
    def calculate_solar_arc_directions(
        self,
        birth_datetime: datetime,
        target_datetime: datetime,
        birth_latitude: float,
        birth_longitude: float
    ) -> Dict:
        """
        Calculate solar arc directions.
        All planets move at the rate of the progressed Sun.
        """
        # Calculate progressed Sun position
        days_lived = (target_datetime - birth_datetime).days
        years_lived = days_lived / 365.25
        
        # Get natal positions
        natal_jd = self._datetime_to_julian(birth_datetime)
        natal_sun_xx, _ = swe.calc_ut(natal_jd, swe.SUN)
        natal_sun_long = natal_sun_xx[0]
        
        # Get progressed Sun
        prog_datetime = birth_datetime + timedelta(days=years_lived)
        prog_jd = self._datetime_to_julian(prog_datetime)
        prog_sun_xx, _ = swe.calc_ut(prog_jd, swe.SUN)
        prog_sun_long = prog_sun_xx[0]
        
        # Solar arc = progressed Sun - natal Sun
        solar_arc = (prog_sun_long - natal_sun_long) % 360
        
        # Apply solar arc to all planets
        directed_planets = {}
        planets = [
            ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
            ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
            ("Saturn", swe.SATURN), ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE),
            ("Pluto", swe.PLUTO), ("NorthNode", swe.MEAN_NODE)
        ]
        
        for planet_name, planet_id in planets:
            xx, _ = swe.calc_ut(natal_jd, planet_id)
            natal_long = xx[0]
            
            directed_long = (natal_long + solar_arc) % 360
            
            directed_planets[planet_name] = {
                "natal_longitude": natal_long,
                "directed_longitude": directed_long,
                "arc": solar_arc,
                "sign": self._get_sign(directed_long),
                "degree_in_sign": directed_long % 30
            }
        
        # Calculate directed angles
        houses, ascmc = swe.houses(natal_jd, birth_latitude, birth_longitude, b'P')
        directed_angles = {
            "ASC": (houses[0] + solar_arc) % 360,
            "MC": (ascmc[1] + solar_arc) % 360
        }
        
        # Find important directed aspects
        important_aspects = self._find_solar_arc_aspects(directed_planets, directed_angles)
        
        return {
            "calculation_date": target_datetime.isoformat(),
            "years_lived": round(years_lived, 2),
            "solar_arc": round(solar_arc, 2),
            "directed_planets": directed_planets,
            "directed_angles": directed_angles,
            "important_aspects": important_aspects
        }
    
    def calculate_solar_return(
        self,
        birth_datetime: datetime,
        return_year: int,
        return_latitude: float,
        return_longitude: float
    ) -> Dict:
        """
        Calculate solar return chart for a specific year.
        
        Args:
            birth_datetime: Native's birth date and time
            return_year: Year to calculate solar return for
            return_latitude: Location latitude for return
            return_longitude: Location longitude for return
        """
        # Get natal Sun position
        natal_jd = self._datetime_to_julian(birth_datetime)
        natal_sun_xx, _ = swe.calc_ut(natal_jd, swe.SUN)
        natal_sun_long = natal_sun_xx[0]
        
        # Find exact moment Sun returns to natal position
        search_start = datetime(return_year, birth_datetime.month, 1)
        return_moment = self._find_sun_return_moment(
            natal_sun_long, search_start
        )
        
        if not return_moment:
            raise ValueError(f"Could not calculate solar return for year {return_year}")
        
        # Calculate full chart for return moment
        return_jd = self._datetime_to_julian(return_moment)
        
        # Calculate planets
        return_planets = {}
        planets = [
            ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
            ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
            ("Saturn", swe.SATURN), ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE),
            ("Pluto", swe.PLUTO), ("NorthNode", swe.MEAN_NODE)
        ]
        
        for planet_name, planet_id in planets:
            xx, ret = swe.calc_ut(return_jd, planet_id)
            
            return_planets[planet_name] = {
                "longitude": xx[0],
                "latitude": xx[1],
                "distance": xx[2],
                "speed": xx[3],
                "sign": self._get_sign(xx[0]),
                "degree_in_sign": xx[0] % 30,
                "is_retrograde": xx[3] < 0
            }
        
        # Calculate houses for return location
        houses, ascmc = swe.houses(return_jd, return_latitude, return_longitude, b'P')
        
        # Determine house positions
        for planet_name, planet_data in return_planets.items():
            planet_data["house"] = self._get_house_position(
                planet_data["longitude"], houses
            )
        
        # Calculate aspects in return chart
        aspects = self._calculate_aspects(return_planets)
        
        # Annual profections
        age_at_return = return_year - birth_datetime.year
        profection_house = (age_at_return % 12) + 1
        
        return {
            "return_year": return_year,
            "return_moment": return_moment.isoformat(),
            "location": {
                "latitude": return_latitude,
                "longitude": return_longitude
            },
            "planets": return_planets,
            "houses": list(houses),
            "angles": {
                "ASC": houses[0],
                "MC": ascmc[1],
                "DC": (houses[0] + 180) % 360,
                "IC": (ascmc[1] + 180) % 360
            },
            "aspects": aspects,
            "profection": {
                "age": age_at_return,
                "house": profection_house,
                "lord": self._get_house_lord(profection_house, houses[0])
            },
            "themes": self._analyze_return_themes(return_planets, houses, aspects)
        }
    
    def calculate_lunar_return(
        self,
        birth_datetime: datetime,
        target_month: datetime,
        return_latitude: float,
        return_longitude: float
    ) -> Dict:
        """Calculate lunar return for a specific month."""
        # Get natal Moon position
        natal_jd = self._datetime_to_julian(birth_datetime)
        natal_moon_xx, _ = swe.calc_ut(natal_jd, swe.MOON)
        natal_moon_long = natal_moon_xx[0]
        
        # Find exact moment Moon returns to natal position
        return_moment = self._find_moon_return_moment(
            natal_moon_long, target_month
        )
        
        if not return_moment:
            raise ValueError(f"Could not calculate lunar return for {target_month}")
        
        # Calculate chart (similar to solar return)
        return self._calculate_return_chart(
            return_moment, return_latitude, return_longitude, "lunar"
        )
    
    def _datetime_to_julian(self, dt: datetime) -> float:
        """Convert datetime to Julian day number."""
        return swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute/60.0 + dt.second/3600.0
        )
    
    def _get_sign(self, longitude: float) -> str:
        """Get zodiac sign from longitude."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[int(longitude / 30)]
    
    def _calculate_moon_phase(self, sun_long: float, moon_long: float) -> Dict:
        """Calculate Moon phase information."""
        phase_angle = (moon_long - sun_long) % 360
        
        # Phase names
        if phase_angle < 45:
            phase_name = "New Moon"
        elif phase_angle < 90:
            phase_name = "Crescent"
        elif phase_angle < 135:
            phase_name = "First Quarter"
        elif phase_angle < 180:
            phase_name = "Gibbous"
        elif phase_angle < 225:
            phase_name = "Full Moon"
        elif phase_angle < 270:
            phase_name = "Disseminating"
        elif phase_angle < 315:
            phase_name = "Last Quarter"
        else:
            phase_name = "Balsamic"
        
        return {
            "phase_angle": round(phase_angle, 2),
            "phase_name": phase_name,
            "illumination": round((1 + math.cos(math.radians(phase_angle))) / 2 * 100, 1)
        }
    
    def _calculate_progressed_aspects(
        self,
        progressed_planets: Dict,
        natal_jd: float,
        latitude: float,
        longitude: float
    ) -> List[Dict]:
        """Calculate important progressed to natal aspects."""
        aspects = []
        
        # Get natal positions
        natal_planets = {}
        for planet_name, planet_data in progressed_planets.items():
            planet_id = getattr(swe, planet_name.upper(), None)
            if planet_id:
                xx, _ = swe.calc_ut(natal_jd, planet_id)
                natal_planets[planet_name] = xx[0]
        
        # Major aspects to check
        aspect_orbs = {
            0: ("conjunction", 1),     # Tight orbs for progressions
            60: ("sextile", 1),
            90: ("square", 1),
            120: ("trine", 1),
            180: ("opposition", 1)
        }
        
        # Check progressed to natal aspects
        for prog_planet, prog_data in progressed_planets.items():
            for natal_planet, natal_long in natal_planets.items():
                prog_long = prog_data["longitude"]
                
                # Calculate aspect
                diff = abs(prog_long - natal_long)
                if diff > 180:
                    diff = 360 - diff
                
                for angle, (aspect_name, orb) in aspect_orbs.items():
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            "progressed": prog_planet,
                            "natal": natal_planet,
                            "aspect": aspect_name,
                            "orb": round(abs(diff - angle), 2),
                            "exact_in_days": self._calculate_exact_aspect_timing(
                                prog_data["speed"], diff - angle
                            )
                        })
                        break
        
        return aspects
    
    def _calculate_exact_aspect_timing(self, daily_motion: float, orb: float) -> Optional[int]:
        """Calculate when aspect becomes exact."""
        if daily_motion == 0:
            return None
        
        # For secondary progressions, 1 day = 1 year
        days = abs(orb / daily_motion)
        return int(days * 365.25)
    
    def _find_sun_return_moment(
        self,
        natal_sun_long: float,
        search_start: datetime
    ) -> Optional[datetime]:
        """Find exact moment Sun returns to natal position."""
        # Search within a month around birthday
        for day_offset in range(-15, 16):
            test_date = search_start + timedelta(days=day_offset)
            
            for hour in range(24):
                test_datetime = test_date.replace(hour=hour)
                test_jd = self._datetime_to_julian(test_datetime)
                
                sun_xx, _ = swe.calc_ut(test_jd, swe.SUN)
                sun_long = sun_xx[0]
                
                # Check if within 0.01 degrees
                if abs(sun_long - natal_sun_long) < 0.01:
                    # Refine to minute
                    return self._refine_return_time(
                        test_datetime, natal_sun_long, swe.SUN
                    )
        
        return None
    
    def _find_moon_return_moment(
        self,
        natal_moon_long: float,
        search_month: datetime
    ) -> Optional[datetime]:
        """Find exact moment Moon returns to natal position."""
        # Moon returns approximately every 27.3 days
        for day_offset in range(30):
            test_date = search_month + timedelta(days=day_offset)
            
            test_jd = self._datetime_to_julian(test_date)
            moon_xx, _ = swe.calc_ut(test_jd, swe.MOON)
            moon_long = moon_xx[0]
            
            # Check if close (Moon moves ~13 degrees per day)
            if abs(moon_long - natal_moon_long) < 13:
                # Refine to minute
                return self._refine_return_time(
                    test_date, natal_moon_long, swe.MOON
                )
        
        return None
    
    def _refine_return_time(
        self,
        approx_time: datetime,
        target_longitude: float,
        planet_id: int
    ) -> datetime:
        """Refine return time to the minute."""
        best_time = approx_time
        best_diff = 360.0
        
        # Search within 2 days
        for hours in range(-24, 25):
            for minutes in range(0, 60, 5):
                test_time = approx_time + timedelta(hours=hours, minutes=minutes)
                test_jd = self._datetime_to_julian(test_time)
                
                xx, _ = swe.calc_ut(test_jd, planet_id)
                test_long = xx[0]
                
                diff = abs(test_long - target_longitude)
                if diff > 180:
                    diff = 360 - diff
                
                if diff < best_diff:
                    best_diff = diff
                    best_time = test_time
                
                if diff < 0.001:  # Good enough
                    return test_time
        
        return best_time
    
    def _get_house_position(self, longitude: float, houses: List[float]) -> int:
        """Determine which house a planet is in."""
        for i in range(12):
            house_start = houses[i]
            house_end = houses[(i + 1) % 12]
            
            # Handle house that crosses 0°
            if house_start > house_end:
                if longitude >= house_start or longitude < house_end:
                    return i + 1
            else:
                if house_start <= longitude < house_end:
                    return i + 1
        
        return 1  # Default to 1st house
    
    def _calculate_aspects(self, planets: Dict) -> List[Dict]:
        """Calculate aspects between planets."""
        aspects = []
        planet_names = list(planets.keys())
        
        # Aspect definitions
        aspect_orbs = {
            0: ("conjunction", 8),
            60: ("sextile", 6),
            90: ("square", 8),
            120: ("trine", 8),
            180: ("opposition", 8)
        }
        
        for i in range(len(planet_names)):
            for j in range(i + 1, len(planet_names)):
                planet1 = planet_names[i]
                planet2 = planet_names[j]
                
                long1 = planets[planet1]["longitude"]
                long2 = planets[planet2]["longitude"]
                
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                for angle, (aspect_name, orb) in aspect_orbs.items():
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "aspect": aspect_name,
                            "angle": angle,
                            "orb": round(abs(diff - angle), 2)
                        })
                        break
        
        return aspects
    
    def _find_solar_arc_aspects(
        self,
        directed_planets: Dict,
        directed_angles: Dict
    ) -> List[Dict]:
        """Find important solar arc aspects to natal positions."""
        aspects = []
        
        # Check directed planets to natal angles
        # In practice, you'd compare to actual natal positions
        # This is simplified
        
        for planet, data in directed_planets.items():
            directed_long = data["directed_longitude"]
            
            # Check if forming aspect to cardinal points
            for angle in [0, 90, 180, 270]:
                if abs(directed_long - angle) < 1:
                    aspects.append({
                        "planet": planet,
                        "aspect_to": f"{angle}° (Cardinal)",
                        "orb": round(abs(directed_long - angle), 2)
                    })
        
        return aspects
    
    def _get_house_lord(self, house: int, asc_longitude: float) -> str:
        """Get the lord of a house based on sign."""
        # Calculate sign of house cusp
        house_cusp = (asc_longitude + (house - 1) * 30) % 360
        sign_index = int(house_cusp / 30)
        
        # Traditional rulerships
        rulers = [
            "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
            "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
        ]
        
        return rulers[sign_index]
    
    def _interpret_current_progressions(
        self,
        progressed_planets: Dict,
        aspects: List[Dict]
    ) -> List[str]:
        """Generate interpretations for current progressions."""
        interpretations = []
        
        # Progressed Moon sign
        moon_sign = progressed_planets["Moon"]["sign"]
        interpretations.append(
            f"Progressed Moon in {moon_sign}: Emotional focus on {moon_sign} themes"
        )
        
        # Important aspects
        for aspect in aspects[:3]:  # Top 3 aspects
            if aspect["orb"] < 0.5:
                interpretations.append(
                    f"Progressed {aspect['progressed']} {aspect['aspect']} "
                    f"natal {aspect['natal']}: Major life theme activation"
                )
        
        return interpretations
    
    def _analyze_return_themes(
        self,
        planets: Dict,
        houses: List[float],
        aspects: List[Dict]
    ) -> List[str]:
        """Analyze themes for return chart."""
        themes = []
        
        # Check angular planets
        angular_houses = [1, 4, 7, 10]
        for planet, data in planets.items():
            if data.get("house") in angular_houses:
                themes.append(f"{planet} angular: {planet} themes prominent this year")
        
        # Check stelliums
        house_counts = {}
        for planet, data in planets.items():
            house = data.get("house", 1)
            house_counts[house] = house_counts.get(house, 0) + 1
        
        for house, count in house_counts.items():
            if count >= 3:
                themes.append(f"Stellium in house {house}: Focus on house {house} matters")
        
        return themes
    
    def _calculate_return_chart(
        self,
        return_moment: datetime,
        latitude: float,
        longitude: float,
        return_type: str
    ) -> Dict:
        """Generic method to calculate any return chart."""
        # Implementation would be similar to solar return
        # This is a placeholder for lunar, venus, mars returns etc.
        return {
            "return_type": return_type,
            "return_moment": return_moment.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude}
        }