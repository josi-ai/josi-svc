# Gap 02: Nakshatra End Times Implementation Plan

## Overview
Calculate and display when the current nakshatra will end for a given birth time.

**Original Format**: `STAR:PUSHYAMI TILL 23:58IST PADA 4`
**Current Format**: `STAR:PUSHYAMI [TIME PENDING] PADA 4`

## Understanding Nakshatra Transitions

### Nakshatra Movement
- Moon travels through 27 nakshatras in ~27.3 days
- Each nakshatra = 13°20' (13.333...°)
- Moon's average speed = ~13°/day
- Actual speed varies from 11° to 15° per day

### Time Calculation Requirements
1. Current Moon position at birth
2. Moon's speed at birth time
3. End boundary of current nakshatra
4. Calculate when Moon will reach that boundary

## Implementation Steps

### 1. Create Nakshatra Timing Calculator

```python
# src/josi/services/nakshatra_timing.py

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import math

class NakshatraTimingCalculator:
    """Calculate nakshatra transition times."""
    
    NAKSHATRA_SPAN = 360.0 / 27.0  # 13.333... degrees
    
    def __init__(self):
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", 
            "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", 
            "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", 
            "Uttara Bhadrapada", "Revati"
        ]
    
    def get_nakshatra_end_time(self, julian_day: float, moon_longitude: float, 
                               moon_speed: float, timezone_offset: float = 5.5) -> Dict:
        """
        Calculate when current nakshatra will end.
        
        Args:
            julian_day: Julian day of birth
            moon_longitude: Moon's longitude at birth
            moon_speed: Moon's speed at birth (degrees/day)
            timezone_offset: Hours from UTC (5.5 for IST)
        
        Returns:
            Dict with nakshatra info and end time
        """
        # Current nakshatra
        nakshatra_num = int(moon_longitude / self.NAKSHATRA_SPAN)
        nakshatra_name = self.nakshatras[nakshatra_num]
        
        # Pada (quarter) within nakshatra
        nakshatra_start = nakshatra_num * self.NAKSHATRA_SPAN
        position_in_nakshatra = moon_longitude - nakshatra_start
        pada = int(position_in_nakshatra / (self.NAKSHATRA_SPAN / 4)) + 1
        
        # End of current nakshatra
        nakshatra_end = (nakshatra_num + 1) * self.NAKSHATRA_SPAN
        if nakshatra_end >= 360:
            nakshatra_end -= 360
        
        # Degrees to travel
        if nakshatra_end > moon_longitude:
            degrees_to_travel = nakshatra_end - moon_longitude
        else:
            degrees_to_travel = (360 - moon_longitude) + nakshatra_end
        
        # Calculate end time using current speed
        if moon_speed > 0:
            days_to_end = degrees_to_travel / moon_speed
        else:
            # Use average speed if current speed is invalid
            days_to_end = degrees_to_travel / 13.1
        
        # More accurate calculation using ephemeris
        end_time_jd = self._find_exact_transition_time(
            julian_day, moon_longitude, nakshatra_end, days_to_end
        )
        
        # Convert to local time
        end_time_local = self._julian_to_datetime(end_time_jd, timezone_offset)
        
        return {
            'nakshatra': nakshatra_name,
            'pada': pada,
            'end_time': end_time_local.strftime('%H:%M'),
            'end_time_full': end_time_local,
            'degrees_remaining': degrees_to_travel,
            'approximate_hours': days_to_end * 24
        }
    
    def _find_exact_transition_time(self, start_jd: float, start_longitude: float,
                                   target_longitude: float, approx_days: float) -> float:
        """
        Use binary search to find exact transition time.
        """
        # Initial bounds
        jd_min = start_jd
        jd_max = start_jd + approx_days * 1.5  # Add buffer
        
        # Binary search for exact time
        epsilon = 1.0 / 1440.0  # 1 minute accuracy
        
        while (jd_max - jd_min) > epsilon:
            jd_mid = (jd_min + jd_max) / 2.0
            
            # Calculate Moon position at mid time
            moon_data = swe.calc_ut(jd_mid, swe.MOON, swe.FLG_SIDEREAL)
            moon_long = moon_data[0][0]
            
            # Check if we've crossed the target
            if self._has_crossed_target(start_longitude, moon_long, target_longitude):
                jd_max = jd_mid
            else:
                jd_min = jd_mid
        
        return jd_mid
    
    def _has_crossed_target(self, start: float, current: float, target: float) -> bool:
        """Check if moon has crossed target longitude."""
        # Handle 360-degree wraparound
        if target < start:  # Crossing 0 degrees
            return current >= target and current < start
        else:
            return current >= target or current < start
    
    def _julian_to_datetime(self, jd: float, tz_offset: float) -> datetime:
        """Convert Julian day to datetime with timezone."""
        # Convert to UTC
        year, month, day, hour, minute, second = swe.revjul(jd)
        
        # Create UTC datetime
        dt_utc = datetime(year, month, day, hour, minute, int(second))
        
        # Add timezone offset
        dt_local = dt_utc + timedelta(hours=tz_offset)
        
        return dt_local
    
    def get_all_nakshatra_transitions(self, julian_day: float, 
                                     timezone_offset: float = 5.5) -> list:
        """
        Get transitions for next 24 hours (useful for daily panchang).
        """
        transitions = []
        current_jd = julian_day
        end_jd = julian_day + 1.0  # Next 24 hours
        
        while current_jd < end_jd:
            # Get Moon position
            moon_data = swe.calc_ut(current_jd, swe.MOON, swe.FLG_SIDEREAL)
            moon_long = moon_data[0][0]
            moon_speed = moon_data[0][3]
            
            # Get current nakshatra info
            nak_info = self.get_nakshatra_end_time(
                current_jd, moon_long, moon_speed, timezone_offset
            )
            
            transitions.append({
                'nakshatra': nak_info['nakshatra'],
                'starts': self._julian_to_datetime(current_jd, timezone_offset),
                'ends': nak_info['end_time_full']
            })
            
            # Move to next nakshatra
            current_jd = self._datetime_to_julian(nak_info['end_time_full']) + 0.001
        
        return transitions
    
    def _datetime_to_julian(self, dt: datetime) -> float:
        """Convert datetime to Julian day."""
        return swe.julday(dt.year, dt.month, dt.day, 
                         dt.hour + dt.minute/60.0 + dt.second/3600.0)
```

### 2. Integration with Astrology Service

Update `astrology_service.py`:

```python
from .nakshatra_timing import NakshatraTimingCalculator

class AstrologyCalculator:
    def __init__(self):
        # ... existing init ...
        self.nakshatra_timing = NakshatraTimingCalculator()
    
    def calculate_vedic_chart(self, dt: datetime, latitude: float, 
                            longitude: float, timezone: Optional[str] = None, 
                            ayanamsa: Optional[int] = None, 
                            house_system: str = 'placidus') -> Dict:
        # ... existing code ...
        
        # After calculating Moon position
        if 'Moon' in planet_positions:
            moon_data = planet_positions['Moon']
            
            # Calculate nakshatra end time
            nak_timing = self.nakshatra_timing.get_nakshatra_end_time(
                julian_day,
                moon_data['longitude'],
                moon_data['speed'],
                5.5  # IST offset, adjust based on location
            )
            
            # Add to Moon data
            moon_data['nakshatra_end_time'] = nak_timing['end_time']
            moon_data['nakshatra_end_full'] = nak_timing['end_time_full']
```

### 3. Update Panchang Calculator

Add similar timing for all panchang elements:

```python
class PanchangCalculator:
    def calculate_tithi_end_time(self, julian_day: float, sun_long: float, 
                                 moon_long: float, sun_speed: float, 
                                 moon_speed: float) -> str:
        """Calculate when current tithi will end."""
        # Current tithi position
        tithi_longitude = (moon_long - sun_long) % 360
        current_tithi = int(tithi_longitude / 12) + 1
        
        # End of current tithi
        tithi_end_longitude = (current_tithi * 12) % 360
        
        # Degrees to travel
        degrees_to_travel = tithi_end_longitude - (tithi_longitude % 12)
        
        # Relative speed (Moon - Sun)
        relative_speed = moon_speed - sun_speed
        
        if relative_speed > 0:
            days_to_end = degrees_to_travel / relative_speed
            end_jd = julian_day + days_to_end
            
            # Convert to time
            end_time = self._julian_to_datetime(end_jd)
            return end_time.strftime('%H:%M')
        
        return "N/A"
    
    def calculate_yoga_end_time(self, julian_day: float, sun_long: float, 
                               moon_long: float, sun_speed: float, 
                               moon_speed: float) -> str:
        """Calculate when current yoga will end."""
        # Current yoga position
        yoga_longitude = (sun_long + moon_long) % 360
        current_yoga = int(yoga_longitude / (360/27)) + 1
        
        # Similar calculation...
        return end_time.strftime('%H:%M')
    
    def calculate_karana_end_time(self, julian_day: float, sun_long: float, 
                                 moon_long: float, sun_speed: float, 
                                 moon_speed: float) -> str:
        """Calculate when current karana will end."""
        # Karana is half of tithi
        tithi_longitude = (moon_long - sun_long) % 360
        current_karana = int(tithi_longitude / 6) + 1
        
        # Similar calculation...
        return end_time.strftime('%H:%M')
```

### 4. Update Export Format

In `generate_josi_traditional_export.py`:

```python
# Update nakshatra line
moon_nakshatra = NAKSHATRA_NAMES.get(chart['planets']['Moon']['nakshatra'], 
                                     chart['planets']['Moon']['nakshatra'])
moon_pada = chart['planets']['Moon']['pada']

# Get end time
if 'nakshatra_end_time' in chart['planets']['Moon']:
    nak_end_time = chart['planets']['Moon']['nakshatra_end_time']
    nak_line = f" STAR:{moon_nakshatra:<10} TILL {nak_end_time}IST  PADA {moon_pada}"
else:
    nak_line = f" STAR:{moon_nakshatra:<10} [TIME PENDING] PADA {moon_pada}"

# Update tithi/yoga/karana with times
if chart.get('panchang'):
    panchang = chart['panchang']
    tithi_time = panchang.get('tithi_end_time', '[PENDING]')
    yoga_time = panchang.get('yoga_end_time', '[PENDING]')
    karana_time = panchang.get('karana_end_time', '[PENDING]')
    
    tithi_str = f"{panchang['tithi']['paksha'].upper():<8} {panchang['tithi']['name'].upper()}FROM {tithi_time}IST"
    yoga_str = f"{panchang['yoga']['name'].upper()} FROM {yoga_time}IST"
    karana_str = f"{panchang['karana']['name'].upper()} TILL {karana_time}IST"
```

### 5. Advanced Features

#### A. Sub-Nakshatra Timings
```python
def get_sub_nakshatra_timing(self, moon_longitude: float, moon_speed: float) -> Dict:
    """Calculate sub-nakshatra (1/9th division) timings."""
    # Each nakshatra has 9 sub-lords
    sub_lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 
                 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
    
    # Calculate current sub-lord and end time
    # ...
```

#### B. Chandra Ashtama Timing
```python
def get_chandra_ashtama_period(self, birth_moon: float, current_jd: float) -> Dict:
    """Calculate when Moon will be in 8th from natal position."""
    # Important for muhurta
    ashtama_start = (birth_moon + 210) % 360  # 7 signs
    ashtama_end = (birth_moon + 240) % 360    # 8 signs
    # ...
```

### 6. Testing Strategy

1. **Accuracy Testing**
   - Compare with ephemeris data
   - Verify against panchang software
   - Check multiple time zones

2. **Edge Cases**
   - Moon at exact nakshatra boundary
   - Very fast/slow Moon
   - Retrograde planets (for yoga calculations)

3. **Performance**
   - Cache calculations
   - Optimize binary search
   - Batch calculations for daily panchang

### 7. Display Variations

Different regional preferences:
```python
DISPLAY_FORMATS = {
    'indian': '{time}IST',
    'western': '{time} {timezone}',
    '24hour': '{time}',
    '12hour': '{time} {ampm}'
}
```

This implementation provides accurate nakshatra transition times matching traditional panchang formats.