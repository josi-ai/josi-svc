# Gap 03: Panchang Element Timings Implementation Plan

## Overview
Calculate and display transition times for Tithi, Yoga, and Karana.

**Original Format**: 
- `THITHI:KRISHNA PANCHAMI FROM 10:26IST`
- `YOGA:INDRA FROM 15:47IST`
- `KARANA:KAULAVA TILL 21:56IST`

**Current Format**: Shows names only without timing

## Understanding Panchang Transitions

### Element Speeds
1. **Tithi**: Based on Moon-Sun angle (12° per tithi)
   - Speed = Moon speed - Sun speed (~12°/day)
   - Duration: ~19-26 hours

2. **Yoga**: Based on Moon+Sun longitude (13.33° per yoga)
   - Speed = Moon speed + Sun speed (~14°/day)
   - Duration: ~18-24 hours

3. **Karana**: Half of tithi (6° per karana)
   - Speed = Moon speed - Sun speed
   - Duration: ~9-13 hours

## Implementation Steps

### 1. Enhanced Panchang Timing Calculator

```python
# src/josi/services/panchang_timing.py

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import math

class PanchangTimingCalculator:
    """Calculate transition times for all panchang elements."""
    
    def __init__(self):
        self.tithi_names = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"
        ]
        
        self.yoga_names = [
            "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
            "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
            "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
            "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
            "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
            "Indra", "Vaidhriti"
        ]
        
        self.karana_names = {
            # Fixed Karanas (occur once in lunar month)
            1: "Kintughna", 2: "Bava", 3: "Balava", 4: "Kaulava",
            5: "Taitila", 6: "Gara", 7: "Vanija", 8: "Vishti",
            9: "Bava", 10: "Balava", 11: "Kaulava", 12: "Taitila",
            13: "Gara", 14: "Vanija", 15: "Vishti", 16: "Bava",
            17: "Balava", 18: "Kaulava", 19: "Taitila", 20: "Gara",
            21: "Vanija", 22: "Vishti", 23: "Bava", 24: "Balava",
            25: "Kaulava", 26: "Taitila", 27: "Gara", 28: "Vanija",
            29: "Vishti", 30: "Bava", 31: "Balava", 32: "Kaulava",
            33: "Taitila", 34: "Gara", 35: "Vanija", 36: "Vishti",
            37: "Bava", 38: "Balava", 39: "Kaulava", 40: "Taitila",
            41: "Gara", 42: "Vanija", 43: "Vishti", 44: "Bava",
            45: "Balava", 46: "Kaulava", 47: "Taitila", 48: "Gara",
            49: "Vanija", 50: "Vishti", 51: "Bava", 52: "Balava",
            53: "Kaulava", 54: "Taitila", 55: "Gara", 56: "Vanija",
            57: "Vishti", 58: "Shakuni", 59: "Chatushpada", 60: "Naga"
        }
    
    def calculate_tithi_timing(self, julian_day: float, sun_data: Tuple, 
                              moon_data: Tuple, tz_offset: float = 5.5) -> Dict:
        """
        Calculate current tithi and when it will end.
        
        Args:
            julian_day: Current Julian day
            sun_data: Sun ephemeris data (longitude, speed)
            moon_data: Moon ephemeris data (longitude, speed)
            tz_offset: Timezone offset in hours
        
        Returns:
            Dict with tithi info and transition times
        """
        sun_long, sun_speed = sun_data[0], sun_data[3]
        moon_long, moon_speed = moon_data[0], moon_data[3]
        
        # Current tithi
        tithi_longitude = (moon_long - sun_long) % 360
        tithi_index = int(tithi_longitude / 12)
        tithi_number = tithi_index + 1
        
        # Paksha (fortnight)
        if tithi_number <= 15:
            paksha = "Shukla"
            tithi_name = self.tithi_names[tithi_index]
        else:
            paksha = "Krishna"
            if tithi_number == 30:
                tithi_name = "Amavasya"
            else:
                tithi_name = self.tithi_names[(tithi_index - 15)]
        
        # Calculate end time
        current_tithi_end = (tithi_index + 1) * 12
        degrees_remaining = current_tithi_end - tithi_longitude
        
        # Find exact transition time
        end_jd = self._find_tithi_transition(
            julian_day, sun_long, moon_long, sun_speed, 
            moon_speed, current_tithi_end
        )
        
        # Convert to local time
        end_time = self._julian_to_local_time(end_jd, tz_offset)
        
        # Also calculate start time (for "FROM" display)
        start_jd = self._find_tithi_transition(
            julian_day - 2, sun_long, moon_long, sun_speed,
            moon_speed, tithi_index * 12, forward=True
        )
        start_time = self._julian_to_local_time(start_jd, tz_offset)
        
        return {
            'number': tithi_number,
            'name': tithi_name,
            'paksha': paksha,
            'degrees': tithi_longitude % 12,
            'start_time': start_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
            'duration_hours': (end_jd - start_jd) * 24
        }
    
    def calculate_yoga_timing(self, julian_day: float, sun_data: Tuple,
                             moon_data: Tuple, tz_offset: float = 5.5) -> Dict:
        """Calculate current yoga and transition times."""
        sun_long, sun_speed = sun_data[0], sun_data[3]
        moon_long, moon_speed = moon_data[0], moon_data[3]
        
        # Current yoga
        yoga_longitude = (sun_long + moon_long) % 360
        yoga_index = int(yoga_longitude / (360/27))
        yoga_name = self.yoga_names[yoga_index]
        
        # Calculate transition times
        yoga_end_longitude = (yoga_index + 1) * (360/27)
        
        # Find exact transition
        end_jd = self._find_yoga_transition(
            julian_day, sun_long, moon_long, sun_speed,
            moon_speed, yoga_end_longitude
        )
        
        # Find start time
        yoga_start_longitude = yoga_index * (360/27)
        start_jd = self._find_yoga_transition(
            julian_day - 2, sun_long, moon_long, sun_speed,
            moon_speed, yoga_start_longitude, forward=True
        )
        
        end_time = self._julian_to_local_time(end_jd, tz_offset)
        start_time = self._julian_to_local_time(start_jd, tz_offset)
        
        return {
            'name': yoga_name,
            'degrees': yoga_longitude % (360/27),
            'start_time': start_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
            'duration_hours': (end_jd - start_jd) * 24
        }
    
    def calculate_karana_timing(self, julian_day: float, sun_data: Tuple,
                               moon_data: Tuple, tz_offset: float = 5.5) -> Dict:
        """Calculate current karana and transition times."""
        sun_long, sun_speed = sun_data[0], sun_data[3]
        moon_long, moon_speed = moon_data[0], moon_data[3]
        
        # Current karana (half tithi)
        tithi_longitude = (moon_long - sun_long) % 360
        karana_index = int(tithi_longitude / 6)
        
        # Get karana name (special handling for fixed karanas)
        if karana_index == 0:
            karana_name = "Kintughna"
        elif karana_index == 57:
            karana_name = "Shakuni"
        elif karana_index == 58:
            karana_name = "Chatushpada"
        elif karana_index == 59:
            karana_name = "Naga"
        else:
            # Repeating karanas
            repeat_index = ((karana_index - 1) % 7) + 2
            karana_name = self.karana_names[repeat_index]
        
        # Calculate end time
        karana_end_longitude = (karana_index + 1) * 6
        
        end_jd = self._find_tithi_transition(
            julian_day, sun_long, moon_long, sun_speed,
            moon_speed, karana_end_longitude
        )
        
        end_time = self._julian_to_local_time(end_jd, tz_offset)
        
        return {
            'name': karana_name,
            'end_time': end_time.strftime('%H:%M'),
            'index': karana_index
        }
    
    def _find_tithi_transition(self, start_jd: float, sun_long: float,
                              moon_long: float, sun_speed: float,
                              moon_speed: float, target_angle: float,
                              forward: bool = False) -> float:
        """Find exact time when tithi angle reaches target."""
        # Estimate time
        current_angle = (moon_long - sun_long) % 360
        
        if forward:
            # Finding past transition
            if target_angle > current_angle:
                angle_diff = current_angle + (360 - target_angle)
            else:
                angle_diff = current_angle - target_angle
            relative_speed = moon_speed - sun_speed
            days_estimate = -angle_diff / relative_speed
        else:
            # Finding future transition
            if target_angle > current_angle:
                angle_diff = target_angle - current_angle
            else:
                angle_diff = (360 - current_angle) + target_angle
            relative_speed = moon_speed - sun_speed
            days_estimate = angle_diff / relative_speed
        
        # Binary search for exact time
        return self._binary_search_transition(
            start_jd, start_jd + days_estimate * 1.5,
            lambda jd: self._get_tithi_angle(jd),
            target_angle
        )
    
    def _find_yoga_transition(self, start_jd: float, sun_long: float,
                             moon_long: float, sun_speed: float,
                             moon_speed: float, target_angle: float,
                             forward: bool = False) -> float:
        """Find exact time when yoga angle reaches target."""
        current_angle = (sun_long + moon_long) % 360
        
        if forward:
            if target_angle > current_angle:
                angle_diff = current_angle + (360 - target_angle)
            else:
                angle_diff = current_angle - target_angle
            combined_speed = moon_speed + sun_speed
            days_estimate = -angle_diff / combined_speed
        else:
            if target_angle > current_angle:
                angle_diff = target_angle - current_angle
            else:
                angle_diff = (360 - current_angle) + target_angle
            combined_speed = moon_speed + sun_speed
            days_estimate = angle_diff / combined_speed
        
        return self._binary_search_transition(
            start_jd, start_jd + days_estimate * 1.5,
            lambda jd: self._get_yoga_angle(jd),
            target_angle
        )
    
    def _binary_search_transition(self, jd_start: float, jd_end: float,
                                 angle_func, target_angle: float) -> float:
        """Binary search for exact transition time."""
        epsilon = 1.0 / 1440.0  # 1 minute accuracy
        
        while (jd_end - jd_start) > epsilon:
            jd_mid = (jd_start + jd_end) / 2.0
            current_angle = angle_func(jd_mid)
            
            # Handle 360-degree wraparound
            if abs(current_angle - target_angle) < 0.01:
                return jd_mid
            
            # Determine which half contains the transition
            start_angle = angle_func(jd_start)
            
            if self._is_angle_between(start_angle, target_angle, current_angle):
                jd_end = jd_mid
            else:
                jd_start = jd_mid
        
        return jd_mid
    
    def _get_tithi_angle(self, jd: float) -> float:
        """Get tithi angle at given Julian day."""
        sun = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0]
        moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0]
        return (moon[0] - sun[0]) % 360
    
    def _get_yoga_angle(self, jd: float) -> float:
        """Get yoga angle at given Julian day."""
        sun = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0]
        moon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0]
        return (sun[0] + moon[0]) % 360
    
    def _is_angle_between(self, start: float, target: float, current: float) -> bool:
        """Check if target is between start and current angles."""
        # Normalize angles
        start = start % 360
        target = target % 360
        current = current % 360
        
        if start <= current:
            return start <= target <= current
        else:  # Wraparound case
            return target >= start or target <= current
    
    def _julian_to_local_time(self, jd: float, tz_offset: float) -> datetime:
        """Convert Julian day to local datetime."""
        year, month, day, hour, minute, second = swe.revjul(jd)
        dt_utc = datetime(year, month, day, hour, minute, int(second))
        dt_local = dt_utc + timedelta(hours=tz_offset)
        return dt_local
```

### 2. Integration with Panchang Calculator

Update existing `panchang_calculator.py`:

```python
def calculate_panchang(self, julian_day: float, sun_longitude: float,
                      moon_longitude: float, latitude: float,
                      longitude: float) -> Dict:
    """Enhanced panchang with timing information."""
    
    # Get full ephemeris data for timing calculations
    sun_data = swe.calc_ut(julian_day, swe.SUN, swe.FLG_SIDEREAL)[0]
    moon_data = swe.calc_ut(julian_day, swe.MOON, swe.FLG_SIDEREAL)[0]
    
    # Initialize timing calculator
    timing_calc = PanchangTimingCalculator()
    
    # Calculate tithi with timing
    tithi_info = timing_calc.calculate_tithi_timing(
        julian_day, sun_data, moon_data
    )
    
    # Calculate yoga with timing
    yoga_info = timing_calc.calculate_yoga_timing(
        julian_day, sun_data, moon_data
    )
    
    # Calculate karana with timing
    karana_info = timing_calc.calculate_karana_timing(
        julian_day, sun_data, moon_data
    )
    
    # ... rest of panchang calculations ...
    
    return {
        'tithi': tithi_info,
        'yoga': yoga_info,
        'karana': karana_info,
        'sunrise': sunrise,
        'sunset': sunset,
        'sidereal_time': sidereal_time,
        'gulika': gulika
    }
```

### 3. Update Export Format

In `generate_josi_traditional_export.py`:

```python
# Format panchang elements with timing
if chart.get('panchang'):
    panchang = chart['panchang']
    
    # Tithi with timing
    tithi = panchang['tithi']
    tithi_str = f"{tithi['paksha'].upper():<8} {tithi['name'].upper()}FROM {tithi['start_time']}IST"
    
    # Yoga with timing
    yoga = panchang['yoga']
    yoga_str = f"{yoga['name'].upper()} FROM {yoga['start_time']}IST"
    
    # Karana with timing
    karana = panchang['karana']
    karana_str = f"{karana['name'].upper()} TILL {karana['end_time']}IST"
else:
    tithi_str = "[CALCULATION PENDING]"
    yoga_str = "[PENDING]"
    karana_str = "[CALCULATION PENDING]"

# Update the display lines
lines.append(f" STAR:{moon_nakshatra:<10} TILL {nak_end_time}IST  PADA {moon_pada}    THITHI:{tithi_str}")
lines.append(f" YOGA:{yoga_str:<32}    KARANA:{karana_str:<20}")
```

### 4. Additional Features

#### A. Panchang for Extended Period
```python
def generate_monthly_panchang(self, start_date: datetime, days: int = 30) -> List[Dict]:
    """Generate panchang for multiple days."""
    panchang_data = []
    
    for day in range(days):
        date = start_date + timedelta(days=day)
        jd = self._datetime_to_julian(date)
        
        # Calculate all transitions for the day
        daily_panchang = {
            'date': date,
            'tithi_transitions': self._get_days_tithi_transitions(jd),
            'yoga_transitions': self._get_days_yoga_transitions(jd),
            'karana_transitions': self._get_days_karana_transitions(jd),
            'nakshatra_transitions': self._get_days_nakshatra_transitions(jd)
        }
        
        panchang_data.append(daily_panchang)
    
    return panchang_data
```

#### B. Special Yoga Timings
```python
def calculate_special_yogas(self, julian_day: float) -> Dict:
    """Calculate special yogas like Ravi Yoga, Guru Pushya, etc."""
    special_yogas = {}
    
    # Ravi Yoga (Sunday + specific nakshatras)
    weekday = self._get_weekday(julian_day)
    moon_nak = self._get_moon_nakshatra(julian_day)
    
    if weekday == 0:  # Sunday
        if moon_nak in ['Ashwini', 'Bharani', 'Krittika']:
            special_yogas['ravi_yoga'] = True
    
    # Guru Pushya (Thursday + Pushya nakshatra)
    if weekday == 4 and moon_nak == 'Pushya':
        special_yogas['guru_pushya'] = True
    
    return special_yogas
```

### 5. Accuracy Considerations

1. **Ephemeris Precision**
   - Use high-precision ephemeris
   - Account for nutation
   - Consider aberration for exact timing

2. **Time Zone Handling**
   - Support multiple time zones
   - Handle DST transitions
   - Show times in user's preferred format

3. **Interpolation Methods**
   - Use cubic interpolation for smoother results
   - Handle retrograde motion edge cases

### 6. Performance Optimization

```python
class PanchangCache:
    """Cache panchang calculations for performance."""
    
    def __init__(self, cache_duration: int = 3600):
        self.cache = {}
        self.cache_duration = cache_duration
    
    def get_or_calculate(self, jd: float, calc_func):
        """Get from cache or calculate."""
        cache_key = f"{jd:.6f}"
        
        if cache_key in self.cache:
            cached_time, cached_value = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_value
        
        # Calculate and cache
        value = calc_func(jd)
        self.cache[cache_key] = (time.time(), value)
        return value
```

This implementation provides accurate panchang element transition times matching traditional formats.