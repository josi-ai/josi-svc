#!/usr/bin/env python3
"""
Direct API comparison without database dependency.
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

# VedicAstroAPI configuration
VEDICASTRO_API_KEY = "268487ad-cdec-578d-8998-b27dc414d84f"
VEDICASTRO_BASE_URL = "https://api.vedicastroapi.com/v3/json"

# Test persons data
TEST_PERSONS = [
    {
        "name": "Valarmathi Kannappan",
        "dob": "11/02/1961",
        "tob": "15:30",
        "lat": 13.1622,
        "lon": 80.005,
        "tz": 5.5,
        "place": "Kovur, Tamil Nadu, India"
    },
    {
        "name": "Janaki Panneerselvam", 
        "dob": "18/12/1982",
        "tob": "10:10",
        "lat": 13.0827,
        "lon": 80.2707,
        "tz": 5.5,
        "place": "Chennai, Tamil Nadu, India"
    }
]

def call_vedicastro_api(person: dict) -> dict:
    """Call VedicAstroAPI with correct endpoint."""
    
    # Try the planet details endpoint
    endpoint = "https://api.vedicastroapi.com/v3-json/horoscope/planet-details"
    
    params = {
        "api_key": VEDICASTRO_API_KEY,
        "dob": person['dob'],
        "tob": person['tob'],
        "lat": person['lat'],
        "lon": person['lon'],
        "tz": person['tz'],
        "lang": "en"
    }
    
    try:
        print(f"    Calling: {endpoint}")
        response = requests.get(endpoint, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"    Success! Got response with keys: {list(data.keys())[:5]}")
            return data
        else:
            print(f"    Error: {response.status_code} - {response.text[:200]}")
            
            # Try alternative endpoint
            alt_endpoint = "https://api.vedicastroapi.com/json/horoscope/planet-details"
            print(f"    Trying alternative: {alt_endpoint}")
            response = requests.get(alt_endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"    Alternative failed: {response.status_code}")
                return {}
    
    except Exception as e:
        print(f"    Exception: {e}")
        return {}

def calculate_locally(person: dict) -> dict:
    """Calculate using local AstrologyCalculator."""
    
    calc = AstrologyCalculator()
    
    # Parse date and time
    dob_parts = person['dob'].split('/')
    dt = datetime(
        int(dob_parts[2]),  # year
        int(dob_parts[1]),  # month
        int(dob_parts[0]),  # day
        int(person['tob'].split(':')[0]),  # hour
        int(person['tob'].split(':')[1])   # minute
    )
    
    # Calculate chart
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=person['lat'],
        longitude=person['lon'],
        timezone="Asia/Kolkata",
        house_system='placidus'
    )
    
    return chart

def compare_results(person: dict):
    """Compare results from API and local calculation."""
    
    print(f"\n{'='*80}")
    print(f"Testing: {person['name']}")
    print(f"DOB: {person['dob']}, TOB: {person['tob']}")
    print(f"Location: {person['lat']}, {person['lon']}")
    print('-' * 80)
    
    # Get VedicAstroAPI results
    print("\n1. Calling VedicAstroAPI...")
    vedic_data = call_vedicastro_api(person)
    
    # Calculate locally
    print("\n2. Calculating locally...")
    local_chart = calculate_locally(person)
    
    # Compare if we got data
    if vedic_data and 'response' in vedic_data:
        print("\n3. Comparison Results:")
        print(f"{'Planet':<12} {'VedicAstro':>12} {'Josi Local':>12} {'Diff (°)':>10} {'Arc Min':>8}")
        print(f"{'-'*12} {'-'*12} {'-'*12} {'-'*10} {'-'*8}")
        
        # Map VedicAstroAPI planets
        vedic_planets = {}
        response_data = vedic_data['response']
        
        # Handle if response is a string (error) or dict
        if isinstance(response_data, str):
            print(f"API returned error: {response_data}")
            return
            
        for planet_id, planet_data in response_data.items():
            if planet_id == '0':  # Ascendant
                vedic_planets['Ascendant'] = planet_data.get('global_degree', 0)
            else:
                name = planet_data.get('full_name', '')
                if name:
                    vedic_planets[name] = planet_data.get('global_degree', 0)
        
        # Compare common planets
        total_diff = 0
        count = 0
        
        for planet_name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Ascendant']:
            if planet_name in vedic_planets:
                vedic_pos = vedic_planets[planet_name]
                
                if planet_name == 'Ascendant':
                    local_pos = local_chart['ascendant']['longitude']
                elif planet_name in local_chart['planets']:
                    local_pos = local_chart['planets'][planet_name]['longitude']
                else:
                    continue
                
                diff = abs(vedic_pos - local_pos)
                arc_min = diff * 60
                
                print(f"{planet_name:<12} {vedic_pos:>12.6f} {local_pos:>12.6f} {diff:>10.6f} {arc_min:>8.2f}'")
                
                total_diff += diff
                count += 1
        
        if count > 0:
            avg_diff = total_diff / count
            print(f"\nAverage difference: {avg_diff:.6f}° ({avg_diff * 60:.2f} arc minutes)")
            print(f"Accuracy: {'EXCELLENT' if avg_diff < 0.01 else 'GOOD' if avg_diff < 0.1 else 'NEEDS IMPROVEMENT'}")
    else:
        print("\n3. Could not get VedicAstroAPI data for comparison")
        print("\nLocal calculation results:")
        print(f"  Ascendant: {local_chart['ascendant']['longitude']:.6f}°")
        print(f"  Sun: {local_chart['planets']['Sun']['longitude']:.6f}°")
        print(f"  Moon: {local_chart['planets']['Moon']['longitude']:.6f}°")
        print(f"  Mars: {local_chart['planets']['Mars']['longitude']:.6f}°")
        print(f"  Rahu: {local_chart['planets']['Rahu']['longitude']:.6f}°")
        print(f"  Ketu: {local_chart['planets']['Ketu']['longitude']:.6f}°")

def main():
    """Run direct comparison tests."""
    
    print("Direct API Comparison Test (No Database Required)")
    print("=" * 80)
    
    for person in TEST_PERSONS:
        compare_results(person)
    
    print(f"\n{'='*80}")
    print("Test completed")

if __name__ == "__main__":
    main()