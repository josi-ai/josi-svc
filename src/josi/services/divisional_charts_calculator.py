"""
Divisional Charts (Varga) Calculator for Vedic Astrology

This module calculates various divisional charts used in Vedic astrology
for analyzing specific areas of life.
"""

from typing import Dict, List, Tuple
import math


class DivisionalChartsCalculator:
    """Calculate divisional charts (D-charts) for Vedic astrology."""
    
    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    def __init__(self):
        """Initialize the divisional charts calculator."""
        pass
    
    def calculate_all_vargas(self, planet_positions: Dict) -> Dict:
        """Calculate all major divisional charts."""
        vargas = {}
        
        # Calculate each divisional chart
        vargas['D1'] = self._format_rasi_chart(planet_positions)  # Rasi (main chart)
        vargas['D2'] = self.calculate_hora_chart(planet_positions)  # Wealth
        vargas['D3'] = self.calculate_drekkana_chart(planet_positions)  # Siblings
        vargas['D4'] = self.calculate_chaturthamsa_chart(planet_positions)  # Property
        vargas['D7'] = self.calculate_saptamsa_chart(planet_positions)  # Children
        vargas['D9'] = self.calculate_navamsa_chart(planet_positions)  # Spouse/Dharma
        vargas['D10'] = self.calculate_dasamsa_chart(planet_positions)  # Career
        vargas['D12'] = self.calculate_dwadasamsa_chart(planet_positions)  # Parents
        vargas['D16'] = self.calculate_shodasamsa_chart(planet_positions)  # Vehicles
        vargas['D20'] = self.calculate_vimsamsa_chart(planet_positions)  # Spiritual
        vargas['D24'] = self.calculate_chaturvimsamsa_chart(planet_positions)  # Education
        vargas['D27'] = self.calculate_saptavimsamsa_chart(planet_positions)  # Strength
        vargas['D30'] = self.calculate_trimsamsa_chart(planet_positions)  # Misfortunes
        vargas['D40'] = self.calculate_khavedamsa_chart(planet_positions)  # Auspicious
        vargas['D45'] = self.calculate_akshavedamsa_chart(planet_positions)  # General
        vargas['D60'] = self.calculate_shashtiamsa_chart(planet_positions)  # Past karma
        
        return vargas
    
    def _format_rasi_chart(self, planet_positions: Dict) -> Dict:
        """Format the main rasi chart (D1)."""
        chart = {sign: [] for sign in self.SIGNS}
        
        for planet, data in planet_positions.items():
            if 'sign' in data:
                chart[data['sign']].append(planet)
        
        return chart
    
    def calculate_navamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Navamsa (D9) - 9th harmonic chart.
        Most important divisional chart for marriage and dharma.
        """
        navamsa_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            
            # Each sign is divided into 9 parts of 3°20' each
            sign_position = longitude % 30
            navamsa_part = int(sign_position / 3.333333) + 1
            
            # Calculate which sign the navamsa falls in
            sign_num = int(longitude / 30)
            
            # Navamsa calculation based on element of sign
            # Fire signs (0,4,8): Count from Aries
            # Earth signs (1,5,9): Count from Capricorn  
            # Air signs (2,6,10): Count from Libra
            # Water signs (3,7,11): Count from Cancer
            
            if sign_num % 4 == 0:  # Fire signs
                navamsa_sign_num = (navamsa_part - 1) % 12
            elif sign_num % 4 == 1:  # Earth signs
                navamsa_sign_num = (9 + navamsa_part - 1) % 12
            elif sign_num % 4 == 2:  # Air signs
                navamsa_sign_num = (6 + navamsa_part - 1) % 12
            else:  # Water signs
                navamsa_sign_num = (3 + navamsa_part - 1) % 12
            
            # Calculate degree within navamsa sign
            navamsa_degree = (sign_position % 3.333333) * 9
            
            navamsa_positions[planet] = {
                'sign': self.SIGNS[navamsa_sign_num],
                'degree': round(navamsa_degree, 2),
                'longitude': navamsa_sign_num * 30 + navamsa_degree
            }
        
        return self._format_chart_by_sign(navamsa_positions)
    
    def calculate_hora_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Hora (D2) - For wealth analysis.
        Each sign divided into 2 parts of 15° each.
        """
        hora_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            sign_position = longitude % 30
            
            # First 15° goes to Sun's hora (Leo), second 15° to Moon's hora (Cancer)
            if sign_position < 15:
                hora_sign = "Leo"  # Sun's hora
            else:
                hora_sign = "Cancer"  # Moon's hora
            
            hora_positions[planet] = {
                'sign': hora_sign,
                'degree': sign_position % 15 * 2  # Expand to full sign
            }
        
        return self._format_chart_by_sign(hora_positions)
    
    def calculate_drekkana_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Drekkana (D3) - For siblings.
        Each sign divided into 3 parts of 10° each.
        """
        drekkana_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            sign_num = int(longitude / 30)
            sign_position = longitude % 30
            
            # Determine which third of the sign
            if sign_position < 10:
                # First drekkana - same sign
                drekkana_sign_num = sign_num
            elif sign_position < 20:
                # Second drekkana - 5th from current sign
                drekkana_sign_num = (sign_num + 4) % 12
            else:
                # Third drekkana - 9th from current sign
                drekkana_sign_num = (sign_num + 8) % 12
            
            drekkana_degree = (sign_position % 10) * 3
            
            drekkana_positions[planet] = {
                'sign': self.SIGNS[drekkana_sign_num],
                'degree': round(drekkana_degree, 2)
            }
        
        return self._format_chart_by_sign(drekkana_positions)
    
    def calculate_chaturthamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Chaturthamsa (D4) - For property and fixed assets.
        Each sign divided into 4 parts of 7°30' each.
        """
        chaturthamsa_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            sign_num = int(longitude / 30)
            sign_position = longitude % 30
            
            # Which quarter of the sign
            quarter = int(sign_position / 7.5)
            
            # Counting pattern: 1st same, 2nd 4th from, 3rd 7th from, 4th 10th from
            offsets = [0, 3, 6, 9]
            chaturthamsa_sign_num = (sign_num + offsets[quarter]) % 12
            
            chaturthamsa_degree = (sign_position % 7.5) * 4
            
            chaturthamsa_positions[planet] = {
                'sign': self.SIGNS[chaturthamsa_sign_num],
                'degree': round(chaturthamsa_degree, 2)
            }
        
        return self._format_chart_by_sign(chaturthamsa_positions)
    
    def calculate_saptamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Saptamsa (D7) - For children and progeny.
        Each sign divided into 7 parts of 4°17'8.57" each.
        """
        saptamsa_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            sign_num = int(longitude / 30)
            sign_position = longitude % 30
            
            # Which seventh of the sign
            seventh = int(sign_position / (30/7))
            
            # Odd signs count from same sign, even signs count from 7th sign
            if sign_num % 2 == 0:  # Odd sign (Aries is 0)
                saptamsa_sign_num = (sign_num + seventh) % 12
            else:  # Even sign
                saptamsa_sign_num = (sign_num + 6 + seventh) % 12
            
            saptamsa_degree = (sign_position % (30/7)) * 7
            
            saptamsa_positions[planet] = {
                'sign': self.SIGNS[saptamsa_sign_num],
                'degree': round(saptamsa_degree, 2)
            }
        
        return self._format_chart_by_sign(saptamsa_positions)
    
    def calculate_dasamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Dasamsa (D10) - For career and profession.
        Each sign divided into 10 parts of 3° each.
        """
        dasamsa_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            sign_num = int(longitude / 30)
            sign_position = longitude % 30
            
            # Which tenth of the sign
            tenth = int(sign_position / 3)
            
            # Odd signs count from same sign, even signs count from 9th sign
            if sign_num % 2 == 0:  # Odd sign
                dasamsa_sign_num = (sign_num + tenth) % 12
            else:  # Even sign
                dasamsa_sign_num = (sign_num + 8 + tenth) % 12
            
            dasamsa_degree = (sign_position % 3) * 10
            
            dasamsa_positions[planet] = {
                'sign': self.SIGNS[dasamsa_sign_num],
                'degree': round(dasamsa_degree, 2)
            }
        
        return self._format_chart_by_sign(dasamsa_positions)
    
    def calculate_dwadasamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Dwadasamsa (D12) - For parents and lineage.
        Each sign divided into 12 parts of 2°30' each.
        """
        dwadasamsa_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            sign_num = int(longitude / 30)
            sign_position = longitude % 30
            
            # Which twelfth of the sign
            twelfth = int(sign_position / 2.5)
            
            # Count from the same sign
            dwadasamsa_sign_num = (sign_num + twelfth) % 12
            
            dwadasamsa_degree = (sign_position % 2.5) * 12
            
            dwadasamsa_positions[planet] = {
                'sign': self.SIGNS[dwadasamsa_sign_num],
                'degree': round(dwadasamsa_degree, 2)
            }
        
        return self._format_chart_by_sign(dwadasamsa_positions)
    
    def calculate_shodasamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Shodasamsa (D16) - For vehicles and conveyances.
        Each sign divided into 16 parts.
        """
        return self._calculate_higher_harmonic(planet_positions, 16)
    
    def calculate_vimsamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Vimsamsa (D20) - For spiritual progress.
        Each sign divided into 20 parts.
        """
        return self._calculate_higher_harmonic(planet_positions, 20)
    
    def calculate_chaturvimsamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Chaturvimsamsa (D24) - For education and learning.
        Each sign divided into 24 parts.
        """
        return self._calculate_higher_harmonic(planet_positions, 24)
    
    def calculate_saptavimsamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Saptavimsamsa (D27) - For strengths and weaknesses.
        Each sign divided into 27 parts.
        """
        return self._calculate_higher_harmonic(planet_positions, 27)
    
    def calculate_trimsamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Trimsamsa (D30) - For misfortunes and evils.
        Special calculation - unequal divisions.
        """
        trimsamsa_positions = {}
        
        # Trimsamsa degrees for odd and even signs
        odd_degrees = [5, 10, 18, 25, 30]  # Mars, Saturn, Jupiter, Mercury, Venus
        odd_rulers = ["Mars", "Saturn", "Jupiter", "Mercury", "Venus"]
        even_degrees = [5, 12, 20, 25, 30]  # Venus, Mercury, Jupiter, Saturn, Mars
        even_rulers = ["Venus", "Mercury", "Jupiter", "Saturn", "Mars"]
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            sign_num = int(longitude / 30)
            sign_position = longitude % 30
            
            # Determine trimsamsa ruler based on degree
            if sign_num % 2 == 0:  # Odd sign
                degrees = odd_degrees
                rulers = odd_rulers
            else:  # Even sign
                degrees = even_degrees
                rulers = even_rulers
            
            # Find which section
            for i, deg in enumerate(degrees):
                if sign_position <= deg:
                    ruler = rulers[i]
                    # Trimsamsa signs are based on the ruler's signs
                    ruler_signs = {
                        "Mars": "Aries",
                        "Venus": "Taurus", 
                        "Mercury": "Gemini",
                        "Jupiter": "Sagittarius",
                        "Saturn": "Aquarius"
                    }
                    trimsamsa_sign = ruler_signs[ruler]
                    break
            
            trimsamsa_positions[planet] = {
                'sign': trimsamsa_sign,
                'ruler': ruler
            }
        
        return self._format_chart_by_sign(trimsamsa_positions)
    
    def calculate_khavedamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Khavedamsa (D40) - For auspicious and inauspicious effects.
        Each sign divided into 40 parts.
        """
        return self._calculate_higher_harmonic(planet_positions, 40)
    
    def calculate_akshavedamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Akshavedamsa (D45) - For all areas of life.
        Each sign divided into 45 parts.
        """
        return self._calculate_higher_harmonic(planet_positions, 45)
    
    def calculate_shashtiamsa_chart(self, planet_positions: Dict) -> Dict:
        """
        Calculate Shashtiamsa (D60) - For past karma and all matters.
        Each sign divided into 60 parts.
        """
        return self._calculate_higher_harmonic(planet_positions, 60)
    
    def _calculate_higher_harmonic(self, planet_positions: Dict, harmonic: int) -> Dict:
        """Generic method to calculate higher harmonic charts."""
        harmonic_positions = {}
        
        for planet, data in planet_positions.items():
            longitude = data.get('longitude', 0)
            
            # Multiply longitude by harmonic and reduce to 360
            harmonic_longitude = (longitude * harmonic) % 360
            
            sign_num = int(harmonic_longitude / 30)
            degree = harmonic_longitude % 30
            
            harmonic_positions[planet] = {
                'sign': self.SIGNS[sign_num],
                'degree': round(degree, 2)
            }
        
        return self._format_chart_by_sign(harmonic_positions)
    
    def _format_chart_by_sign(self, positions: Dict) -> Dict:
        """Format positions into a chart organized by sign."""
        chart = {sign: [] for sign in self.SIGNS}
        
        for planet, data in positions.items():
            if 'sign' in data:
                chart[data['sign']].append(planet)
        
        return chart
    
    def get_important_vargas(self, all_vargas: Dict) -> Dict:
        """Get the most important divisional charts for display."""
        important = {
            'D1': all_vargas.get('D1', {}),   # Rasi
            'D2': all_vargas.get('D2', {}),   # Hora
            'D3': all_vargas.get('D3', {}),   # Drekkana
            'D9': all_vargas.get('D9', {}),   # Navamsa
            'D10': all_vargas.get('D10', {}), # Dasamsa
            'D12': all_vargas.get('D12', {}), # Dwadasamsa
            'D30': all_vargas.get('D30', {})  # Trimsamsa
        }
        return important