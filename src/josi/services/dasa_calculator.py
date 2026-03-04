"""
Vimshottari Dasa Calculator for Vedic Astrology

This module calculates the Vimshottari Dasa system - a 120-year planetary period system
used in Vedic astrology for timing events and predictions.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math


class DasaCalculator:
    """Calculate Vimshottari Dasa periods based on Moon's nakshatra position."""
    
    # Vimshottari Dasa sequence with years
    DASA_SEQUENCE = [
        ('Ketu', 7),
        ('Venus', 20),
        ('Sun', 6),
        ('Moon', 10),
        ('Mars', 7),
        ('Rahu', 18),
        ('Jupiter', 16),
        ('Saturn', 19),
        ('Mercury', 17)
    ]
    
    # Total cycle years
    TOTAL_YEARS = 120
    
    # Nakshatra rulers (1-27)
    NAKSHATRA_RULERS = {
        1: 'Ketu',    # Ashwini
        2: 'Venus',   # Bharani
        3: 'Sun',     # Krittika
        4: 'Moon',    # Rohini
        5: 'Mars',    # Mrigashira
        6: 'Rahu',    # Ardra
        7: 'Jupiter', # Punarvasu
        8: 'Saturn',  # Pushya
        9: 'Mercury', # Ashlesha
        10: 'Ketu',   # Magha
        11: 'Venus',  # Purva Phalguni
        12: 'Sun',    # Uttara Phalguni
        13: 'Moon',   # Hasta
        14: 'Mars',   # Chitra
        15: 'Rahu',   # Swati
        16: 'Jupiter',# Vishakha
        17: 'Saturn', # Anuradha
        18: 'Mercury',# Jyeshtha
        19: 'Ketu',   # Mula
        20: 'Venus',  # Purva Ashadha
        21: 'Sun',    # Uttara Ashadha
        22: 'Moon',   # Shravana
        23: 'Mars',   # Dhanishta
        24: 'Rahu',   # Shatabhisha
        25: 'Jupiter',# Purva Bhadrapada
        26: 'Saturn', # Uttara Bhadrapada
        27: 'Mercury' # Revati
    }
    
    def calculate_nakshatra_details(self, moon_longitude: float) -> Dict:
        """Calculate nakshatra number, pada, and progress from Moon's longitude."""
        # Each nakshatra is 13°20' = 13.333... degrees
        nakshatra_span = 360.0 / 27.0  # 13.333... degrees
        pada_span = nakshatra_span / 4.0  # 3.333... degrees per pada
        
        # Calculate nakshatra (1-27)
        nakshatra_num = int(moon_longitude / nakshatra_span) + 1
        
        # Calculate pada (1-4)
        nakshatra_progress = moon_longitude % nakshatra_span
        pada = int(nakshatra_progress / pada_span) + 1
        
        # Calculate percentage through nakshatra
        percent_complete = (nakshatra_progress / nakshatra_span) * 100
        
        return {
            'nakshatra': nakshatra_num,
            'pada': pada,
            'percent_complete': percent_complete,
            'ruler': self.NAKSHATRA_RULERS[nakshatra_num]
        }
    
    def get_dasa_start_index(self, ruler: str) -> int:
        """Get the index in DASA_SEQUENCE for a given ruler."""
        for i, (planet, _) in enumerate(self.DASA_SEQUENCE):
            if planet == ruler:
                return i
        return 0
    
    def calculate_birth_balance(self, moon_longitude: float, birth_date: datetime) -> Dict:
        """Calculate the balance of dasa at birth."""
        nakshatra_details = self.calculate_nakshatra_details(moon_longitude)
        
        # Get the ruling planet and its dasa years
        ruler = nakshatra_details['ruler']
        dasa_index = self.get_dasa_start_index(ruler)
        dasa_years = self.DASA_SEQUENCE[dasa_index][1]
        
        # Calculate how much of the dasa has passed
        percent_remaining = 100 - nakshatra_details['percent_complete']
        years_remaining = (percent_remaining / 100) * dasa_years
        
        # Convert to years, months, days
        total_days = years_remaining * 365.25
        years = int(years_remaining)
        remaining_days = total_days - (years * 365.25)
        months = int(remaining_days / 30.44)
        days = int(remaining_days % 30.44)
        
        return {
            'ruler': ruler,
            'total_years': dasa_years,
            'balance': {
                'years': years,
                'months': months,
                'days': days,
                'total_days': int(total_days)
            },
            'percent_remaining': percent_remaining
        }
    
    def calculate_dasa_periods(self, moon_longitude: float, birth_date: datetime) -> List[Dict]:
        """Calculate all major dasa periods from birth."""
        birth_balance = self.calculate_birth_balance(moon_longitude, birth_date)
        
        periods = []
        current_date = birth_date
        
        # First period is the birth balance
        start_index = self.get_dasa_start_index(birth_balance['ruler'])
        
        # Add the birth balance period
        end_date = current_date + timedelta(days=birth_balance['balance']['total_days'])
        periods.append({
            'planet': birth_balance['ruler'],
            'start_date': current_date,
            'end_date': end_date,
            'years': birth_balance['total_years'],
            'is_birth_balance': True
        })
        current_date = end_date
        
        # Add subsequent full dasa periods
        for i in range(1, 9):  # 8 more periods after birth balance
            dasa_index = (start_index + i) % 9
            planet, years = self.DASA_SEQUENCE[dasa_index]
            
            end_date = current_date + timedelta(days=int(years * 365.25))
            periods.append({
                'planet': planet,
                'start_date': current_date,
                'end_date': end_date,
                'years': years,
                'is_birth_balance': False
            })
            current_date = end_date
        
        return periods
    
    def calculate_bhukti_periods(self, major_dasa: Dict) -> List[Dict]:
        """Calculate sub-periods (bhukti) within a major dasa."""
        planet = major_dasa['planet']
        start_date = major_dasa['start_date']
        total_days = (major_dasa['end_date'] - start_date).days
        
        # Find the index of the major dasa planet
        major_index = self.get_dasa_start_index(planet)
        
        bhuktis = []
        current_date = start_date
        
        # Bhukti order starts with the major dasa planet
        for i in range(9):
            bhukti_index = (major_index + i) % 9
            bhukti_planet, bhukti_years = self.DASA_SEQUENCE[bhukti_index]
            
            # Bhukti proportion = (bhukti years / 120) * major dasa years
            bhukti_days = (bhukti_years / 120.0) * total_days
            end_date = current_date + timedelta(days=int(bhukti_days))
            
            # Don't exceed major dasa end date
            if end_date > major_dasa['end_date']:
                end_date = major_dasa['end_date']
            
            bhuktis.append({
                'planet': bhukti_planet,
                'start_date': current_date,
                'end_date': end_date,
                'days': int(bhukti_days)
            })
            
            current_date = end_date
            if current_date >= major_dasa['end_date']:
                break
        
        return bhuktis
    
    def get_current_dasa_bhukti(self, moon_longitude: float, birth_date: datetime, 
                                current_date: Optional[datetime] = None) -> Dict:
        """Get the current major and minor dasa periods."""
        if current_date is None:
            current_date = datetime.now()
        
        # Handle timezone-aware vs naive datetimes
        if birth_date.tzinfo is not None and current_date.tzinfo is None:
            # Make current_date timezone aware
            current_date = current_date.replace(tzinfo=birth_date.tzinfo)
        elif birth_date.tzinfo is None and current_date.tzinfo is not None:
            # Make current_date timezone naive
            current_date = current_date.replace(tzinfo=None)
        
        # Calculate all dasa periods
        dasa_periods = self.calculate_dasa_periods(moon_longitude, birth_date)
        
        # Find current major dasa
        current_dasa = None
        for dasa in dasa_periods:
            if dasa['start_date'] <= current_date <= dasa['end_date']:
                current_dasa = dasa
                break
        
        if not current_dasa:
            return {}
        
        # Calculate bhukti periods for current dasa
        bhukti_periods = self.calculate_bhukti_periods(current_dasa)
        
        # Find current bhukti
        current_bhukti = None
        for bhukti in bhukti_periods:
            if bhukti['start_date'] <= current_date <= bhukti['end_date']:
                current_bhukti = bhukti
                break
        
        # Calculate birth balance info
        birth_balance = self.calculate_birth_balance(moon_longitude, birth_date)
        
        return {
            'current': {
                'major': current_dasa['planet'],
                'major_start': current_dasa['start_date'].strftime('%Y-%m-%d'),
                'major_end': current_dasa['end_date'].strftime('%Y-%m-%d'),
                'minor': current_bhukti['planet'] if current_bhukti else None,
                'minor_start': current_bhukti['start_date'].strftime('%Y-%m-%d') if current_bhukti else None,
                'minor_end': current_bhukti['end_date'].strftime('%Y-%m-%d') if current_bhukti else None
            },
            'birth_balance': {
                'planet': birth_balance['ruler'],
                'years': birth_balance['balance']['years'],
                'months': birth_balance['balance']['months'],
                'days': birth_balance['balance']['days']
            }
        }
    
    def format_dasa_bhukti_table(self, moon_longitude: float, birth_date: datetime) -> List[str]:
        """Format dasa-bhukti periods for traditional chart export."""
        dasa_periods = self.calculate_dasa_periods(moon_longitude, birth_date)
        
        lines = []
        lines.append("BALANCE OF DASA AT BIRTH:")
        
        # Birth balance
        birth_balance = self.calculate_birth_balance(moon_longitude, birth_date)
        lines.append(f"{birth_balance['ruler'].upper():8} {birth_balance['balance']['years']} YEARS "
                    f"{birth_balance['balance']['months']} MONTHS {birth_balance['balance']['days']} DAYS")
        lines.append("")
        lines.append("DASA BHUKTI PERIODS:")
        lines.append("-" * 70)
        
        # Show first few dasa periods with their bhuktis
        for i, dasa in enumerate(dasa_periods[:3]):  # Show first 3 dasas
            lines.append(f"\n{dasa['planet'].upper()} DASA: "
                        f"{dasa['start_date'].strftime('%d-%m-%Y')} TO "
                        f"{dasa['end_date'].strftime('%d-%m-%Y')}")
            
            # Get bhukti periods
            bhuktis = self.calculate_bhukti_periods(dasa)
            for j, bhukti in enumerate(bhuktis[:5]):  # Show first 5 bhuktis
                lines.append(f"  {bhukti['planet']:8} "
                           f"{bhukti['start_date'].strftime('%d-%m-%Y')} TO "
                           f"{bhukti['end_date'].strftime('%d-%m-%Y')}")
        
        return lines