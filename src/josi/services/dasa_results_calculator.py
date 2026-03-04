"""
Dasa Results Calculator
Calculates house results for dasa-bhukti periods based on planetary positions and lordships
"""

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
        """Get houses owned by the planet based on ascendant."""
        # Get ascendant sign
        if 'ascendant' not in chart_data:
            return []
        
        asc_sign = chart_data['ascendant'].get('sign', 'Aries')
        
        # Sign to number mapping
        sign_to_num = {
            'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
            'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
            'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
        }
        
        # Planet ownership of signs
        sign_ownership = {
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
        
        asc_num = sign_to_num.get(asc_sign, 1)
        owned_signs = sign_ownership.get(planet, [])
        
        # Convert sign numbers to house numbers based on ascendant
        owned_houses = []
        for sign_num in owned_signs:
            house = ((sign_num - asc_num) % 12) + 1
            owned_houses.append(house)
        
        return owned_houses
    
    def _get_aspected_houses(self, planet: str, from_house: int, 
                            chart_data: Dict) -> List[int]:
        """Get houses aspected by the planet."""
        if not from_house:
            return []
        
        aspects = []
        
        # Full aspects (7th)
        aspects.append(((from_house - 1) + 6) % 12 + 1)
        
        # Special aspects
        if planet == 'Mars':
            aspects.extend([
                ((from_house - 1) + 3) % 12 + 1,  # 4th aspect
                ((from_house - 1) + 7) % 12 + 1   # 8th aspect
            ])
        elif planet == 'Jupiter':
            aspects.extend([
                ((from_house - 1) + 4) % 12 + 1,  # 5th aspect
                ((from_house - 1) + 8) % 12 + 1   # 9th aspect
            ])
        elif planet == 'Saturn':
            aspects.extend([
                ((from_house - 1) + 2) % 12 + 1,  # 3rd aspect
                ((from_house - 1) + 9) % 12 + 1   # 10th aspect
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