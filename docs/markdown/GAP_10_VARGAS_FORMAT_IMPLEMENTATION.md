# Gap 10: Vargas Display Format Implementation Plan

## Overview
Implement traditional Vargas (divisional charts) display format with Sanskrit sign names.

**Original Format**:
```
VARGAS     D2  D3  D4  D5  D6  D7  D8  D9 D10 D11 D12 D16 D20 D24 D27 D30 D40 D45 D60
LAGNA      3   9   3   6   4   4   4   2  11   8   7   7   6  11   5   2   2   3   1
SURY       11  3   11  8   10  10  2   9  2    11  1   7   5   1   10  11  7   8   11
CHAN       4   8   4   2   2   2   2   3  5    2   2   10  5   10  1   6   6   1   6
KUJA       10  10  10  2   4   10  2   1  1    6   2   6   2   10  7   10  2   3   10
BUDH       12  4   12  10  12  12  4   4  4    12  1   4   7   1   11  3   12  12  11
GURU       7   7   7   8   3   11  7   6  6    7   9   3   8   4   7   5   11  12  7
SUKR       10  2   10  7   9   9   11  1  10   7   11  11  2   6   4   3   11  1   7
SANI       11  7   11  2   3   11  11  10 11   9   11  11  11  3   10  10  3   4   6
RAHU       9   9   9   9   9   9   9   9  9    9   9   9   9   9   9   9   9   9   9
KETU       3   3   3   3   3   3   3   3  3    3   3   3   3   3   3   3   3   3   3
```

**Current Format**: Shows sign names in English

## Understanding Vargas Format

### Sanskrit Sign Names
1. मेष (Mesha) - Aries - 1
2. वृष (Vrisha) - Taurus - 2  
3. मिथुन (Mithuna) - Gemini - 3
4. कर्क (Karka) - Cancer - 4
5. सिंह (Simha) - Leo - 5
6. कन्या (Kanya) - Virgo - 6
7. तुला (Tula) - Libra - 7
8. वृश्चिक (Vrischika) - Scorpio - 8
9. धनु (Dhanu) - Sagittarius - 9
10. मकर (Makara) - Capricorn - 10
11. कुम्भ (Kumbha) - Aquarius - 11
12. मीन (Meena) - Pisces - 12

### Display Options
1. **Numeric**: 1-12 (most compact)
2. **Sanskrit**: Using sign abbreviations
3. **English**: Full sign names
4. **Symbols**: Zodiac symbols

## Implementation Steps

### 1. Create Vargas Formatter

```python
# src/josi/services/vargas_formatter.py

from typing import Dict, List, Optional
import unicodedata

class VargasFormatter:
    """Format divisional charts in traditional style."""
    
    def __init__(self):
        # Sign mappings
        self.sign_numbers = {
            'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
            'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
            'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
        }
        
        # Sanskrit sign names (transliterated)
        self.sanskrit_signs = {
            1: 'Mesh', 2: 'Vrish', 3: 'Mithun', 4: 'Kark',
            5: 'Simh', 6: 'Kanya', 7: 'Tula', 8: 'Vrisch',
            9: 'Dhanu', 10: 'Makar', 11: 'Kumbh', 12: 'Meen'
        }
        
        # Short forms (3 chars)
        self.sign_short = {
            1: 'ARI', 2: 'TAU', 3: 'GEM', 4: 'CAN',
            5: 'LEO', 6: 'VIR', 7: 'LIB', 8: 'SCO',
            9: 'SAG', 10: 'CAP', 11: 'AQU', 12: 'PIS'
        }
        
        # Varga names and order
        self.varga_order = [
            'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9',
            'D10', 'D11', 'D12', 'D16', 'D20', 'D24', 'D27',
            'D30', 'D40', 'D45', 'D60'
        ]
        
        # Planet display order
        self.planet_order = [
            'Ascendant', 'Sun', 'Moon', 'Mars', 'Mercury',
            'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'
        ]
        
        # Planet abbreviations
        self.planet_abbr = {
            'Ascendant': 'LAGNA', 'Sun': 'SURY', 'Moon': 'CHAN',
            'Mars': 'KUJA', 'Mercury': 'BUDH', 'Jupiter': 'GURU',
            'Venus': 'SUKR', 'Saturn': 'SANI', 'Rahu': 'RAHU', 'Ketu': 'KETU'
        }
    
    def format_vargas_table(self, vargas_data: Dict, 
                          format_type: str = 'numeric') -> List[str]:
        """
        Format vargas in traditional table format.
        
        Args:
            vargas_data: Dict with varga calculations
            format_type: 'numeric', 'sanskrit', 'english', 'short'
            
        Returns:
            List of formatted lines
        """
        lines = []
        
        # Header line with varga names
        header = "VARGAS    "
        for varga in self.varga_order:
            if varga in vargas_data:
                header += f" {varga:>3}"
        lines.append(header)
        
        # Process each planet
        for planet in self.planet_order:
            if planet not in vargas_data.get('D1', {}):
                continue
            
            # Start line with planet name
            line = f"{self.planet_abbr[planet]:<10}"
            
            # Add varga positions
            for varga in self.varga_order:
                if varga not in vargas_data:
                    line += "   -"
                    continue
                
                varga_data = vargas_data[varga]
                if planet in varga_data:
                    sign = varga_data[planet].get('sign', '')
                    
                    # Convert to desired format
                    if format_type == 'numeric':
                        sign_num = self.sign_numbers.get(sign, 0)
                        line += f" {sign_num:>3}" if sign_num else "   -"
                    elif format_type == 'sanskrit':
                        sign_num = self.sign_numbers.get(sign, 0)
                        sanskrit = self.sanskrit_signs.get(sign_num, '-')
                        line += f" {sanskrit[:3]:>3}"
                    elif format_type == 'short':
                        sign_num = self.sign_numbers.get(sign, 0)
                        short = self.sign_short.get(sign_num, '-')
                        line += f" {short:>3}"
                    else:  # english
                        line += f" {sign[:3]:>3}"
                else:
                    line += "   -"
            
            lines.append(line)
        
        return lines
    
    def format_single_varga(self, varga_name: str, varga_data: Dict,
                          include_degrees: bool = False) -> List[str]:
        """
        Format a single varga chart in detail.
        
        Args:
            varga_name: Name of the varga (e.g., 'D9')
            varga_data: Positions in this varga
            include_degrees: Whether to show degrees within sign
            
        Returns:
            List of formatted lines
        """
        lines = []
        
        # Header
        varga_full_names = {
            'D1': 'RASI', 'D2': 'HORA', 'D3': 'DREKKANA', 'D4': 'CHATURTHAMSA',
            'D5': 'PANCHAMSA', 'D6': 'SHASHTAMSA', 'D7': 'SAPTAMSA', 'D8': 'ASHTAMSA',
            'D9': 'NAVAMSA', 'D10': 'DASAMSA', 'D11': 'RUDRAMSA', 'D12': 'DWADASAMSA',
            'D16': 'SHODASAMSA', 'D20': 'VIMSAMSA', 'D24': 'CHATURVIMSAMSA',
            'D27': 'NAKSHATRAMSA', 'D30': 'TRIMSAMSA', 'D40': 'KHAVEDAMSA',
            'D45': 'AKSHAVEDAMSA', 'D60': 'SHASHTIAMSA'
        }
        
        full_name = varga_full_names.get(varga_name, varga_name)
        lines.append(f"{full_name} CHART ({varga_name})")
        lines.append("-" * 40)
        
        # Planet positions
        for planet in self.planet_order:
            if planet not in varga_data:
                continue
            
            data = varga_data[planet]
            sign = data.get('sign', '')
            sign_num = self.sign_numbers.get(sign, 0)
            
            line = f"{self.planet_abbr[planet]:<8}"
            
            # Add sign in multiple formats
            if sign_num:
                line += f" {sign_num:>2}"
                line += f" {self.sanskrit_signs[sign_num]:<7}"
                line += f" {sign:<12}"
                
                if include_degrees and 'longitude' in data:
                    deg_in_sign = data['longitude'] % 30
                    line += f" {deg_in_sign:>6.2f}°"
            
            lines.append(line)
        
        return lines
    
    def create_compressed_vargas_view(self, vargas_data: Dict) -> List[str]:
        """
        Create a compressed view showing essential vargas only.
        
        Shows: D1, D9, D3, D12, D30, D60
        """
        lines = []
        essential_vargas = ['D1', 'D9', 'D3', 'D12', 'D30', 'D60']
        
        # Header
        header = "PLANET    RASI  NAVAMSA DREKKANA DWADASAMSA TRIMSAMSA SHASHTIAMSA"
        lines.append(header)
        lines.append("-" * len(header))
        
        for planet in self.planet_order:
            line = f"{self.planet_abbr[planet]:<10}"
            
            for varga in essential_vargas:
                if varga in vargas_data and planet in vargas_data[varga]:
                    sign = vargas_data[varga][planet].get('sign', '')
                    sign_num = self.sign_numbers.get(sign, 0)
                    
                    if varga == 'D1':
                        # Show sign name for Rasi
                        line += f"{sign[:4]:<5}"
                    else:
                        # Show number for others
                        line += f"{sign_num:>3}  "
                else:
                    line += "  -  "
            
            lines.append(line)
        
        return lines
    
    def calculate_varga_bala(self, vargas_data: Dict) -> Dict:
        """
        Calculate Varga Bala (strength in divisional charts).
        
        Based on dignity in each varga.
        """
        varga_bala = {}
        
        # Dignity points
        dignity_points = {
            'own_sign': 3.0,
            'exaltation': 2.5,
            'friend': 2.0,
            'neutral': 1.5,
            'enemy': 1.0,
            'debilitation': 0.5
        }
        
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            total_points = 0
            varga_count = 0
            
            for varga in self.varga_order:
                if varga in vargas_data and planet in vargas_data[varga]:
                    dignity = self._get_planet_dignity(
                        planet, vargas_data[varga][planet].get('sign', '')
                    )
                    total_points += dignity_points.get(dignity, 1.0)
                    varga_count += 1
            
            if varga_count > 0:
                varga_bala[planet] = round(total_points / varga_count, 2)
        
        return varga_bala
    
    def _get_planet_dignity(self, planet: str, sign: str) -> str:
        """Determine planet's dignity in a sign."""
        # Simplified dignity calculation
        own_signs = {
            'Sun': ['Leo'],
            'Moon': ['Cancer'],
            'Mars': ['Aries', 'Scorpio'],
            'Mercury': ['Gemini', 'Virgo'],
            'Jupiter': ['Sagittarius', 'Pisces'],
            'Venus': ['Taurus', 'Libra'],
            'Saturn': ['Capricorn', 'Aquarius']
        }
        
        exaltation = {
            'Sun': 'Aries',
            'Moon': 'Taurus',
            'Mars': 'Capricorn',
            'Mercury': 'Virgo',
            'Jupiter': 'Cancer',
            'Venus': 'Pisces',
            'Saturn': 'Libra'
        }
        
        if sign in own_signs.get(planet, []):
            return 'own_sign'
        elif sign == exaltation.get(planet):
            return 'exaltation'
        # Add friend/enemy logic
        else:
            return 'neutral'
    
    def format_special_vargas(self, vargas_data: Dict) -> Dict:
        """
        Format special vargas with additional information.
        
        D9 - Marriage and dharma
        D10 - Career 
        D12 - Parents
        D24 - Education
        D27 - Strengths and weaknesses
        """
        special_formats = {}
        
        # D9 Special format
        if 'D9' in vargas_data:
            d9_lines = ["NAVAMSA (D9) - Marriage & Dharma"]
            d9_lines.append("=" * 40)
            
            # Check navamsa lagna lord
            asc_sign = vargas_data['D9'].get('Ascendant', {}).get('sign', '')
            d9_lines.append(f"Navamsa Lagna: {asc_sign}")
            
            # Check 7th house
            # Add marriage timing indicators
            
            special_formats['D9'] = d9_lines
        
        # D10 Special format
        if 'D10' in vargas_data:
            d10_lines = ["DASAMSA (D10) - Career & Status"]
            d10_lines.append("=" * 40)
            
            # Career indicators
            # 10th lord position
            
            special_formats['D10'] = d10_lines
        
        return special_formats
```

### 2. Integration with Export

Update `generate_josi_traditional_export.py`:

```python
# Import formatter
from src.josi.services.vargas_formatter import VargasFormatter

def add_vargas_table(lines: List[str], chart: Dict):
    """Add formatted vargas table."""
    
    if not chart.get('vargas'):
        lines.append("")
        lines.append("VARGAS: [CALCULATION PENDING]")
        return
    
    formatter = VargasFormatter()
    
    # Add section header
    lines.append("")
    
    # Format main vargas table in numeric format
    vargas_lines = formatter.format_vargas_table(
        chart['vargas'], 
        format_type='numeric'
    )
    lines.extend(vargas_lines)
    
    # Optionally add compressed view
    lines.append("")
    compressed_lines = formatter.create_compressed_vargas_view(chart['vargas'])
    lines.extend(compressed_lines)

# In main export function
add_vargas_table(lines, chart)
```

### 3. Sanskrit Display Options

```python
class SanskritVargasDisplay:
    """Display vargas with Sanskrit/Devanagari text."""
    
    def __init__(self):
        # Devanagari sign names
        self.devanagari_signs = {
            1: 'मेष', 2: 'वृष', 3: 'मिथुन', 4: 'कर्क',
            5: 'सिंह', 6: 'कन्या', 7: 'तुला', 8: 'वृश्चिक',
            9: 'धनु', 10: 'मकर', 11: 'कुम्भ', 12: 'मीन'
        }
        
        # Varga names in Sanskrit
        self.sanskrit_varga_names = {
            'D1': 'राशि', 'D2': 'होरा', 'D3': 'द्रेक्काण',
            'D4': 'चतुर्थांश', 'D5': 'पंचमांश', 'D6': 'षष्ठांश',
            'D7': 'सप्तमांश', 'D8': 'अष्टमांश', 'D9': 'नवमांश',
            'D10': 'दशमांश', 'D11': 'रुद्रांश', 'D12': 'द्वादशांश',
            'D16': 'षोडशांश', 'D20': 'विंशांश', 'D24': 'चतुर्विंशांश',
            'D27': 'नक्षत्रांश', 'D30': 'त्रिंशांश', 'D40': 'खवेदांश',
            'D45': 'अक्षवेदांश', 'D60': 'षष्ट्यंश'
        }
    
    def format_with_devanagari(self, vargas_data: Dict) -> List[str]:
        """Format with Devanagari script."""
        lines = []
        
        # Check if terminal supports Unicode
        try:
            test = 'मेष'
            test.encode('utf-8')
            use_devanagari = True
        except:
            use_devanagari = False
        
        if use_devanagari:
            # Use actual Devanagari
            for planet, data in vargas_data.items():
                sign_num = self.get_sign_number(data.get('sign', ''))
                devanagari = self.devanagari_signs.get(sign_num, '')
                lines.append(f"{planet}: {devanagari}")
        else:
            # Fall back to transliteration
            lines.append("(Devanagari not supported in current environment)")
        
        return lines
```

### 4. Advanced Varga Analysis

```python
class VargaAnalysis:
    """Advanced analysis of varga positions."""
    
    @staticmethod
    def calculate_varga_vimshopaka_bala(vargas_data: Dict) -> Dict:
        """
        Calculate Vimshopaka Bala based on dignity in vargas.
        
        Different schemes:
        - Shadvarga: 6 vargas
        - Saptavarga: 7 vargas
        - Dashavarga: 10 vargas
        - Shodashavarga: 16 vargas
        """
        # Shadvarga weights
        shadvarga_weights = {
            'D1': 6, 'D2': 2, 'D3': 4,
            'D9': 5, 'D12': 2, 'D30': 1
        }
        
        vimshopaka_bala = {}
        
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            total_points = 0
            
            for varga, weight in shadvarga_weights.items():
                if varga in vargas_data and planet in vargas_data[varga]:
                    dignity = get_dignity(planet, vargas_data[varga][planet]['sign'])
                    points = dignity_to_points(dignity) * weight
                    total_points += points
            
            # Convert to 20-point scale
            max_points = sum(shadvarga_weights.values()) * 20
            vimshopaka_bala[planet] = round(total_points * 20 / max_points, 2)
        
        return vimshopaka_bala
    
    @staticmethod
    def find_varga_patterns(vargas_data: Dict) -> Dict:
        """Find special patterns in vargas."""
        patterns = {
            'vargottama': [],      # Same sign in D1 and D9
            'pushkara_navamsa': [], # Special navamsas
            'parivartana': []      # Exchanges in vargas
        }
        
        # Check Vargottama
        if 'D1' in vargas_data and 'D9' in vargas_data:
            for planet in vargas_data['D1']:
                if planet in vargas_data['D9']:
                    if vargas_data['D1'][planet]['sign'] == vargas_data['D9'][planet]['sign']:
                        patterns['vargottama'].append(planet)
        
        return patterns
```

### 5. Testing

```python
def test_vargas_format():
    """Test vargas formatting."""
    
    # Sample vargas data
    test_vargas = {
        'D1': {
            'Ascendant': {'sign': 'Gemini', 'longitude': 75.0},
            'Sun': {'sign': 'Aquarius', 'longitude': 320.0},
            'Moon': {'sign': 'Cancer', 'longitude': 105.0}
        },
        'D9': {
            'Ascendant': {'sign': 'Taurus', 'longitude': 45.0},
            'Sun': {'sign': 'Sagittarius', 'longitude': 260.0},
            'Moon': {'sign': 'Gemini', 'longitude': 75.0}
        }
        # Add more vargas...
    }
    
    formatter = VargasFormatter()
    
    # Test numeric format
    numeric_lines = formatter.format_vargas_table(test_vargas, 'numeric')
    assert any('3' in line and '11' in line for line in numeric_lines)
    
    # Test Sanskrit format
    sanskrit_lines = formatter.format_vargas_table(test_vargas, 'sanskrit')
    assert any('Mithun' in line or 'Kumbh' in line for line in sanskrit_lines)
    
    print("Vargas format test passed!")
```

This implementation provides traditional vargas display format with numeric output matching the original format, plus options for Sanskrit and other display styles.