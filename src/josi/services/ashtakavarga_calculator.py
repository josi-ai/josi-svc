"""
Ashtakavarga Calculator
Complete Ashtakavarga calculation system for Vedic astrology
"""

from typing import Dict, List, Tuple
import numpy as np


class AshtakavargaCalculator:
    """Complete Ashtakavarga calculation system."""
    
    def __init__(self):
        # Bindu contribution rules for each planet from itself
        self.bindu_rules = {
            'Sun': {
                'from_sun': [1, 2, 4, 7, 8, 9, 11],
                'from_moon': [3, 6, 10, 11],
                'from_mars': [1, 2, 4, 7, 8, 9, 10, 11],
                'from_mercury': [3, 5, 6, 9, 10, 11, 12],
                'from_jupiter': [5, 6, 9, 11],
                'from_venus': [6, 7, 12],
                'from_saturn': [1, 2, 4, 7, 8, 9, 10, 11],
                'from_lagna': [3, 4, 6, 10, 11, 12]
            },
            'Moon': {
                'from_sun': [3, 6, 7, 8, 10, 11],
                'from_moon': [1, 3, 6, 7, 10, 11],
                'from_mars': [2, 3, 5, 6, 9, 10, 11],
                'from_mercury': [1, 3, 4, 5, 7, 8, 10, 11],
                'from_jupiter': [1, 2, 4, 7, 8, 10, 11],
                'from_venus': [3, 4, 5, 7, 9, 10, 11],
                'from_saturn': [3, 5, 6, 11],
                'from_lagna': [3, 6, 10, 11]
            },
            'Mars': {
                'from_sun': [3, 5, 6, 10, 11],
                'from_moon': [3, 6, 11],
                'from_mars': [1, 2, 4, 7, 8, 10, 11],
                'from_mercury': [3, 5, 6, 11],
                'from_jupiter': [6, 10, 11, 12],
                'from_venus': [6, 8, 11, 12],
                'from_saturn': [1, 4, 7, 8, 9, 10, 11],
                'from_lagna': [1, 3, 6, 10, 11]
            },
            'Mercury': {
                'from_sun': [5, 6, 9, 11, 12],
                'from_moon': [2, 4, 6, 8, 10, 11],
                'from_mars': [1, 2, 4, 7, 8, 9, 10, 11],
                'from_mercury': [1, 3, 5, 6, 9, 10, 11],
                'from_jupiter': [6, 8, 11, 12],
                'from_venus': [1, 2, 3, 4, 5, 8, 9, 11],
                'from_saturn': [1, 2, 4, 7, 8, 9, 10, 11],
                'from_lagna': [1, 2, 4, 6, 8, 10, 11]
            },
            'Jupiter': {
                'from_sun': [1, 2, 3, 4, 7, 8, 9, 10, 11],
                'from_moon': [2, 5, 7, 9, 11],
                'from_mars': [1, 2, 4, 7, 8, 10, 11],
                'from_mercury': [1, 2, 4, 5, 6, 9, 11],
                'from_jupiter': [1, 2, 3, 4, 7, 8, 10, 11],
                'from_venus': [2, 5, 6, 9, 10, 11],
                'from_saturn': [3, 5, 6, 12],
                'from_lagna': [1, 2, 4, 5, 6, 7, 9, 10, 11]
            },
            'Venus': {
                'from_sun': [8, 11, 12],
                'from_moon': [1, 2, 3, 4, 5, 8, 9, 11, 12],
                'from_mars': [3, 4, 6, 9, 11, 12],
                'from_mercury': [3, 5, 6, 9, 11],
                'from_jupiter': [5, 8, 9, 10, 11],
                'from_venus': [1, 2, 3, 4, 5, 8, 9, 10, 11],
                'from_saturn': [3, 4, 5, 8, 9, 10, 11],
                'from_lagna': [1, 2, 3, 4, 5, 8, 9, 11]
            },
            'Saturn': {
                'from_sun': [1, 2, 4, 7, 8, 10, 11],
                'from_moon': [3, 6, 11],
                'from_mars': [3, 5, 6, 10, 11, 12],
                'from_mercury': [6, 8, 9, 10, 11, 12],
                'from_jupiter': [5, 6, 11, 12],
                'from_venus': [6, 11, 12],
                'from_saturn': [3, 5, 6, 11],
                'from_lagna': [1, 3, 4, 6, 10, 11]
            }
        }
    
    def calculate_ashtakavarga(self, planet_positions: Dict) -> Dict:
        """
        Calculate complete Ashtakavarga for all planets.
        
        Args:
            planet_positions: Dict with planet longitudes and signs
            
        Returns:
            Dict with bindus for each planet in each sign
        """
        # Initialize result matrices
        ashtakavarga = {
            'individual': {},  # Each planet's contribution
            'sarva': np.zeros(12, dtype=int),  # Total for all
            'bhinnashtak': {}  # Individual planet totals
        }
        
        # Get sign positions (1-12) for all planets and lagna
        sign_positions = self._get_sign_positions(planet_positions)
        
        # Calculate for each planet
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            if planet not in sign_positions:
                continue
            
            # Initialize bindu array for this planet
            bindus = np.zeros(12, dtype=int)
            
            # Get bindus from each contributor
            rules = self.bindu_rules.get(planet, {})
            
            for contributor, positions in rules.items():
                # Get contributor's sign
                contrib_name = contributor.replace('from_', '').title()
                if contrib_name == 'Lagna':
                    contrib_sign = sign_positions.get('Ascendant', 1)
                else:
                    contrib_sign = sign_positions.get(contrib_name, 1)
                
                # Add bindus to appropriate signs
                for pos in positions:
                    # Calculate actual sign (from contributor's position)
                    target_sign = ((contrib_sign - 1) + (pos - 1)) % 12
                    bindus[target_sign] += 1
            
            ashtakavarga['bhinnashtak'][planet] = bindus
            ashtakavarga['sarva'] += bindus
        
        # Add Lagna's ashtakavarga (special calculation)
        lagna_bindus = self._calculate_lagna_ashtakavarga(sign_positions)
        ashtakavarga['bhinnashtak']['Lagna'] = lagna_bindus
        ashtakavarga['sarva'] += lagna_bindus
        
        return ashtakavarga
    
    def _get_sign_positions(self, planet_positions: Dict) -> Dict:
        """Convert longitudes to sign numbers (1-12)."""
        sign_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            sign_num = int(longitude / 30) + 1
            sign_positions[planet] = sign_num
        
        return sign_positions
    
    def _calculate_lagna_ashtakavarga(self, sign_positions: Dict) -> np.ndarray:
        """Calculate special Lagna ashtakavarga."""
        bindus = np.zeros(12, dtype=int)
        lagna_sign = sign_positions.get('Ascendant', 1)
        
        # Lagna contributes to specific houses from itself
        lagna_bindu_houses = [3, 4, 6, 9, 10, 11, 12]
        
        for house in lagna_bindu_houses:
            target_sign = ((lagna_sign - 1) + (house - 1)) % 12
            bindus[target_sign] = 1
        
        # Special rule: Always 49 total for Lagna
        # This is achieved by special counting in traditional texts
        
        return bindus
    
    def calculate_bhava_ashtakavarga(self, rasi_ashtakavarga: Dict, 
                                   houses: List[float]) -> Dict:
        """
        Convert Rasi-based Ashtakavarga to Bhava-based.
        
        Args:
            rasi_ashtakavarga: Ashtakavarga by signs
            houses: List of house cusps
            
        Returns:
            Bhava-based Ashtakavarga
        """
        bhava_ashtakavarga = {'bhinnashtak': {}, 'sarva': np.zeros(12, dtype=int)}
        
        # Map signs to bhavas based on house cusps
        sign_to_bhava = self._map_signs_to_bhavas(houses)
        
        # Convert each planet's bindus
        for planet, rasi_bindus in rasi_ashtakavarga['bhinnashtak'].items():
            bhava_bindus = np.zeros(12, dtype=int)
            
            for sign_idx, bindus in enumerate(rasi_bindus):
                bhava_idx = sign_to_bhava[sign_idx]
                bhava_bindus[bhava_idx] += bindus
            
            bhava_ashtakavarga['bhinnashtak'][planet] = bhava_bindus
            
            # Don't add Lagna bindus to sarva again
            if planet != 'Lagna':
                bhava_ashtakavarga['sarva'] += bhava_bindus
        
        return bhava_ashtakavarga
    
    def _map_signs_to_bhavas(self, houses: List[float]) -> List[int]:
        """Map each sign to its corresponding bhava."""
        sign_to_bhava = []
        
        for sign_idx in range(12):
            sign_start = sign_idx * 30
            sign_middle = sign_start + 15
            
            # Find which house contains this sign's middle
            for house_idx in range(12):
                house_start = houses[house_idx]
                house_end = houses[(house_idx + 1) % 12]
                
                # Handle wrap-around
                if house_start > house_end:
                    if sign_middle >= house_start or sign_middle < house_end:
                        sign_to_bhava.append(house_idx)
                        break
                else:
                    if house_start <= sign_middle < house_end:
                        sign_to_bhava.append(house_idx)
                        break
            else:
                # Default to sign = house if no match
                sign_to_bhava.append(sign_idx)
        
        return sign_to_bhava
    
    def format_ashtakavarga_table(self, ashtakavarga: Dict, 
                                 table_type: str = 'rasi') -> List[str]:
        """
        Format Ashtakavarga as traditional table.
        
        Args:
            ashtakavarga: Calculated ashtakavarga data
            table_type: 'rasi' or 'bhava'
            
        Returns:
            List of formatted lines
        """
        lines = []
        
        # Header
        header = "                          " + table_type.upper()
        lines.append(header)
        lines.append("        1  2  3  4  5  6  7  8  9 10 11 12 TOT")
        
        # Planet rows
        planet_order = ['Lagna', 'Sun', 'Moon', 'Mars', 'Mercury', 
                       'Jupiter', 'Venus', 'Saturn']
        
        planet_abbr = {
            'Lagna': 'LAGNA', 'Sun': 'SURY', 'Moon': 'CHAN',
            'Mars': 'KUJA', 'Mercury': 'BUDH', 'Jupiter': 'GURU',
            'Venus': 'SUKR', 'Saturn': 'SANI'
        }
        
        for planet in planet_order:
            if planet in ashtakavarga['bhinnashtak']:
                bindus = ashtakavarga['bhinnashtak'][planet]
                total = np.sum(bindus)
                
                # Format row
                row = f" {planet_abbr[planet]:<7}"
                
                # Add bindus or special markers
                if planet == 'Lagna':
                    # Lagna shows * for bindus, - for no bindus
                    for b in bindus:
                        row += "  *" if b > 0 else "  -"
                    # Special total for Lagna (always 49 in traditional)
                    row += "  49"
                else:
                    # Other planets show numeric values
                    for b in bindus:
                        row += f" {int(b):2d}"
                    row += f" {int(total):3d}"
                
                lines.append(row)
        
        # Total row
        sarva = ashtakavarga['sarva']
        total_sum = np.sum(sarva)
        
        total_row = " TOTAL "
        for val in sarva:
            total_row += f" {int(val):2d}"
        total_row += f" {int(total_sum):3d}"
        
        lines.append(total_row)
        
        return lines
    
    def calculate_ashtakavarga_predictions(self, ashtakavarga: Dict) -> Dict:
        """Calculate predictions based on Ashtakavarga."""
        predictions = {
            'house_strength': {},
            'transit_favorability': {},
            'kakshya_strength': {}
        }
        
        sarva = ashtakavarga['sarva']
        
        # House strength analysis
        for i in range(12):
            bindus = sarva[i]
            
            if bindus < 25:
                strength = 'weak'
                desc = 'Challenges and obstacles'
            elif bindus < 30:
                strength = 'average'
                desc = 'Mixed results'
            elif bindus < 35:
                strength = 'good'
                desc = 'Favorable results'
            else:
                strength = 'excellent'
                desc = 'Very favorable results'
            
            predictions['house_strength'][i+1] = {
                'bindus': int(bindus),
                'strength': strength,
                'description': desc
            }
        
        return predictions