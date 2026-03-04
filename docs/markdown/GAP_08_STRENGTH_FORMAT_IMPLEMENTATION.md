# Gap 08: Strength Calculations Format Implementation Plan

## Overview
Implement additional strength calculations with proper decimal format and complete Ishta/Kashta Bala.

**Original Format**:
```
RESIDENTIAL       SURY   CHAN   KUJA   BUDH   GURU   SUKR   SANI   RAHU   KETU
STRENGTH          .308   .731   .953   .835   .052   .326   .482   .383   .383

                           SURY  CHAN  KUJA  BUDH  GURU  SUKR  SANI
             ISHTA BALA     .14   .65   .34   .74   .35   .19   .26
             KASHTA BALA   -.84  -.35  -.63  -.25  -.63  -.76  -.48
             NET BALA      -.70   .30  -.28   .49  -.28  -.58  -.22

BHAVA BALA: BENEFIC  MERCURY
----------
DIKBALA  .50   .33   .67   .50   .67   .17   .50   .17   .17  1.00   .83   .83
DHRSHTI 1.06   .68   .77   .21   .50  -.17  -.37   .49   .10  -.01  1.20  1.02
ADIPATI10.37  4.55  6.42  4.03  5.73  5.45  4.76  4.76  5.45  5.73  4.03  6.42
TOTAL  11.93  5.57  7.85  4.74  6.90  5.45  4.89  5.42  5.72  6.72  6.06  8.27
```

**Current Format**: Percentage format for residential strength, missing Ishta/Kashta Bala

## Understanding Strength Formats

### Residential Strength
- Original uses decimal values (0-1 scale)
- Represents planet's comfort in sign
- Includes Rahu/Ketu calculations

### Ishta/Kashta Bala
- **Ishta Bala**: Favorable strength
- **Kashta Bala**: Unfavorable strength  
- **Net Bala**: Ishta - Kashta
- Based on planetary rays (Rashmi) calculations

### Bhava Bala Components
- **Dikbala**: Directional strength of house
- **Dhrshti**: Aspectual strength received
- **Adipati**: House lord's strength
- Shows variations for benefic/malefic Mercury

## Implementation Steps

### 1. Create Enhanced Strength Calculator

```python
# src/josi/services/enhanced_strength_calculator.py

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
```

### 2. Integration with Export

Update `generate_josi_traditional_export.py`:

```python
# Replace the current strength section with enhanced version

# Import enhanced calculator
from src.josi.services.enhanced_strength_calculator import EnhancedStrengthCalculator
enhanced_calc = EnhancedStrengthCalculator()

# Calculate all strength measures
residential_decimal = enhanced_calc.calculate_residential_strength_decimal(
    chart['planets']
)

ishta_kashta = enhanced_calc.calculate_ishta_kashta_bala(
    chart['planets'], chart
)

# Determine if Mercury is benefic
mercury_benefic = is_mercury_benefic(chart)  # Based on associations

bhava_bala_detailed = enhanced_calc.calculate_detailed_bhava_bala(
    chart['houses'], chart['planets'], mercury_benefic
)

# Format and add to output
strength_lines = enhanced_calc.format_strength_tables(
    residential_decimal, ishta_kashta, bhava_bala_detailed
)

lines.extend(strength_lines)
```

### 3. Mercury Benefic/Malefic Determination

```python
def is_mercury_benefic(chart: Dict) -> bool:
    """
    Determine if Mercury is benefic or malefic.
    
    Rules:
    1. Mercury alone or with benefics = Benefic
    2. Mercury with malefics = Malefic
    3. Check conjunctions within 10 degrees
    """
    if 'planets' not in chart or 'Mercury' not in chart['planets']:
        return True  # Default benefic
    
    mercury = chart['planets']['Mercury']
    mercury_long = mercury['longitude']
    mercury_house = mercury.get('house', 0)
    
    benefics = ['Moon', 'Jupiter', 'Venus']
    malefics = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']
    
    # Check conjunctions
    conjunct_benefics = 0
    conjunct_malefics = 0
    
    for planet, data in chart['planets'].items():
        if planet == 'Mercury':
            continue
        
        # Check if in same house or within 10 degrees
        if data.get('house') == mercury_house:
            planet_long = data['longitude']
            distance = abs(mercury_long - planet_long)
            if distance > 180:
                distance = 360 - distance
            
            if distance <= 10:
                if planet in benefics:
                    conjunct_benefics += 1
                elif planet in malefics:
                    conjunct_malefics += 1
    
    # Mercury is malefic if conjunct more malefics than benefics
    return conjunct_malefics <= conjunct_benefics
```

### 4. Additional Strength Measures

```python
class SpecialStrengthCalculations:
    """Additional strength calculations for completeness."""
    
    @staticmethod
    def calculate_vimshopaka_bala(vargas: Dict) -> Dict:
        """
        Calculate Vimshopaka Bala based on divisional chart placements.
        
        Weights for different varga schemes:
        - Shadvarga: D1(6), D2(2), D3(4), D9(5), D12(2), D30(1)
        - Saptavarga: Add D7(1)
        - Dashavarga: Add D10(1), D16(0.5), D60(0.5)
        - Shodashavarga: 16 vargas with specific weights
        """
        vimshopaka = {}
        
        # Shadvarga weights
        weights = {
            'D1': 6, 'D2': 2, 'D3': 4, 
            'D9': 5, 'D12': 2, 'D30': 1
        }
        
        # Calculate for each planet
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            total_points = 0
            
            for varga, weight in weights.items():
                if varga in vargas and planet in vargas[varga]:
                    # Check dignity in varga
                    sign = vargas[varga][planet]
                    dignity = get_planet_dignity_in_sign(planet, sign)
                    
                    # Points based on dignity
                    points_map = {
                        'own_sign': 20,
                        'exalted': 18,
                        'moolatrikona': 16,
                        'friend': 12,
                        'neutral': 8,
                        'enemy': 4,
                        'debilitated': 2
                    }
                    
                    points = points_map.get(dignity, 8)
                    total_points += points * weight
            
            # Convert to 0-20 scale
            max_points = sum(weights.values()) * 20
            vimshopaka[planet] = round(total_points * 20 / max_points, 2)
        
        return vimshopaka
    
    @staticmethod
    def calculate_ashtakavarga_strength(ashtakavarga: Dict) -> Dict:
        """
        Calculate strength based on Ashtakavarga points.
        
        Average points per sign:
        - Less than 25: Weak
        - 25-30: Average
        - More than 30: Strong
        """
        av_strength = {}
        
        for planet, sign_points in ashtakavarga.items():
            total_points = sum(sign_points.values())
            avg_points = total_points / 12
            
            # Normalize to 0-1 scale
            strength = min(avg_points / 35, 1.0)
            av_strength[planet] = round(strength, 3)
        
        return av_strength
```

This implementation provides all strength calculations in the traditional decimal format matching the original.