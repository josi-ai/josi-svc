#!/usr/bin/env python3
"""
Collect test data from VedicAstroAPI for validation of our astrology calculations.
This script fetches real astronomical data to validate our implementation.
"""
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
API_KEY = "30548028-046d-54bb-abd7-8db05db5536b"
BASE_URL = "https://api.vedicastroapi.com/v3-json"
RATE_LIMIT_DELAY = 0.5  # seconds between requests

# Test data storage paths
TEST_DATA_DIR = Path("test_data/vedicastro_api")
RAW_RESPONSES_DIR = TEST_DATA_DIR / "raw_responses"
PROCESSED_DATA_DIR = TEST_DATA_DIR / "processed_data"
VALIDATION_RESULTS_DIR = TEST_DATA_DIR / "validation_results"

# Create directories
for dir_path in [RAW_RESPONSES_DIR, PROCESSED_DATA_DIR, VALIDATION_RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

class VedicAstroAPIClient:
    """Client for fetching data from VedicAstroAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make API request with error handling"""
        self._rate_limit()
        
        # Add API key and language
        params['api_key'] = self.api_key
        params['lang'] = 'en'
        
        url = f"{BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 200:
                return data
            else:
                logger.error(f"API error for {endpoint}: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return None
    
    def get_planet_details(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        """Fetch planetary positions"""
        return self._make_request("horoscope/planet-details", {
            'dob': dob,
            'tob': tob,
            'lat': lat,
            'lon': lon,
            'tz': tz
        })
    
    def get_extended_kundli(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        """Fetch extended kundli details"""
        return self._make_request("extended-horoscope/extended-kundli-details", {
            'dob': dob,
            'tob': tob,
            'lat': lat,
            'lon': lon,
            'tz': tz
        })
    
    def get_panchang(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        """Fetch panchang details"""
        return self._make_request("panchang/panchang", {
            'dob': dob,
            'tob': tob,
            'lat': lat,
            'lon': lon,
            'tz': tz
        })
    
    def get_mahadasha(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        """Fetch mahadasha details"""
        return self._make_request("dashas/maha-dasha", {
            'dob': dob,
            'tob': tob,
            'lat': lat,
            'lon': lon,
            'tz': tz
        })
    
    def get_western_planets(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        """Fetch western astrology planet positions"""
        return self._make_request("western/planet-details", {
            'dob': dob,
            'tob': tob,
            'lat': lat,
            'lon': lon,
            'tz': tz
        })

def load_test_cases() -> List[Dict]:
    """Load test cases from the markdown file"""
    test_cases = []
    
    # Celebrity test cases
    celebrities = [
        {
            "name": "Albert_Einstein",
            "dob": "14/03/1879",
            "tob": "11:30",
            "lat": 48.4011,
            "lon": 9.9876,
            "tz": 1
        },
        {
            "name": "Carl_Jung",
            "dob": "26/07/1875",
            "tob": "19:32",
            "lat": 47.5969,
            "lon": 9.3256,
            "tz": 1
        },
        {
            "name": "Marie_Curie",
            "dob": "07/11/1867",
            "tob": "12:00",
            "lat": 52.2297,
            "lon": 21.0122,
            "tz": 1
        },
        {
            "name": "Steve_Jobs",
            "dob": "24/02/1955",
            "tob": "19:15",
            "lat": 37.3382,
            "lon": -122.0363,
            "tz": -8
        }
    ]
    
    # Edge cases
    edge_cases = [
        {
            "name": "Reykjavik_Summer_Solstice",
            "dob": "21/06/2024",
            "tob": "12:00",
            "lat": 64.1466,
            "lon": -21.9426,
            "tz": 0
        },
        {
            "name": "Quito_Spring_Equinox",
            "dob": "20/03/2024",
            "tob": "12:00",
            "lat": -0.1807,
            "lon": -78.4678,
            "tz": -5
        },
        {
            "name": "Singapore_Equator",
            "dob": "01/01/2024",
            "tob": "00:00",
            "lat": 1.3521,
            "lon": 103.8198,
            "tz": 8
        }
    ]
    
    # Special astronomical events
    astronomical_events = [
        {
            "name": "Solar_Eclipse_2024",
            "dob": "08/04/2024",
            "tob": "18:18",
            "lat": 40.7128,
            "lon": -74.0060,
            "tz": -5
        },
        {
            "name": "Mercury_Retrograde_Start_2024",
            "dob": "01/04/2024",
            "tob": "22:14",
            "lat": 51.5074,
            "lon": -0.1278,
            "tz": 0
        }
    ]
    
    # Indian family test cases
    indian_family = [
        {
            "name": "Panneerselvam_Chandrasekaran",
            "dob": "20/08/1954",
            "tob": "18:20",  # 06:20 PM
            "lat": 12.8185,   # Kanchipuram
            "lon": 79.6947,
            "tz": 5.5         # India Standard Time
        },
        {
            "name": "Valarmathi_Kannappan",
            "dob": "11/02/1961",
            "tob": "15:30",  # 03:30 PM
            "lat": 13.1622,   # Kovur (near Chennai)
            "lon": 80.0050,
            "tz": 5.5
        },
        {
            "name": "Janaki_Panneerselvam",
            "dob": "18/12/1982",
            "tob": "10:10",  # 10:10 AM
            "lat": 13.0827,   # Chennai
            "lon": 80.2707,
            "tz": 5.5
        },
        {
            "name": "Govindarajan_Panneerselvam",
            "dob": "29/12/1989",
            "tob": "12:12",  # 12:12 PM
            "lat": 13.0827,   # Chennai
            "lon": 80.2707,
            "tz": 5.5
        }
    ]
    
    test_cases.extend(celebrities)
    test_cases.extend(edge_cases)
    test_cases.extend(astronomical_events)
    test_cases.extend(indian_family)
    
    return test_cases

def collect_data_for_test_case(client: VedicAstroAPIClient, test_case: Dict) -> Dict:
    """Collect all relevant data for a single test case"""
    logger.info(f"Collecting data for: {test_case['name']}")
    
    result = {
        "test_case": test_case,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {}
    }
    
    # Collect different types of data
    endpoints = [
        ("planet_details", client.get_planet_details),
        ("extended_kundli", client.get_extended_kundli),
        ("panchang", client.get_panchang),
        ("mahadasha", client.get_mahadasha),
        ("western_planets", client.get_western_planets)
    ]
    
    for endpoint_name, endpoint_func in endpoints:
        logger.info(f"  Fetching {endpoint_name}...")
        data = endpoint_func(
            test_case['dob'],
            test_case['tob'],
            test_case['lat'],
            test_case['lon'],
            test_case['tz']
        )
        
        if data:
            result['data'][endpoint_name] = data['response']
            
            # Save raw response
            filename = f"{test_case['name']}_{endpoint_name}.json"
            filepath = RAW_RESPONSES_DIR / endpoint_name / filename
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            logger.error(f"  Failed to fetch {endpoint_name}")
    
    return result

def process_collected_data(collected_data: List[Dict]):
    """Process and organize collected data for validation"""
    logger.info("Processing collected data...")
    
    # Extract key values for comparison
    processed = {
        "planetary_positions": [],
        "house_cusps": [],
        "ascendants": [],
        "dasha_periods": [],
        "panchang_elements": []
    }
    
    for data in collected_data:
        test_name = data['test_case']['name']
        
        # Extract planetary positions
        if 'planet_details' in data['data']:
            planets = data['data']['planet_details']
            for planet_data in planets:
                processed['planetary_positions'].append({
                    "test_case": test_name,
                    "planet": planet_data['name'],
                    "longitude": planet_data['longitude'],
                    "latitude": planet_data.get('latitude', 0),
                    "speed": planet_data.get('speed', 0),
                    "retrograde": planet_data.get('retrograde', False)
                })
        
        # Extract ascendant and houses
        if 'extended_kundli' in data['data']:
            kundli = data['data']['extended_kundli']
            if 'ascendant' in kundli:
                processed['ascendants'].append({
                    "test_case": test_name,
                    "ascendant": kundli['ascendant'],
                    "ascendant_degree": kundli.get('ascendant_degree', 0)
                })
            
            if 'houses' in kundli:
                for i, house in enumerate(kundli['houses'], 1):
                    processed['house_cusps'].append({
                        "test_case": test_name,
                        "house": i,
                        "cusp": house.get('degree', 0),
                        "sign": house.get('sign', '')
                    })
        
        # Extract dasha periods
        if 'mahadasha' in data['data']:
            dasha_data = data['data']['mahadasha']
            if 'mahadasha_order' in dasha_data:
                processed['dasha_periods'].append({
                    "test_case": test_name,
                    "dasha_order": dasha_data['mahadasha'],
                    "start_dates": dasha_data['mahadasha_order'],
                    "remaining_at_birth": dasha_data.get('dasha_remaining_at_birth', '')
                })
        
        # Extract panchang elements
        if 'panchang' in data['data']:
            panchang = data['data']['panchang']
            processed['panchang_elements'].append({
                "test_case": test_name,
                "tithi": panchang.get('tithi', ''),
                "nakshatra": panchang.get('nakshatra', ''),
                "yoga": panchang.get('yoga', ''),
                "karana": panchang.get('karana', '')
            })
    
    # Save processed data
    for category, data in processed.items():
        filepath = PROCESSED_DATA_DIR / f"{category}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    logger.info(f"Processed data saved to {PROCESSED_DATA_DIR}")

def create_validation_report(collected_data: List[Dict]):
    """Create a validation report template"""
    report = {
        "generated_date": datetime.utcnow().isoformat(),
        "total_test_cases": len(collected_data),
        "api_endpoints_tested": [
            "planet_details",
            "extended_kundli",
            "panchang",
            "mahadasha",
            "western_planets"
        ],
        "test_cases": [d['test_case']['name'] for d in collected_data],
        "validation_criteria": {
            "planetary_longitude": {
                "tolerance": 0.01,
                "unit": "degrees",
                "description": "Maximum acceptable difference in planetary positions"
            },
            "ascendant": {
                "tolerance": 0.1,
                "unit": "degrees",
                "description": "Maximum acceptable difference in ascendant calculation"
            },
            "house_cusps": {
                "tolerance": 0.5,
                "unit": "degrees",
                "description": "Maximum acceptable difference in house cusp positions"
            },
            "dasha_dates": {
                "tolerance": 1,
                "unit": "days",
                "description": "Maximum acceptable difference in dasha period dates"
            },
            "panchang_elements": {
                "tolerance": 0,
                "unit": "exact match",
                "description": "Tithi, nakshatra, yoga, karana must match exactly"
            }
        },
        "next_steps": [
            "Run our astrology calculations for the same test cases",
            "Compare results against VedicAstroAPI data",
            "Generate accuracy metrics",
            "Identify and fix any discrepancies"
        ]
    }
    
    filepath = VALIDATION_RESULTS_DIR / "validation_report_template.json"
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Validation report template saved to {filepath}")

def main():
    """Main execution function"""
    logger.info("Starting VedicAstroAPI test data collection...")
    
    # Initialize client
    client = VedicAstroAPIClient(API_KEY)
    
    # Load test cases
    test_cases = load_test_cases()
    logger.info(f"Loaded {len(test_cases)} test cases")
    
    # Collect data
    collected_data = []
    for test_case in test_cases:
        result = collect_data_for_test_case(client, test_case)
        collected_data.append(result)
        
        # Save intermediate results
        filepath = TEST_DATA_DIR / f"collected_{test_case['name']}.json"
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
    
    # Process collected data
    process_collected_data(collected_data)
    
    # Create validation report
    create_validation_report(collected_data)
    
    # Save complete dataset
    complete_dataset = {
        "collection_date": datetime.utcnow().isoformat(),
        "api_key_used": API_KEY[:10] + "...",  # Partial key for security
        "test_cases": collected_data
    }
    
    filepath = TEST_DATA_DIR / "complete_dataset.json"
    with open(filepath, 'w') as f:
        json.dump(complete_dataset, f, indent=2)
    
    logger.info(f"\nData collection complete!")
    logger.info(f"Raw responses saved to: {RAW_RESPONSES_DIR}")
    logger.info(f"Processed data saved to: {PROCESSED_DATA_DIR}")
    logger.info(f"Validation templates saved to: {VALIDATION_RESULTS_DIR}")
    
    print("\n✅ Test data collection successful!")
    print(f"\nNext steps:")
    print(f"1. Run our astrology calculations for the same test cases")
    print(f"2. Use scripts/validate_against_vedicastro.py to compare results")
    print(f"3. Review validation reports in {VALIDATION_RESULTS_DIR}")

if __name__ == "__main__":
    main()