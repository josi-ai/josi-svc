# Vedic Astrology Calculations Implementation Plan

## Overview
This document outlines the implementation plan for all missing calculations marked as [CALCULATION PENDING] in the traditional export format.

## Priority Order (Based on Importance)

### 1. 🌙 Panchang Calculations (HIGH PRIORITY)
These are fundamental to Vedic astrology and should be implemented first.

#### a) Tithi (Lunar Day)
- **Formula**: Based on the angular distance between Sun and Moon
- **Calculation**: `(Moon_longitude - Sun_longitude) / 12`
- **Types**: 30 tithis (15 in Shukla Paksha, 15 in Krishna Paksha)
- **Implementation**: Add to `astrology_service.py`

#### b) Yoga (Sun-Moon Yoga)
- **Formula**: `(Sun_longitude + Moon_longitude) / 13.333`
- **Types**: 27 Yogas (Vishkumbha to Vaidhriti)
- **Implementation**: Create yoga calculation method

#### c) Karana (Half Tithi)
- **Formula**: Half of a tithi, 60 karanas in a lunar month
- **Calculation**: `(Moon_longitude - Sun_longitude) / 6`
- **Types**: 11 karanas (4 fixed, 7 movable)

#### d) Sunrise/Sunset Times
- **Library**: Use `skyfield` or `pyephem`
- **Input**: Date, latitude, longitude
- **Output**: Local sunrise and sunset times

#### e) Sidereal Time
- **Formula**: Local Sidereal Time (LST) calculation
- **Implementation**: Use Swiss Ephemeris `swe.sidtime()`

### 2. 🪐 Gulika/Mandi Position (HIGH PRIORITY)
- **Concept**: Upagraha (sub-planet) based on Saturn
- **Calculation**: Based on day/night duration and weekday
- **Formula**: Specific time periods ruled by Saturn's son
- **Implementation**: New method in astrology service

### 3. 📅 Dasa-Bhukti System (HIGH PRIORITY)
- **System**: Vimshottari Dasa (120-year cycle)
- **Starting Point**: Based on Moon's nakshatra at birth
- **Sequence**: Ketu(7), Venus(20), Sun(6), Moon(10), Mars(7), Rahu(18), Jupiter(16), Saturn(19), Mercury(17)
- **Balance**: Calculate remaining dasa at birth
- **Implementation**: Create `DasaCalculator` class

### 4. 🏠 Bhava (House) Calculations (MEDIUM PRIORITY)
- **Current**: We have house positions
- **Needed**: Bhava Madhya (house midpoints)
- **Formula**: Based on ascendant and house system
- **Implementation**: Enhance existing house calculations

### 5. 📊 Divisional Charts (MEDIUM PRIORITY)
- **Priority Order**:
  1. Navamsa (D9) - Marriage/Dharma
  2. Hora (D2) - Wealth
  3. Drekkana (D3) - Siblings
  4. Saptamsa (D7) - Children
  5. Dasamsa (D10) - Career
  6. Dwadasamsa (D12) - Parents
  7. Trimsamsa (D30) - Misfortunes

### 6. 💪 Strength Calculations (MEDIUM PRIORITY)
- **Shadbala**: Six-fold planetary strength
  - Sthana Bala (Positional)
  - Dig Bala (Directional)
  - Kala Bala (Temporal)
  - Chesta Bala (Motional)
  - Naisargika Bala (Natural)
  - Drik Bala (Aspectual)
- **Bhava Bala**: House strengths
- **Residential Strength**: Planet's strength in signs

### 7. 🔢 Ashtakavarga (LOW PRIORITY)
- **Concept**: Point system for transits
- **Calculation**: Complex matrix calculations
- **Implementation**: Create `AshtakavargaCalculator`

## Implementation Strategy

### Phase 1: Core Panchang (Week 1-2)
```python
# Add to astrology_service.py
def calculate_tithi(sun_lon: float, moon_lon: float) -> dict:
    """Calculate lunar day (tithi)"""
    diff = (moon_lon - sun_lon) % 360
    tithi_num = int(diff / 12) + 1
    # Return tithi name, paksha, percentage
    
def calculate_yoga(sun_lon: float, moon_lon: float) -> dict:
    """Calculate Sun-Moon yoga"""
    total = (sun_lon + moon_lon) % 360
    yoga_num = int(total / 13.333333) + 1
    # Return yoga name and end time
    
def calculate_karana(sun_lon: float, moon_lon: float) -> dict:
    """Calculate half-tithi (karana)"""
    diff = (moon_lon - sun_lon) % 360
    karana_num = int(diff / 6) + 1
    # Return karana name and end time
```

### Phase 2: Time Calculations (Week 2-3)
```python
def calculate_sunrise_sunset(date: datetime, lat: float, lon: float) -> dict:
    """Calculate sunrise and sunset times"""
    # Use skyfield or pyephem
    
def calculate_sidereal_time(dt: datetime, lon: float) -> str:
    """Calculate local sidereal time"""
    # Use Swiss Ephemeris
```

### Phase 3: Dasa System (Week 3-4)
```python
class DasaCalculator:
    def calculate_vimshottari_dasa(self, moon_longitude: float, birth_date: datetime) -> dict:
        """Calculate complete Vimshottari dasa periods"""
        # Get nakshatra and pada
        # Calculate balance of birth dasa
        # Generate all dasa-bhukti periods
```

### Phase 4: Advanced Calculations (Week 4-6)
- Implement divisional charts
- Add strength calculations
- Create Ashtakavarga system

## Required Libraries

### Existing
- `pyswisseph` - Already used for planetary positions
- `skyfield` - For astronomical calculations

### May Need to Add
- `pyephem` - Alternative for sunrise/sunset
- Custom implementations for Vedic-specific calculations

## Testing Strategy

1. **Unit Tests**: For each calculation method
2. **Validation**: Compare with:
   - VedicAstroAPI results
   - Professional software outputs
   - Published ephemeris data
3. **Test Data**: Use our 5 test persons

## API Integration

### Enhance Chart Response
```python
{
    "planets": {...},  # Existing
    "houses": {...},   # Existing
    "panchang": {      # New
        "tithi": {"name": "Panchami", "paksha": "Krishna", "percent": 45.2},
        "yoga": {"name": "Indra", "end_time": "15:47"},
        "karana": {"name": "Kaulava", "end_time": "21:56"},
        "sunrise": "06:22",
        "sunset": "17:38",
        "sidereal_time": "2:10:47"
    },
    "upagrahas": {     # New
        "gulika": {"longitude": 84.29, "sign": "Gemini", "nakshatra": "Punarvasu"}
    },
    "dasa": {          # New
        "current": {
            "major": "Ketu",
            "minor": "Saturn",
            "end_date": "2024-02-12"
        },
        "birth_balance": {"years": 2, "months": 2, "days": 2}
    }
}
```

## Priority Implementation Order

1. **Immediate (This Week)**:
   - Tithi calculation
   - Yoga calculation
   - Karana calculation
   - Sunrise/Sunset

2. **Next Week**:
   - Gulika/Mandi
   - Sidereal Time
   - Basic Dasa calculation

3. **Following Weeks**:
   - Complete Dasa-Bhukti
   - Navamsa chart
   - Basic Shadbala

4. **Future**:
   - All divisional charts
   - Complete strength calculations
   - Ashtakavarga system

## Success Metrics

- All [CALCULATION PENDING] replaced with actual values
- Accuracy within 1 minute for time calculations
- Dasa calculations match professional software
- Export format shows no placeholders for Phase 1 items

This phased approach ensures we implement the most important calculations first, allowing the traditional export to show meaningful data progressively.