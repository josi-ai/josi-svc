# Gap 04: Gulika Nakshatra Ruler Implementation Plan

## Overview
Add nakshatra ruler information to Gulika display.

**Original Format**: `GULI 84:29 PUNARVAS 2 GURU`
**Current Format**: `GULI 156:13 UTTRAPHA 1` (missing ruler and pada)

## Understanding Gulika

### Gulika Calculation
- Gulika (Mandi) is a mathematical point, not a physical planet
- Based on Saturn's portion of the day/night
- Position calculated as ascendant at Gulika time
- Moves through nakshatras like other planets

### Nakshatra Rulers
Each nakshatra is ruled by one of the nine planets:
- Ketu rules: Ashwini, Magha, Mula
- Venus rules: Bharani, Purva Phalguni, Purva Ashadha
- Sun rules: Krittika, Uttara Phalguni, Uttara Ashadha
- Moon rules: Rohini, Hasta, Shravana
- Mars rules: Mrigashira, Chitra, Dhanishta
- Rahu rules: Ardra, Swati, Shatabhisha
- Jupiter rules: Punarvasu, Vishakha, Purva Bhadrapada
- Saturn rules: Pushya, Anuradha, Uttara Bhadrapada
- Mercury rules: Ashlesha, Jyeshtha, Revati

## Implementation Steps

### 1. Update Nakshatra Ruler Mapping

```python
# src/josi/services/nakshatra_utils.py

class NakshatraUtils:
    """Utilities for nakshatra calculations and information."""
    
    NAKSHATRA_RULERS = {
        # Complete mapping with all variations
        'Ashwini': 'Ketu', 'Aswini': 'Ketu', 'ASWINI': 'Ketu',
        'Bharani': 'Venus', 'BHARANI': 'Venus',
        'Krittika': 'Sun', 'Krithika': 'Sun', 'KRITHIKA': 'Sun',
        'Rohini': 'Moon', 'ROHINI': 'Moon',
        'Mrigashira': 'Mars', 'Mrigasira': 'Mars', 'MRIGASIRA': 'Mars',
        'Ardra': 'Rahu', 'Aridra': 'Rahu', 'ARIDRA': 'Rahu',
        'Punarvasu': 'Jupiter', 'Punarvas': 'Jupiter', 'PUNARVAS': 'Jupiter',
        'Pushya': 'Saturn', 'Pushyami': 'Saturn', 'PUSHYAMI': 'Saturn',
        'Ashlesha': 'Mercury', 'Aslesha': 'Mercury', 'ASLESHA': 'Mercury',
        'Magha': 'Ketu', 'Makha': 'Ketu', 'MAKHA': 'Ketu',
        'Purva Phalguni': 'Venus', 'Purvaphalguni': 'Venus', 'Purvapha': 'Venus',
        'Uttara Phalguni': 'Sun', 'Uttaraphalguni': 'Sun', 'Uttrapha': 'Sun',
        'Hasta': 'Moon', 'HASTA': 'Moon',
        'Chitra': 'Mars', 'Chithra': 'Mars', 'CHITHRA': 'Mars',
        'Swati': 'Rahu', 'Swathi': 'Rahu', 'SWATHI': 'Rahu',
        'Vishakha': 'Jupiter', 'Visakha': 'Jupiter', 'VISAKHA': 'Jupiter',
        'Anuradha': 'Saturn', 'ANURADHA': 'Saturn',
        'Jyeshtha': 'Mercury', 'Jyeshta': 'Mercury', 'JYESHTA': 'Mercury',
        'Mula': 'Ketu', 'Moola': 'Ketu', 'MOOLA': 'Ketu',
        'Purva Ashadha': 'Venus', 'Purvashadha': 'Venus', 'Purashad': 'Venus',
        'Uttara Ashadha': 'Sun', 'Uttarashadha': 'Sun', 'Uttrasad': 'Sun',
        'Shravana': 'Moon', 'Sravana': 'Moon', 'SRAVANA': 'Moon',
        'Dhanishta': 'Mars', 'Dhanista': 'Mars', 'DHANISTA': 'Mars',
        'Shatabhisha': 'Rahu', 'Satabhis': 'Rahu', 'SATABHIS': 'Rahu',
        'Purva Bhadrapada': 'Jupiter', 'Purvabhadra': 'Jupiter', 'Purvbdra': 'Jupiter',
        'Uttara Bhadrapada': 'Saturn', 'Uttarabhadra': 'Saturn', 'Uttrbdra': 'Saturn',
        'Revati': 'Mercury', 'Revathi': 'Mercury', 'REVATHI': 'Mercury'
    }
    
    # Ruler to short form mapping for display
    RULER_SHORT_FORMS = {
        'Ketu': 'KETU',
        'Venus': 'SUKR',
        'Sun': 'SURY',
        'Moon': 'CHAN',
        'Mars': 'KUJA',
        'Rahu': 'RAHU',
        'Jupiter': 'GURU',
        'Saturn': 'SANI',
        'Mercury': 'BUDH'
    }
    
    @classmethod
    def get_nakshatra_ruler(cls, nakshatra: str) -> str:
        """Get ruler of a nakshatra, handling variations."""
        # Try exact match first
        if nakshatra in cls.NAKSHATRA_RULERS:
            return cls.NAKSHATRA_RULERS[nakshatra]
        
        # Try case-insensitive match
        nakshatra_upper = nakshatra.upper()
        for key, ruler in cls.NAKSHATRA_RULERS.items():
            if key.upper() == nakshatra_upper:
                return ruler
        
        # Try partial match
        for key, ruler in cls.NAKSHATRA_RULERS.items():
            if nakshatra_upper in key.upper() or key.upper() in nakshatra_upper:
                return ruler
        
        return 'Unknown'
    
    @classmethod
    def get_ruler_short_form(cls, ruler: str) -> str:
        """Get short form of ruler name for display."""
        return cls.RULER_SHORT_FORMS.get(ruler, ruler[:4].upper())
    
    @classmethod
    def calculate_nakshatra_pada(cls, longitude: float) -> Tuple[str, int, str]:
        """
        Calculate nakshatra, pada, and ruler from longitude.
        
        Returns:
            Tuple of (nakshatra_name, pada, ruler)
        """
        # Each nakshatra is 13°20' = 13.333... degrees
        nakshatra_span = 360.0 / 27.0
        pada_span = nakshatra_span / 4.0
        
        # Standard nakshatra names
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
            "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
            "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]
        
        # Calculate nakshatra index
        nak_index = int(longitude / nakshatra_span)
        nakshatra_name = nakshatras[nak_index]
        
        # Calculate pada
        position_in_nak = longitude % nakshatra_span
        pada = int(position_in_nak / pada_span) + 1
        
        # Get ruler
        ruler = cls.get_nakshatra_ruler(nakshatra_name)
        
        return nakshatra_name, pada, ruler
```

### 2. Update Gulika Calculation

Enhance the Gulika calculation in `panchang_calculator.py`:

```python
def calculate_gulika(self, julian_day: float, latitude: float, longitude: float,
                    sunrise_jd: float, sunset_jd: float) -> Dict:
    """Enhanced Gulika calculation with nakshatra and pada."""
    
    # ... existing Gulika calculation code ...
    
    # Calculate Gulika's longitude (ascendant at Gulika time)
    gulika_longitude = self._calculate_ascendant_at_time(gulika_time_jd, latitude, longitude)
    
    # Get nakshatra, pada, and ruler
    from .nakshatra_utils import NakshatraUtils
    nakshatra, pada, ruler = NakshatraUtils.calculate_nakshatra_pada(gulika_longitude)
    
    # Get sign
    sign_num = int(gulika_longitude / 30)
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    return {
        "longitude": round(gulika_longitude, 2),
        "sign": signs[sign_num],
        "nakshatra": nakshatra,
        "pada": pada,
        "ruler": ruler,
        "weekday": weekday,
        "portion": portion,
        "time": self._julian_to_time(gulika_time_jd)
    }
```

### 3. Update Export Format

Update the Gulika display in `generate_josi_traditional_export.py`:

```python
# Import nakshatra utils
from src.josi.services.nakshatra_utils import NakshatraUtils

# Update NAKSHATRA_RULERS to use the comprehensive mapping
NAKSHATRA_RULERS = NakshatraUtils.NAKSHATRA_RULERS

# Update Gulika display
if chart.get('panchang') and chart['panchang'].get('gulika'):
    gulika = chart['panchang']['gulika']
    guli_deg_str = format_degrees(gulika['longitude'])
    
    # Get nakshatra info
    guli_nak = gulika.get('nakshatra', '[PENDING]')
    guli_pada = gulika.get('pada', 1)
    guli_ruler = gulika.get('ruler', '')
    
    if guli_nak != '[PENDING]':
        # Format nakshatra name (abbreviated to 8 chars)
        guli_nak_short = NAKSHATRA_NAMES.get(guli_nak, guli_nak)[:8]
        
        # Get ruler short form
        guli_ruler_short = NakshatraUtils.get_ruler_short_form(guli_ruler)
        
        # Format: "GULI 84:29 PUNARVAS 2 GURU"
        lines.append(f" GULI   {guli_deg_str:<7} {guli_nak_short:<10} {guli_pada}    {guli_ruler_short:<4}")
    else:
        lines.append(f" GULI   {guli_deg_str:<7} [NAKSHATRA PENDING]")
else:
    lines.append(" GULI   [CALCULATION PENDING]")
```

### 4. Additional Enhancements

#### A. Gulika in Different House Systems
```python
def calculate_gulika_in_houses(self, gulika_longitude: float, houses: List[float]) -> int:
    """Determine which house Gulika occupies."""
    for i in range(12):
        house_start = houses[i]
        house_end = houses[(i + 1) % 12] if i < 11 else houses[0]
        
        # Handle house cusps that cross 0°
        if house_start > house_end:
            if gulika_longitude >= house_start or gulika_longitude < house_end:
                return i + 1
        else:
            if house_start <= gulika_longitude < house_end:
                return i + 1
    
    return 1  # Default to first house
```

#### B. Special Gulika Considerations
```python
class GulikaSpecialRules:
    """Special rules and significations for Gulika."""
    
    @staticmethod
    def get_gulika_effects(gulika_house: int, gulika_sign: str, 
                          gulika_nakshatra: str) -> Dict:
        """Get special effects based on Gulika's position."""
        effects = {
            'house_effects': {
                1: "Obstacles in self-development",
                2: "Financial challenges",
                3: "Issues with siblings",
                4: "Property disputes",
                5: "Challenges with children",
                6: "Health issues, but victory over enemies",
                7: "Marital challenges",
                8: "Chronic health issues",
                9: "Obstacles in fortune",
                10: "Career obstacles",
                11: "Delayed gains",
                12: "Hidden enemies, expenses"
            },
            'sign_effects': {
                'Aries': "Aggressive obstacles",
                'Taurus': "Financial delays",
                # ... etc
            }
        }
        
        return {
            'house': effects['house_effects'].get(gulika_house, ''),
            'sign': effects['sign_effects'].get(gulika_sign, '')
        }
```

### 5. Mandi vs Gulika Clarification

```python
def calculate_mandi_gulika_difference(self, weekday: int, 
                                     day_duration: float) -> Dict:
    """
    Some traditions differentiate between Mandi and Gulika.
    
    Mandi: Beginning of Saturn's portion
    Gulika: Middle of Saturn's portion
    """
    # Saturn's portion for each weekday
    saturn_portions = {
        0: 7,  # Sunday - 7th portion
        1: 6,  # Monday - 6th portion
        2: 5,  # Tuesday - 5th portion
        3: 4,  # Wednesday - 4th portion
        4: 3,  # Thursday - 3rd portion
        5: 2,  # Friday - 2nd portion
        6: 1   # Saturday - 1st portion
    }
    
    portion = saturn_portions[weekday]
    portion_duration = day_duration / 8
    
    # Mandi at start of portion
    mandi_time = (portion - 1) * portion_duration
    
    # Gulika at middle of portion
    gulika_time = mandi_time + (portion_duration / 2)
    
    return {
        'mandi_time': mandi_time,
        'gulika_time': gulika_time,
        'difference_minutes': (gulika_time - mandi_time) * 60
    }
```

### 6. Testing and Validation

```python
def test_gulika_calculations():
    """Test Gulika calculations against known values."""
    test_cases = [
        {
            'date': datetime(1998, 12, 7, 21, 15),
            'location': (13.0667, 80.2333),  # Chennai
            'expected_gulika': 84.29,
            'expected_nakshatra': 'Punarvasu',
            'expected_pada': 2,
            'expected_ruler': 'Jupiter'
        },
        # Add more test cases
    ]
    
    for test in test_cases:
        result = calculate_gulika_for_datetime(
            test['date'], 
            test['location'][0], 
            test['location'][1']
        )
        
        assert abs(result['longitude'] - test['expected_gulika']) < 0.5
        assert result['nakshatra'] == test['expected_nakshatra']
        assert result['pada'] == test['expected_pada']
        assert result['ruler'] == test['expected_ruler']
```

### 7. Display Format Variations

Different software may show Gulika differently:

```python
GULIKA_DISPLAY_FORMATS = {
    'standard': "GULI {deg:>7} {nak:<10} {pada} {ruler:<4}",
    'compact': "GUL {deg:>6} {nak:<8}",
    'detailed': "GULIKA {deg:>7} {sign:<12} {nak:<15} PADA-{pada} LORD-{ruler}",
    'western': "Gulika {deg:>7} in {sign}, {nak} ({ruler})"
}
```

This implementation ensures Gulika displays with complete nakshatra information including the ruler, matching traditional astrology software formats.