# VedicAstroAPI Validation Approach

## Overview

We're using VedicAstroAPI as a reference source to validate our astrology calculations. This document outlines our comprehensive validation strategy.

## Test Data Collection

### 1. Test Cases Created
- **Celebrity Charts**: Einstein, Jung, Marie Curie, Steve Jobs (verified birth data)
- **Geographic Edge Cases**: Polar regions, equatorial locations, international date line
- **Astronomical Events**: Eclipses, equinoxes, solstices, retrograde stations
- **Time Edge Cases**: Midnight births, DST transitions
- **Random Cases**: 100+ generated cases covering global locations and dates

### 2. API Endpoints Used
```yaml
Core Calculations:
- /horoscope/planet-details          # Planetary positions
- /extended-horoscope/extended-kundli-details  # Full chart data
- /western/planet-details            # Western positions for cross-validation

Vedic Specific:
- /panchang/panchang                # Tithi, nakshatra, yoga, karana
- /dashas/maha-dasha                # Vimshottari dasha periods

Matching & Analysis:
- /dosha/mangal-dosh                # Dosha calculations
- /matching/north-match             # Compatibility scoring
```

### 3. Data Storage Structure
```
test_data/vedicastro_api/
├── raw_responses/              # Original API responses
│   ├── planet_details/
│   ├── extended_kundli/
│   ├── panchang/
│   └── mahadasha/
├── processed_data/             # Extracted values for comparison
│   ├── planetary_positions.json
│   ├── ascendants.json
│   ├── house_cusps.json
│   └── panchang_elements.json
└── validation_results/         # Comparison reports
    └── validation_report_YYYYMMDD.json
```

## Validation Process

### 1. Data Collection Script
`scripts/collect_vedicastro_test_data.py`:
- Fetches data for all test cases
- Implements rate limiting (0.5s between requests)
- Saves raw responses and processed data
- Creates validation report template

### 2. Validation Script
`scripts/validate_against_vedicastro.py`:
- Loads VedicAstroAPI reference data
- Calculates same charts using our system
- Compares results within defined tolerances
- Generates accuracy reports

### 3. Validation Criteria
```python
THRESHOLDS = {
    "planetary_longitude": 0.01,   # ±0.01° (36 arcseconds)
    "planetary_latitude": 0.01,    # ±0.01°
    "ascendant": 0.1,             # ±0.1° (6 arcminutes)
    "house_cusps": 0.5,           # ±0.5° (30 arcminutes)
    "dasha_dates": 1,             # ±1 day
    "panchang_elements": "exact"   # Exact string match
}
```

## How to Run Validation

### Step 1: Collect Test Data
```bash
cd scripts
python collect_vedicastro_test_data.py
```
This will:
- Fetch data for all test cases from VedicAstroAPI
- Save responses in `test_data/vedicastro_api/`
- Process and organize data for validation

### Step 2: Run Validation
```bash
python validate_against_vedicastro.py
```
This will:
- Load reference data
- Calculate using our system
- Compare results
- Generate accuracy report

### Step 3: Review Results
Check `test_data/vedicastro_api/validation_results/` for:
- Detailed comparison reports
- Accuracy percentages
- Lists of discrepancies

## Expected Outcomes

### Success Criteria
- **Planetary Positions**: >99% accuracy (within 0.01°)
- **Ascendant**: >95% accuracy (within 0.1°)
- **House Cusps**: >90% accuracy (within 0.5°)
- **Panchang Elements**: >95% exact matches
- **Dasha Periods**: >99% accuracy (within 1 day)

### Common Discrepancies
1. **Ayanamsa Differences**: Different systems use slightly different values
2. **House Systems**: Placidus vs Equal vs Whole Sign variations
3. **Timezone Handling**: Historical timezone data differences
4. **Ephemeris Sources**: Swiss Ephemeris vs JPL variations

## Benefits of This Approach

1. **Real-World Validation**: Using a production API ensures realistic testing
2. **Comprehensive Coverage**: Tests edge cases and special astronomical events
3. **Automated Comparison**: Scripts handle bulk validation efficiently
4. **Clear Metrics**: Quantifiable accuracy measurements
5. **Continuous Testing**: Can be integrated into CI/CD pipeline

## Next Steps

1. **Fix Discrepancies**: Address any calculation differences found
2. **Expand Test Cases**: Add more edge cases as needed
3. **Performance Testing**: Compare calculation speeds
4. **API Integration Tests**: Validate our API responses match expected formats
5. **Documentation**: Update calculation docs based on findings

## API Key Security

The API key is stored in the script but should be moved to environment variables:
```bash
export VEDICASTRO_API_KEY="your-api-key-here"
```

## Conclusion

This validation approach provides confidence in our astronomical calculations by comparing against an established astrology API. The automated scripts make it easy to run comprehensive tests and track accuracy improvements over time.