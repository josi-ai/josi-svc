"""
Bhava (House) Calculator
Calculate Bhava chart and related information for Vedic astrology
"""

import math
from typing import Dict, List, Tuple
from datetime import datetime
import swisseph as swe


class BhavaCalculator:
    """Calculate Bhava (house) chart and related information."""
    
    def __init__(self):
        self.signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        self.sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        
        self.nakshatra_lords = {
            "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun",
            "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
            "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
            "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
            "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
            "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshtha": "Mercury",
            "Mula": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
            "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
            "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
        }
    
    def calculate_bhava_chart(self, houses: List[float], house_system: str = 'placidus') -> Dict:
        """
        Calculate complete bhava chart information.
        
        Args:
            houses: List of 12 house cusps (already calculated)
            house_system: House system used
            
        Returns:
            Dict with bhava information
        """
        bhava_data = {
            'house_system': house_system,
            'houses': []
        }
        
        for i in range(12):
            house_num = i + 1
            
            # Get cusp (madhya)
            cusp = houses[i]
            
            # Calculate start and end points
            if house_system.lower() == 'equal':
                # Equal houses: each house is 30° from ascendant
                start = (cusp - 15) % 360
                end = (cusp + 15) % 360
            else:
                # Unequal houses: midpoint between cusps
                prev_cusp = houses[i-1] if i > 0 else houses[11]
                next_cusp = houses[i+1] if i < 11 else houses[0]
                
                # Calculate midpoints
                start = self._calculate_midpoint(prev_cusp, cusp)
                end = self._calculate_midpoint(cusp, next_cusp)
            
            # Get sign and nakshatra information
            cusp_sign = self._get_sign(cusp)
            cusp_nakshatra = self._get_nakshatra(cusp)
            
            # Get lords
            sign_lord = self.sign_lords.get(cusp_sign, '')
            nakshatra_lord = self.nakshatra_lords.get(cusp_nakshatra, '')
            
            bhava_info = {
                'number': house_num,
                'cusp': cusp,
                'start': start,
                'end': end,
                'span': self._calculate_span(start, end),
                'sign': cusp_sign,
                'sign_lord': sign_lord,
                'nakshatra': cusp_nakshatra,
                'nakshatra_lord': nakshatra_lord
            }
            
            bhava_data['houses'].append(bhava_info)
        
        return bhava_data
    
    def create_bhava_chart_display(self, bhava_data: Dict, planets: Dict) -> List[str]:
        """Create ASCII bhava chart similar to rasi chart."""
        # Initialize houses
        bhava_houses = {i: [] for i in range(1, 13)}
        
        # Place planets in bhava chart
        for planet, data in planets.items():
            planet_long = data['longitude']
            
            # Find which bhava contains this planet
            for house in bhava_data['houses']:
                if self._is_in_house(planet_long, house['start'], house['end']):
                    bhava_houses[house['number']].append(planet)
                    break
        
        # Create chart lines (South Indian format)
        lines = []
        lines.append("                    +-------+-------+-------+-------+")
        
        # Top row (houses 12, 1, 2, 3)
        for row_idx in range(5):
            if row_idx == 0 or row_idx == 4:
                lines.append("                    !       !       !       !       !")
            else:
                row_planets = ["", "", "", ""]
                for i, house_num in enumerate([12, 1, 2, 3]):
                    if len(bhava_houses[house_num]) > (row_idx - 1):
                        planet = bhava_houses[house_num][row_idx - 1]
                        row_planets[i] = self._get_planet_abbr(planet)
                
                line = "                    !"
                for p in row_planets:
                    line += f"{p:^7}!"
                lines.append(line)
        
        lines.append("                    +-------+-------+-------+-------+")
        
        # Middle section
        lines.append("                    !       !               !       !")
        lines.append("                    !       !               !       !")
        
        # Houses 11 and 4
        h11_planets = ' '.join([self._get_planet_abbr(p) for p in bhava_houses[11][:2]])
        h4_planets = ' '.join([self._get_planet_abbr(p) for p in bhava_houses[4][:2]])
        lines.append(f"                    !{h11_planets:^7}!               !{h4_planets:^7}!")
        
        lines.append("                    !       !               !       !")
        lines.append("                    !       !               !       !")
        lines.append("                    +-------+    BHAVA      +-------+")
        lines.append("                    !       !               !       !")
        lines.append("                    !       !               !       !")
        
        # Houses 10 and 5
        h10_planets = ' '.join([self._get_planet_abbr(p) for p in bhava_houses[10][:2]])
        h5_planets = ' '.join([self._get_planet_abbr(p) for p in bhava_houses[5][:2]])
        lines.append(f"                    !{h10_planets:^7}!               !{h5_planets:^7}!")
        
        lines.append("                    !       !               !       !")
        lines.append("                    !       !               !       !")
        lines.append("                    +-------+-------+-------+-------+")
        
        # Bottom row (houses 9, 8, 7, 6)
        for row_idx in range(5):
            if row_idx == 0 or row_idx == 4:
                lines.append("                    !       !       !       !       !")
            else:
                row_planets = ["", "", "", ""]
                for i, house_num in enumerate([9, 8, 7, 6]):
                    if len(bhava_houses[house_num]) > (row_idx - 1):
                        planet = bhava_houses[house_num][row_idx - 1]
                        row_planets[i] = self._get_planet_abbr(planet)
                
                line = "                    !"
                for p in row_planets:
                    line += f"{p:^7}!"
                lines.append(line)
        
        lines.append("                    +-------+-------+-------+-------+")
        
        return lines
    
    def create_bhava_details_table(self, bhava_data: Dict) -> List[str]:
        """Create detailed bhava table with degrees and lords."""
        lines = []
        
        # Header
        lines.append(" BHAVA   MIDDLE     START    RASI  STAR  BHAVA   MIDDLE     START    RASI  STAR")
        lines.append("          DEG:MN     DEG:MN   LORD  LORD          DEG:MN     DEG:MN   LORD  LORD")
        
        # Format houses in two columns
        for i in range(6):
            left_house = bhava_data['houses'][i]
            right_house = bhava_data['houses'][i + 6]
            
            # Format degrees
            left_cusp = self._format_degrees(left_house['cusp'])
            left_start = self._format_degrees(left_house['start'])
            right_cusp = self._format_degrees(right_house['cusp'])
            right_start = self._format_degrees(right_house['start'])
            
            # Get abbreviated lords
            left_sign_lord = self._get_planet_abbr(left_house['sign_lord'])
            left_nak_lord = self._get_planet_abbr(left_house['nakshatra_lord'])
            right_sign_lord = self._get_planet_abbr(right_house['sign_lord'])
            right_nak_lord = self._get_planet_abbr(right_house['nakshatra_lord'])
            
            line = f"   {left_house['number']:>2}    {left_cusp:>8}    {left_start:>8}   "
            line += f"{left_sign_lord:<4}  {left_nak_lord:<4}"
            line += f"   {right_house['number']:>2}    {right_cusp:>8}    {right_start:>8}   "
            line += f"{right_sign_lord:<4}  {right_nak_lord:<4}"
            
            lines.append(line)
        
        return lines
    
    def _calculate_midpoint(self, deg1: float, deg2: float) -> float:
        """Calculate midpoint between two degrees."""
        # Handle wraparound
        if abs(deg2 - deg1) > 180:
            if deg1 > deg2:
                deg2 += 360
            else:
                deg1 += 360
        
        midpoint = (deg1 + deg2) / 2
        return midpoint % 360
    
    def _calculate_span(self, start: float, end: float) -> float:
        """Calculate angular span of house."""
        if end > start:
            return end - start
        else:
            return (360 - start) + end
    
    def _is_in_house(self, longitude: float, start: float, end: float) -> bool:
        """Check if a longitude falls within house boundaries."""
        if start < end:
            return start <= longitude < end
        else:  # House crosses 0°
            return longitude >= start or longitude < end
    
    def _get_sign(self, longitude: float) -> str:
        """Get zodiac sign for a longitude."""
        sign_num = int(longitude / 30)
        return self.signs[sign_num]
    
    def _get_nakshatra(self, longitude: float) -> str:
        """Get nakshatra for a longitude."""
        nak_num = int(longitude / (360/27))
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
            "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
            "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]
        return nakshatras[nak_num]
    
    def _format_degrees(self, degrees: float) -> str:
        """Format degrees as DDD:MM."""
        deg = int(degrees)
        min = int((degrees - deg) * 60)
        return f"{deg:3d}:{min:02d}"
    
    def _get_planet_abbr(self, planet: str) -> str:
        """Get planet abbreviation."""
        abbr = {
            'Sun': 'SURY', 'Moon': 'CHAN', 'Mars': 'KUJA',
            'Mercury': 'BUDH', 'Jupiter': 'GURU', 'Venus': 'SUKR',
            'Saturn': 'SANI', 'Rahu': 'RAHU', 'Ketu': 'KETU',
            'Ascendant': 'LAG', 'Gulika': 'GUL'
        }
        return abbr.get(planet, planet[:3].upper())
    
    def calculate_bhava_strength_factors(self, bhava_data: Dict, 
                                       planet_positions: Dict) -> Dict:
        """Calculate additional bhava strength factors."""
        factors = {}
        
        for house in bhava_data['houses']:
            house_num = house['number']
            
            # Count planets in house
            occupants = []
            for planet, data in planet_positions.items():
                if self._is_in_house(data['longitude'], house['start'], house['end']):
                    occupants.append(planet)
            
            # Check aspects on house cusp
            aspects = self._get_aspects_on_degree(house['cusp'], planet_positions)
            
            # Check lord placement
            lord = house['sign_lord']
            lord_house = None
            if lord in planet_positions:
                lord_long = planet_positions[lord]['longitude']
                for h in bhava_data['houses']:
                    if self._is_in_house(lord_long, h['start'], h['end']):
                        lord_house = h['number']
                        break
            
            factors[house_num] = {
                'occupants': occupants,
                'aspects': aspects,
                'lord_placement': lord_house,
                'span': house['span']
            }
        
        return factors
    
    def _get_aspects_on_degree(self, degree: float, planets: Dict) -> List[str]:
        """Get planets aspecting a specific degree."""
        aspecting = []
        
        for planet, data in planets.items():
            if planet in ['Rahu', 'Ketu']:
                continue
            
            planet_long = data['longitude']
            
            # Calculate aspect angle
            aspect_angle = abs(degree - planet_long)
            if aspect_angle > 180:
                aspect_angle = 360 - aspect_angle
            
            # Check for aspects
            if 170 <= aspect_angle <= 190:  # Opposition
                aspecting.append(planet)
            elif planet == 'Jupiter':
                if 115 <= aspect_angle <= 125:  # 5th aspect
                    aspecting.append(planet)
                elif 235 <= aspect_angle <= 245:  # 9th aspect
                    aspecting.append(planet)
            elif planet == 'Mars':
                if 85 <= aspect_angle <= 95:  # 4th aspect
                    aspecting.append(planet)
                elif 205 <= aspect_angle <= 215:  # 8th aspect
                    aspecting.append(planet)
            elif planet == 'Saturn':
                if 55 <= aspect_angle <= 65:  # 3rd aspect
                    aspecting.append(planet)
                elif 265 <= aspect_angle <= 275:  # 10th aspect
                    aspecting.append(planet)
        
        return aspecting