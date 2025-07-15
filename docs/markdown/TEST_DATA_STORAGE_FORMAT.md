# Test Data Storage Format Guide

## Overview
This document describes how test data from VedicAstroAPI is stored and organized for validation purposes.

## 1. Raw API Responses

### Location: `test_data/vedicastro_api/raw_responses/{endpoint_name}/{test_case}_{endpoint}.json`

### Example: `Albert_Einstein_planet_details.json`
```json
{
  "status": 200,
  "response": [
    {
      "name": "Sun",
      "longitude": 353.5234,
      "latitude": 0.0001,
      "speed": 0.9856,
      "retrograde": false,
      "sign": "Pisces",
      "degree": 23.5234,
      "house": 8
    },
    {
      "name": "Moon",
      "longitude": 254.3421,
      "latitude": -4.2341,
      "speed": 12.3456,
      "retrograde": false,
      "sign": "Sagittarius",
      "degree": 14.3421,
      "house": 4
    }
    // ... other planets
  ],
  "remaining_api_calls": 393498
}
```

## 2. Individual Test Case Files

### Location: `test_data/vedicastro_api/collected_{test_case_name}.json`

### Example: `collected_Albert_Einstein.json`
```json
{
  "test_case": {
    "name": "Albert_Einstein",
    "dob": "14/03/1879",
    "tob": "11:30",
    "lat": 48.4011,
    "lon": 9.9876,
    "tz": 1
  },
  "timestamp": "2024-12-15T10:30:45.123456",
  "data": {
    "planet_details": {
      // Planetary positions data
    },
    "extended_kundli": {
      // Chart details including houses, ascendant
    },
    "panchang": {
      // Tithi, nakshatra, yoga, karana
    },
    "mahadasha": {
      // Dasha periods and dates
    },
    "western_planets": {
      // Western astrology positions
    }
  }
}
```

## 3. Processed Data Files

### A. Planetary Positions
**Location**: `test_data/vedicastro_api/processed_data/planetary_positions.json`

```json
[
  {
    "test_case": "Albert_Einstein",
    "planet": "Sun",
    "longitude": 353.5234,
    "latitude": 0.0001,
    "speed": 0.9856,
    "retrograde": false
  },
  {
    "test_case": "Albert_Einstein",
    "planet": "Moon",
    "longitude": 254.3421,
    "latitude": -4.2341,
    "speed": 12.3456,
    "retrograde": false
  },
  // ... all planets for all test cases
]
```

### B. House Cusps
**Location**: `test_data/vedicastro_api/processed_data/house_cusps.json`

```json
[
  {
    "test_case": "Albert_Einstein",
    "house": 1,
    "cusp": 101.3456,
    "sign": "Cancer"
  },
  {
    "test_case": "Albert_Einstein",
    "house": 2,
    "cusp": 124.5678,
    "sign": "Leo"
  },
  // ... all 12 houses for all test cases
]
```

### C. Ascendants
**Location**: `test_data/vedicastro_api/processed_data/ascendants.json`

```json
[
  {
    "test_case": "Albert_Einstein",
    "ascendant": "Cancer",
    "ascendant_degree": 11.3456
  },
  {
    "test_case": "Carl_Jung",
    "ascendant": "Aquarius",
    "ascendant_degree": 26.7890
  }
  // ... for all test cases
]
```

### D. Panchang Elements
**Location**: `test_data/vedicastro_api/processed_data/panchang_elements.json`

```json
[
  {
    "test_case": "Albert_Einstein",
    "tithi": "Shukla Dashami",
    "nakshatra": "Mula",
    "yoga": "Vishkumbha",
    "karana": "Vanija"
  }
  // ... for all test cases
]
```

### E. Dasha Periods
**Location**: `test_data/vedicastro_api/processed_data/dasha_periods.json`

```json
[
  {
    "test_case": "Albert_Einstein",
    "dasha_order": ["Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun"],
    "start_dates": [
      "Fri Jun 28 1875",
      "Sun Jun 28 1885",
      "Tue Jun 28 1892"
      // ... remaining dates
    ],
    "remaining_at_birth": "3 years 7 months 14 days"
  }
  // ... for all test cases
]
```

## 4. Complete Dataset File

### Location: `test_data/vedicastro_api/complete_dataset.json`

```json
{
  "collection_date": "2024-12-15T10:30:45.123456",
  "api_key_used": "30548028-0...",  // Partial key for security
  "test_cases": [
    {
      "test_case": { /* test case details */ },
      "timestamp": "2024-12-15T10:30:45.123456",
      "data": { /* all API responses */ }
    },
    // ... all test cases
  ]
}
```

## 5. Validation Results

### Location: `test_data/vedicastro_api/validation_results/validation_report_YYYYMMDD_HHMMSS.json`

```json
{
  "validation_date": "2024-12-15T14:30:22.123456",
  "summary": {
    "total_tests": 150,
    "passed": 145,
    "failed": 5,
    "accuracy_percentage": 96.67
  },
  "categories": [
    {
      "category": "planetary_positions",
      "total_tests": 90,
      "passed": 88,
      "failed": 2,
      "details": [
        {
          "test_case": "Albert_Einstein",
          "planet": "Sun",
          "reference": 353.5234,
          "calculated": 353.5245,
          "difference": 0.0011,
          "threshold": 0.01,
          "passed": true
        }
        // ... all test results
      ]
    },
    {
      "category": "ascendants",
      "total_tests": 10,
      "passed": 9,
      "failed": 1,
      "details": [ /* ... */ ]
    }
  ],
  "discrepancies": [
    {
      "test_case": "Polar_Region_Test",
      "planet": "Moon",
      "reference": 123.4567,
      "calculated": 123.5678,
      "difference": 0.1111,
      "threshold": 0.01,
      "passed": false
    }
    // ... all failures
  ],
  "thresholds_used": {
    "planetary_longitude": 0.01,
    "planetary_latitude": 0.01,
    "ascendant": 0.1,
    "house_cusps": 0.5,
    "dasha_dates": 1
  }
}
```

## 6. How to Access the Data

### Python Examples:

```python
import json
from pathlib import Path

# Load all planetary positions
with open('test_data/vedicastro_api/processed_data/planetary_positions.json', 'r') as f:
    planetary_data = json.load(f)

# Get positions for a specific test case
einstein_planets = [p for p in planetary_data if p['test_case'] == 'Albert_Einstein']

# Load complete dataset
with open('test_data/vedicastro_api/complete_dataset.json', 'r') as f:
    all_data = json.load(f)

# Access specific API response
for test in all_data['test_cases']:
    if test['test_case']['name'] == 'Albert_Einstein':
        planet_details = test['data']['planet_details']
        break
```

## 7. Data Retention Strategy

1. **Raw Responses**: Keep indefinitely for debugging
2. **Processed Data**: Update when re-running collection
3. **Validation Results**: Keep history of all runs
4. **Complete Dataset**: Archive previous versions

## 8. Backup Recommendation

```bash
# Backup entire test data directory
tar -czf test_data_backup_$(date +%Y%m%d).tar.gz test_data/

# Or use git to track changes
git add test_data/
git commit -m "Test data snapshot $(date +%Y-%m-%d)"
```

## Benefits of This Structure

1. **Traceability**: Can trace any result back to original API response
2. **Efficiency**: Processed data allows quick validation without re-parsing
3. **Debugging**: Raw responses help identify API changes or issues
4. **History**: Validation reports track accuracy improvements over time
5. **Flexibility**: Easy to add new test cases or endpoints