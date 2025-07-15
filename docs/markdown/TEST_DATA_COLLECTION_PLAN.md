# Test Data Collection Plan for Astronomical Verification

## 🎯 Required Test Data Categories

### 1. **Ephemeris Reference Data**

#### A. **NASA JPL Horizons System**
- **URL**: https://ssd.jpl.nasa.gov/horizons/
- **Data Available**: High-precision planetary positions
- **Access Method**: Web interface, email, API
- **What to collect**:
  - Planetary positions for specific dates/times
  - Sun, Moon, and planet coordinates
  - Format: J2000 ecliptic longitude/latitude

**Collection Script**:
```python
# get_jpl_data.py
import requests
from datetime import datetime

def get_jpl_ephemeris(body, start_date, end_date):
    """
    Fetch ephemeris data from JPL Horizons
    Bodies: Sun=10, Moon=301, Mercury=199, Venus=299, etc.
    """
    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        'format': 'json',
        'COMMAND': body,
        'EPHEM_TYPE': 'OBSERVER',
        'CENTER': '500@399',  # Earth center
        'START_TIME': start_date.strftime('%Y-%m-%d'),
        'STOP_TIME': end_date.strftime('%Y-%m-%d'),
        'STEP_SIZE': '1 d',
        'QUANTITIES': '1,2,4',  # RA/DEC, Apparent positions
    }
    # Process and return data
```

#### B. **Swiss Ephemeris Test Data**
- **URL**: https://www.astro.com/swisseph/
- **Download**: Test ephemeris files and validation data
- **What to collect**:
  - SE test suite data files
  - Benchmark positions
  - Ayanamsa values for different systems

#### C. **IMCCE (Paris Observatory)**
- **URL**: https://www.imcce.fr/
- **Data**: French national ephemeris
- **Use**: Cross-validation of planetary positions

### 2. **Astronomical Event Data**

#### A. **Equinoxes and Solstices (2000-2030)**
```python
ASTRONOMICAL_EVENTS = {
    "spring_equinoxes": [
        {"date": "2000-03-20 07:35 UTC", "sun_longitude": 0.0},
        {"date": "2010-03-20 17:32 UTC", "sun_longitude": 0.0},
        {"date": "2020-03-20 03:50 UTC", "sun_longitude": 0.0},
        {"date": "2024-03-20 03:06 UTC", "sun_longitude": 0.0},
        {"date": "2025-03-20 09:01 UTC", "sun_longitude": 0.0},
    ],
    "summer_solstices": [
        {"date": "2024-06-20 20:51 UTC", "sun_longitude": 90.0},
        {"date": "2025-06-21 02:42 UTC", "sun_longitude": 90.0},
    ],
    "autumn_equinoxes": [
        {"date": "2024-09-22 12:44 UTC", "sun_longitude": 180.0},
        {"date": "2025-09-22 18:19 UTC", "sun_longitude": 180.0},
    ],
    "winter_solstices": [
        {"date": "2024-12-21 09:20 UTC", "sun_longitude": 270.0},
        {"date": "2025-12-21 15:03 UTC", "sun_longitude": 270.0},
    ]
}
```

#### B. **Eclipse Data**
- **Source**: NASA Eclipse Website
- **URL**: https://eclipse.gsfc.nasa.gov/
- **Data to collect**:
  ```python
  ECLIPSE_DATA = {
      "solar_eclipses": [
          {"date": "2024-04-08 18:18 UTC", "type": "total", "sun_moon_conjunction": True},
          {"date": "2024-10-02 18:46 UTC", "type": "annular"},
      ],
      "lunar_eclipses": [
          {"date": "2024-03-25 07:13 UTC", "type": "penumbral", "sun_moon_opposition": True},
          {"date": "2024-09-18 02:44 UTC", "type": "partial"},
      ]
  }
  ```

#### C. **Mercury Retrograde Periods**
```python
MERCURY_RETROGRADES = [
    {"start": "2024-04-01", "station_retrograde": "2024-04-01 22:14 UTC", "end": "2024-04-25"},
    {"start": "2024-08-05", "station_retrograde": "2024-08-05 04:56 UTC", "end": "2024-08-28"},
    {"start": "2024-11-26", "station_retrograde": "2024-11-26 03:42 UTC", "end": "2024-12-15"},
]
```

### 3. **Verified Chart Data**

#### A. **Celebrity Birth Charts**
Sources to scrape/collect from:
1. **AstroDatabank** (Astro.com)
   - URL: https://www.astro.com/astro-databank/
   - Rodden Rating AA (most reliable)

2. **Famous Charts to Collect**:
```python
CELEBRITY_CHARTS = {
    "albert_einstein": {
        "birth": "1879-03-14 11:30:00 LMT",
        "location": "Ulm, Germany",
        "coordinates": {"lat": 48.4011, "lon": 9.9876},
        "source": "Birth certificate (Rodden AA)",
        "expected_positions": {
            "sun": {"sign": "Pisces", "degree": 23.48},
            "moon": {"sign": "Sagittarius", "degree": 14.32},
            "asc": {"sign": "Cancer", "degree": 11.38}
        }
    },
    "carl_jung": {
        "birth": "1875-07-26 19:29:00 LMT",
        "location": "Kesswil, Switzerland",
        "coordinates": {"lat": 47.5969, "lon": 9.3256},
        "source": "Church records (Rodden AA)"
    },
    "marie_curie": {
        "birth": "1867-11-07 12:00:00 LMT",
        "location": "Warsaw, Poland",
        "coordinates": {"lat": 52.2297, "lon": 21.0122},
        "source": "Biography (Rodden B)"
    }
}
```

#### B. **Test Chart Collection Script**
```python
# collect_astrocom_data.py
from selenium import webdriver
import json
import time

def collect_chart_from_astrocom(birth_data):
    """
    Automated collection from Astro.com
    Note: Respect rate limits and terms of service
    """
    driver = webdriver.Chrome()
    driver.get("https://www.astro.com/cgi/chart.cgi")
    
    # Fill form programmatically
    # Extract positions
    # Save to database
```

### 4. **House System Test Data**

#### A. **Placidus House Tables**
- **Source**: "Tables of Houses" by Raphael
- **Data needed**: House cusps for various latitudes/times

#### B. **Special Test Cases**
```python
HOUSE_SYSTEM_TESTS = {
    "polar_circle": {
        "location": "Reykjavik, Iceland",
        "coordinates": {"lat": 64.1466, "lon": -21.9426},
        "test_dates": ["2024-06-21", "2024-12-21"],  # Extreme sun positions
        "notes": "Test house systems at high latitudes"
    },
    "equator": {
        "location": "Quito, Ecuador", 
        "coordinates": {"lat": -0.1807, "lon": -78.4678},
        "notes": "MC should be ~90° from ASC"
    }
}
```

### 5. **Vedic Astrology Specific Data**

#### A. **Ayanamsa Values**
```python
AYANAMSA_VALUES = {
    "lahiri": {
        "1900-01-01": 22.44266,
        "1950-01-01": 23.11217,
        "2000-01-01": 23.85438,
        "2024-01-01": 24.15890,
        "2025-01-01": 24.17305,
        "source": "Indian Astronomical Ephemeris"
    },
    "krishnamurti": {
        "2000-01-01": 23.77444,
        "2024-01-01": 24.07896
    }
}
```

#### B. **Panchang Elements Test Data**
```python
PANCHANG_TEST_DATA = {
    "2024-01-01": {
        "tithi": {"name": "Krishna Chaturthi", "index": 19},
        "nakshatra": {"name": "Pushya", "index": 8},
        "yoga": {"name": "Vishkumbha", "index": 1},
        "karana": {"name": "Vishti", "index": 7},
        "source": "drikpanchang.com"
    }
}
```

### 6. **Data Collection Tools**

#### A. **Web Scraping Tools**
```python
# requirements_scraping.txt
selenium==4.15.0
beautifulsoup4==4.12.0
requests==2.31.0
pandas==2.1.0
```

#### B. **API Clients**
```python
# astro_apis.py
class AstroDataCollector:
    def __init__(self):
        self.apis = {
            'jpl_horizons': 'https://ssd.jpl.nasa.gov/api/horizons.api',
            'astro_seek': 'https://horoscopes.astro-seek.com/api/',
            'imcce': 'https://api.imcce.fr/miriade/'
        }
    
    def fetch_planetary_positions(self, date, location):
        """Fetch from multiple sources for comparison."""
        pass
```

## 📋 Data Collection Action Plan

### Week 1: Automated Collection Setup
1. **Set up web scraping environment**
   - Install Selenium, BeautifulSoup
   - Create browser automation scripts
   - Implement rate limiting

2. **Create JPL Horizons client**
   - API integration
   - Batch data retrieval
   - Format conversion tools

3. **Build Astro.com scraper**
   - Respect robots.txt
   - Implement polite crawling
   - Chart data extraction

### Week 2: Manual Data Collection
1. **Purchase/Download ephemeris tables**
   - American Ephemeris 2021-2030
   - Raphael's Ephemeris
   - Swiss Ephemeris files

2. **Collect historical data**
   - Famous birth charts
   - Historical astronomical events
   - Published calculation examples

### Week 3: Data Validation & Storage
1. **Create test database**
   ```sql
   CREATE TABLE test_ephemeris (
       id SERIAL PRIMARY KEY,
       datetime TIMESTAMP WITH TIME ZONE,
       body VARCHAR(20),
       longitude DECIMAL(10,6),
       latitude DECIMAL(10,6),
       distance DECIMAL(12,8),
       source VARCHAR(50),
       collected_date DATE
   );
   ```

2. **Implement data validation**
   - Cross-reference multiple sources
   - Flag discrepancies
   - Calculate consensus values

### Week 4: Test Data API
1. **Create test data service**
   ```python
   class TestDataService:
       def get_verified_position(self, body, datetime):
           """Return verified position from multiple sources."""
           pass
       
       def get_test_chart(self, chart_id):
           """Return complete verified chart data."""
           pass
   ```

## 🔐 Legal & Ethical Considerations

1. **Respect Terms of Service**
   - Astro.com: Personal use allowed, no commercial scraping
   - NASA: Public domain data
   - Check each source's robots.txt

2. **Rate Limiting**
   ```python
   import time
   
   class PoliteScaper:
       def __init__(self, delay=1.0):
           self.delay = delay
           self.last_request = 0
       
       def wait(self):
           elapsed = time.time() - self.last_request
           if elapsed < self.delay:
               time.sleep(self.delay - elapsed)
           self.last_request = time.time()
   ```

3. **Attribution**
   - Always credit data sources
   - Maintain source references
   - Document collection methods

## 📊 Expected Data Volume

- **Ephemeris positions**: ~10,000 data points
- **Test charts**: 500-1,000 verified charts
- **Astronomical events**: 200+ events
- **House calculations**: 1,000+ test cases
- **Total storage**: ~50MB JSON/CSV

## 🚀 Next Steps

1. **Prioritize data sources**
   - Start with NASA JPL (most accurate)
   - Add Astro.com for cross-validation
   - Include Swiss Ephemeris tests

2. **Begin automated collection**
   - Set up scheduled scrapers
   - Implement data pipeline
   - Create validation checks

3. **Manual verification**
   - Spot-check collected data
   - Compare multiple sources
   - Document discrepancies

This comprehensive data collection will provide the foundation for verifying your astronomical calculations to professional standards.