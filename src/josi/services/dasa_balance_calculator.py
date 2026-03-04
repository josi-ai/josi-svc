# src/josi/services/dasa_balance_calculator.py

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math

class DasaBalanceCalculator:
    """
    Calculate dasa balance at birth following VedAstro methodology.
    
    This implementation calculates the remaining Vimshottari dasa period
    based on Moon's position in nakshatra at the time of birth.
    """
    
    def __init__(self):
        # Vimshottari dasa periods in years
        self.dasa_years = {
            'Ketu': 7,
            'Venus': 20,
            'Sun': 6,
            'Moon': 10,
            'Mars': 7,
            'Rahu': 18,
            'Jupiter': 16,
            'Saturn': 19,
            'Mercury': 17
        }
        
        # Nakshatra rulers in order (0-26)
        self.nakshatra_rulers = [
            'Ketu',     # 0 - Ashwini
            'Venus',    # 1 - Bharani
            'Sun',      # 2 - Krittika
            'Moon',     # 3 - Rohini
            'Mars',     # 4 - Mrigashira
            'Rahu',     # 5 - Ardra
            'Jupiter',  # 6 - Punarvasu
            'Saturn',   # 7 - Pushya
            'Mercury',  # 8 - Ashlesha
            'Ketu',     # 9 - Magha
            'Venus',    # 10 - Purva Phalguni
            'Sun',      # 11 - Uttara Phalguni
            'Moon',     # 12 - Hasta
            'Mars',     # 13 - Chitra
            'Rahu',     # 14 - Swati
            'Jupiter',  # 15 - Vishakha
            'Saturn',   # 16 - Anuradha
            'Mercury',  # 17 - Jyeshtha
            'Ketu',     # 18 - Mula
            'Venus',    # 19 - Purva Ashadha
            'Sun',      # 20 - Uttara Ashadha
            'Moon',     # 21 - Shravana
            'Mars',     # 22 - Dhanishtha
            'Rahu',     # 23 - Shatabhisha
            'Jupiter',  # 24 - Purva Bhadrapada
            'Saturn',   # 25 - Uttara Bhadrapada
            'Mercury'   # 26 - Revati
        ]
        
        # Nakshatra names
        self.nakshatra_names = [
            'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira',
            'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha', 'Magha',
            'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra',
            'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula',
            'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha',
            'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
        ]
        
        # Dasa sequence for Vimshottari system
        self.dasa_sequence = [
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars',
            'Rahu', 'Jupiter', 'Saturn', 'Mercury'
        ]
    
    def get_nakshatra_name(self, index: int) -> str:
        """Get nakshatra name from index."""
        return self.nakshatra_names[index % 27]
    
    def calculate_dasa_balance_at_birth(self, moon_longitude: float, birth_datetime: datetime) -> Dict:
        """
        Calculate dasa balance at birth based on Moon's position.
        
        Args:
            moon_longitude: Moon's sidereal longitude in degrees (0-360)
            birth_datetime: Date and time of birth
            
        Returns:
            Dictionary with dasa balance information
        """
        # Each nakshatra is 13°20' (13.3333... degrees or 800 minutes)
        nakshatra_span = 360.0 / 27
        
        # Find which nakshatra Moon is in
        nakshatra_index = int(moon_longitude / nakshatra_span)
        
        # How far Moon has traversed in the nakshatra (in degrees)
        degrees_traversed = moon_longitude % nakshatra_span
        
        # Proportion of nakshatra remaining
        proportion_remaining = 1 - (degrees_traversed / nakshatra_span)
        
        # Get the ruling planet of current nakshatra
        ruler = self.nakshatra_rulers[nakshatra_index]
        
        # Calculate remaining dasa period
        total_years = self.dasa_years[ruler]
        remaining_years_decimal = total_years * proportion_remaining
        
        # Convert to years, months, days
        years = int(remaining_years_decimal)
        remaining_months_decimal = (remaining_years_decimal - years) * 12
        months = int(remaining_months_decimal)
        remaining_days_decimal = (remaining_months_decimal - months) * 30  # Using 30-day month
        days = int(remaining_days_decimal)
        
        # Calculate exact end date of current dasa
        total_days_remaining = int(remaining_years_decimal * 365.2422)  # Using tropical year
        dasa_end_date = birth_datetime + timedelta(days=total_days_remaining)
        
        # Calculate the start of the dasa
        total_dasa_days = int(total_years * 365.2422)
        dasa_start_date = dasa_end_date - timedelta(days=total_dasa_days)
        
        return {
            'planet': ruler,
            'nakshatra_index': nakshatra_index,
            'nakshatra_name': self.get_nakshatra_name(nakshatra_index),
            'degrees_traversed': degrees_traversed,
            'proportion_remaining': proportion_remaining,
            'years': years,
            'months': months,
            'days': days,
            'total_days': total_days_remaining,
            'dasa_start_date': dasa_start_date.isoformat(),
            'dasa_end_date': dasa_end_date.isoformat(),
            'exact_balance_years': remaining_years_decimal
        }
    
    def calculate_all_dasa_periods(self, moon_longitude: float, birth_datetime: datetime) -> List[Dict]:
        """
        Calculate all dasa periods for the entire 120-year cycle.
        
        Args:
            moon_longitude: Moon's sidereal longitude in degrees (0-360)
            birth_datetime: Date and time of birth
            
        Returns:
            List of all dasa periods with start and end dates
        """
        # First get the balance at birth
        balance = self.calculate_dasa_balance_at_birth(moon_longitude, birth_datetime)
        
        # Find the position of current dasa in the sequence
        current_planet = balance['planet']
        current_index = self.dasa_sequence.index(current_planet)
        
        # Initialize list with the remaining portion of birth dasa
        dasa_periods = [{
            'planet': current_planet,
            'start_date': birth_datetime.isoformat(),
            'end_date': balance['dasa_end_date'],
            'duration_years': balance['exact_balance_years'],
            'is_birth_dasa': True
        }]
        
        # Calculate subsequent dasas
        current_date = datetime.fromisoformat(balance['dasa_end_date'])
        
        # Continue for the rest of the 120-year cycle
        for i in range(1, 9):  # 8 more dasas after the birth dasa
            planet_index = (current_index + i) % 9
            planet = self.dasa_sequence[planet_index]
            duration_years = self.dasa_years[planet]
            duration_days = int(duration_years * 365.2422)
            
            end_date = current_date + timedelta(days=duration_days)
            
            dasa_periods.append({
                'planet': planet,
                'start_date': current_date.isoformat(),
                'end_date': end_date.isoformat(),
                'duration_years': duration_years,
                'is_birth_dasa': False
            })
            
            current_date = end_date
        
        return dasa_periods
    
    def calculate_bhukti_periods(self, dasa_planet: str, dasa_start: datetime, dasa_end: datetime) -> List[Dict]:
        """
        Calculate bhukti (sub-periods) within a dasa.
        
        Args:
            dasa_planet: The planet ruling the main dasa
            dasa_start: Start date of the dasa
            dasa_end: End date of the dasa
            
        Returns:
            List of bhukti periods within the dasa
        """
        # Find the starting position in the sequence
        start_index = self.dasa_sequence.index(dasa_planet)
        
        # Total duration of the dasa in days
        total_days = (dasa_end - dasa_start).days
        
        # Calculate proportional duration for each bhukti
        dasa_years = self.dasa_years[dasa_planet]
        bhukti_periods = []
        current_date = dasa_start
        
        for i in range(9):
            # Bhukti follows the same sequence starting from the dasa planet
            bhukti_index = (start_index + i) % 9
            bhukti_planet = self.dasa_sequence[bhukti_index]
            
            # Bhukti duration is proportional to the planet's dasa years
            bhukti_years = self.dasa_years[bhukti_planet]
            bhukti_proportion = bhukti_years / 120.0  # 120 is total Vimshottari cycle
            bhukti_days = int(total_days * bhukti_proportion)
            
            bhukti_end = current_date + timedelta(days=bhukti_days)
            
            # Adjust last bhukti to match dasa end exactly
            if i == 8:
                bhukti_end = dasa_end
            
            bhukti_periods.append({
                'planet': bhukti_planet,
                'start_date': current_date.isoformat(),
                'end_date': bhukti_end.isoformat(),
                'duration_days': (bhukti_end - current_date).days
            })
            
            current_date = bhukti_end
        
        return bhukti_periods
    
    def get_current_dasa_bhukti(self, moon_longitude: float, birth_datetime: datetime, 
                                current_datetime: Optional[datetime] = None) -> Dict:
        """
        Get the current dasa and bhukti for a given date.
        
        Args:
            moon_longitude: Moon's sidereal longitude at birth
            birth_datetime: Date and time of birth
            current_datetime: Date to check (defaults to now)
            
        Returns:
            Dictionary with current dasa and bhukti information
        """
        if current_datetime is None:
            # Make timezone-aware if birth_datetime has timezone
            if birth_datetime.tzinfo is not None:
                current_datetime = datetime.now(birth_datetime.tzinfo)
            else:
                current_datetime = datetime.now()
        
        # Get all dasa periods
        dasa_periods = self.calculate_all_dasa_periods(moon_longitude, birth_datetime)
        
        # Find current dasa
        current_dasa = None
        for dasa in dasa_periods:
            start = datetime.fromisoformat(dasa['start_date'])
            end = datetime.fromisoformat(dasa['end_date'])
            
            if start <= current_datetime <= end:
                current_dasa = dasa
                break
        
        if not current_dasa:
            return None
        
        # Calculate bhukti periods for current dasa
        dasa_start = datetime.fromisoformat(current_dasa['start_date'])
        dasa_end = datetime.fromisoformat(current_dasa['end_date'])
        bhukti_periods = self.calculate_bhukti_periods(
            current_dasa['planet'], dasa_start, dasa_end
        )
        
        # Find current bhukti
        current_bhukti = None
        for bhukti in bhukti_periods:
            start = datetime.fromisoformat(bhukti['start_date'])
            end = datetime.fromisoformat(bhukti['end_date'])
            
            if start <= current_datetime <= end:
                current_bhukti = bhukti
                break
        
        return {
            'maha_dasa': current_dasa['planet'],
            'maha_dasa_start': current_dasa['start_date'],
            'maha_dasa_end': current_dasa['end_date'],
            'bhukti': current_bhukti['planet'] if current_bhukti else None,
            'bhukti_start': current_bhukti['start_date'] if current_bhukti else None,
            'bhukti_end': current_bhukti['end_date'] if current_bhukti else None,
            'check_date': current_datetime.isoformat()
        }