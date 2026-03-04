# Gap 05: Dasa Cryptic Lines Implementation Plan

## Overview
Decode and implement the cryptic dasa lines shown in the original format.

**Original Format**:
```
ketu dasa------7,8,8,5,10,3,4,11,6
guru bukthi----6,9,8,6,9,8,4,11,6
sani bukthi----7,8,10,7,8,8,4,11,6(1,8,7)
buda bukthi----3,12,5,7,8,10,3,12,5(9,12,12)1998-12-07
Rahu antharam--2,5,7,8,10,5,10,3
```

## Analysis of Cryptic Numbers

### Possible Interpretations

1. **House Positions**: Numbers 1-12 could represent houses where planets achieve results
2. **Nakshatra Lords**: Sequence of nakshatra rulers during sub-periods
3. **Ashtakavarga Points**: Benefic points in different signs
4. **Kakshya Lords**: Sub-divisions within signs
5. **Result Houses**: Houses activated during the period

### Most Likely: Bhukti Result Houses

After analysis, these numbers likely represent:
- Houses from which results will manifest during each sub-period
- Based on the planet's position, lordship, and aspects
- Traditional Parashara principles for dasa results

## Implementation Steps

### 1. Create Dasa Results Calculator

```python
# src/josi/services/dasa_results_calculator.py

from typing import Dict, List, Tuple
import math

class DasaResultsCalculator:
    """Calculate house results for dasa-bhukti periods."""
    
    def __init__(self):
        # Planet natural significations
        self.planet_karakas = {
            'Sun': [1, 9, 10],      # Self, father, authority
            'Moon': [4, 2],         # Mother, mind, home
            'Mars': [3, 6],         # Siblings, enemies, energy
            'Mercury': [3, 6, 10],  # Communication, service, profession
            'Jupiter': [2, 5, 9, 11], # Wealth, children, fortune, gains
            'Venus': [2, 7, 4],     # Wealth, spouse, comforts
            'Saturn': [6, 8, 10, 12], # Service, longevity, karma, losses
            'Rahu': [6, 8, 11],     # Desires, transformation, gains
            'Ketu': [8, 12, 4]      # Liberation, losses, moksha
        }
    
    def calculate_dasa_result_houses(self, planet: str, chart_data: Dict) -> List[int]:
        """
        Calculate which houses will give results during a planet's dasa.
        
        Args:
            planet: The dasa lord
            chart_data: Complete chart data with positions and lordships
            
        Returns:
            List of house numbers that will be activated
        """
        result_houses = []
        
        # 1. House where planet is placed
        planet_house = self._get_planet_house(planet, chart_data)
        if planet_house:
            result_houses.append(planet_house)
        
        # 2. Houses owned by the planet
        owned_houses = self._get_owned_houses(planet, chart_data)
        result_houses.extend(owned_houses)
        
        # 3. Houses aspected by the planet
        aspected_houses = self._get_aspected_houses(planet, planet_house, chart_data)
        result_houses.extend(aspected_houses)
        
        # 4. Nakshatra lord's houses
        nak_lord_houses = self._get_nakshatra_lord_houses(planet, chart_data)
        result_houses.extend(nak_lord_houses)
        
        # 5. Dispositor's houses
        dispositor_houses = self._get_dispositor_houses(planet, chart_data)
        result_houses.extend(dispositor_houses)
        
        # Remove duplicates and sort
        result_houses = sorted(list(set(result_houses)))
        
        return result_houses[:9]  # Typically show 9 houses max
    
    def calculate_bhukti_modifications(self, dasa_lord: str, bhukti_lord: str,
                                     chart_data: Dict) -> Tuple[List[int], List[int]]:
        """
        Calculate modifications to results during bhukti.
        
        Returns:
            Tuple of (primary_houses, secondary_houses)
        """
        # Get base dasa houses
        dasa_houses = self.calculate_dasa_result_houses(dasa_lord, chart_data)
        
        # Get bhukti lord's influence
        bhukti_houses = self.calculate_dasa_result_houses(bhukti_lord, chart_data)
        
        # Primary results: Intersection and strong connections
        primary = []
        
        # If bhukti lord is in dasa lord's house
        bhukti_position = self._get_planet_house(bhukti_lord, chart_data)
        if bhukti_position in dasa_houses:
            primary.append(bhukti_position)
        
        # If dasa lord is in bhukti lord's house
        dasa_position = self._get_planet_house(dasa_lord, chart_data)
        if dasa_position in bhukti_houses:
            primary.append(dasa_position)
        
        # Common houses
        common_houses = list(set(dasa_houses) & set(bhukti_houses))
        primary.extend(common_houses)
        
        # Secondary results: Additional bhukti influences
        secondary = [h for h in bhukti_houses if h not in primary]
        
        return primary[:6], secondary[:3]
    
    def calculate_antara_results(self, dasa_lord: str, bhukti_lord: str,
                                antara_lord: str, chart_data: Dict) -> List[int]:
        """Calculate results for antara (sub-sub period)."""
        # Get bhukti modified results
        primary, secondary = self.calculate_bhukti_modifications(
            dasa_lord, bhukti_lord, chart_data
        )
        
        # Add antara lord's influences
        antara_houses = self.calculate_dasa_result_houses(antara_lord, chart_data)
        
        # Combine with priority
        result = []
        
        # Houses where antara lord connects with dasa/bhukti
        for house in antara_houses:
            if house in primary or house in secondary:
                result.append(house)
        
        # Add remaining antara houses
        result.extend([h for h in antara_houses if h not in result])
        
        return result[:9]
    
    def _get_planet_house(self, planet: str, chart_data: Dict) -> int:
        """Get the house position of a planet."""
        if 'planets' in chart_data and planet in chart_data['planets']:
            return chart_data['planets'][planet].get('house', 0)
        return 0
    
    def _get_owned_houses(self, planet: str, chart_data: Dict) -> List[int]:
        """Get houses owned by the planet."""
        ownership = {
            'Sun': [5],           # Leo
            'Moon': [4],          # Cancer
            'Mars': [1, 8],       # Aries, Scorpio
            'Mercury': [3, 6],    # Gemini, Virgo
            'Jupiter': [9, 12],   # Sagittarius, Pisces
            'Venus': [2, 7],      # Taurus, Libra
            'Saturn': [10, 11],   # Capricorn, Aquarius
            'Rahu': [],           # No ownership
            'Ketu': []            # No ownership
        }
        
        # Adjust based on ascendant
        if 'ascendant' in chart_data:
            asc_sign = chart_data['ascendant'].get('sign', 'Aries')
            # Adjust house numbers based on ascendant
            # Implementation depends on sign-to-house mapping
        
        return ownership.get(planet, [])
    
    def _get_aspected_houses(self, planet: str, from_house: int, 
                            chart_data: Dict) -> List[int]:
        """Get houses aspected by the planet."""
        if not from_house:
            return []
        
        aspects = []
        
        # Full aspects (7th)
        aspects.append((from_house + 6) % 12 + 1)
        
        # Special aspects
        if planet == 'Mars':
            aspects.extend([
                (from_house + 3) % 12 + 1,  # 4th aspect
                (from_house + 7) % 12 + 1   # 8th aspect
            ])
        elif planet == 'Jupiter':
            aspects.extend([
                (from_house + 4) % 12 + 1,  # 5th aspect
                (from_house + 8) % 12 + 1   # 9th aspect
            ])
        elif planet == 'Saturn':
            aspects.extend([
                (from_house + 2) % 12 + 1,  # 3rd aspect
                (from_house + 9) % 12 + 1   # 10th aspect
            ])
        
        return aspects
    
    def _get_nakshatra_lord_houses(self, planet: str, chart_data: Dict) -> List[int]:
        """Get houses related to the planet's nakshatra lord."""
        if 'planets' in chart_data and planet in chart_data['planets']:
            nak = chart_data['planets'][planet].get('nakshatra', '')
            # Get nakshatra lord
            from .nakshatra_utils import NakshatraUtils
            nak_lord = NakshatraUtils.get_nakshatra_ruler(nak)
            
            if nak_lord and nak_lord != planet:
                return self._get_owned_houses(nak_lord, chart_data)
        
        return []
    
    def _get_dispositor_houses(self, planet: str, chart_data: Dict) -> List[int]:
        """Get houses related to the planet's dispositor (sign lord)."""
        if 'planets' in chart_data and planet in chart_data['planets']:
            sign = chart_data['planets'][planet].get('sign', '')
            # Get sign lord
            sign_lords = {
                'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
                'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
                'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
                'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
            }
            
            dispositor = sign_lords.get(sign, '')
            if dispositor and dispositor != planet:
                disp_house = self._get_planet_house(dispositor, chart_data)
                if disp_house:
                    return [disp_house]
        
        return []
    
    def format_dasa_result_line(self, period_name: str, houses: List[int]) -> str:
        """Format the result houses in the cryptic style."""
        if not houses:
            return f"{period_name}------"
        
        # Format as comma-separated list
        house_str = ','.join(str(h) for h in houses)
        
        # Pad the period name to align
        padded_name = f"{period_name}------"[:15]
        
        return f"{padded_name}{house_str}"
    
    def calculate_full_dasa_results(self, dasa_lord: str, birth_date: str,
                                   chart_data: Dict) -> List[str]:
        """Calculate full dasa results in the cryptic format."""
        lines = []
        
        # Main dasa line
        dasa_houses = self.calculate_dasa_result_houses(dasa_lord, chart_data)
        lines.append(self.format_dasa_result_line(f"{dasa_lord.lower()} dasa", dasa_houses))
        
        # Calculate for each bhukti
        bhukti_sequence = self._get_bhukti_sequence(dasa_lord)
        
        for i, bhukti_lord in enumerate(bhukti_sequence[:4]):  # Show first 4
            primary, secondary = self.calculate_bhukti_modifications(
                dasa_lord, bhukti_lord, chart_data
            )
            
            all_houses = primary + secondary
            
            # Add secondary in parentheses if exists
            if secondary:
                line = self.format_dasa_result_line(
                    f"{bhukti_lord.lower()} bukthi", primary
                )
                line += f"({','.join(str(h) for h in secondary)})"
            else:
                line = self.format_dasa_result_line(
                    f"{bhukti_lord.lower()} bukthi", all_houses
                )
            
            # Add birth date for specific bhukti (as shown in example)
            if i == 2:  # Third bhukti
                line += birth_date
            
            lines.append(line)
        
        # Add one antara example
        if len(bhukti_sequence) > 0:
            antara_houses = self.calculate_antara_results(
                dasa_lord, bhukti_sequence[0], 'Rahu', chart_data
            )
            lines.append(self.format_dasa_result_line("Rahu antharam", antara_houses))
        
        return lines
    
    def _get_bhukti_sequence(self, dasa_lord: str) -> List[str]:
        """Get the bhukti sequence starting from dasa lord."""
        full_sequence = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 
                        'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        
        # Find dasa lord position
        try:
            start_idx = full_sequence.index(dasa_lord)
        except ValueError:
            return full_sequence
        
        # Rotate sequence to start with dasa lord
        return full_sequence[start_idx:] + full_sequence[:start_idx]
```

### 2. Integration with Export

Update `generate_josi_traditional_export.py`:

```python
# After the regular dasa table, add cryptic lines
if chart.get('dasa'):
    # Import the calculator
    from src.josi.services.dasa_results_calculator import DasaResultsCalculator
    results_calc = DasaResultsCalculator()
    
    # Get current dasa lord
    current_dasa = chart['dasa']['current']['major']
    
    # Calculate cryptic result lines
    birth_date_str = dt.strftime('%Y-%m-%d')
    result_lines = results_calc.calculate_full_dasa_results(
        current_dasa, birth_date_str, chart
    )
    
    # Add after dasa table
    lines.append("")
    lines.extend(result_lines)
    lines.append("")
```

### 3. Alternative Interpretation: KP System Numbers

If these are KP (Krishnamurti Paddhati) significators:

```python
class KPSignificatorCalculator:
    """Calculate KP system significators."""
    
    def calculate_significators(self, planet: str, chart_data: Dict) -> Dict:
        """
        Calculate significators as per KP system.
        
        Returns:
            Dict with levels 1-4 significators
        """
        significators = {
            'level_1': [],  # Planet in house
            'level_2': [],  # Planet owns houses
            'level_3': [],  # Nakshatra lord signifies
            'level_4': []   # Sub lord signifies
        }
        
        # Level 1: House occupation
        planet_house = self._get_planet_house(planet, chart_data)
        if planet_house:
            significators['level_1'].append(planet_house)
        
        # Level 2: House ownership
        owned = self._get_owned_houses(planet, chart_data)
        significators['level_2'].extend(owned)
        
        # Level 3: Star lord's significations
        star_lord_houses = self._get_star_lord_significations(planet, chart_data)
        significators['level_3'].extend(star_lord_houses)
        
        # Level 4: Sub lord's significations
        sub_lord_houses = self._get_sub_lord_significations(planet, chart_data)
        significators['level_4'].extend(sub_lord_houses)
        
        return significators
    
    def format_kp_significators(self, planet: str, significators: Dict) -> str:
        """Format significators in compact form."""
        all_houses = []
        
        # Combine all levels with priority
        for level in ['level_1', 'level_2', 'level_3', 'level_4']:
            all_houses.extend(significators[level])
        
        # Remove duplicates, keep order
        seen = set()
        unique_houses = []
        for h in all_houses:
            if h not in seen:
                seen.add(h)
                unique_houses.append(h)
        
        return ','.join(str(h) for h in unique_houses[:9])
```

### 4. Testing Against Original

```python
def test_cryptic_lines():
    """Test if our calculation matches the original cryptic lines."""
    
    # Original data
    original = {
        'ketu_dasa': [7, 8, 8, 5, 10, 3, 4, 11, 6],
        'guru_bukthi': [6, 9, 8, 6, 9, 8, 4, 11, 6],
        'sani_bukthi': [7, 8, 10, 7, 8, 8, 4, 11, 6],
        'sani_extra': [1, 8, 7],
        'buda_bukthi': [3, 12, 5, 7, 8, 10, 3, 12, 5],
        'buda_extra': [9, 12, 12],
        'rahu_antharam': [2, 5, 7, 8, 10, 5, 10, 3]
    }
    
    # Load test chart
    chart_data = load_test_chart('archana')
    
    # Calculate using our method
    calc = DasaResultsCalculator()
    
    # Verify Ketu dasa houses
    ketu_houses = calc.calculate_dasa_result_houses('Ketu', chart_data)
    assert ketu_houses == original['ketu_dasa'], f"Mismatch: {ketu_houses}"
    
    # Continue for other periods...
```

### 5. Documentation

```python
"""
Dasa Result Houses Interpretation:

The numbers represent houses that will be activated during the period:

1. First House - Self, personality, new beginnings
2. Second House - Wealth, family, speech
3. Third House - Siblings, courage, short travels
4. Fourth House - Mother, home, education, comfort
5. Fifth House - Children, intelligence, speculation
6. Sixth House - Enemies, disease, service
7. Seventh House - Marriage, partnerships, business
8. Eighth House - Transformation, occult, inheritance
9. Ninth House - Fortune, father, higher learning
10. Tenth House - Career, status, authority
11. Eleventh House - Gains, friends, aspirations
12. Twelfth House - Losses, spirituality, foreign

The sequence shows which life areas will be most active during each period.
"""
```

This implementation provides a framework for generating the cryptic dasa result lines, though the exact algorithm may need refinement based on the specific astrological school or software being replicated.