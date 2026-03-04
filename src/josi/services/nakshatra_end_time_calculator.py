"""
Nakshatra End Time Calculator
Calculates exact times when Moon transitions between nakshatras
"""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import math
import logging

logger = logging.getLogger(__name__)


class NakshatraEndTimeCalculator:
    """Calculate exact nakshatra transition times."""
    
    # Nakshatra names
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
        "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
        "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
        "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"
    ]
    
    # Each nakshatra is 13°20' = 13.333... degrees
    NAKSHATRA_SPAN = 360.0 / 27.0  # 13.333... degrees
    
    def __init__(self):
        """Initialize calculator."""
        swe.set_ephe_path('')  # Use built-in ephemeris
    
    def get_nakshatra_end_time(self, julian_day: float, moon_longitude: float, 
                              moon_speed: float, timezone_offset: float = 5.5) -> Dict:
        """
        Calculate when the current nakshatra will end.
        
        Args:
            julian_day: Current Julian day
            moon_longitude: Moon's current longitude
            moon_speed: Moon's speed (degrees per day)
            timezone_offset: Hours from UTC (5.5 for IST)
            
        Returns:
            Dict with end time and related information
        """
        # Current nakshatra
        current_nak_index = int(moon_longitude / self.NAKSHATRA_SPAN)
        current_nakshatra = self.NAKSHATRAS[current_nak_index]
        
        # Calculate where in the nakshatra we are
        position_in_nak = moon_longitude % self.NAKSHATRA_SPAN
        degrees_remaining = self.NAKSHATRA_SPAN - position_in_nak
        
        # If moon speed is not available, use average
        if moon_speed == 0 or moon_speed is None:
            moon_speed = 13.176  # Average moon speed in degrees per day
        
        # Estimate time to nakshatra end (rough calculation)
        days_to_end = degrees_remaining / abs(moon_speed)
        rough_end_jd = julian_day + days_to_end
        
        # Use binary search for precise calculation
        end_jd = self._find_exact_transition_time(
            julian_day, rough_end_jd, current_nak_index
        )
        
        # Convert to local time
        end_datetime = self._julian_to_datetime(end_jd, timezone_offset)
        
        # Format time
        end_time_str = end_datetime.strftime("%H:%M")
        
        # Calculate duration
        duration_hours = (end_jd - julian_day) * 24
        
        # Next nakshatra
        next_nak_index = (current_nak_index + 1) % 27
        next_nakshatra = self.NAKSHATRAS[next_nak_index]
        
        return {
            "current_nakshatra": current_nakshatra,
            "end_time": end_time_str,
            "end_datetime": end_datetime,
            "end_julian_day": end_jd,
            "duration_hours": round(duration_hours, 2),
            "degrees_remaining": round(degrees_remaining, 3),
            "next_nakshatra": next_nakshatra,
            "position_in_nakshatra": round(position_in_nak, 3)
        }
    
    def _find_exact_transition_time(self, start_jd: float, estimated_end_jd: float,
                                   current_nak_index: int) -> float:
        """
        Use binary search to find exact nakshatra transition time.
        
        Args:
            start_jd: Current time
            estimated_end_jd: Rough estimate of end time
            current_nak_index: Current nakshatra index
            
        Returns:
            Exact Julian day of transition
        """
        # Binary search parameters
        low = start_jd
        high = estimated_end_jd + 0.5  # Add buffer
        tolerance = 1.0 / (24 * 60 * 60)  # 1 second accuracy
        
        # Target longitude where nakshatra changes
        target_longitude = ((current_nak_index + 1) * self.NAKSHATRA_SPAN) % 360
        
        max_iterations = 50
        iteration = 0
        
        while (high - low) > tolerance and iteration < max_iterations:
            mid = (low + high) / 2
            
            # Calculate moon position at mid time
            moon_data = swe.calc_ut(mid, swe.MOON, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
            moon_long = moon_data[0][0]
            
            # Check if we've crossed the boundary
            if self._has_crossed_nakshatra(moon_long, target_longitude, current_nak_index):
                high = mid
            else:
                low = mid
            
            iteration += 1
        
        return (low + high) / 2
    
    def _has_crossed_nakshatra(self, moon_long: float, target_long: float, 
                               current_nak_index: int) -> bool:
        """
        Check if moon has crossed into next nakshatra.
        
        Handles the wrap-around at 360 degrees.
        """
        # Handle wrap-around case (Revati to Ashwini)
        if current_nak_index == 26:  # Revati
            # Moon crosses from ~360 to ~0
            return moon_long < 180  # Has wrapped around
        else:
            # Normal case
            return moon_long >= target_long
    
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
    
    def calculate_all_nakshatra_times(self, julian_day: float, 
                                     timezone_offset: float = 5.5) -> Dict:
        """
        Calculate nakshatra times for the day.
        
        Returns all nakshatra transitions for the current day.
        """
        transitions = []
        
        # Start from beginning of the day
        dt = self._julian_to_datetime(julian_day, timezone_offset)
        start_of_day = datetime(dt.year, dt.month, dt.day)
        start_jd = self._datetime_to_julian(start_of_day, timezone_offset)
        
        # End of day
        end_of_day = start_of_day + timedelta(days=1)
        end_jd = self._datetime_to_julian(end_of_day, timezone_offset)
        
        current_jd = start_jd
        
        while current_jd < end_jd:
            # Get moon position
            moon_data = swe.calc_ut(current_jd, swe.MOON, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
            moon_long = moon_data[0][0]
            moon_speed = moon_data[0][3]
            
            # Get nakshatra end time
            nak_end = self.get_nakshatra_end_time(
                current_jd, moon_long, moon_speed, timezone_offset
            )
            
            # If end time is within the day, add it
            if nak_end['end_julian_day'] <= end_jd:
                transitions.append({
                    'nakshatra': nak_end['current_nakshatra'],
                    'end_time': nak_end['end_time'],
                    'duration_hours': nak_end['duration_hours']
                })
                
                # Move to next nakshatra
                current_jd = nak_end['end_julian_day'] + 0.001
            else:
                # Nakshatra extends beyond the day
                duration = (end_jd - current_jd) * 24
                transitions.append({
                    'nakshatra': nak_end['current_nakshatra'],
                    'end_time': 'Next day',
                    'duration_hours': round(duration, 2)
                })
                break
        
        return {
            'date': dt.strftime('%Y-%m-%d'),
            'transitions': transitions
        }
    
    def _datetime_to_julian(self, dt: datetime, timezone_offset: float) -> float:
        """Convert datetime to Julian day."""
        # Convert to UTC
        utc_dt = dt - timedelta(hours=timezone_offset)
        
        # Convert to Julian day
        hour_decimal = utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
        
        return jd
    
    def format_nakshatra_with_end_time(self, nakshatra_data: Dict) -> str:
        """
        Format nakshatra with end time for display.
        
        Example: "STAR:PUSHYAMI UPTO 3:27 AM PADA 4"
        """
        nakshatra = nakshatra_data.get('current_nakshatra', '')
        end_time = nakshatra_data.get('end_time', '')
        
        # Determine AM/PM
        if ':' in end_time:
            hour = int(end_time.split(':')[0])
            if hour < 12:
                time_period = "AM"
                if hour == 0:
                    hour = 12
            else:
                time_period = "PM"
                if hour > 12:
                    hour -= 12
            
            minute = end_time.split(':')[1]
            formatted_time = f"{hour}:{minute} {time_period}"
        else:
            formatted_time = end_time
        
        return f"UPTO {formatted_time}"