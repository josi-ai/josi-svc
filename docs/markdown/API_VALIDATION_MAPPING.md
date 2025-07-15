# API Validation Mapping: Our APIs vs VedicAstroAPI

## APIs We Can Validate

### 1. **Chart Calculations** ✅
**Our API**: `/api/v1/charts/calculate`
**VedicAstroAPI Endpoints**:
- `/horoscope/planet-details` - Planetary positions
- `/extended-horoscope/extended-kundli-details` - Full chart with houses
- `/western/planet-details` - Western planetary positions

**What We Can Validate**:
- Planetary longitudes (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- Planetary latitudes and speeds
- Retrograde status
- Ascendant degree
- House cusps (12 houses)
- Zodiac sign placements

### 2. **Panchang Calculations** ✅
**Our API**: `/api/v1/panchang/calculate`
**VedicAstroAPI Endpoints**:
- `/panchang/panchang` - All panchang elements

**What We Can Validate**:
- Tithi (lunar day)
- Nakshatra (lunar mansion)
- Yoga
- Karana
- Sunrise/Sunset times
- Moonrise/Moonset times

### 3. **Dasha Calculations** ✅
**Our API**: `/api/v1/dashas/vimshottari`
**VedicAstroAPI Endpoints**:
- `/dashas/maha-dasha` - Main periods
- `/dashas/antardasha` - Sub-periods
- `/dashas/current-mahadasha` - Current running dasha

**What We Can Validate**:
- Mahadasha order
- Start and end dates
- Remaining dasha at birth
- Current dasha/antardasha

### 4. **Compatibility Matching** ✅
**Our API**: `/api/v1/compatibility/ashtakoota`
**VedicAstroAPI Endpoints**:
- `/matching/north-match` - North Indian matching
- `/matching/south-match` - South Indian matching

**What We Can Validate**:
- Individual guna scores (8 categories)
- Total compatibility score
- Dosha analysis in matching

### 5. **Divisional Charts** ✅
**Our API**: `/api/v1/charts/{chart_id}/divisional`
**VedicAstroAPI Endpoints**:
- `/horoscope/divisional-charts` - D1-D60 charts

**What We Can Validate**:
- D9 (Navamsa) positions
- D10 (Dashamsa) positions
- Other divisional chart placements

### 6. **Dosha Analysis** ✅
**Our API**: `/api/v1/charts/{chart_id}/doshas`
**VedicAstroAPI Endpoints**:
- `/dosha/mangal-dosh` - Manglik analysis
- `/dosha/kaalsarp-dosh` - Kaal Sarp analysis
- `/dosha/pitra-dosh` - Pitra dosha

**What We Can Validate**:
- Dosha presence (true/false)
- Dosha severity/score
- Contributing factors

### 7. **Planetary Aspects** ✅
**Our API**: `/api/v1/charts/{chart_id}/aspects`
**VedicAstroAPI Endpoints**:
- `/horoscope/planetary-aspects` - Vedic aspects
- `/western/aspects` - Western aspects

**What We Can Validate**:
- Aspect relationships
- Aspect degrees/orbs
- Aspect types

### 8. **Ayanamsa Values** ✅
**Our API**: Internal calculations
**VedicAstroAPI**: Uses in all Vedic calculations

**What We Can Validate**:
- Lahiri ayanamsa values
- Krishnamurti ayanamsa values
- Other ayanamsa systems

## APIs We CANNOT Validate (No VedicAstroAPI Equivalent)

### 1. **Advanced Features** ❌
- `/api/v1/charts/{chart_id}/yogas` - Specific yoga combinations
- `/api/v1/charts/{chart_id}/strengths` - Shadbala calculations (partial data available)
- `/api/v1/transits/current` - Real-time transits (they have transit dates only)

### 2. **AI/ML Features** ❌
- `/api/v1/ai/interpret` - Our AI interpretations
- `/api/v1/ai/neural-pathway` - Psychological questions
- `/api/v1/predictions/personalized` - ML-based predictions

### 3. **Marketplace Features** ❌
- `/api/v1/astrologers/*` - Astrologer management
- `/api/v1/consultations/*` - Booking system
- `/api/v1/remedies/personalized` - Custom remedies

### 4. **User Management** ❌
- `/api/v1/auth/*` - Authentication endpoints
- `/api/v1/persons/*` - User profiles

## Validation Test Script

```python
# Example validation for planetary positions
async def validate_planetary_positions():
    # Our API call
    our_chart = await calculate_chart(
        person_id=test_person_id,
        systems="vedic",
        house_system="PLACIDUS",
        ayanamsa="LAHIRI"
    )
    
    # VedicAstroAPI call
    vedic_response = call_vedicastro_api(
        "/horoscope/planet-details",
        {
            "dob": "14/03/1879",
            "tob": "11:30",
            "lat": 48.4011,
            "lon": 9.9876,
            "tz": 1
        }
    )
    
    # Compare
    for planet in our_chart["planets"]:
        vedic_planet = find_planet(vedic_response, planet["name"])
        diff = abs(planet["longitude"] - vedic_planet["longitude"])
        assert diff < 0.01, f"{planet['name']} difference: {diff}°"
```

## Validation Priority

### High Priority (Core Calculations)
1. Planetary positions
2. Ascendant and houses
3. Panchang elements
4. Dasha calculations

### Medium Priority (Derived Calculations)
1. Divisional charts
2. Compatibility matching
3. Dosha analysis
4. Aspects

### Low Priority (Nice to Have)
1. Gem suggestions
2. Rudraksha recommendations
3. Numerology calculations

## Data Collection Strategy

1. **Create Test Suite**:
   ```bash
   test_data/
   ├── planetary_validation/
   ├── panchang_validation/
   ├── dasha_validation/
   └── compatibility_validation/
   ```

2. **Run Parallel Validations**:
   - Collect VedicAstroAPI data
   - Calculate using our system
   - Compare and generate reports

3. **Continuous Monitoring**:
   - Set up daily validation runs
   - Track accuracy trends
   - Alert on significant deviations

## Success Metrics

- **Planetary Positions**: >99% within 0.01°
- **Ascendant**: >95% within 0.1°
- **Panchang**: >95% exact match
- **Dasha Dates**: >99% within 1 day
- **Compatibility Scores**: >90% within 2 points

This validation will ensure our core astrological calculations match industry standards!