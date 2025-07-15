# Indian Family Test Cases - Quick Reference

## Family Members

### 1. **Panneerselvam Chandrasekaran** (Father)
- **DOB**: August 20, 1954
- **TOB**: 6:20 PM (18:20)
- **Place**: Kanchipuram, Tamil Nadu
- **Coordinates**: 12.8185°N, 79.6947°E
- **Age**: 70 years (as of 2024)

### 2. **Valarmathi Kannappan** (Mother)
- **DOB**: February 11, 1961
- **TOB**: 3:30 PM (15:30)
- **Place**: Kovur, Tamil Nadu
- **Coordinates**: 13.1622°N, 80.0050°E
- **Age**: 63 years (as of 2024)

### 3. **Janaki Panneerselvam** (Daughter)
- **DOB**: December 18, 1982
- **TOB**: 10:10 AM
- **Place**: Chennai, Tamil Nadu
- **Coordinates**: 13.0827°N, 80.2707°E
- **Age**: 41 years (as of 2024)

### 4. **Govindarajan Panneerselvam** (Son)
- **DOB**: December 29, 1989
- **TOB**: 12:12 PM
- **Place**: Chennai, Tamil Nadu
- **Coordinates**: 13.0827°N, 80.2707°E
- **Age**: 34 years (as of 2024)

## Test Scenarios

### Individual Chart Analysis
- Vedic charts for all 4 members
- Dasha periods comparison
- Planetary strengths
- Dosha analysis

### Family Compatibility Tests
1. **Spouse Compatibility**: Panneerselvam & Valarmathi
2. **Parent-Child**: 
   - Father-Daughter
   - Father-Son
   - Mother-Daughter
   - Mother-Son
3. **Sibling Compatibility**: Janaki & Govindarajan

### Special Astrological Features
- **Panneerselvam**: Evening birth, temple city
- **Valarmathi**: Afternoon birth, coastal influence
- **Janaki**: Morning birth, Saturn return age
- **Govindarajan**: Noon birth, year-end birth

## API Test Commands

```bash
# Collect data for all family members
python scripts/collect_vedicastro_test_data.py

# Files created:
# - collected_Panneerselvam_Chandrasekaran.json
# - collected_Valarmathi_Kannappan.json
# - collected_Janaki_Panneerselvam.json
# - collected_Govindarajan_Panneerselvam.json

# Validate our calculations
python scripts/validate_against_vedicastro.py

# Check specific person
python scripts/test_data_utilities.py --person "Panneerselvam_Chandrasekaran"
```

## Expected Validations

1. **Planetary Positions**: All 4 charts
2. **Ascendant/Lagna**: Different times = different ascendants
3. **Dasha Periods**: 
   - Current dashas for each person
   - Birth dasha balance
4. **Panchang Elements**: 
   - Different tithis, nakshatras
   - Tamil calendar considerations
5. **Compatibility Scores**:
   - Ashtakoota matching
   - Dashkoota matching

## Benefits for Testing

1. **Real Family Data**: Actual birth data, not synthetic
2. **IST Timezone**: Tests half-hour timezone offset
3. **Tamil Nadu Region**: Consistent geographic area
4. **Age Range**: 34-70 years, different life stages
5. **Relationship Testing**: Parent-child, siblings, spouses
6. **Different Birth Times**: Morning, afternoon, evening, noon