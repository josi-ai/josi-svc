import swisseph as swe
from datetime import datetime
from typing import Dict, List, Tuple
import json
import math
import pytz


class AstrologyCalculator:
    PLANETS = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE,  # North Node
        'Ketu': swe.OSCU_APOG,  # South Node (180° from Rahu)
    }
    
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    def __init__(self):
        swe.set_ephe_path('')  # Use built-in ephemeris
        self.current_ayanamsa = 'lahiri'  # Default ayanamsa
    
    def set_ayanamsa(self, ayanamsa_name: str) -> None:
        """Set the ayanamsa system for Vedic calculations."""
        ayanamsa_modes = {
            'lahiri': swe.SIDM_LAHIRI,
            'krishnamurti': swe.SIDM_KRISHNAMURTI,
            'raman': swe.SIDM_RAMAN,
            'yukteshwar': swe.SIDM_YUKTESHWAR,
            'fagan_bradley': swe.SIDM_FAGAN_BRADLEY,
            'true_citra': swe.SIDM_TRUE_CITRA,
            'true_revati': swe.SIDM_TRUE_REVATI,
            'aldebaran_15tau': swe.SIDM_ALDEBARAN_15TAU,
            'galcenter_0sag': swe.SIDM_GALCENT_0SAG
        }
        
        mode = ayanamsa_modes.get(ayanamsa_name.lower(), swe.SIDM_LAHIRI)
        swe.set_sid_mode(mode)
        self.current_ayanamsa = ayanamsa_name
    
    def _datetime_to_julian(self, dt: datetime) -> float:
        """Convert datetime to Julian day number with improved precision."""
        # Convert to UTC if the datetime has timezone info
        if dt.tzinfo is not None:
            utc_dt = dt.astimezone(pytz.UTC)
        else:
            # Assume UTC if no timezone info
            utc_dt = dt
        
        # Higher precision time calculation
        decimal_hour = (utc_dt.hour * 3600.0 + 
                       utc_dt.minute * 60.0 + 
                       utc_dt.second + 
                       utc_dt.microsecond / 1e6) / 3600.0
        
        return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)
    
    def _get_ayanamsa(self, julian_day: float, system: str = None) -> float:
        """Get ayanamsa value for Vedic calculations."""
        # Use the system parameter if provided, otherwise use current setting
        if system:
            self.set_ayanamsa(system)
        
        return swe.get_ayanamsa(julian_day)
    
    def _calculate_houses(self, julian_day: float, latitude: float, longitude: float, sidereal: bool = False) -> List[float]:
        """Calculate house cusps."""
        # Use sidereal flag for Vedic calculations
        if sidereal:
            houses, ascmc = swe.houses_ex(julian_day, latitude, longitude, b'P', swe.FLG_SIDEREAL)
        else:
            houses, ascmc = swe.houses(julian_day, latitude, longitude, b'P')  # Placidus
        return houses
    
    def _get_nakshatra_pada(self, longitude: float) -> Tuple[str, int]:
        """Get nakshatra and pada from longitude."""
        nakshatra_index = int(longitude / 13.333333)
        pada = int((longitude % 13.333333) / 3.333333) + 1
        return self.NAKSHATRAS[nakshatra_index], pada
    
    def _get_sign(self, longitude: float) -> str:
        """Get zodiac sign from longitude."""
        sign_index = int(longitude / 30)
        return self.SIGNS[sign_index]
    
    def calculate_vedic_chart(self, dt: datetime, latitude: float, longitude: float, timezone: str = None) -> Dict:
        """Calculate Vedic astrology chart."""
        # Ensure datetime is timezone-aware
        if dt.tzinfo is None and timezone:
            import pytz
            tz = pytz.timezone(timezone)
            dt = tz.localize(dt)
        
        julian_day = self._datetime_to_julian(dt)
        ayanamsa = self._get_ayanamsa(julian_day)
        houses = self._calculate_houses(julian_day, latitude, longitude, sidereal=True)
        
        planet_positions = {}
        
        for planet_name, planet_id in self.PLANETS.items():
            if planet_name == 'Ketu':
                # Ketu is always 180° from Rahu
                rahu_pos = planet_positions['Rahu']['longitude']
                ketu_longitude = (rahu_pos + 180) % 360
                planet_data = {
                    'longitude': ketu_longitude,
                    'latitude': -planet_positions['Rahu']['latitude'],
                    'speed': -planet_positions['Rahu']['speed']
                }
            else:
                # Use sidereal flag for Vedic calculations to get direct sidereal positions
                result = swe.calc(julian_day, planet_id, swe.FLG_SIDEREAL)
                planet_data = {
                    'longitude': result[0][0],
                    'latitude': result[0][1],
                    'speed': result[0][3]
                }
            
            # Already have sidereal longitude from FLG_SIDEREAL flag
            sidereal_longitude = planet_data['longitude']
            
            # Determine house
            house = 1
            for i in range(12):
                house_start = houses[i]
                house_end = houses[(i + 1) % 12]
                
                if house_start <= sidereal_longitude < house_end:
                    house = i + 1
                    break
                elif house_start > house_end:  # Crosses 0°
                    if sidereal_longitude >= house_start or sidereal_longitude < house_end:
                        house = i + 1
                        break
            
            nakshatra, pada = self._get_nakshatra_pada(sidereal_longitude)
            sign = self._get_sign(sidereal_longitude)
            
            planet_positions[planet_name] = {
                'longitude': sidereal_longitude,
                'latitude': planet_data['latitude'],
                'speed': planet_data['speed'],
                'house': house,
                'sign': sign,
                'nakshatra': nakshatra,
                'pada': pada
            }
        
        # Calculate ascendant - houses are already sidereal
        asc_longitude = houses[0]
        nakshatra, pada = self._get_nakshatra_pada(asc_longitude)
        sign = self._get_sign(asc_longitude)
        
        return {
            'chart_type': 'vedic',
            'ayanamsa': ayanamsa,
            'ascendant': {
                'longitude': asc_longitude,
                'sign': sign,
                'nakshatra': nakshatra,
                'pada': pada
            },
            'houses': houses,  # Already sidereal
            'planets': planet_positions
        }
    
    def calculate_south_indian_chart(self, dt: datetime, latitude: float, longitude: float) -> Dict:
        """Calculate South Indian style chart (same calculations, different display format)."""
        vedic_chart = self.calculate_vedic_chart(dt, latitude, longitude)
        vedic_chart['chart_type'] = 'south_indian'
        
        # South Indian chart uses fixed houses, signs rotate
        # The display format would be different in the frontend
        return vedic_chart
    
    def calculate_western_chart(self, dt: datetime, latitude: float, longitude: float) -> Dict:
        """Calculate Western astrology chart (tropical zodiac)."""
        julian_day = self._datetime_to_julian(dt)
        houses = self._calculate_houses(julian_day, latitude, longitude)
        
        planet_positions = {}
        
        for planet_name, planet_id in self.PLANETS.items():
            if planet_name == 'Ketu':
                # Skip Ketu for Western astrology
                continue
            
            result = swe.calc(julian_day, planet_id)
            longitude = result[0][0]
            
            # Determine house
            house = 1
            for i in range(12):
                house_start = houses[i]
                house_end = houses[(i + 1) % 12]
                
                if house_start <= longitude < house_end:
                    house = i + 1
                    break
                elif house_start > house_end:  # Crosses 0°
                    if longitude >= house_start or longitude < house_end:
                        house = i + 1
                        break
            
            sign = self._get_sign(longitude)
            
            planet_positions[planet_name] = {
                'longitude': longitude,
                'latitude': result[0][1],
                'speed': result[0][3],
                'house': house,
                'sign': sign
            }
        
        # Calculate ascendant
        asc_longitude = houses[0]
        sign = self._get_sign(asc_longitude)
        
        return {
            'chart_type': 'western',
            'ascendant': {
                'longitude': asc_longitude,
                'sign': sign
            },
            'houses': houses,
            'planets': planet_positions
        }
    
    def calculate_divisional_chart(self, dt: datetime, latitude: float, longitude: float, division: int) -> Dict:
        """
        Calculate Vedic divisional charts (Varga charts).
        
        Args:
            dt: Birth datetime
            latitude: Birth latitude
            longitude: Birth longitude  
            division: Division number (1-60)
        
        Returns:
            Dict with divisional chart data
        """
        # First get the natal chart for basic planetary positions
        natal_chart = self.calculate_vedic_chart(dt, latitude, longitude)
        
        # Calculate divisional positions for each planet
        divisional_positions = {}
        
        for planet_name, planet_data in natal_chart['planets'].items():
            natal_longitude = planet_data['longitude']
            
            # Calculate divisional longitude based on division
            divisional_longitude = self._calculate_divisional_position(natal_longitude, division)
            
            # Get sign and house for divisional position
            sign = self._get_sign(divisional_longitude)
            house = self._get_house_from_longitude(divisional_longitude, natal_chart['ascendant']['longitude'])
            
            divisional_positions[planet_name] = {
                'longitude': divisional_longitude,
                'latitude': planet_data.get('latitude', 0),
                'speed': planet_data.get('speed', 0),
                'house': house,
                'sign': sign,
                'natal_longitude': natal_longitude
            }
        
        # Calculate divisional ascendant
        natal_asc = natal_chart['ascendant']['longitude']
        divisional_asc = self._calculate_divisional_position(natal_asc, division)
        divisional_asc_sign = self._get_sign(divisional_asc)
        
        # Calculate divisional houses
        divisional_houses = []
        for i in range(12):
            house_longitude = (divisional_asc + (i * 30)) % 360
            divisional_houses.append(house_longitude)
        
        return {
            'chart_type': f'divisional_D{division}',
            'division': division,
            'division_name': self._get_division_name(division),
            'ascendant': {
                'longitude': divisional_asc,
                'sign': divisional_asc_sign
            },
            'houses': divisional_houses,
            'planets': divisional_positions,
            'natal_reference': {
                'ascendant': natal_chart['ascendant'],
                'planets': {name: {'longitude': data['longitude']} for name, data in natal_chart['planets'].items()}
            }
        }
    
    def _calculate_divisional_position(self, longitude: float, division: int) -> float:
        """
        Calculate position in divisional chart based on standard Vedic formula.
        
        The general formula for divisional charts:
        Divisional position = ((longitude % (30/division)) * division) % 360
        """
        if division == 1:  # D1 - Rasi chart (same as natal)
            return longitude
        
        # Get position within sign (0-30 degrees)
        sign_number = int(longitude // 30)
        degree_in_sign = longitude % 30
        
        if division == 9:  # D9 - Navamsa (most important)
            # Special Navamsa calculation
            navamsa_num = int(degree_in_sign // (30/9))
            if sign_number % 2 == 0:  # Even signs (0,2,4,6,8,10)
                navamsa_sign = (navamsa_num) % 12
            else:  # Odd signs (1,3,5,7,9,11)
                navamsa_sign = (8 + navamsa_num) % 12
            
            degree_in_navamsa = (degree_in_sign % (30/9)) * 9
            return navamsa_sign * 30 + degree_in_navamsa
        
        else:
            # Standard divisional formula for other charts
            division_part = int(degree_in_sign // (30/division))
            degree_in_division = (degree_in_sign % (30/division)) * division
            
            # Calculate which sign the divisional position falls in
            divisional_sign = (sign_number * division + division_part) % 12
            
            return divisional_sign * 30 + degree_in_division
    
    def _get_house_from_longitude(self, longitude: float, ascendant: float) -> int:
        """Get house number from longitude relative to ascendant."""
        relative_position = (longitude - ascendant) % 360
        house = int(relative_position // 30) + 1
        return house if house <= 12 else house - 12
    
    def _get_division_name(self, division: int) -> str:
        """Get the traditional name for divisional chart."""
        names = {
            1: "Rasi (Birth Chart)",
            2: "Hora (Wealth)",
            3: "Drekkana (Siblings)",
            4: "Chaturthamsa (Property)",
            7: "Saptamsa (Children)",
            9: "Navamsa (Marriage/Dharma)",
            10: "Dasamsa (Career)",
            12: "Dvadasamsa (Parents)",
            16: "Shodasamsa (Vehicles)",
            20: "Vimsamsa (Spiritual)",
            24: "Chaturvimsamsa (Learning)",
            27: "Bhamsa (Strength/Weakness)",
            30: "Trimsamsa (Misfortune)",
            40: "Khavedamsa (Auspicious/Inauspicious)",
            45: "Akshavedamsa (General)",
            60: "Shashtyamsa (Overall)"
        }
        return names.get(division, f"D{division} Divisional Chart")
    
    def calculate_synastry(self, chart1: Dict, chart2: Dict) -> Dict:
        """
        Calculate basic synastry aspects between two charts.
        
        Args:
            chart1: First person's chart data
            chart2: Second person's chart data
            
        Returns:
            Dictionary with synastry analysis
        """
        # Basic synastry implementation
        aspects = []
        house_overlays = []
        
        # Calculate major aspects between planets
        for planet1_name, planet1_data in chart1.get("planets", {}).items():
            for planet2_name, planet2_data in chart2.get("planets", {}).items():
                long1 = planet1_data.get("longitude", 0)
                long2 = planet2_data.get("longitude", 0)
                
                # Calculate angular difference
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for major aspects (with 8° orb)
                orb = 8
                aspect_type = None
                
                if diff <= orb:  # Conjunction
                    aspect_type = "Conjunction"
                elif abs(diff - 60) <= orb:  # Sextile
                    aspect_type = "Sextile" 
                elif abs(diff - 90) <= orb:  # Square
                    aspect_type = "Square"
                elif abs(diff - 120) <= orb:  # Trine
                    aspect_type = "Trine"
                elif abs(diff - 180) <= orb:  # Opposition
                    aspect_type = "Opposition"
                
                if aspect_type:
                    influence = "Harmonious" if aspect_type in ["Conjunction", "Sextile", "Trine"] else "Challenging"
                    aspects.append({
                        "planet1": planet1_name,
                        "planet2": planet2_name,
                        "aspect": aspect_type,
                        "orb": round(min(diff, abs(diff - 60), abs(diff - 90), abs(diff - 120), abs(diff - 180)), 2),
                        "influence": influence,
                        "interpretation": f"{planet1_name} {aspect_type} {planet2_name} - {influence} connection"
                    })
        
        # Calculate house overlays
        for planet_name, planet_data in chart2.get("planets", {}).items():
            house = planet_data.get("house", 1)
            house_overlays.append({
                "planet": planet_name,
                "person": "Person 2",
                "falls_in_house": house,
                "house_meaning": self._get_house_meaning(house),
                "interpretation": f"{planet_name} activates themes of {self._get_house_meaning(house).lower()}"
            })
        
        return {
            "aspects": aspects[:10],  # Limit to first 10 aspects
            "house_overlays": house_overlays,
            "composite_points": {
                "sun_midpoint": self._calculate_midpoint(
                    chart1.get("planets", {}).get("Sun", {}).get("longitude", 0),
                    chart2.get("planets", {}).get("Sun", {}).get("longitude", 0)
                ),
                "moon_midpoint": self._calculate_midpoint(
                    chart1.get("planets", {}).get("Moon", {}).get("longitude", 0),
                    chart2.get("planets", {}).get("Moon", {}).get("longitude", 0)
                )
            },
            "themes": [
                "Communication and understanding",
                "Emotional connection", 
                "Shared values and goals",
                "Physical and romantic attraction"
            ],
            "dynamics": [
                "Power balance in relationship",
                "Areas of harmony and tension",
                "Growth opportunities together",
                "Long-term compatibility factors"
            ]
        }
    
    def _calculate_midpoint(self, long1: float, long2: float) -> float:
        """Calculate midpoint between two longitudes."""
        diff = abs(long1 - long2)
        if diff > 180:
            # Take shorter path around circle
            if long1 > long2:
                midpoint = (long1 + long2 + 360) / 2
            else:
                midpoint = (long1 + 360 + long2) / 2
        else:
            midpoint = (long1 + long2) / 2
        
        return midpoint % 360
    
    def _get_house_meaning(self, house: int) -> str:
        """Get meaning of astrological house."""
        meanings = {
            1: "Identity and self-expression",
            2: "Values and resources", 
            3: "Communication and learning",
            4: "Home and family",
            5: "Creativity and romance",
            6: "Service and health",
            7: "Partnerships and relationships", 
            8: "Transformation and shared resources",
            9: "Philosophy and higher learning",
            10: "Career and reputation",
            11: "Friendships and social groups",
            12: "Spirituality and subconscious"
        }
        return meanings.get(house, f"House {house}")