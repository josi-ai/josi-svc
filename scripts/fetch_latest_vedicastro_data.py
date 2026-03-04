#!/usr/bin/env python3
"""
Fetch latest data from VedicAstroAPI for all 5 test persons.
"""

import requests
import json
import os
from datetime import datetime
import time

# VedicAstroAPI configuration
API_KEY = "30548028-046d-54bb-abd7-8db05db5536b"
BASE_URL = "https://api.vedicastroapi.com/v3-json/horoscope"

# All 5 test persons data
TEST_PERSONS = [
    {
        "name": "Archana_M",
        "display_name": "Archana M",
        "dob": "07/12/1998",  # DD/MM/YYYY format
        "tob": "21:15",
        "lat": 13.0827,
        "lon": 80.2707,
        "tz": 5.5,
        "place": "Chennai, Tamil Nadu, India",
        "gender": "female"
    },
    {
        "name": "Valarmathi_Kannappan",
        "display_name": "Valarmathi Kannappan",
        "dob": "11/02/1961",
        "tob": "15:30",
        "lat": 13.1622,
        "lon": 80.005,
        "tz": 5.5,
        "place": "Kovur, Tamil Nadu, India",
        "gender": "female"
    },
    {
        "name": "Janaki_Panneerselvam",
        "display_name": "Janaki Panneerselvam",
        "dob": "18/12/1982",
        "tob": "10:10",
        "lat": 13.0827,
        "lon": 80.2707,
        "tz": 5.5,
        "place": "Chennai, Tamil Nadu, India",
        "gender": "female"
    },
    {
        "name": "Govindarajan_Panneerselvam",
        "display_name": "Govindarajan Panneerselvam",
        "dob": "29/12/1989",
        "tob": "12:12",
        "lat": 13.0827,
        "lon": 80.2707,
        "tz": 5.5,
        "place": "Chennai, Tamil Nadu, India",
        "gender": "male"
    },
    {
        "name": "Panneerselvam_Chandrasekaran",
        "display_name": "Panneerselvam Chandrasekaran",
        "dob": "20/08/1954",
        "tob": "18:20",
        "lat": 12.8185,
        "lon": 79.6947,
        "tz": 5.5,
        "place": "Kanchipuram, Tamil Nadu, India",
        "gender": "male"
    }
]

def fetch_planet_details(person):
    """Fetch planet details from VedicAstroAPI."""
    endpoint = f"{BASE_URL}/planet-details"
    
    params = {
        "api_key": API_KEY,
        "dob": person['dob'],
        "tob": person['tob'],
        "lat": person['lat'],
        "lon": person['lon'],
        "tz": person['tz'],
        "lang": "en"
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Error {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None

def fetch_extended_kundli(person):
    """Fetch extended kundli data."""
    endpoint = f"{BASE_URL}/extended-kundli"
    
    params = {
        "api_key": API_KEY,
        "dob": person['dob'],
        "tob": person['tob'],
        "lat": person['lat'],
        "lon": person['lon'],
        "tz": person['tz'],
        "lang": "en"
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def save_data(person, data):
    """Save fetched data to file."""
    timestamp = datetime.now().isoformat()
    
    # Create output directory
    output_dir = "test_data/vedicastro_api/latest_fetch"
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare data structure
    output_data = {
        "test_case": {
            "name": person['name'],
            "display_name": person['display_name'],
            "dob": person['dob'],
            "tob": person['tob'],
            "lat": person['lat'],
            "lon": person['lon'],
            "tz": person['tz'],
            "place": person['place'],
            "gender": person['gender']
        },
        "timestamp": timestamp,
        "data": data
    }
    
    # Save to file
    filename = f"{output_dir}/{person['name']}_latest.json"
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"  Saved to: {filename}")

def main():
    """Fetch latest data for all test persons."""
    print("Fetching Latest VedicAstroAPI Data")
    print("=" * 80)
    print(f"API Key: {API_KEY}")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    successful = 0
    failed = 0
    
    for i, person in enumerate(TEST_PERSONS, 1):
        print(f"\n[{i}/5] {person['display_name']}")
        print(f"  DOB: {person['dob']}, TOB: {person['tob']}")
        print(f"  Location: {person['place']}")
        
        # Fetch planet details
        print("  Fetching planet details...", end="", flush=True)
        planet_data = fetch_planet_details(person)
        
        if planet_data and 'response' in planet_data:
            print(" Success!")
            
            # Check if response is an error
            if isinstance(planet_data['response'], str):
                print(f"  API Error: {planet_data['response']}")
                failed += 1
                continue
            
            # Fetch extended kundli
            print("  Fetching extended kundli...", end="", flush=True)
            extended_data = fetch_extended_kundli(person)
            if extended_data:
                print(" Success!")
            else:
                print(" Failed (non-critical)")
            
            # Combine data
            all_data = {
                "planet_details": planet_data.get('response', {}),
                "extended_kundli": extended_data.get('response', {}) if extended_data else {}
            }
            
            # Save data
            save_data(person, all_data)
            successful += 1
            
        else:
            print(" Failed!")
            failed += 1
        
        # Small delay between requests
        if i < len(TEST_PERSONS):
            time.sleep(1)
    
    # Summary
    print(f"\n{'='*80}")
    print("Summary:")
    print(f"  Total persons: {len(TEST_PERSONS)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    
    if failed > 0:
        print("\nNote: If you see 'out of api calls' errors, the API key may have reached its limit.")

if __name__ == "__main__":
    main()