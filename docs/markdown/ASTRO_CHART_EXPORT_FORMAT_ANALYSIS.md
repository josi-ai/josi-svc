# Astro Chart Export Format Analysis

## Overview
The astro-chart-export files contain comprehensive Vedic astrology chart data in a text-based format. The data is organized into multiple sections providing detailed astrological calculations and positions.

## Sections Breakdown

### 1. Header Information (Lines 1-7)
- **Title**: Person's name with software version
- **Birth Details**:
  - Date of birth with day name
  - Time of birth in IST with timezone
  - Place coordinates (latitude/longitude) with city name
- **Astronomical Data**:
  - Sidereal time
  - Ayanamsa value
  - Sunrise/Sunset times
- **Panchang Details**:
  - Nakshatra (star) with pada and duration
  - Tithi (lunar day) with timing
  - Yoga with timing
  - Karana with timing

### 2. Planetary Positions (Lines 9-19)
**Nirayana Longitudes** - Sidereal positions of planets:
- Format: PLANET DEG:MIN STAR PADA RULER
- Includes: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu, Lagna (Ascendant), Gulika
- Shows retrograde planets

### 3. Chart Diagrams (Lines 21-45)
Two visual charts side by side:
- **RASI Chart** (Birth Chart): Shows planetary positions in 12 houses
- **NAVAMSA Chart** (D9 Divisional Chart): Shows navamsa positions
- Format: ASCII box diagrams with planet abbreviations

### 4. Dasha Information (Lines 47-84)
- **Current Dasha**: Shows remaining years/months/days at birth
- **Running Period**: Current dasha-bhukti with end date
- **Dasha Sequence**: Detailed sub-periods for each planet
- **Complete Dasha Table**: All major and minor periods with dates

### 5. Bhava Chart (Lines 86-118)
- **Bhava Diagram**: House cusps chart
- **Bhava Details Table**:
  - House number
  - Middle degree
  - Starting degree
  - Rasi (sign) lord
  - Star (nakshatra) lord

### 6. Strength Calculations (Lines 120-122)
**Residential Strength**: Numerical values for each planet (0-1 scale)

### 7. Varga Charts (Lines 126-137)
Divisional chart positions for each planet in:
- Rasi, Hora, Drekkana, Saptamsa, Navamsa, Dwadasamsa, Trimsamsa, Dasamsa

### 8. Ashtakavarga (Lines 139-149)
- Benefic points for each planet in each sign
- Format: Points(Kakshya)
- Sarva Ashtakavarga totals

### 9. Sodya Pinda (Lines 151-154)
Three types of pinda calculations:
- Rasi Pinda
- Graha Pinda
- Sodya Pinda

### 10. Shadbala (Lines 156-185)
Comprehensive strength analysis:
- **Six Types of Strength**:
  - Sthana (Positional)
  - Dig (Directional)
  - Chesta (Motional)
  - Naisargika (Natural)
  - Kala (Temporal)
  - Drishti (Aspectual)
- **Total Shadbala** and relative strength
- **Ishta/Kashta Bala**: Benefic and malefic strength
- **Bhava Bala**: House strengths

## Data Fields to Extract

### Person Information
- Name
- Date of Birth
- Time of Birth
- Place of Birth (City, Coordinates)
- Gender (if available)

### Astronomical Data
- Ayanamsa
- Sidereal Time
- Sunrise/Sunset
- Timezone

### Planetary Positions
- Longitude for each planet
- Sign placement
- Nakshatra and pada
- Retrograde status

### Charts
- Rasi chart positions
- Navamsa positions
- House cusps

### Timing
- Current dasha-bhukti
- Nakshatra details
- Panchang elements

### Strengths
- Shadbala values
- Residential strength
- Bhava bala

## Implementation Notes

To generate similar exports, we need:
1. Precise astronomical calculations
2. Vedic astrology specific calculations (Ayanamsa, Nakshatras, Dashas)
3. Multiple divisional charts
4. Strength calculations (Shadbala)
5. ASCII chart rendering
6. Proper formatting for fixed-width display

The format appears to be from a traditional Vedic astrology software (Version 6.1 from 1991), maintaining compatibility with older systems while providing comprehensive astrological data.