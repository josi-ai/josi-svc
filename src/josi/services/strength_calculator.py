"""
Planetary Strength (Bala) Calculator for Vedic Astrology

This module calculates various strength measures including:
- Shadbala (Six-fold strength)
- Bhava Bala (House strength)
- Residential Strength
"""

from typing import Dict, List, Tuple
import math
from datetime import datetime
import swisseph as swe


class StrengthCalculator:
    """Calculate various strength measures in Vedic astrology."""
    
    # Planetary relationships
    PLANET_FRIENDS = {
        'Sun': ['Moon', 'Mars', 'Jupiter'],
        'Moon': ['Sun', 'Mercury'],
        'Mars': ['Sun', 'Moon', 'Jupiter'],
        'Mercury': ['Sun', 'Venus'],
        'Jupiter': ['Sun', 'Moon', 'Mars'],
        'Venus': ['Mercury', 'Saturn'],
        'Saturn': ['Mercury', 'Venus'],
        'Rahu': ['Mercury', 'Venus', 'Saturn'],
        'Ketu': ['Mars', 'Jupiter']
    }
    
    PLANET_ENEMIES = {
        'Sun': ['Venus', 'Saturn'],
        'Moon': ['None'],
        'Mars': ['Mercury'],
        'Mercury': ['Moon'],
        'Jupiter': ['Mercury', 'Venus'],
        'Venus': ['Sun', 'Moon'],
        'Saturn': ['Sun', 'Moon', 'Mars'],
        'Rahu': ['Sun', 'Moon', 'Mars'],
        'Ketu': ['Mercury', 'Venus', 'Saturn']
    }
    
    # Exaltation and debilitation points
    EXALTATION_POINTS = {
        'Sun': 10.0,      # 10° Aries
        'Moon': 33.0,     # 3° Taurus
        'Mars': 298.0,    # 28° Capricorn
        'Mercury': 165.0, # 15° Virgo
        'Jupiter': 95.0,  # 5° Cancer
        'Venus': 357.0,   # 27° Pisces
        'Saturn': 200.0,  # 20° Libra
        'Rahu': 60.0,     # 0° Gemini
        'Ketu': 240.0     # 0° Sagittarius
    }
    
    # Sign rulers
    SIGN_RULERS = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    
    def __init__(self):
        """Initialize the strength calculator."""
        self.shadbala_components = {}
    
    def calculate_shadbala(self, planet_positions: Dict, houses: List[float], 
                          birth_time: datetime, latitude: float) -> Dict:
        """
        Calculate Shadbala (six-fold strength) for all planets.
        
        Returns strength in Rupas (60 Virupas = 1 Rupa).
        """
        shadbala = {}
        
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            if planet not in planet_positions:
                continue
                
            planet_data = planet_positions[planet]
            
            # Calculate all six components
            sthana_bala = self._calculate_sthana_bala(planet, planet_data, planet_positions)
            dig_bala = self._calculate_dig_bala(planet, planet_data, houses)
            kala_bala = self._calculate_kala_bala(planet, planet_data, birth_time)
            chesta_bala = self._calculate_chesta_bala(planet, planet_data)
            naisargika_bala = self._get_naisargika_bala(planet)
            drik_bala = self._calculate_drik_bala(planet, planet_positions)
            
            # Total Shadbala
            total = (sthana_bala + dig_bala + kala_bala + 
                    chesta_bala + naisargika_bala + drik_bala)
            
            shadbala[planet] = {
                'sthana_bala': round(sthana_bala, 2),
                'dig_bala': round(dig_bala, 2),
                'kala_bala': round(kala_bala, 2),
                'chesta_bala': round(chesta_bala, 2),
                'naisargika_bala': round(naisargika_bala, 2),
                'drik_bala': round(drik_bala, 2),
                'total': round(total, 2),
                'rupas': round(total / 60, 2)  # Convert to Rupas
            }
        
        return shadbala
    
    def _calculate_sthana_bala(self, planet: str, planet_data: Dict, 
                               all_planets: Dict) -> float:
        """
        Calculate positional strength.
        Includes: Uchcha (exaltation), Saptavargaja, Ojhayugma, 
                  Kendradi, Drekkana balas.
        """
        total = 0.0
        
        # 1. Uchcha Bala (Exaltation strength)
        longitude = planet_data.get('longitude', 0)
        exalt_point = self.EXALTATION_POINTS.get(planet, 0)
        
        # Distance from exaltation point
        distance = abs(longitude - exalt_point)
        if distance > 180:
            distance = 360 - distance
        
        # Maximum 60 virupas at exaltation, 0 at debilitation (180° away)
        uchcha_bala = 60 * (1 - distance / 180)
        total += uchcha_bala
        
        # 2. Saptavargaja Bala (Strength from 7 divisional charts)
        # Simplified - based on sign placement
        sign = planet_data.get('sign', '')
        if sign:
            # Own sign
            sign_ruler = self.SIGN_RULERS.get(sign, '')
            if sign_ruler == planet:
                total += 30  # Swakshetra
            # Friend's sign
            elif sign_ruler in self.PLANET_FRIENDS.get(planet, []):
                total += 15  # Mitra
            # Enemy's sign
            elif sign_ruler in self.PLANET_ENEMIES.get(planet, []):
                total += 3.75  # Shatru
            else:
                total += 7.5  # Sama (neutral)
        
        # 3. Ojhayugma Bala (Odd-even strength)
        # Males (Sun, Mars, Jupiter) strong in odd signs
        # Females (Moon, Venus) strong in even signs
        # Mercury strong in both
        sign_num = int(longitude / 30)
        if planet in ['Sun', 'Mars', 'Jupiter']:
            if sign_num % 2 == 0:  # Odd sign (0-indexed)
                total += 15
        elif planet in ['Moon', 'Venus']:
            if sign_num % 2 == 1:  # Even sign
                total += 15
        elif planet == 'Mercury':
            total += 15  # Always gets it
        
        # 4. Kendradi Bala (Angular strength)
        house = planet_data.get('house', 1)
        if house in [1, 4, 7, 10]:  # Kendra (angles)
            total += 60
        elif house in [2, 5, 8, 11]:  # Panaphara (succedent)
            total += 30
        elif house in [3, 6, 9, 12]:  # Apoklima (cadent)
            total += 15
        
        # 5. Drekkana Bala
        # Males strong in first drekkana, females in second, neutrals in third
        degree_in_sign = longitude % 30
        if planet in ['Sun', 'Mars', 'Jupiter'] and degree_in_sign < 10:
            total += 10
        elif planet in ['Moon', 'Venus'] and 10 <= degree_in_sign < 20:
            total += 10
        elif planet in ['Mercury', 'Saturn'] and degree_in_sign >= 20:
            total += 10
        
        return total
    
    def _calculate_dig_bala(self, planet: str, planet_data: Dict, houses: List[float]) -> float:
        """
        Calculate directional strength.
        Planets have maximum strength in specific houses.
        """
        # Directional strength houses
        dig_bala_houses = {
            'Sun': 10,      # 10th house (South)
            'Moon': 4,      # 4th house (North)
            'Mars': 10,     # 10th house (South)
            'Mercury': 1,   # 1st house (East)
            'Jupiter': 1,   # 1st house (East)
            'Venus': 4,     # 4th house (North)
            'Saturn': 7     # 7th house (West)
        }
        
        house = planet_data.get('house', 1)
        optimal_house = dig_bala_houses.get(planet, 1)
        
        # Calculate house distance
        distance = abs(house - optimal_house)
        if distance > 6:
            distance = 12 - distance
        
        # Maximum 60 virupas at optimal house, 0 at opposite
        dig_bala = 60 * (1 - distance / 6)
        
        return dig_bala
    
    def _calculate_kala_bala(self, planet: str, planet_data: Dict, 
                             birth_time: datetime) -> float:
        """
        Calculate temporal strength.
        Includes: Diurnal, Lunar, Annual, and other time-based factors.
        """
        total = 0.0
        
        # 1. Diurnal strength (simplified)
        hour = birth_time.hour
        
        # Day planets (Sun, Jupiter, Venus) strong during day
        # Night planets (Moon, Mars, Saturn) strong at night
        # Mercury strong at sunrise/sunset
        
        if planet in ['Sun', 'Jupiter', 'Venus']:
            if 6 <= hour < 18:  # Day time
                total += 30
            else:
                total += 15
        elif planet in ['Moon', 'Mars', 'Saturn']:
            if hour < 6 or hour >= 18:  # Night time
                total += 30
            else:
                total += 15
        elif planet == 'Mercury':
            if 5 <= hour <= 7 or 17 <= hour <= 19:  # Twilight
                total += 30
            else:
                total += 20
        
        # 2. Paksha Bala (Lunar phase strength)
        # Benefics strong in bright half, malefics in dark half
        # This requires Moon's position relative to Sun
        # Simplified version
        if planet in ['Moon', 'Mercury', 'Jupiter', 'Venus']:
            total += 30  # Benefic bonus
        else:
            total += 20
        
        # 3. Tribhaga Bala (Part of day/night strength)
        # Different planets rule different parts of day/night
        total += 20  # Simplified
        
        # 4. Varsha (Year), Masa (Month), Vara (Weekday), Hora (Hour) lords
        # Simplified - weekday ruler gets bonus
        weekday = birth_time.weekday()
        weekday_rulers = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        weekday_ruler = weekday_rulers[(weekday + 1) % 7]  # Adjust for Sunday = 0
        
        if planet == weekday_ruler:
            total += 15
        
        return total
    
    def _calculate_chesta_bala(self, planet: str, planet_data: Dict) -> float:
        """
        Calculate motional strength.
        Based on retrogression, speed, etc.
        """
        speed = planet_data.get('speed', 0)
        
        # Sun and Moon don't have Chesta Bala in traditional sense
        if planet in ['Sun', 'Moon']:
            return 30.0  # Fixed value
        
        # Retrograde planets get maximum Chesta Bala
        if speed < 0:
            return 60.0
        
        # Direct motion - based on speed relative to average
        # Simplified calculation
        average_speeds = {
            'Mars': 0.52,
            'Mercury': 1.38,
            'Jupiter': 0.08,
            'Venus': 1.21,
            'Saturn': 0.03
        }
        
        avg_speed = average_speeds.get(planet, 1.0)
        
        # Faster than average gets more strength
        if abs(speed) > avg_speed:
            return 45.0
        else:
            return 30.0
    
    def _get_naisargika_bala(self, planet: str) -> float:
        """Get natural strength of planets."""
        natural_strength = {
            'Sun': 60.0,
            'Moon': 51.43,
            'Mars': 17.14,
            'Mercury': 25.71,
            'Jupiter': 34.29,
            'Venus': 42.86,
            'Saturn': 8.57
        }
        return natural_strength.get(planet, 0.0)
    
    def _calculate_drik_bala(self, planet: str, all_planets: Dict) -> float:
        """
        Calculate aspectual strength.
        Based on aspects received from other planets.
        """
        total = 0.0
        planet_long = all_planets[planet]['longitude']
        
        # Check aspects from all other planets
        for other_planet, other_data in all_planets.items():
            if other_planet == planet or other_planet in ['Rahu', 'Ketu']:
                continue
            
            other_long = other_data['longitude']
            
            # Calculate angular distance
            distance = abs(planet_long - other_long)
            if distance > 180:
                distance = 360 - distance
            
            # Check for aspects (simplified)
            aspect_strength = 0
            
            # Opposition (180°)
            if 170 <= distance <= 190:
                aspect_strength = 1.0
            # Trine (120°)
            elif 110 <= distance <= 130:
                aspect_strength = 0.75
            # Square (90°)
            elif 80 <= distance <= 100:
                aspect_strength = 0.5
            # Sextile (60°)
            elif 50 <= distance <= 70:
                aspect_strength = 0.25
            # Conjunction (0°)
            elif distance <= 10:
                aspect_strength = 1.0
            
            # Benefic aspects add, malefic subtract
            if aspect_strength > 0:
                if other_planet in ['Jupiter', 'Venus', 'Mercury', 'Moon']:
                    total += aspect_strength * 30
                else:  # Malefic
                    total -= aspect_strength * 30
        
        # Ensure positive value
        return max(0, total + 30)  # Base value of 30
    
    def calculate_bhava_bala(self, houses: List[float], planet_positions: Dict) -> Dict:
        """Calculate house strengths."""
        bhava_bala = {}
        
        for i in range(12):
            house_num = i + 1
            strength = 0.0
            
            # 1. Bhavadhipati Bala (House lord strength)
            # Get the sign of the house cusp
            house_longitude = houses[i]
            sign_num = int(house_longitude / 30)
            signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            sign = signs[sign_num]
            
            # Get house lord
            house_lord = self.SIGN_RULERS.get(sign, '')
            
            # Add lord's shadbala contribution (simplified)
            if house_lord and house_lord in planet_positions:
                strength += 100  # Base strength from lord
            
            # 2. Bhava Dig Bala (House directional strength)
            if house_num in [1, 10]:  # Angular houses strongest
                strength += 60
            elif house_num in [4, 7]:
                strength += 50
            elif house_num in [2, 5, 8, 11]:  # Succedent
                strength += 30
            else:  # Cadent
                strength += 15
            
            # 3. Aspects on house (simplified)
            # Check if benefics aspect the house
            for planet, data in planet_positions.items():
                if planet in ['Jupiter', 'Venus']:
                    planet_house = data.get('house', 0)
                    # Jupiter aspects 5, 7, 9 houses from itself
                    if planet == 'Jupiter':
                        if house_num in [(planet_house + 4) % 12 + 1,
                                       (planet_house + 6) % 12 + 1,
                                       (planet_house + 8) % 12 + 1]:
                            strength += 30
                    # Venus aspects 7th
                    elif planet == 'Venus':
                        if house_num == (planet_house + 6) % 12 + 1:
                            strength += 20
            
            bhava_bala[f"House_{house_num}"] = round(strength, 2)
        
        return bhava_bala
    
    def calculate_residential_strength(self, planet_positions: Dict) -> Dict:
        """
        Calculate residential strength of planets in signs.
        Shows how comfortable a planet is in its current sign.
        """
        residential_strength = {}
        
        for planet, data in planet_positions.items():
            if planet in ['Rahu', 'Ketu', 'Ascendant']:
                continue
            
            sign = data.get('sign', '')
            if not sign:
                continue
            
            # Determine strength based on sign placement
            sign_ruler = self.SIGN_RULERS.get(sign, '')
            
            strength_type = ""
            strength_value = 0
            
            # Own sign (Swakshetra)
            if sign_ruler == planet:
                strength_type = "Own Sign"
                strength_value = 100
            
            # Exaltation (Uchcha)
            elif self._is_exalted(planet, sign):
                strength_type = "Exalted"
                strength_value = 100
            
            # Moolatrikona
            elif self._is_moolatrikona(planet, sign):
                strength_type = "Moolatrikona"
                strength_value = 90
            
            # Friend's sign
            elif sign_ruler in self.PLANET_FRIENDS.get(planet, []):
                strength_type = "Friend's Sign"
                strength_value = 50
            
            # Neutral sign
            elif sign_ruler not in self.PLANET_ENEMIES.get(planet, []):
                strength_type = "Neutral Sign"
                strength_value = 25
            
            # Enemy's sign
            elif sign_ruler in self.PLANET_ENEMIES.get(planet, []):
                strength_type = "Enemy's Sign"
                strength_value = 12.5
            
            # Debilitation
            if self._is_debilitated(planet, sign):
                strength_type = "Debilitated"
                strength_value = 0
            
            residential_strength[planet] = {
                'sign': sign,
                'ruler': sign_ruler,
                'strength_type': strength_type,
                'strength_value': strength_value
            }
        
        return residential_strength
    
    def _is_exalted(self, planet: str, sign: str) -> bool:
        """Check if planet is exalted in given sign."""
        exaltation_signs = {
            'Sun': 'Aries',
            'Moon': 'Taurus',
            'Mars': 'Capricorn',
            'Mercury': 'Virgo',
            'Jupiter': 'Cancer',
            'Venus': 'Pisces',
            'Saturn': 'Libra'
        }
        return exaltation_signs.get(planet) == sign
    
    def _is_debilitated(self, planet: str, sign: str) -> bool:
        """Check if planet is debilitated in given sign."""
        debilitation_signs = {
            'Sun': 'Libra',
            'Moon': 'Scorpio',
            'Mars': 'Cancer',
            'Mercury': 'Pisces',
            'Jupiter': 'Capricorn',
            'Venus': 'Virgo',
            'Saturn': 'Aries'
        }
        return debilitation_signs.get(planet) == sign
    
    def _is_moolatrikona(self, planet: str, sign: str) -> bool:
        """Check if planet is in moolatrikona sign."""
        moolatrikona_signs = {
            'Sun': 'Leo',
            'Moon': 'Taurus',
            'Mars': 'Aries',
            'Mercury': 'Virgo',
            'Jupiter': 'Sagittarius',
            'Venus': 'Libra',
            'Saturn': 'Aquarius'
        }
        return moolatrikona_signs.get(planet) == sign
    
    def format_shadbala_summary(self, shadbala: Dict) -> List[str]:
        """Format Shadbala results for display."""
        lines = []
        lines.append("SHADBALA (PLANETARY STRENGTHS):")
        lines.append("-" * 70)
        lines.append("PLANET    STHANA   DIG    KALA  CHESTA  NAISRG   DRIK   TOTAL  RUPAS")
        
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            if planet in shadbala:
                s = shadbala[planet]
                lines.append(f"{planet:8} {s['sthana_bala']:7.1f} {s['dig_bala']:6.1f} "
                           f"{s['kala_bala']:6.1f} {s['chesta_bala']:6.1f} "
                           f"{s['naisargika_bala']:6.1f} {s['drik_bala']:6.1f} "
                           f"{s['total']:7.1f} {s['rupas']:6.2f}")
        
        return lines