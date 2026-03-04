"""
Compressed Dasa Formatter
Formats dasa-bhukti periods in compressed table format
"""

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
    
    def create_compressed_from_periods(self, dasa_periods: List[Dict],
                                     birth_date: datetime, num_dasas: int = 3) -> List[str]:
        """
        Create compressed table from already calculated periods.
        
        This is a simpler version that works with the dasa periods
        we already have in the chart data.
        """
        lines = []
        
        # Header
        lines.append("DASA ENDS ON   BHUKTHI FROM - TO    BHUKTHI FROM - TO    BHUKTHI FROM - TO    ")
        lines.append("")
        
        # Reference year for compression
        ref_year = birth_date.year
        
        # Process each dasa (limit to num_dasas)
        shown_dasas = 0
        for dasa in dasa_periods:
            if shown_dasas >= num_dasas:
                break
                
            dasa_name = dasa['planet']
            # Handle both datetime objects and strings
            if isinstance(dasa['end_date'], datetime):
                dasa_end = dasa['end_date']
            else:
                dasa_end = datetime.strptime(dasa['end_date'], '%Y-%m-%d')
            
            # Format dasa header
            dasa_header = self.format_dasa_header(dasa_name, dasa_end)
            
            # Get bhukti periods
            bhukti_periods = dasa.get('bhuktis', [])
            if not bhukti_periods:
                continue
            
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
                        # Handle both datetime objects and strings
                        if isinstance(bhukti['start_date'], datetime):
                            start = bhukti['start_date']
                        else:
                            start = datetime.strptime(bhukti['start_date'], '%Y-%m-%d')
                        
                        if isinstance(bhukti['end_date'], datetime):
                            end = bhukti['end_date']
                        else:
                            end = datetime.strptime(bhukti['end_date'], '%Y-%m-%d')
                        
                        bhukti_str = self.format_bhukti_period(
                            bhukti['planet'],
                            start,
                            end,
                            ref_year
                        )
                        line_parts.append(bhukti_str)
                
                # Join parts with space
                line = " ".join(line_parts)
                lines.append(line)
            
            shown_dasas += 1
        
        return lines