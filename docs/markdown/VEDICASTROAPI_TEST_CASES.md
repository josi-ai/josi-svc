# VedicAstroAPI Test Cases for Validation

## Test Case Categories

### 1. Geographic Edge Cases

#### A. Polar Regions (High Latitudes)
```yaml
polar_test_cases:
  - name: "Reykjavik, Iceland"
    lat: 64.1466
    lon: -21.9426
    tz: 0
    test_dates: ["21/06/2024", "21/12/2024"]  # Summer/Winter solstice
    
  - name: "Murmansk, Russia"
    lat: 68.9585
    lon: 33.0827
    tz: 3
    test_dates: ["21/06/2024", "21/12/2024"]
    
  - name: "Ushuaia, Argentina"
    lat: -54.8019
    lon: -68.3030
    tz: -3
    test_dates: ["21/06/2024", "21/12/2024"]
```

#### B. Equatorial Regions
```yaml
equatorial_test_cases:
  - name: "Quito, Ecuador"
    lat: -0.1807
    lon: -78.4678
    tz: -5
    test_dates: ["20/03/2024", "23/09/2024"]  # Equinoxes
    
  - name: "Kampala, Uganda"
    lat: 0.3476
    lon: 32.5825
    tz: 3
    test_dates: ["20/03/2024", "23/09/2024"]
    
  - name: "Singapore"
    lat: 1.3521
    lon: 103.8198
    tz: 8
    test_dates: ["20/03/2024", "23/09/2024"]
```

#### C. International Date Line
```yaml
date_line_test_cases:
  - name: "Apia, Samoa"
    lat: -13.8507
    lon: -171.7514
    tz: 13
    test_dates: ["31/12/2024", "01/01/2025"]
    
  - name: "Kiritimati, Kiribati"
    lat: 1.8721
    lon: -157.3626
    tz: 14
    test_dates: ["31/12/2024", "01/01/2025"]
```

### 2. Time-Based Edge Cases

#### A. Birth Times
```yaml
time_edge_cases:
  - midnight: "00:00"
  - just_after_midnight: "00:01"
  - just_before_midnight: "23:59"
  - noon: "12:00"
  - dawn_approximate: "06:00"
  - dusk_approximate: "18:00"
```

#### B. Special Dates
```yaml
special_dates:
  - leap_year_feb29: "29/02/2024"
  - non_leap_year_feb28: "28/02/2023"
  - year_2000_millennium: "01/01/2000"
  - dst_spring_forward: "10/03/2024"  # US DST
  - dst_fall_back: "03/11/2024"      # US DST
```

### 3. Astronomical Event Test Cases

#### A. Eclipse Dates
```yaml
eclipse_test_cases:
  - solar_eclipse_2024: "08/04/2024"
  - lunar_eclipse_2024: "25/03/2024"
  - solar_eclipse_2023: "14/10/2023"
```

#### B. Planetary Stations
```yaml
retrograde_test_cases:
  - mercury_retrograde_start: "01/04/2024"
  - mercury_direct: "25/04/2024"
  - venus_retrograde: "22/07/2023"
  - mars_retrograde: "30/10/2022"
```

### 4. Celebrity Birth Data (Verified)

```yaml
celebrity_test_cases:
  - name: "Albert Einstein"
    dob: "14/03/1879"
    tob: "11:30"
    lat: 48.4011
    lon: 9.9876
    tz: 1
    
  - name: "Carl Jung"
    dob: "26/07/1875"
    tob: "19:32"
    lat: 47.5969
    lon: 9.3256
    tz: 1
    
  - name: "Marie Curie"
    dob: "07/11/1867"
    tob: "12:00"
    lat: 52.2297
    lon: 21.0122
    tz: 1
    
  - name: "Nikola Tesla"
    dob: "10/07/1856"
    tob: "00:00"
    lat: 44.8041
    lon: 15.3242
    tz: 1
    
  - name: "Steve Jobs"
    dob: "24/02/1955"
    tob: "19:15"
    lat: 37.3382
    lon: -122.0363
    tz: -8
```

### 5. Indian Family Test Cases (Real Data)

```yaml
indian_family_test_cases:
  - name: "Panneerselvam Chandrasekaran"
    dob: "20/08/1954"
    tob: "18:20"  # 06:20 PM
    lat: 12.8185   # Kanchipuram, Tamil Nadu
    lon: 79.6947
    tz: 5.5        # IST
    notes: "Born in temple city, traditional Tamil family"
    
  - name: "Valarmathi Kannappan"
    dob: "11/02/1961"
    tob: "15:30"  # 03:30 PM
    lat: 13.1622   # Kovur, Tamil Nadu
    lon: 80.0050
    tz: 5.5
    notes: "Born near Chennai, coastal region"
    
  - name: "Janaki Panneerselvam"
    dob: "18/12/1982"
    tob: "10:10"  # 10:10 AM
    lat: 13.0827   # Chennai, Tamil Nadu
    lon: 80.2707
    tz: 5.5
    notes: "Born in metropolitan Chennai"
    
  - name: "Govindarajan Panneerselvam"
    dob: "29/12/1989"
    tob: "12:12"  # 12:12 PM
    lat: 13.0827   # Chennai, Tamil Nadu
    lon: 80.2707
    tz: 5.5
    notes: "Born in Chennai, near year end"
```

**Benefits of Indian Test Cases**:
- All use IST (UTC+5:30) timezone
- Southern Indian locations (Tamil Nadu)
- Family relationships for compatibility testing
- Mix of rural (Kanchipuram) and urban (Chennai) births
- Various times of day (morning, afternoon, evening)
- Span from 1954 to 1989 (35 years)

### 6. Random Test Data Generator

```python
import random
from datetime import datetime, timedelta

def generate_random_test_cases(count=100):
    """Generate random test cases for comprehensive coverage"""
    test_cases = []
    
    # Major cities for realistic coordinates
    cities = [
        {"name": "New York", "lat": 40.7128, "lon": -74.0060, "tz": -5},
        {"name": "London", "lat": 51.5074, "lon": -0.1278, "tz": 0},
        {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "tz": 9},
        {"name": "Sydney", "lat": -33.8688, "lon": 151.2093, "tz": 10},
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "tz": 5.5},
        {"name": "Cairo", "lat": 30.0444, "lon": 31.2357, "tz": 2},
        {"name": "Moscow", "lat": 55.7558, "lon": 37.6173, "tz": 3},
        {"name": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729, "tz": -3},
        {"name": "Cape Town", "lat": -33.9249, "lon": 18.4241, "tz": 2},
        {"name": "Dubai", "lat": 25.2048, "lon": 55.2708, "tz": 4}
    ]
    
    for i in range(count):
        # Random date between 1900 and 2024
        start_date = datetime(1900, 1, 1)
        end_date = datetime(2024, 12, 31)
        random_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        # Random time
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        
        # Random city
        city = random.choice(cities)
        
        test_cases.append({
            "id": f"random_{i+1}",
            "dob": random_date.strftime("%d/%m/%Y"),
            "tob": f"{hour:02d}:{minute:02d}",
            "lat": city["lat"],
            "lon": city["lon"],
            "tz": city["tz"],
            "location": city["name"]
        })
    
    return test_cases
```

### 6. Specific Validation Test Cases

#### A. House System Variations
```yaml
house_system_tests:
  - system: "placidus"
    test_latitudes: [0, 30, 45, 60, 66]  # Different latitudes
  - system: "koch"
    test_latitudes: [0, 30, 45, 60, 66]
  - system: "equal"
    test_latitudes: [0, 30, 45, 60, 66]
```

#### B. Ayanamsa Variations
```yaml
ayanamsa_tests:
  - name: "Lahiri"
    test_dates: ["01/01/1900", "01/01/1950", "01/01/2000", "01/01/2024"]
  - name: "Krishnamurti"
    test_dates: ["01/01/1900", "01/01/1950", "01/01/2000", "01/01/2024"]
  - name: "Raman"
    test_dates: ["01/01/1900", "01/01/1950", "01/01/2000", "01/01/2024"]
```

### 7. API Endpoints to Test

```yaml
api_endpoints_matrix:
  core_calculations:
    - endpoint: "/planet-details"
      validate: ["longitude", "latitude", "speed", "retrograde"]
    - endpoint: "/extended-kundli-details"
      validate: ["ascendant", "houses", "signs", "nakshatras"]
    - endpoint: "/divisional-charts"
      validate: ["D1", "D9", "D10", "D12"]
      
  dasha_calculations:
    - endpoint: "/maha-dasha"
      validate: ["start_date", "end_date", "planet_order"]
    - endpoint: "/antardasha"
      validate: ["sub_periods", "dates"]
      
  panchang_elements:
    - endpoint: "/panchang"
      validate: ["tithi", "nakshatra", "yoga", "karana"]
    - endpoint: "/moon-phase"
      validate: ["phase", "illumination", "distance"]
      
  matching:
    - endpoint: "/north-match"
      validate: ["total_score", "individual_scores"]
    - endpoint: "/south-match"
      validate: ["total_score", "individual_scores"]
```

### 8. Batch Test Execution Plan

```yaml
batch_execution:
  phase_1_basic:
    - celebrity_charts: 5 cases
    - equatorial_tests: 3 cases
    - polar_tests: 3 cases
    
  phase_2_comprehensive:
    - random_cases: 50 cases
    - edge_cases: 20 cases
    - special_dates: 10 cases
    
  phase_3_stress:
    - high_volume: 500 cases
    - concurrent_requests: 10 parallel
```

## Test Data Collection Strategy

### 1. API Call Structure
```python
def call_vedicastro_api(endpoint, params):
    """
    Standard API call structure
    """
    base_url = "https://api.vedicastroapi.com/v3-json"
    params['api_key'] = API_KEY
    params['lang'] = 'en'
    
    response = requests.get(f"{base_url}{endpoint}", params=params)
    return response.json()
```

### 2. Data Storage Structure
```
test_data/
├── raw_responses/           # Original API responses
│   ├── planet_details/
│   ├── kundli_details/
│   ├── dashas/
│   └── panchang/
├── processed_data/          # Extracted key values
│   ├── planetary_positions.json
│   ├── house_cusps.json
│   ├── dasha_periods.json
│   └── panchang_elements.json
├── validation_results/      # Comparison results
│   ├── accuracy_reports/
│   └── discrepancy_logs/
└── test_metadata.json       # Test case metadata
```

### 3. Validation Criteria

```yaml
validation_thresholds:
  planetary_longitude:
    tolerance: 0.01  # degrees
    critical: false
    
  ascendant:
    tolerance: 0.1   # degrees
    critical: true
    
  house_cusps:
    tolerance: 0.5   # degrees
    critical: true
    
  dasha_dates:
    tolerance: 1     # days
    critical: true
    
  tithi:
    tolerance: 0     # exact match
    critical: true
```

## Usage Instructions

1. **Generate Test Cases**: Use the random generator for bulk cases
2. **Execute API Calls**: Run batches with rate limiting
3. **Store Responses**: Save both raw and processed data
4. **Validate Results**: Compare against our calculations
5. **Generate Reports**: Create accuracy metrics and identify discrepancies