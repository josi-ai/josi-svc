# Gap 01: Tamil Calendar Information Implementation Plan

## Overview
Implement Tamil calendar month, paksha, tithi number, and day/night indicator display.

**Original Format**: `BAHDANYA KARTHIKA 22 NIGHT`
**Current Format**: `[PANCHANG DATA PENDING]`

## Understanding Tamil Calendar

### Tamil Months (Solar)
1. Chithirai (Apr 14 - May 14)
2. Vaikasi (May 15 - Jun 14)
3. Aani (Jun 15 - Jul 15)
4. Aadi (Jul 16 - Aug 16)
5. Aavani (Aug 17 - Sep 16)
6. Purattasi (Sep 17 - Oct 16)
7. Aippasi (Oct 17 - Nov 15)
8. Karthigai (Nov 16 - Dec 15)
9. Margazhi (Dec 16 - Jan 13)
10. Thai (Jan 14 - Feb 12)
11. Maasi (Feb 13 - Mar 13)
12. Panguni (Mar 14 - Apr 13)

### Tamil Pakshas
- **Shukla Paksha**: Waxing Moon (Valarpirai)
- **Krishna Paksha**: Waning Moon (Theipirai)

### Tamil Tithis
1. Prathamai (1st)
2. Dvitiya (2nd)
3. Tritiya (3rd)
4. Chaturthi (4th)
5. Panchami (5th)
6. Shashti (6th)
7. Saptami (7th)
8. Ashtami (8th)
9. Navami (9th)
10. Dasami (10th)
11. Ekadasi (11th)
12. Dwadasi (12th)
13. Trayodasi (13th)
14. Chaturdasi (14th)
15. Pournami/Amavasya (15th)

### Additional Terms
- **Bahdanya**: Refers to auspicious/inauspicious nature
- **Day/Night**: Based on birth time relative to sunrise/sunset

## Implementation Steps

### 1. Create Tamil Calendar Module

```python
# src/josi/services/tamil_calendar.py

class TamilCalendar:
    """Calculate Tamil calendar elements for astrology."""
    
    TAMIL_MONTHS = [
        ('Chithirai', 14, 4),   # Start day, month
        ('Vaikasi', 15, 5),
        ('Aani', 15, 6),
        ('Aadi', 16, 7),
        ('Aavani', 17, 8),
        ('Purattasi', 17, 9),
        ('Aippasi', 17, 10),
        ('Karthigai', 16, 11),
        ('Margazhi', 16, 12),
        ('Thai', 14, 1),
        ('Maasi', 13, 2),
        ('Panguni', 14, 3)
    ]
    
    TAMIL_WEEKDAYS = {
        0: 'Nyayiru',    # Sunday
        1: 'Thingal',    # Monday
        2: 'Sevvai',     # Tuesday
        3: 'Budhan',     # Wednesday
        4: 'Viyazhan',   # Thursday
        5: 'Velli',      # Friday
        6: 'Sani'        # Saturday
    }
    
    TAMIL_TITHI_NAMES = {
        1: 'Prathamai',
        2: 'Dvitiya',
        3: 'Tritiya',
        4: 'Chaturthi',
        5: 'Panchami',
        6: 'Shashti',
        7: 'Saptami',
        8: 'Ashtami',
        9: 'Navami',
        10: 'Dasami',
        11: 'Ekadasi',
        12: 'Dwadasi',
        13: 'Trayodasi',
        14: 'Chaturdasi',
        15: 'Pournami'  # or Amavasya
    }
    
    def get_tamil_month(self, date: datetime) -> str:
        """Get Tamil month based on solar calendar."""
        day = date.day
        month = date.month
        
        for i, (tamil_month, start_day, start_month) in enumerate(self.TAMIL_MONTHS):
            next_idx = (i + 1) % 12
            next_day, next_month = self.TAMIL_MONTHS[next_idx][1], self.TAMIL_MONTHS[next_idx][2]
            
            # Handle year boundary
            if start_month > next_month:  # December to January
                if month == start_month and day >= start_day:
                    return tamil_month
                elif month == next_month and day < next_day:
                    return tamil_month
            else:  # Normal months
                if month == start_month and day >= start_day:
                    if month == next_month:
                        if day < next_day:
                            return tamil_month
                    else:
                        return tamil_month
                elif start_month < month < next_month:
                    return tamil_month
        
        return self.TAMIL_MONTHS[0][0]  # Default
    
    def get_bahdanya_classification(self, tithi: int, nakshatra: str, 
                                   weekday: int, yoga: str) -> str:
        """
        Determine Bahdanya (auspicious/inauspicious) classification.
        This is a simplified version - full calculation is complex.
        """
        # Inauspicious combinations (simplified)
        inauspicious_tithis = [4, 8, 9, 14]  # Chaturthi, Ashtami, Navami, Chaturdasi
        inauspicious_nakshatras = ['Bharani', 'Krittika', 'Ashlesha', 'Jyeshtha']
        
        if tithi in inauspicious_tithis:
            return 'DURMUHURTHA'
        elif nakshatra in inauspicious_nakshatras:
            return 'DURYOGA'
        else:
            return 'BAHDANYA'
    
    def format_tamil_panchang_line(self, date: datetime, tithi_info: dict, 
                                  nakshatra: str, sunrise: datetime, 
                                  sunset: datetime) -> str:
        """Format the Tamil panchang line for export."""
        # Get Tamil month
        tamil_month = self.get_tamil_month(date)
        
        # Get tithi number and paksha
        tithi_num = tithi_info['number']
        paksha = tithi_info['paksha']
        
        # Tamil paksha names
        tamil_paksha = 'VALARPIRAI' if paksha == 'Shukla' else 'THEIPIRAI'
        
        # Day/Night determination
        birth_hour = date.hour + date.minute / 60.0
        sunrise_hour = sunrise.hour + sunrise.minute / 60.0
        sunset_hour = sunset.hour + sunset.minute / 60.0
        
        day_night = 'DAY' if sunrise_hour <= birth_hour < sunset_hour else 'NIGHT'
        
        # Bahdanya classification
        weekday = date.weekday()
        bahdanya = self.get_bahdanya_classification(
            tithi_num, nakshatra, weekday, ''
        )
        
        # Format: "BAHDANYA KARTHIKA 22 NIGHT"
        # Note: The number might refer to the lunar day in Tamil calendar
        tamil_day = date.day  # This needs more research for exact calculation
        
        return f"{bahdanya} {tamil_month.upper()} {tamil_day} {day_night}"
```

### 2. Integration with Panchang Calculator

Update `panchang_calculator.py`:

```python
def calculate_panchang(self, julian_day: float, sun_longitude: float, 
                      moon_longitude: float, latitude: float, 
                      longitude: float) -> Dict:
    """Enhanced panchang with Tamil calendar."""
    
    # Existing calculations...
    
    # Add Tamil calendar info
    from .tamil_calendar import TamilCalendar
    tamil_cal = TamilCalendar()
    
    dt = self._julian_to_datetime(julian_day)
    
    # Get Tamil panchang line
    tamil_info = tamil_cal.format_tamil_panchang_line(
        dt, tithi, nakshatra_name, 
        sunrise_dt, sunset_dt
    )
    
    return {
        'tithi': tithi,
        'yoga': yoga,
        'karana': karana,
        'sunrise': sunrise,
        'sunset': sunset,
        'sidereal_time': sidereal_time,
        'gulika': gulika,
        'tamil_panchang': tamil_info  # New field
    }
```

### 3. Update Export Format

In `generate_josi_traditional_export.py`:

```python
# Replace the placeholder line
if chart.get('panchang') and chart['panchang'].get('tamil_panchang'):
    tamil_line = chart['panchang']['tamil_panchang']
else:
    tamil_line = "[TAMIL PANCHANG PENDING]"

# Line 4 of export
lines.append(f" {tamil_line:<40} PLACE:{lat_str} {lon_str} {person['place_of_birth']:<20}")
```

### 4. Additional Enhancements

#### A. Lunar Day Calculation
The "22" in the example might refer to:
- Lunar day count from new moon
- Tamil calendar day
- Special calculation based on nakshatra

#### B. Special Day Classifications
```python
SPECIAL_DAYS = {
    'Akshaya Tritiya': (2, 3),      # Vaikasi Tritiya
    'Thai Pusam': (10, 'Pushya'),   # Thai month, Pushya star
    'Karthigai Deepam': (7, 'Krittika')  # Karthigai month, Krittika star
}
```

#### C. Festival Integration
```python
def get_festival_info(self, date: datetime, tithi: int, 
                     nakshatra: str, tamil_month: str) -> Optional[str]:
    """Check if date corresponds to any Tamil festival."""
    festivals = {
        ('Thai', 1): 'Thai Pongal',
        ('Aadi', 18): 'Aadi Perukku',
        ('Aavani', 'Hasta'): 'Vinayagar Chaturthi',
        # ... more festivals
    }
    # Implementation...
```

### 5. Testing Requirements

1. **Date Range Testing**
   - Test all 12 Tamil months
   - Verify month transitions
   - Handle leap years

2. **Accuracy Verification**
   - Compare with Tamil panchangam
   - Verify against traditional calendars
   - Cross-check with existing astrology software

3. **Edge Cases**
   - Birth at exact sunrise/sunset
   - Month transition dates
   - Regional variations

### 6. Data Sources

1. **Tamil Almanac Data**
   - Government Tamil calendar
   - Vakya Panchangam
   - Drik Panchangam

2. **Calculation Methods**
   - Solar month determination
   - Adhika masa (intercalary month) handling
   - Regional variations (Chennai vs other regions)

### 7. Future Enhancements

1. **Regional Variations**
   - Different Tamil regions may have slight variations
   - Support for Sri Lankan Tamil calendar
   - Malaysian/Singapore Tamil calendar

2. **Additional Information**
   - Rahu Kalam for the day
   - Gulika Kalam
   - Yamagandam

3. **Auspicious Timing**
   - Abhijit Muhurta
   - Amrita Kalam
   - Varjyam periods

This implementation will provide authentic Tamil calendar information matching traditional astrology software formats.