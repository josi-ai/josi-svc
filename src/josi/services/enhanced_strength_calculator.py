"""
Enhanced Strength Calculator
Calculate all strength measures in traditional decimal format
"""

import math
from typing import Dict, List, Tuple
from datetime import datetime


class EnhancedStrengthCalculator:
    """Calculate all strength measures in traditional decimal format."""
    
    def __init__(self):
        # Planetary rays (Rashmi) for Ishta/Kashta calculation
        self.planetary_rays = {
            'Sun': 5.0,
            'Moon': 9.0,
            'Mars': 5.0,
            'Mercury': 9.0,
            'Jupiter': 10.0,
            'Venus': 8.0,
            'Saturn': 5.0
        }
        
        # Exaltation points for calculations
        self.exaltation_points = {
            'Sun': 10.0,      # 10° Aries
            'Moon': 33.0,     # 3° Taurus
            'Mars': 298.0,    # 28° Capricorn
            'Mercury': 165.0, # 15° Virgo
            'Jupiter': 95.0,  # 5° Cancer
            'Venus': 357.0,   # 27° Pisces
            'Saturn': 200.0,  # 20° Libra
            'Rahu': 60.0,     # 0° Gemini (some say 20° Gemini)
            'Ketu': 240.0     # 0° Sagittarius
        }
        
        # Deep exaltation/debilitation points
        self.deep_exaltation = {
            'Sun': 10.0,
            'Moon': 33.0,
            'Mars': 298.0,
            'Mercury': 165.0,
            'Jupiter': 95.0,
            'Venus': 357.0,
            'Saturn': 200.0
        }
        
        self.deep_debilitation = {
            'Sun': 190.0,     # 10° Libra
            'Moon': 213.0,    # 3° Scorpio
            'Mars': 118.0,    # 28° Cancer
            'Mercury': 345.0, # 15° Pisces
            'Jupiter': 275.0, # 5° Capricorn
            'Venus': 177.0,   # 27° Virgo
            'Saturn': 20.0    # 20° Aries
        }
    
    def calculate_residential_strength_decimal(self, planet_positions: Dict) -> Dict:
        """
        Calculate residential strength in decimal format (0-1).
        
        This is different from the percentage format and follows
        traditional calculation methods.
        """
        residential_strength = {}
        
        for planet, data in planet_positions.items():
            if planet == 'Ascendant':
                continue
            
            longitude = data.get('longitude', 0)
            sign = data.get('sign', '')
            
            # Calculate Uchcha Bala (exaltation strength)
            if planet in self.exaltation_points:
                exalt_point = self.exaltation_points[planet]
                
                # Angular distance from exaltation
                distance = abs(longitude - exalt_point)
                if distance > 180:
                    distance = 360 - distance
                
                # Strength decreases linearly from exaltation to debilitation
                # 1.0 at exaltation, 0.0 at debilitation (180° away)
                uchcha_bala = 1.0 - (distance / 180.0)
                
                # Apply Ojha's formula for more nuanced calculation
                if planet in self.deep_exaltation:
                    deep_exalt = self.deep_exaltation[planet]
                    deep_debil = self.deep_debilitation[planet]
                    
                    # Additional refinement based on exact degrees
                    if abs(longitude - deep_exalt) < 1:
                        uchcha_bala = 1.0
                    elif abs(longitude - deep_debil) < 1:
                        uchcha_bala = 0.0
            else:
                # For Rahu/Ketu, use sign-based strength
                uchcha_bala = self._calculate_node_strength(planet, sign)
            
            # Additional factors for residential strength
            # 1. Sign relationship (own sign, friend's sign, etc.)
            sign_strength = self._calculate_sign_relationship_strength(planet, sign)
            
            # 2. Navamsa strength (would need D9 positions)
            navamsa_strength = 0.5  # Placeholder
            
            # Combined residential strength
            # Traditional formula weights
            residential = (uchcha_bala * 0.5 + 
                         sign_strength * 0.3 + 
                         navamsa_strength * 0.2)
            
            residential_strength[planet] = round(residential, 3)
        
        return residential_strength
    
    def calculate_ishta_kashta_bala(self, planet_positions: Dict, 
                                   chart_info: Dict) -> Dict:
        """
        Calculate Ishta and Kashta Bala.
        
        Based on:
        1. Planetary rays (Rashmi)
        2. Exaltation strength (Uchcha Bala)
        3. Chesta Bala (motional strength)
        4. Other factors
        """
        ishta_kashta = {}
        
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            if planet not in planet_positions:
                continue
            
            data = planet_positions[planet]
            
            # Get base rays
            rays = self.planetary_rays[planet]
            
            # Calculate Uchcha Rashmi (exaltation rays)
            longitude = data['longitude']
            exalt_point = self.exaltation_points[planet]
            
            distance = abs(longitude - exalt_point)
            if distance > 180:
                distance = 360 - distance
            
            # Uchcha Rashmi calculation
            uchcha_rashmi = rays * (1 - distance / 180)
            
            # Calculate Chesta Rashmi (motion rays)
            speed = data.get('speed', 0)
            chesta_rashmi = self._calculate_chesta_rashmi(planet, speed, rays)
            
            # Ishta Rashmi (favorable rays)
            ishta_rashmi = (uchcha_rashmi + chesta_rashmi) / 2
            
            # Convert to Rupas (60 Virupas = 1 Rupa)
            ishta_phala = ishta_rashmi * ishta_rashmi / 10
            ishta_bala = ishta_phala / 60
            
            # Kashta Bala (unfavorable)
            kashta_phala = (rays * rays / 10) - ishta_phala
            kashta_bala = kashta_phala / 60
            
            # Net Bala
            net_bala = ishta_bala - kashta_bala
            
            ishta_kashta[planet] = {
                'ishta': round(ishta_bala, 2),
                'kashta': round(-kashta_bala, 2),  # Shown as negative
                'net': round(net_bala, 2)
            }
        
        return ishta_kashta
    
    def calculate_detailed_bhava_bala(self, houses: List[float], 
                                    planet_positions: Dict,
                                    benefic_mercury: bool = True) -> Dict:
        """
        Calculate detailed Bhava Bala with all components.
        
        Args:
            houses: House cusps
            planet_positions: Planet positions
            benefic_mercury: Whether Mercury is benefic or malefic
            
        Returns:
            Dict with Dikbala, Dhrshti, Adipati, and Total for each house
        """
        bhava_bala = {
            'benefic_mercury': benefic_mercury,
            'components': {},
            'totals': {}
        }
        
        for i in range(12):
            house_num = i + 1
            house_cusp = houses[i]
            
            # 1. Dikbala (Directional strength)
            dikbala = self._calculate_house_dikbala(house_num)
            
            # 2. Dhrshti Bala (Aspectual strength)
            dhrshti = self._calculate_house_dhrshti(
                house_cusp, planet_positions, benefic_mercury
            )
            
            # 3. Adipati Bala (Lord's strength)
            adipati = self._calculate_house_adipati_bala(
                house_num, planet_positions
            )
            
            # Total
            total = dikbala + dhrshti + adipati
            
            bhava_bala['components'][house_num] = {
                'dikbala': round(dikbala, 2),
                'dhrshti': round(dhrshti, 2),
                'adipati': round(adipati, 2)
            }
            
            bhava_bala['totals'][house_num] = round(total, 2)
        
        return bhava_bala
    
    def _calculate_node_strength(self, planet: str, sign: str) -> float:
        """Calculate strength for Rahu/Ketu based on sign placement."""
        # Rahu is strong in: Gemini, Virgo, Aquarius
        # Ketu is strong in: Sagittarius, Pisces, Gemini
        
        if planet == 'Rahu':
            strong_signs = ['Gemini', 'Virgo', 'Aquarius']
            weak_signs = ['Sagittarius', 'Pisces']
        else:  # Ketu
            strong_signs = ['Sagittarius', 'Pisces', 'Gemini']
            weak_signs = ['Gemini', 'Virgo']
        
        if sign in strong_signs:
            return 0.75
        elif sign in weak_signs:
            return 0.25
        else:
            return 0.5
    
    def _calculate_sign_relationship_strength(self, planet: str, sign: str) -> float:
        """Calculate strength based on sign rulership and friendship."""
        # Sign rulers
        sign_rulers = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
            'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
            'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
        }
        
        # Natural friendships
        friendships = {
            'Sun': {'friends': ['Moon', 'Mars', 'Jupiter'], 
                   'enemies': ['Venus', 'Saturn']},
            'Moon': {'friends': ['Sun', 'Mercury'], 
                    'enemies': []},
            'Mars': {'friends': ['Sun', 'Moon', 'Jupiter'], 
                    'enemies': ['Mercury']},
            'Mercury': {'friends': ['Sun', 'Venus'], 
                       'enemies': ['Moon']},
            'Jupiter': {'friends': ['Sun', 'Moon', 'Mars'], 
                       'enemies': ['Mercury', 'Venus']},
            'Venus': {'friends': ['Mercury', 'Saturn'], 
                     'enemies': ['Sun', 'Moon']},
            'Saturn': {'friends': ['Mercury', 'Venus'], 
                      'enemies': ['Sun', 'Moon', 'Mars']},
            'Rahu': {'friends': ['Mercury', 'Venus', 'Saturn'], 
                    'enemies': ['Sun', 'Moon', 'Mars']},
            'Ketu': {'friends': ['Mars', 'Jupiter'], 
                    'enemies': ['Mercury', 'Venus']}
        }
        
        ruler = sign_rulers.get(sign, '')
        
        # Own sign
        if ruler == planet:
            return 1.0
        
        # Friend's sign
        if ruler in friendships.get(planet, {}).get('friends', []):
            return 0.75
        
        # Enemy's sign
        if ruler in friendships.get(planet, {}).get('enemies', []):
            return 0.25
        
        # Neutral
        return 0.5
    
    def _calculate_chesta_rashmi(self, planet: str, speed: float, rays: float) -> float:
        """Calculate Chesta Rashmi based on planetary motion."""
        # Average speeds (degrees per day)
        avg_speeds = {
            'Sun': 0.9856,
            'Moon': 13.176,
            'Mars': 0.524,
            'Mercury': 1.383,
            'Jupiter': 0.083,
            'Venus': 1.210,
            'Saturn': 0.033
        }
        
        avg_speed = avg_speeds.get(planet, 1.0)
        
        # Retrograde gets maximum
        if speed < 0:
            return rays
        
        # Direct motion
        speed_ratio = abs(speed) / avg_speed
        
        # Faster than average
        if speed_ratio > 1:
            chesta_rashmi = rays * min(speed_ratio, 2.0) / 2.0
        else:
            # Slower than average
            chesta_rashmi = rays * speed_ratio
        
        return chesta_rashmi
    
    def _calculate_house_dikbala(self, house_num: int) -> float:
        """Calculate directional strength of house."""
        # Angular houses (1,4,7,10) have maximum dikbala
        if house_num in [1, 4, 7, 10]:
            return 1.0
        # Succedent houses (2,5,8,11)
        elif house_num in [2, 5, 8, 11]:
            return 0.5
        # Cadent houses (3,6,9,12)
        else:
            return 0.25
    
    def _calculate_house_dhrshti(self, house_cusp: float, planets: Dict, 
                                benefic_mercury: bool) -> float:
        """Calculate aspectual strength received by house."""
        total_dhrshti = 0.0
        
        # Define benefics and malefics
        if benefic_mercury:
            benefics = ['Moon', 'Mercury', 'Jupiter', 'Venus']
            malefics = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']
        else:
            benefics = ['Moon', 'Jupiter', 'Venus']
            malefics = ['Sun', 'Mars', 'Mercury', 'Saturn', 'Rahu', 'Ketu']
        
        for planet, data in planets.items():
            if planet == 'Ascendant':
                continue
            
            planet_long = data['longitude']
            
            # Calculate aspect
            aspect_angle = abs(house_cusp - planet_long)
            if aspect_angle > 180:
                aspect_angle = 360 - aspect_angle
            
            aspect_strength = 0
            
            # Full aspect (180°)
            if 175 <= aspect_angle <= 185:
                aspect_strength = 1.0
            # Special aspects
            elif planet == 'Mars' and (82 <= aspect_angle <= 98 or 202 <= aspect_angle <= 218):
                aspect_strength = 0.75
            elif planet == 'Jupiter' and (115 <= aspect_angle <= 125 or 235 <= aspect_angle <= 245):
                aspect_strength = 0.75
            elif planet == 'Saturn' and (55 <= aspect_angle <= 65 or 265 <= aspect_angle <= 275):
                aspect_strength = 0.75
            
            # Apply benefic/malefic nature
            if aspect_strength > 0:
                if planet in benefics:
                    total_dhrshti += aspect_strength
                else:
                    total_dhrshti -= aspect_strength * 0.5
        
        return total_dhrshti
    
    def _calculate_house_adipati_bala(self, house_num: int, planets: Dict) -> float:
        """Calculate house lord's strength."""
        # House to sign mapping (for Aries ascendant, adjust as needed)
        house_signs = {
            1: 'Aries', 2: 'Taurus', 3: 'Gemini', 4: 'Cancer',
            5: 'Leo', 6: 'Virgo', 7: 'Libra', 8: 'Scorpio',
            9: 'Sagittarius', 10: 'Capricorn', 11: 'Aquarius', 12: 'Pisces'
        }
        
        sign_rulers = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
            'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
            'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
        }
        
        # This is simplified - should use actual house cusps
        sign = house_signs.get(house_num, 'Aries')
        ruler = sign_rulers.get(sign, 'Mars')
        
        # Get ruler's shadbala (simplified)
        if ruler in planets:
            # Use residential strength as proxy
            ruler_strength = self._calculate_sign_relationship_strength(
                ruler, planets[ruler].get('sign', '')
            )
            return ruler_strength * 10  # Scale up for display
        
        return 5.0  # Default

    def format_strength_tables(self, residential: Dict, ishta_kashta: Dict,
                             bhava_bala: Dict) -> List[str]:
        """Format all strength tables in traditional style."""
        lines = []
        
        # Residential Strength
        lines.append("RESIDENTIAL       SURY   CHAN   KUJA   BUDH   GURU   SUKR   SANI   RAHU   KETU")
        res_line = "STRENGTH        "
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
            if planet in residential:
                res_line += f"  {residential[planet]:>.3f}"
            else:
                res_line += "     - "
        lines.append(res_line)
        lines.append("")
        
        # Ishta/Kashta Bala
        lines.append("                           SURY  CHAN  KUJA  BUDH  GURU  SUKR  SANI")
        
        ishta_line = "             ISHTA BALA  "
        kashta_line = "             KASHTA BALA "
        net_line = "             NET BALA    "
        
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            if planet in ishta_kashta:
                ik = ishta_kashta[planet]
                ishta_line += f"  {ik['ishta']:>.2f}"
                kashta_line += f" {ik['kashta']:>.2f}"
                net_line += f" {ik['net']:>.2f}"
            else:
                ishta_line += "     -"
                kashta_line += "     -"
                net_line += "     -"
        
        lines.extend([ishta_line, kashta_line, net_line])
        lines.append("")
        
        # Bhava Bala
        mercury_type = "BENEFIC" if bhava_bala['benefic_mercury'] else "MALEFIC"
        lines.append(f"BHAVA BALA: {mercury_type}  MERCURY")
        lines.append("----------")
        
        # Components
        dikbala_line = "DIKBALA"
        dhrshti_line = "DHRSHTI"
        adipati_line = "ADIPATI"
        total_line = "TOTAL  "
        
        for i in range(1, 13):
            comp = bhava_bala['components'][i]
            dikbala_line += f" {comp['dikbala']:>5.2f}"
            dhrshti_line += f" {comp['dhrshti']:>5.2f}"
            adipati_line += f" {comp['adipati']:>5.2f}"
            total_line += f" {bhava_bala['totals'][i]:>5.2f}"
        
        lines.extend([dikbala_line, dhrshti_line, adipati_line, total_line])
        
        return lines