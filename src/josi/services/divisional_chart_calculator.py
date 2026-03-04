# src/josi/services/divisional_chart_calculator.py

from typing import Dict, List, Optional
import math

class DivisionalChartCalculator:
    """
    Calculate all divisional charts (D1-D60) based on VedAstro methodology.
    
    This implementation follows traditional Vedic astrology rules where each
    sign is divided into specific portions for different divisional charts.
    """
    
    def __init__(self):
        # Divisional chart definitions
        self.divisions = {
            'D1': 1,    # Rasi (Birth Chart)
            'D2': 2,    # Hora (Wealth)
            'D3': 3,    # Drekkana (Siblings)
            'D4': 4,    # Chaturthamsa (Property)
            'D5': 5,    # Panchamsa (Progeny)
            'D6': 6,    # Shashtamsa (Health)
            'D7': 7,    # Saptamsa (Children)
            'D8': 8,    # Ashtamsa (Longevity)
            'D9': 9,    # Navamsa (Marriage/Dharma)
            'D10': 10,  # Dasamsa (Career)
            'D11': 11,  # Rudramsa (Death/Destruction)
            'D12': 12,  # Dwadasamsa (Parents)
            'D16': 16,  # Shodasamsa (Vehicles)
            'D20': 20,  # Vimsamsa (Spiritual Progress)
            'D24': 24,  # Chaturvimsamsa (Education)
            'D27': 27,  # Nakshatramsa (Strengths/Weaknesses)
            'D30': 30,  # Trimsamsa (Misfortunes)
            'D40': 40,  # Khavedamsa (Maternal Legacy)
            'D45': 45,  # Akshavedamsa (Paternal Legacy)
            'D60': 60   # Shashtiamsa (Past Karma)
        }
        
        # Zodiac signs
        self.signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer',
            'Leo', 'Virgo', 'Libra', 'Scorpio',
            'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        # Sign elements for special calculations
        self.sign_elements = {
            0: 'Fire', 4: 'Fire', 8: 'Fire',      # Aries, Leo, Sagittarius
            1: 'Earth', 5: 'Earth', 9: 'Earth',   # Taurus, Virgo, Capricorn
            2: 'Air', 6: 'Air', 10: 'Air',        # Gemini, Libra, Aquarius
            3: 'Water', 7: 'Water', 11: 'Water'   # Cancer, Scorpio, Pisces
        }
    
    def get_sign_name(self, index: int) -> str:
        """Get sign name from index (0-11)."""
        return self.signs[index % 12]
    
    def calculate_all_vargas(self, longitude: float) -> Dict[str, Dict]:
        """
        Calculate position in all divisional charts for a given longitude.
        
        Args:
            longitude: Sidereal longitude in degrees (0-360)
            
        Returns:
            Dictionary with divisional chart positions
        """
        vargas = {}
        
        for division_name, division_number in self.divisions.items():
            if division_number == 9:
                # Special calculation for Navamsa
                vargas[division_name] = self.calculate_navamsa(longitude)
            elif division_number == 2:
                # Special calculation for Hora
                vargas[division_name] = self.calculate_hora(longitude)
            elif division_number == 3:
                # Special calculation for Drekkana
                vargas[division_name] = self.calculate_drekkana(longitude)
            elif division_number == 30:
                # Special calculation for Trimsamsa
                vargas[division_name] = self.calculate_trimsamsa(longitude)
            else:
                # Standard cyclic calculation
                vargas[division_name] = self.calculate_divisional_position(longitude, division_number)
        
        return vargas
    
    def calculate_divisional_position(self, longitude: float, division: int) -> Dict:
        """
        Calculate position in divisional chart using standard cyclic method.
        
        Args:
            longitude: Sidereal longitude in degrees (0-360)
            division: Division number (e.g., 9 for Navamsa)
            
        Returns:
            Dictionary with sign, degrees, and longitude in divisional chart
        """
        # Each sign is 30 degrees
        sign_index = int(longitude / 30)
        degrees_in_sign = longitude % 30
        
        # Calculate which division of the sign
        division_size = 30.0 / division
        division_index = int(degrees_in_sign / division_size)
        
        # Calculate the new sign based on division rules
        # This follows the cyclic pattern used in traditional astrology
        new_sign_index = (sign_index * division + division_index) % 12
        
        # Calculate degrees in the new sign
        degrees_in_division = (degrees_in_sign % division_size) * division
        
        return {
            'sign_index': new_sign_index,
            'sign': self.get_sign_name(new_sign_index),
            'degrees': degrees_in_division,
            'longitude': new_sign_index * 30 + degrees_in_division
        }
    
    def calculate_navamsa(self, longitude: float) -> Dict:
        """
        Calculate Navamsa (D9) position with special rules.
        
        Each sign divided into 9 parts of 3°20' each.
        Starting points based on sign element:
        - Fire signs start from Aries
        - Earth signs start from Capricorn
        - Air signs start from Libra
        - Water signs start from Cancer
        """
        sign_index = int(longitude / 30)
        degrees_in_sign = longitude % 30
        
        # Each navamsa is 3°20' (3.333... degrees)
        navamsa_size = 30.0 / 9
        navamsa_index = int(degrees_in_sign / navamsa_size)
        
        # Starting points based on sign element
        element = sign_index % 4
        start_signs = {
            0: 0,   # Fire -> Aries (0)
            1: 9,   # Earth -> Capricorn (9)
            2: 6,   # Air -> Libra (6)
            3: 3    # Water -> Cancer (3)
        }
        
        new_sign_index = (start_signs[element] + navamsa_index) % 12
        degrees_in_navamsa = (degrees_in_sign % navamsa_size) * 9
        
        return {
            'sign_index': new_sign_index,
            'sign': self.get_sign_name(new_sign_index),
            'degrees': degrees_in_navamsa,
            'longitude': new_sign_index * 30 + degrees_in_navamsa
        }
    
    def calculate_hora(self, longitude: float) -> Dict:
        """
        Calculate Hora (D2) chart position.
        
        Special rules:
        - Odd signs: First 15° -> Leo, Last 15° -> Cancer
        - Even signs: First 15° -> Cancer, Last 15° -> Leo
        """
        sign_index = int(longitude / 30)
        degrees_in_sign = longitude % 30
        
        if sign_index % 2 == 0:  # Odd sign (0-indexed)
            new_sign_index = 4 if degrees_in_sign < 15 else 3  # Leo : Cancer
        else:  # Even sign
            new_sign_index = 3 if degrees_in_sign < 15 else 4  # Cancer : Leo
        
        degrees_in_hora = (degrees_in_sign % 15) * 2
        
        return {
            'sign_index': new_sign_index,
            'sign': self.get_sign_name(new_sign_index),
            'degrees': degrees_in_hora,
            'longitude': new_sign_index * 30 + degrees_in_hora
        }
    
    def calculate_drekkana(self, longitude: float) -> Dict:
        """
        Calculate Drekkana (D3) chart position.
        
        Each sign divided into 3 parts of 10° each:
        - 1st part: Same sign
        - 2nd part: 5th sign from it
        - 3rd part: 9th sign from it
        """
        sign_index = int(longitude / 30)
        degrees_in_sign = longitude % 30
        
        drekkana_index = int(degrees_in_sign / 10)
        
        if drekkana_index == 0:
            new_sign_index = sign_index
        elif drekkana_index == 1:
            new_sign_index = (sign_index + 4) % 12  # 5th sign
        else:
            new_sign_index = (sign_index + 8) % 12  # 9th sign
        
        degrees_in_drekkana = (degrees_in_sign % 10) * 3
        
        return {
            'sign_index': new_sign_index,
            'sign': self.get_sign_name(new_sign_index),
            'degrees': degrees_in_drekkana,
            'longitude': new_sign_index * 30 + degrees_in_drekkana
        }
    
    def calculate_trimsamsa(self, longitude: float) -> Dict:
        """
        Calculate Trimsamsa (D30) chart position.
        
        Special distribution based on odd/even signs:
        - Different degree ranges ruled by different planets
        """
        sign_index = int(longitude / 30)
        degrees_in_sign = longitude % 30
        
        # Trimsamsa distribution for odd signs
        odd_distribution = [
            (5, 0),    # 0-5° -> Aries
            (10, 10),  # 5-10° -> Aquarius
            (18, 8),   # 10-18° -> Sagittarius
            (25, 2),   # 18-25° -> Gemini
            (30, 6)    # 25-30° -> Libra
        ]
        
        # Trimsamsa distribution for even signs
        even_distribution = [
            (5, 1),    # 0-5° -> Taurus
            (12, 5),   # 5-12° -> Virgo
            (20, 2),   # 12-20° -> Gemini
            (25, 8),   # 20-25° -> Sagittarius
            (30, 9)    # 25-30° -> Capricorn
        ]
        
        distribution = odd_distribution if sign_index % 2 == 0 else even_distribution
        
        new_sign_index = 0
        for limit, sign in distribution:
            if degrees_in_sign <= limit:
                new_sign_index = sign
                break
        
        # Simple degree calculation for Trimsamsa
        degrees_in_trimsamsa = degrees_in_sign
        
        return {
            'sign_index': new_sign_index,
            'sign': self.get_sign_name(new_sign_index),
            'degrees': degrees_in_trimsamsa,
            'longitude': new_sign_index * 30 + degrees_in_trimsamsa
        }
    
    def get_varga_chart(self, planet_positions: Dict[str, float], division_name: str) -> Dict[str, Dict]:
        """
        Calculate divisional chart positions for all planets.
        
        Args:
            planet_positions: Dictionary of planet names to longitudes
            division_name: Name of divisional chart (e.g., 'D9')
            
        Returns:
            Dictionary of planet positions in the divisional chart
        """
        if division_name not in self.divisions:
            raise ValueError(f"Unknown divisional chart: {division_name}")
        
        division_number = self.divisions[division_name]
        varga_positions = {}
        
        for planet_name, longitude in planet_positions.items():
            if division_name == 'D9':
                varga_positions[planet_name] = self.calculate_navamsa(longitude)
            elif division_name == 'D2':
                varga_positions[planet_name] = self.calculate_hora(longitude)
            elif division_name == 'D3':
                varga_positions[planet_name] = self.calculate_drekkana(longitude)
            elif division_name == 'D30':
                varga_positions[planet_name] = self.calculate_trimsamsa(longitude)
            else:
                varga_positions[planet_name] = self.calculate_divisional_position(
                    longitude, division_number
                )
        
        return varga_positions