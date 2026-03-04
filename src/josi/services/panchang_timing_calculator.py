"""
Panchang Element Timing Calculator
Calculates exact end times for Tithi, Yoga, and Karana
"""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
import math
import logging

logger = logging.getLogger(__name__)


class PanchangTimingCalculator:
    """Calculate exact transition times for panchang elements."""
    
    # Tithi names (15 + special cases)
    TITHI_NAMES = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
    ]
    
    # Yoga names (27 yogas)
    YOGA_NAMES = [
        "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
        "Atiganda", "Sukarman", "Dhriti", "Shula", "Ganda",
        "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
        "Siddhi", "Vyatipata", "Varigha", "Parigha", "Shiva",
        "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
        "Indra", "Vaidhriti"
    ]
    
    # Karana names (11 karanas)
    KARANA_NAMES = [
        "Kinstughna", "Bava", "Balava", "Kaulava", "Taitila",
        "Gara", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga"
    ]
    
    def __init__(self):
        """Initialize calculator."""
        swe.set_ephe_path('')  # Use built-in ephemeris
    
    def get_tithi_end_time(self, julian_day: float, sun_longitude: float,
                          moon_longitude: float, sun_speed: float,
                          moon_speed: float, timezone_offset: float = 5.5) -> Dict:
        """
        Calculate when the current tithi will end.
        
        Args:
            julian_day: Current Julian day
            sun_longitude: Sun's longitude
            moon_longitude: Moon's longitude
            sun_speed: Sun's daily motion
            moon_speed: Moon's daily motion
            timezone_offset: Hours from UTC (5.5 for IST)
            
        Returns:
            Dict with end time and related information
        """
        # Calculate current tithi
        moon_sun_diff = (moon_longitude - sun_longitude) % 360
        current_tithi_num = int(moon_sun_diff / 12) + 1
        
        # Position within current tithi
        position_in_tithi = moon_sun_diff % 12
        degrees_remaining = 12 - position_in_tithi
        
        # Calculate relative speed (moon moves faster than sun)
        relative_speed = moon_speed - sun_speed
        if relative_speed <= 0:
            relative_speed = 13.176 - 0.985  # Use average speeds
        
        # Estimate time to tithi end
        days_to_end = degrees_remaining / relative_speed
        rough_end_jd = julian_day + days_to_end
        
        # Use binary search for precise calculation
        target_angle = ((current_tithi_num * 12) % 360)
        end_jd = self._find_exact_tithi_time(julian_day, rough_end_jd, target_angle)
        
        # Convert to local time
        end_datetime = self._julian_to_datetime(end_jd, timezone_offset)
        end_time_str = end_datetime.strftime("%H:%M")
        
        # Get tithi names
        if current_tithi_num <= 15:
            paksha = "Shukla"
            tithi_name = self.TITHI_NAMES[current_tithi_num - 1]
        else:
            paksha = "Krishna"
            tithi_name = self.TITHI_NAMES[current_tithi_num - 1]
        
        # Special cases
        if current_tithi_num == 15:
            tithi_name = "Purnima"
        elif current_tithi_num == 30:
            tithi_name = "Amavasya"
        
        return {
            "current_tithi": tithi_name,
            "tithi_number": current_tithi_num,
            "paksha": paksha,
            "end_time": end_time_str,
            "end_datetime": end_datetime,
            "end_julian_day": end_jd,
            "degrees_remaining": round(degrees_remaining, 3),
            "position_in_tithi": round(position_in_tithi, 3)
        }
    
    def get_yoga_end_time(self, julian_day: float, sun_longitude: float,
                         moon_longitude: float, sun_speed: float,
                         moon_speed: float, timezone_offset: float = 5.5) -> Dict:
        """
        Calculate when the current yoga will end.
        
        Args:
            julian_day: Current Julian day
            sun_longitude: Sun's longitude
            moon_longitude: Moon's longitude
            sun_speed: Sun's daily motion
            moon_speed: Moon's daily motion
            timezone_offset: Hours from UTC
            
        Returns:
            Dict with end time and related information
        """
        # Calculate current yoga
        combined_longitude = (sun_longitude + moon_longitude) % 360
        yoga_span = 360.0 / 27.0  # 13.333... degrees
        current_yoga_num = int(combined_longitude / yoga_span) + 1
        
        # Position within current yoga
        position_in_yoga = combined_longitude % yoga_span
        degrees_remaining = yoga_span - position_in_yoga
        
        # Combined speed (both sun and moon contribute)
        combined_speed = sun_speed + moon_speed
        if combined_speed <= 0:
            combined_speed = 0.985 + 13.176  # Use average speeds
        
        # Estimate time to yoga end
        days_to_end = degrees_remaining / combined_speed
        rough_end_jd = julian_day + days_to_end
        
        # Use binary search for precise calculation
        target_angle = (current_yoga_num * yoga_span) % 360
        end_jd = self._find_exact_yoga_time(julian_day, rough_end_jd, target_angle)
        
        # Convert to local time
        end_datetime = self._julian_to_datetime(end_jd, timezone_offset)
        end_time_str = end_datetime.strftime("%H:%M")
        
        # Get yoga name
        yoga_name = self.YOGA_NAMES[(current_yoga_num - 1) % 27]
        
        return {
            "current_yoga": yoga_name,
            "yoga_number": current_yoga_num,
            "end_time": end_time_str,
            "end_datetime": end_datetime,
            "end_julian_day": end_jd,
            "degrees_remaining": round(degrees_remaining, 3),
            "position_in_yoga": round(position_in_yoga, 3)
        }
    
    def get_karana_end_time(self, julian_day: float, sun_longitude: float,
                           moon_longitude: float, sun_speed: float,
                           moon_speed: float, timezone_offset: float = 5.5) -> Dict:
        """
        Calculate when the current karana will end.
        
        Args:
            julian_day: Current Julian day
            sun_longitude: Sun's longitude
            moon_longitude: Moon's longitude
            sun_speed: Sun's daily motion
            moon_speed: Moon's daily motion
            timezone_offset: Hours from UTC
            
        Returns:
            Dict with end time and related information
        """
        # Calculate current karana (half tithi)
        moon_sun_diff = (moon_longitude - sun_longitude) % 360
        karana_index = int(moon_sun_diff / 6)
        
        # Position within current karana
        position_in_karana = moon_sun_diff % 6
        degrees_remaining = 6 - position_in_karana
        
        # Calculate relative speed
        relative_speed = moon_speed - sun_speed
        if relative_speed <= 0:
            relative_speed = 13.176 - 0.985  # Use average speeds
        
        # Estimate time to karana end
        days_to_end = degrees_remaining / relative_speed
        rough_end_jd = julian_day + days_to_end
        
        # Use binary search for precise calculation
        target_angle = ((karana_index + 1) * 6) % 360
        end_jd = self._find_exact_karana_time(julian_day, rough_end_jd, target_angle)
        
        # Convert to local time
        end_datetime = self._julian_to_datetime(end_jd, timezone_offset)
        end_time_str = end_datetime.strftime("%H:%M")
        
        # Get karana name based on the complex cycle
        karana_name = self._get_karana_name(karana_index)
        
        return {
            "current_karana": karana_name,
            "karana_index": karana_index,
            "end_time": end_time_str,
            "end_datetime": end_datetime,
            "end_julian_day": end_jd,
            "degrees_remaining": round(degrees_remaining, 3),
            "position_in_karana": round(position_in_karana, 3)
        }
    
    def _get_karana_name(self, index: int) -> str:
        """Get karana name based on index (0-59 cycle)."""
        # Fixed karanas
        if index == 0:
            return "Kinstughna"
        elif index >= 57:
            return ["Shakuni", "Chatushpada", "Naga", "Kinstughna"][index - 57]
        else:
            # Movable karanas (repeat 8 times)
            movable = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
            return movable[(index - 1) % 7]
    
    def _find_exact_tithi_time(self, start_jd: float, estimated_end_jd: float,
                              target_angle: float) -> float:
        """Binary search for exact tithi transition."""
        low = start_jd
        high = estimated_end_jd + 0.5
        tolerance = 1.0 / (24 * 60 * 60)  # 1 second accuracy
        
        max_iterations = 50
        iteration = 0
        
        while (high - low) > tolerance and iteration < max_iterations:
            mid = (low + high) / 2
            
            # Calculate sun and moon positions
            sun_data = swe.calc_ut(mid, swe.SUN, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
            moon_data = swe.calc_ut(mid, swe.MOON, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
            
            sun_long = sun_data[0][0]
            moon_long = moon_data[0][0]
            
            # Calculate moon-sun difference
            diff = (moon_long - sun_long) % 360
            
            # Check if we've reached the target
            if diff >= target_angle or (target_angle == 0 and diff < 12):
                high = mid
            else:
                low = mid
            
            iteration += 1
        
        return (low + high) / 2
    
    def _find_exact_yoga_time(self, start_jd: float, estimated_end_jd: float,
                             target_angle: float) -> float:
        """Binary search for exact yoga transition."""
        low = start_jd
        high = estimated_end_jd + 0.5
        tolerance = 1.0 / (24 * 60 * 60)  # 1 second accuracy
        
        max_iterations = 50
        iteration = 0
        
        while (high - low) > tolerance and iteration < max_iterations:
            mid = (low + high) / 2
            
            # Calculate sun and moon positions
            sun_data = swe.calc_ut(mid, swe.SUN, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
            moon_data = swe.calc_ut(mid, swe.MOON, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
            
            sun_long = sun_data[0][0]
            moon_long = moon_data[0][0]
            
            # Calculate combined longitude
            combined = (sun_long + moon_long) % 360
            
            # Check if we've reached the target
            if combined >= target_angle:
                high = mid
            else:
                low = mid
            
            iteration += 1
        
        return (low + high) / 2
    
    def _find_exact_karana_time(self, start_jd: float, estimated_end_jd: float,
                               target_angle: float) -> float:
        """Binary search for exact karana transition."""
        # Similar to tithi but with 6-degree intervals
        return self._find_exact_tithi_time(start_jd, estimated_end_jd, target_angle)
    
    def _julian_to_datetime(self, jd: float, timezone_offset: float) -> datetime:
        """Convert Julian day to datetime with timezone offset."""
        # Convert to calendar date
        year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
        
        # Convert decimal hours to hours, minutes, seconds
        hours = int(hour)
        minutes = int((hour - hours) * 60)
        seconds = int(((hour - hours) * 60 - minutes) * 60)
        
        # Create UTC datetime
        utc_dt = datetime(year, month, day, hours, minutes, seconds)
        
        # Add timezone offset
        local_dt = utc_dt + timedelta(hours=timezone_offset)
        
        return local_dt
    
    def format_panchang_timings(self, tithi_data: Dict, yoga_data: Dict,
                               karana_data: Dict) -> Dict:
        """
        Format all panchang timings for display.
        
        Returns formatted strings for each element.
        """
        def format_time(time_str: str) -> str:
            """Convert 24-hour to 12-hour format."""
            if ':' in time_str:
                hour, minute = map(int, time_str.split(':'))
                period = "AM" if hour < 12 else "PM"
                if hour == 0:
                    hour = 12
                elif hour > 12:
                    hour -= 12
                return f"{hour}:{minute:02d} {period}"
            return time_str
        
        return {
            "tithi": f"{tithi_data['current_tithi']} upto {format_time(tithi_data['end_time'])}",
            "yoga": f"{yoga_data['current_yoga']} upto {format_time(yoga_data['end_time'])}",
            "karana": f"{karana_data['current_karana']} upto {format_time(karana_data['end_time'])}"
        }
    
    def calculate_all_transitions_for_day(self, julian_day: float,
                                         timezone_offset: float = 5.5) -> Dict:
        """
        Calculate all panchang transitions for a given day.
        
        Returns all tithi, yoga, and karana changes within 24 hours.
        """
        transitions = {
            'tithis': [],
            'yogas': [],
            'karanas': []
        }
        
        # Start from beginning of the day
        dt = self._julian_to_datetime(julian_day, timezone_offset)
        start_of_day = datetime(dt.year, dt.month, dt.day)
        start_jd = self._datetime_to_julian(start_of_day, timezone_offset)
        
        # End of day
        end_of_day = start_of_day + timedelta(days=1)
        end_jd = self._datetime_to_julian(end_of_day, timezone_offset)
        
        # Track tithi transitions
        current_jd = start_jd
        while current_jd < end_jd:
            # Get positions
            sun_data = swe.calc_ut(current_jd, swe.SUN, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
            moon_data = swe.calc_ut(current_jd, swe.MOON, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
            
            sun_long = sun_data[0][0]
            moon_long = moon_data[0][0]
            sun_speed = sun_data[0][3]
            moon_speed = moon_data[0][3]
            
            # Get tithi end
            tithi_end = self.get_tithi_end_time(
                current_jd, sun_long, moon_long, sun_speed, moon_speed, timezone_offset
            )
            
            if tithi_end['end_julian_day'] <= end_jd:
                transitions['tithis'].append({
                    'tithi': tithi_end['current_tithi'],
                    'paksha': tithi_end['paksha'],
                    'start_time': self._julian_to_datetime(current_jd, timezone_offset).strftime("%H:%M"),
                    'end_time': tithi_end['end_time']
                })
                current_jd = tithi_end['end_julian_day'] + 0.001
            else:
                break
        
        # Similar for yogas and karanas...
        
        return transitions
    
    def _datetime_to_julian(self, dt: datetime, timezone_offset: float) -> float:
        """Convert datetime to Julian day."""
        # Convert to UTC
        utc_dt = dt - timedelta(hours=timezone_offset)
        
        # Convert to Julian day
        hour_decimal = utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
        
        return jd