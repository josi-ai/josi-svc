# Gap 06: Compressed Dasa Table Implementation Plan

## Overview
Implement the compressed multi-column dasa-bhukti table format.

**Original Format**:
```
DASA ENDS ON   BHUKTHI FROM - TO    BHUKTHI FROM - TO    BHUKTHI FROM - TO    

SANI  9FEB2001  GURU  6DEC98- 9FEB 1
BUDH  9FEB2018  BUDH  9FEB 1- 6JUL 3 KETU  6JUL 3- 3JUL 4 SUKR  3JUL 4- 3MAY 7
                SURY  3MAY 7- 9MAR 8 CHAN  9MAR 8- 9AUG 9 KUJA  9AUG 9- 6AUG10
                RAHU  6AUG10-24FEB13 GURU 24FEB13- 1JUN15 SANI  1JUN15- 9FEB18
```

**Current Format**: Single column vertical list

## Understanding Compressed Format

### Format Structure
1. **Column 1**: Dasa name and end date
2. **Columns 2-4**: Three bhukti periods per line
3. **Date Format**: `DDMMMYY` or `DDMMM Y` (space-saving)
4. **Alignment**: Fixed-width columns for readability

### Space-Saving Techniques
- Abbreviated month names (3 letters)
- Year shown as 1-2 digits when century is obvious
- Multiple bhuktis per line
- Continuation lines without repeating dasa name

## Implementation Steps

### 1. Create Compressed Dasa Formatter

```python
# src/josi/services/compressed_dasa_formatter.py

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

class CompressedDasaFormatter:
    """Format dasa-bhukti periods in compressed table format."""
    
    def __init__(self):
        # Month abbreviations
        self.month_abbr = {
            1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
            5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
            9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'
        }
        
        # Planet abbreviations for display
        self.planet_abbr = {
            'Sun': 'SURY', 'Moon': 'CHAN', 'Mars': 'KUJA',
            'Mercury': 'BUDH', 'Jupiter': 'GURU', 'Venus': 'SUKR',
            'Saturn': 'SANI', 'Rahu': 'RAHU', 'Ketu': 'KETU'
        }
    
    def format_date_compressed(self, date: datetime, ref_year: int = None) -> str:
        """
        Format date in compressed form.
        
        Examples:
            2001-02-09 -> "9FEB 1" (if ref_year is 2000)
            1998-12-06 -> "6DEC98"
            2013-02-24 -> "24FEB13"
        """
        day = date.day
        month = self.month_abbr[date.month]
        year = date.year
        
        # Determine year format
        if ref_year and abs(year - ref_year) < 10:
            # Single digit year for nearby years
            year_str = str(year % 10)
        elif year >= 2000:
            # Two digit year for 2000s
            year_str = f"{year % 100:02d}"
        else:
            # Two digit year for 1900s
            year_str = f"{year % 100:02d}"
        
        # Format: DDMMMYY with smart spacing
        if len(str(day)) == 1:
            return f"{day:>2}{month}{year_str:>2}"
        else:
            return f"{day}{month}{year_str:>2}"
    
    def format_bhukti_period(self, bhukti_name: str, start_date: datetime,
                           end_date: datetime, ref_year: int = None) -> str:
        """
        Format a single bhukti period.
        
        Example: "GURU  6DEC98- 9FEB 1"
        """
        name = self.planet_abbr.get(bhukti_name, bhukti_name[:4].upper())
        start_str = self.format_date_compressed(start_date, ref_year)
        end_str = self.format_date_compressed(end_date, ref_year)
        
        # Fixed width formatting
        return f"{name:<5} {start_str:>7}-{end_str:>7}"
    
    def format_dasa_header(self, dasa_name: str, end_date: datetime) -> str:
        """
        Format dasa header with end date.
        
        Example: "SANI  9FEB2001"
        """
        name = self.planet_abbr.get(dasa_name, dasa_name[:4].upper())
        date_str = self.format_date_compressed(end_date)
        
        return f"{name:<5} {date_str:>8}"
    
    def create_compressed_dasa_table(self, dasa_periods: List[Dict],
                                   birth_date: datetime) -> List[str]:
        """
        Create complete compressed dasa table.
        
        Args:
            dasa_periods: List of dasa periods with bhukti sub-periods
            birth_date: Birth date for reference
            
        Returns:
            List of formatted lines
        """
        lines = []
        
        # Header
        lines.append("DASA ENDS ON   BHUKTHI FROM - TO    BHUKTHI FROM - TO    BHUKTHI FROM - TO    ")
        lines.append("")
        
        # Reference year for compression
        ref_year = birth_date.year
        
        # Process each dasa
        for dasa in dasa_periods:
            dasa_name = dasa['planet']
            dasa_end = dasa['end_date']
            bhukti_periods = dasa.get('bhukti_periods', [])
            
            # Skip if no bhukti data
            if not bhukti_periods:
                continue
            
            # First line with dasa header
            dasa_header = self.format_dasa_header(dasa_name, dasa_end)
            
            # Group bhuktis in sets of 3
            for i in range(0, len(bhukti_periods), 3):
                line_parts = []
                
                # Add dasa header only on first line
                if i == 0:
                    line_parts.append(dasa_header)
                else:
                    line_parts.append(" " * 15)  # Empty space for continuation
                
                # Add up to 3 bhukti periods
                for j in range(3):
                    if i + j < len(bhukti_periods):
                        bhukti = bhukti_periods[i + j]
                        bhukti_str = self.format_bhukti_period(
                            bhukti['planet'],
                            bhukti['start_date'],
                            bhukti['end_date'],
                            ref_year
                        )
                        line_parts.append(bhukti_str)
                
                # Join parts with space
                line = " ".join(line_parts)
                lines.append(line)
        
        return lines
    
    def create_compressed_from_calculator(self, dasa_calc, moon_longitude: float,
                                        birth_date: datetime, num_dasas: int = 9) -> List[str]:
        """
        Create compressed table using DasaCalculator output.
        
        Args:
            dasa_calc: DasaCalculator instance
            moon_longitude: Moon's longitude at birth
            birth_date: Birth datetime
            num_dasas: Number of dasas to show
            
        Returns:
            List of formatted lines
        """
        # Get dasa periods
        dasa_periods = dasa_calc.calculate_dasa_periods(moon_longitude, birth_date)
        
        # Process each dasa to add bhukti periods
        for i, dasa in enumerate(dasa_periods[:num_dasas]):
            # Calculate bhukti periods
            bhukti_periods = dasa_calc.calculate_bhukti_periods(dasa)
            dasa['bhukti_periods'] = bhukti_periods
        
        # Create compressed table
        return self.create_compressed_dasa_table(dasa_periods[:num_dasas], birth_date)
    
    def create_two_column_format(self, dasa_periods: List[Dict],
                                birth_date: datetime) -> List[str]:
        """
        Alternative two-column format for narrower displays.
        """
        lines = []
        lines.append("DASA ENDS ON   BHUKTHI FROM - TO    BHUKTHI FROM - TO")
        lines.append("")
        
        ref_year = birth_date.year
        
        for dasa in dasa_periods:
            dasa_header = self.format_dasa_header(dasa['planet'], dasa['end_date'])
            bhukti_periods = dasa.get('bhukti_periods', [])
            
            for i in range(0, len(bhukti_periods), 2):
                line_parts = []
                
                if i == 0:
                    line_parts.append(dasa_header)
                else:
                    line_parts.append(" " * 15)
                
                for j in range(2):
                    if i + j < len(bhukti_periods):
                        bhukti = bhukti_periods[i + j]
                        bhukti_str = self.format_bhukti_period(
                            bhukti['planet'],
                            bhukti['start_date'],
                            bhukti['end_date'],
                            ref_year
                        )
                        line_parts.append(bhukti_str)
                
                lines.append(" ".join(line_parts))
        
        return lines
    
    def create_extended_format(self, dasa_calc, moon_longitude: float,
                             birth_date: datetime) -> List[str]:
        """
        Extended format showing Dasa-Bhukti-Antara periods.
        """
        lines = []
        lines.append("DASA-BHUKTI-ANTARA PERIODS")
        lines.append("=" * 80)
        
        dasa_periods = dasa_calc.calculate_dasa_periods(moon_longitude, birth_date)
        
        for dasa in dasa_periods[:3]:  # Show first 3 dasas
            lines.append(f"\n{dasa['planet'].upper()} DASA: "
                        f"{dasa['start_date'].strftime('%d-%b-%Y')} to "
                        f"{dasa['end_date'].strftime('%d-%b-%Y')}")
            
            bhukti_periods = dasa_calc.calculate_bhukti_periods(dasa)
            
            for bhukti in bhukti_periods[:3]:  # Show first 3 bhuktis
                lines.append(f"  {bhukti['planet']:8} "
                           f"{bhukti['start_date'].strftime('%d-%b-%y')} to "
                           f"{bhukti['end_date'].strftime('%d-%b-%y')}")
                
                # Calculate antara periods
                antara_periods = self.calculate_antara_periods(bhukti, dasa_calc)
                
                for antara in antara_periods[:3]:  # Show first 3 antaras
                    lines.append(f"    {antara['planet']:6} "
                               f"{antara['start_date'].strftime('%d-%m-%y')} to "
                               f"{antara['end_date'].strftime('%d-%m-%y')}")
        
        return lines
    
    def calculate_antara_periods(self, bhukti: Dict, dasa_calc) -> List[Dict]:
        """Calculate antara (sub-sub) periods within a bhukti."""
        bhukti_planet = bhukti['planet']
        bhukti_start = bhukti['start_date']
        bhukti_days = (bhukti['end_date'] - bhukti_start).days
        
        # Find bhukti planet index
        for i, (planet, _) in enumerate(dasa_calc.DASA_SEQUENCE):
            if planet == bhukti_planet:
                bhukti_index = i
                break
        else:
            bhukti_index = 0
        
        antaras = []
        current_date = bhukti_start
        
        # Antara sequence starts with bhukti lord
        for i in range(9):
            antara_index = (bhukti_index + i) % 9
            antara_planet, antara_years = dasa_calc.DASA_SEQUENCE[antara_index]
            
            # Antara proportion
            antara_days = (antara_years / 120.0) * bhukti_days
            end_date = current_date + timedelta(days=int(antara_days))
            
            if end_date > bhukti['end_date']:
                end_date = bhukti['end_date']
            
            antaras.append({
                'planet': antara_planet,
                'start_date': current_date,
                'end_date': end_date
            })
            
            current_date = end_date
            if current_date >= bhukti['end_date']:
                break
        
        return antaras
```

### 2. Integration with Export

Update `generate_josi_traditional_export.py`:

```python
def add_compressed_dasa_table(lines: List[str], chart: Dict, dt: datetime):
    """Add compressed dasa table to export."""
    
    if not chart.get('dasa'):
        return
    
    # Import formatter and calculator
    from src.josi.services.compressed_dasa_formatter import CompressedDasaFormatter
    from src.josi.services.dasa_calculator import DasaCalculator
    
    formatter = CompressedDasaFormatter()
    dasa_calc = DasaCalculator()
    
    # Get moon longitude
    moon_long = chart['planets']['Moon']['longitude']
    
    # Generate compressed table
    compressed_lines = formatter.create_compressed_from_calculator(
        dasa_calc, moon_long, dt, num_dasas=9
    )
    
    # Add to output
    lines.extend(compressed_lines)
    lines.append("")

# In main generation function, replace the simple dasa table with:
add_compressed_dasa_table(lines, chart, dt)
```

### 3. Alternative Formats

```python
class DasaDisplayFormats:
    """Different dasa display format options."""
    
    @staticmethod
    def ultra_compressed_format(dasa_periods: List[Dict]) -> List[str]:
        """
        Ultra-compressed single-line format.
        Example: "SANI:98-01 BUDH:01-18(Bu:01-03,Ke:03-04,Su:04-07...)"
        """
        lines = []
        
        for dasa in dasa_periods[:5]:  # First 5 dasas
            dasa_str = f"{dasa['planet'][:4]}:"
            dasa_str += f"{dasa['start_date'].strftime('%y')}-"
            dasa_str += f"{dasa['end_date'].strftime('%y')}"
            
            # Add first few bhuktis in parentheses
            if 'bhukti_periods' in dasa:
                bhukti_strs = []
                for b in dasa['bhukti_periods'][:3]:
                    b_str = f"{b['planet'][:2]}:"
                    b_str += f"{b['start_date'].strftime('%m/%y')}"
                    bhukti_strs.append(b_str)
                
                dasa_str += f"({','.join(bhukti_strs)}...)"
            
            lines.append(dasa_str)
        
        return lines
    
    @staticmethod
    def graphical_timeline_format(dasa_periods: List[Dict], 
                                 width: int = 80) -> List[str]:
        """
        ASCII timeline format.
        
        |----SANI----|--------BUDH--------|--KETU--|-----SUKR-----|
        1998         2001                2018     2025           2045
        """
        lines = []
        
        # Calculate total span
        start_date = dasa_periods[0]['start_date']
        end_date = dasa_periods[-1]['end_date']
        total_days = (end_date - start_date).days
        
        # Create timeline
        timeline = ['-'] * width
        labels = []
        
        for dasa in dasa_periods:
            # Calculate position
            dasa_start_days = (dasa['start_date'] - start_date).days
            dasa_end_days = (dasa['end_date'] - start_date).days
            
            start_pos = int((dasa_start_days / total_days) * width)
            end_pos = int((dasa_end_days / total_days) * width)
            
            # Add to timeline
            if end_pos > start_pos:
                timeline[start_pos] = '|'
                timeline[end_pos-1] = '|'
                
                # Add dasa name in middle
                name_pos = (start_pos + end_pos) // 2
                name = dasa['planet'][:4]
                
                labels.append((name_pos, name, dasa['start_date'].year))
        
        # Create output
        timeline_str = ''.join(timeline)
        lines.append(timeline_str)
        
        # Add year labels
        year_line = [' '] * width
        for pos, name, year in labels:
            year_str = str(year)
            for i, char in enumerate(year_str):
                if pos + i < width:
                    year_line[pos + i] = char
        
        lines.append(''.join(year_line))
        
        return lines
```

### 4. Responsive Table Width

```python
def adjust_table_width(terminal_width: int) -> int:
    """Determine how many bhukti columns to show based on terminal width."""
    
    # Each bhukti column needs ~25 characters
    # Base needs ~15 characters
    
    if terminal_width < 60:
        return 1  # Single column
    elif terminal_width < 85:
        return 2  # Two columns
    elif terminal_width < 110:
        return 3  # Three columns
    else:
        return 4  # Four columns
```

### 5. Testing

```python
def test_compressed_format():
    """Test compressed dasa format against original."""
    
    # Test data
    test_birth = datetime(1998, 12, 7, 21, 15)
    test_moon_long = 105.133  # Archana's moon
    
    # Generate compressed table
    formatter = CompressedDasaFormatter()
    dasa_calc = DasaCalculator()
    
    lines = formatter.create_compressed_from_calculator(
        dasa_calc, test_moon_long, test_birth
    )
    
    # Verify format
    assert "DASA ENDS ON" in lines[0]
    assert "BHUKTHI FROM - TO" in lines[0]
    
    # Check specific entries
    for line in lines:
        if "SANI" in line and "9FEB" in line:
            assert "GURU" in line
            assert "6DEC98" in line
            break
    else:
        assert False, "Expected SANI dasa entry not found"
    
    print("Compressed format test passed!")
```

This implementation provides the compressed multi-column dasa table format, matching traditional astrology software output while being adaptable to different display widths.