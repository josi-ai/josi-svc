"""
Tamil Calendar Calculator
Calculates Tamil solar months, pakshas, tithis, and related information
"""

from datetime import datetime
from typing import Dict, Tuple
import math


class TamilCalendar:
    """Calculate Tamil calendar information including solar months and pakshas."""
    
    # Tamil solar months with start dates (approximate)
    TAMIL_MONTHS = [
        ('Chithirai', 14, 4),      # ~April 14
        ('Vaikasi', 15, 5),        # ~May 15
        ('Aani', 15, 6),           # ~June 15
        ('Aadi', 17, 7),           # ~July 17
        ('Aavani', 17, 8),         # ~August 17
        ('Purattasi', 17, 9),      # ~September 17
        ('Aippasi', 18, 10),       # ~October 18
        ('Karthikai', 17, 11),     # ~November 17
        ('Margazhi', 16, 12),      # ~December 16
        ('Thai', 15, 1),           # ~January 15
        ('Maasi', 13, 2),          # ~February 13
        ('Panguni', 15, 3)         # ~March 15
    ]
    
    # Day/Night determination thresholds (in hours)
    DAY_START = 6.0   # 6 AM
    DAY_END = 18.0    # 6 PM
    
    def __init__(self):
        """Initialize Tamil Calendar calculator."""
        pass
    
    def get_tamil_date(self, date: datetime, sun_longitude: float) -> Dict:
        """
        Calculate Tamil date information.
        
        Args:
            date: Datetime object
            sun_longitude: Sun's sidereal longitude
            
        Returns:
            Dict with Tamil month, day, year, and additional info
        """
        # Calculate Tamil month based on sun's sidereal position
        tamil_month_info = self._calculate_tamil_month_by_sun(sun_longitude)
        
        # Calculate Tamil year
        # Tamil year is 78 years behind Gregorian (Saka era)
        tamil_year = date.year - 78
        
        # Adjust year if before Tamil new year (mid-April)
        if date.month < 4 or (date.month == 4 and date.day < 14):
            tamil_year -= 1
        
        # Get Tamil month name
        tamil_month = tamil_month_info['month']
        
        # Calculate day within Tamil month
        # This is approximate - proper calculation needs exact sun ingress times
        tamil_day = self._calculate_tamil_day(date, tamil_month_info['index'])
        
        # Get Tamil weekday
        tamil_weekday = self._get_tamil_weekday(date.weekday())
        
        return {
            'month': tamil_month,
            'day': tamil_day,
            'year': tamil_year,
            'weekday': tamil_weekday,
            'month_index': tamil_month_info['index']
        }
    
    def _calculate_tamil_month_by_sun(self, sun_longitude: float) -> Dict:
        """
        Determine Tamil month based on sun's sidereal longitude.
        
        Each Tamil month corresponds to sun's transit through a zodiac sign.
        """
        # Each zodiac sign is 30 degrees
        sign_index = int(sun_longitude / 30)
        
        # Tamil months start with Mesha (Aries) = Chithirai
        # Mapping: 0=Aries=Chithirai, 1=Taurus=Vaikasi, etc.
        tamil_month_index = sign_index
        tamil_month_name = self.TAMIL_MONTHS[tamil_month_index][0]
        
        return {
            'month': tamil_month_name,
            'index': tamil_month_index,
            'sign_index': sign_index
        }
    
    def _calculate_tamil_day(self, date: datetime, month_index: int) -> int:
        """
        Calculate day within Tamil month.
        
        This is a simplified calculation. Proper calculation requires
        exact sun ingress times for each month.
        """
        # Get approximate start date of Tamil month
        month_info = self.TAMIL_MONTHS[month_index]
        month_start_day = month_info[1]
        month_start_month = month_info[2]
        
        # Handle year boundary
        year = date.year
        if month_start_month > date.month:
            year -= 1
        
        # Create approximate start date
        month_start = datetime(year, month_start_month, month_start_day)
        
        # Calculate days elapsed
        if date >= month_start:
            days_elapsed = (date - month_start).days + 1
        else:
            # Handle case where date is before month start (next year's month)
            next_year_start = datetime(year + 1, month_start_month, month_start_day)
            days_elapsed = (date - next_year_start).days + 1
        
        # Tamil months have 29-32 days, ensure within bounds
        return max(1, min(32, days_elapsed))
    
    def _get_tamil_weekday(self, weekday: int) -> str:
        """Get Tamil name for weekday."""
        tamil_weekdays = [
            'திங்கள்',      # Monday - Thingal
            'செவ்வாய்',     # Tuesday - Sevvai
            'புதன்',        # Wednesday - Budhan
            'வியாழன்',      # Thursday - Viyazhan
            'வெள்ளி',       # Friday - Velli
            'சனி',          # Saturday - Sani
            'ஞாயிறு'       # Sunday - Gnayiru
        ]
        
        # Also provide transliterated versions
        tamil_weekdays_translit = [
            'Thingal',      # Monday
            'Sevvai',       # Tuesday
            'Budhan',       # Wednesday
            'Viyazhan',     # Thursday
            'Velli',        # Friday
            'Sani',         # Saturday
            'Gnayiru'       # Sunday
        ]
        
        return tamil_weekdays_translit[weekday]
    
    def get_paksha_tithi_tamil(self, tithi_data: Dict, moon_longitude: float,
                               birth_time: datetime) -> Dict:
        """
        Get Tamil-specific paksha and tithi information.
        
        Args:
            tithi_data: Tithi calculation from PanchangCalculator
            moon_longitude: Moon's longitude
            birth_time: Birth datetime
            
        Returns:
            Dict with Tamil paksha name and day/night determination
        """
        # Tamil paksha names
        paksha_tamil = {
            'Shukla': 'வளர்பிறை',  # Valar Pirai (Waxing)
            'Krishna': 'தேய்பிறை',  # Thei Pirai (Waning)
            'Purnima': 'பௌர்ணமி',   # Pournami (Full Moon)
            'Amavasya': 'அமாவாசை'   # Amavasai (New Moon)
        }
        
        paksha_translit = {
            'Shukla': 'Valar Pirai',
            'Krishna': 'Thei Pirai', 
            'Purnima': 'Pournami',
            'Amavasya': 'Amavasai'
        }
        
        # Get paksha from tithi data
        paksha = tithi_data.get('paksha', 'Shukla')
        
        # Determine if birth was during day or night
        birth_hour = birth_time.hour + birth_time.minute / 60.0
        is_day_birth = self.DAY_START <= birth_hour < self.DAY_END
        
        # Tamil tithi names (1-15 for each paksha)
        tamil_tithi_names = [
            'பிரதமை',      # Prathamai
            'துவிதியை',     # Dvitiyai
            'திருதியை',     # Tritiyai
            'சதுர்த்தி',    # Chaturthi
            'பஞ்சமி',      # Panchami
            'சஷ்டி',       # Shashti
            'சப்தமி',      # Saptami
            'அஷ்டமி',      # Ashtami
            'நவமி',        # Navami
            'தசமி',        # Dasami
            'ஏகாதசி',      # Ekadasi
            'துவாதசி',      # Dvadasi
            'திரயோதசி',    # Trayodasi
            'சதுர்த்தசி',   # Chaturdasi
            'பௌர்ணமி/அமாவாசை'  # Pournami/Amavasai
        ]
        
        tithi_translit = [
            'Prathamai', 'Dvitiyai', 'Tritiyai', 'Chaturthi', 'Panchami',
            'Shashti', 'Saptami', 'Ashtami', 'Navami', 'Dasami',
            'Ekadasi', 'Dvadasi', 'Trayodasi', 'Chaturdasi', 'Pournami/Amavasai'
        ]
        
        tithi_number = tithi_data.get('number', 1)
        tithi_index = (tithi_number - 1) % 15
        
        return {
            'paksha_tamil': paksha_translit.get(paksha, paksha),
            'paksha_original': paksha,
            'tithi_tamil': tithi_translit[min(tithi_index, 14)],
            'tithi_number': tithi_number,
            'is_day_birth': is_day_birth,
            'birth_time_type': 'Day' if is_day_birth else 'Night'
        }
    
    def format_tamil_calendar_info(self, tamil_date: Dict, paksha_tithi: Dict) -> str:
        """
        Format Tamil calendar information for display.
        
        Returns formatted string matching traditional format.
        """
        # Format: "TAMIL: AADI 24, 5121  KRISHNA PANCHAMI (DAY)"
        
        month = tamil_date['month'].upper()
        day = tamil_date['day']
        year = tamil_date['year']
        
        paksha = paksha_tithi['paksha_original'].upper()
        tithi_name = paksha_tithi['tithi_tamil'].upper()
        
        # Use original Sanskrit names for paksha in display
        if paksha == 'KRISHNA':
            paksha_display = 'KRISHNA'
        elif paksha == 'SHUKLA':
            paksha_display = 'SHUKLA'
        else:
            paksha_display = paksha
        
        day_night = paksha_tithi['birth_time_type'].upper()
        
        # Get the standard Sanskrit tithi name (not Tamil)
        tithi_number = paksha_tithi['tithi_number']
        sanskrit_tithi_names = [
            "PRATIPADA", "DWITIYA", "TRITIYA", "CHATURTHI", "PANCHAMI",
            "SHASHTHI", "SAPTAMI", "ASHTAMI", "NAVAMI", "DASHAMI",
            "EKADASHI", "DWADASHI", "TRAYODASHI", "CHATURDASHI"
        ]
        
        if tithi_number == 15:
            tithi_display = "PURNIMA" if paksha == "SHUKLA" else "PURNIMA"
        elif tithi_number == 30:
            tithi_display = "AMAVASYA"
        else:
            tithi_idx = (tithi_number - 1) % 15
            if tithi_idx < len(sanskrit_tithi_names):
                tithi_display = sanskrit_tithi_names[tithi_idx]
            else:
                tithi_display = f"TITHI-{tithi_number}"
        
        return f"TAMIL: {month} {day:2d}, {year}  {paksha_display} {tithi_display} ({day_night})"
    
    def get_tamil_year_name(self, tamil_year: int) -> str:
        """
        Get the name of Tamil year in 60-year cycle.
        
        Tamil years follow a 60-year cycle with specific names.
        """
        # 60-year cycle names (Prabhava to Akshaya)
        year_names = [
            'Prabhava', 'Vibhava', 'Sukla', 'Pramodoota', 'Prachorpati',
            'Aangirasa', 'Srimukha', 'Bhava', 'Yuva', 'Dhatu',
            'Eswara', 'Vehudhanya', 'Pramadi', 'Vikrama', 'Vishu',
            'Chitrabhanu', 'Svabhanu', 'Tarana', 'Parthiva', 'Vyaya',
            'Sarvajith', 'Sarvadhári', 'Virodhi', 'Vikruthi', 'Khara',
            'Nandana', 'Vijaya', 'Jaya', 'Manmatha', 'Durmukhi',
            'Hevilambi', 'Vilambi', 'Vikari', 'Sharvari', 'Plava',
            'Shubhakruth', 'Shobhakruth', 'Krodhi', 'Vishvavasu', 'Parabhava',
            'Plavanga', 'Kilaka', 'Saumya', 'Sadharana', 'Virodhikruth',
            'Paridhavi', 'Pramadeecha', 'Ananda', 'Rakshasa', 'Nala',
            'Pingala', 'Kalayukthi', 'Siddharthi', 'Raudri', 'Durmathi',
            'Dundubhi', 'Rudhirodhari', 'Raktakshi', 'Krodhana', 'Akshaya'
        ]
        
        # Calculate position in 60-year cycle
        # The cycle starts from Prabhava (1987, 1927, 1867...)
        cycle_position = (tamil_year - 1987) % 60
        
        return year_names[cycle_position]