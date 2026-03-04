#!/usr/bin/env python3
"""
Real-world API comparison test between VedicAstroAPI and Josi API.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List
import time
import os

# API Configuration
VEDICASTRO_API_KEY = "268487ad-cdec-578d-8998-b27dc414d84f"
VEDICASTRO_BASE_URL = "https://api.vedicastroapi.com/v3/json"

JOSI_API_KEY = "test-api-key"  # Update this with actual API key
JOSI_BASE_URL = "http://localhost:8001/api/v1"

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
    },
    {
        "name": "Govindarajan Panneerselvam",
        "dob": "15/05/1990",
        "tob": "10:30",
        "lat": 13.0827,
        "lon": 80.2707,
        "tz": 5.5,
        "place": "Chennai, Tamil Nadu, India"
    }
]

def call_vedicastro_api(person: Dict) -> Dict:
    """Call VedicAstroAPI for planet details."""
    endpoint = f"{VEDICASTRO_BASE_URL}/horoscope/planet-details"
    
    dob_parts = person['dob'].split('/')
    tob_parts = person['tob'].split(':')
    
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
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error calling VedicAstroAPI: {e}")
        return {}

def call_josi_api(person: Dict) -> Dict:
    """Call Josi API for chart calculation."""
    
    # First, create a person
    person_endpoint = f"{JOSI_BASE_URL}/persons"
    
    # Parse date and time
    dob_parts = person['dob'].split('/')
    dob_date = f"{dob_parts[2]}-{dob_parts[1].zfill(2)}-{dob_parts[0].zfill(2)}"
    
    tob_parts = person['tob'].split(':')
    tob_time = f"{tob_parts[0].zfill(2)}:{tob_parts[1].zfill(2)}:00"
    
    person_data = {
        "name": person['name'].split()[0],
        "date_of_birth": dob_date,
        "time_of_birth": f"{dob_date}T{tob_time}",
        "latitude": person['lat'],
        "longitude": person['lon'],
        "timezone": "Asia/Kolkata",
        "place_of_birth": person['place']
    }
    
    headers = {
        "X-API-Key": JOSI_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Create person
        person_response = requests.post(person_endpoint, json=person_data, headers=headers)
        if person_response.status_code != 200:
            print(f"Error creating person: {person_response.status_code} - {person_response.text}")
            return {}
        
        person_id = person_response.json()['data']['person_id']
        
        # Calculate chart
        chart_endpoint = f"{JOSI_BASE_URL}/charts/calculate"
        chart_data = {
            "person_id": person_id,
            "chart_type": "south_indian"
        }
        
        chart_response = requests.post(chart_endpoint, json=chart_data, headers=headers)
        if chart_response.status_code != 200:
            print(f"Error calculating chart: {chart_response.status_code} - {chart_response.text}")
            return {}
            
        return chart_response.json()['data']
    
    except Exception as e:
        print(f"Error calling Josi API: {e}")
        return {}

def extract_planet_positions(vedicastro_data: Dict, josi_data: Dict) -> tuple:
    """Extract planet positions from both API responses."""
    
    vedicastro_planets = {}
    josi_planets = {}
    
    # Extract from VedicAstroAPI
    if 'response' in vedicastro_data:
        for planet_id, planet_data in vedicastro_data['response'].items():
            if planet_id != '0':  # Skip ascendant
                name = planet_data.get('full_name', '')
                if name:
                    vedicastro_planets[name] = planet_data.get('global_degree', 0)
        
        # Get ascendant
        if '0' in vedicastro_data['response']:
            vedicastro_planets['Ascendant'] = vedicastro_data['response']['0'].get('global_degree', 0)
    
    # Extract from Josi API
    if 'chart_data' in josi_data and 'planets' in josi_data['chart_data']:
        for planet_name, planet_data in josi_data['chart_data']['planets'].items():
            josi_planets[planet_name] = planet_data.get('longitude', 0)
    
    if 'chart_data' in josi_data and 'ascendant' in josi_data['chart_data']:
        josi_planets['Ascendant'] = josi_data['chart_data']['ascendant'].get('longitude', 0)
    
    return vedicastro_planets, josi_planets

def compare_results(person: Dict, vedicastro_data: Dict, josi_data: Dict) -> Dict:
    """Compare results from both APIs."""
    
    vedicastro_planets, josi_planets = extract_planet_positions(vedicastro_data, josi_data)
    
    comparison = {
        "person": person['name'],
        "timestamp": datetime.now().isoformat(),
        "planets": {}
    }
    
    # Map planet names
    planet_mapping = {
        'Sun': 'Sun',
        'Moon': 'Moon',
        'Mars': 'Mars',
        'Mercury': 'Mercury',
        'Jupiter': 'Jupiter',
        'Venus': 'Venus',
        'Saturn': 'Saturn',
        'Rahu': 'Rahu',
        'Ketu': 'Ketu',
        'Ascendant': 'Ascendant'
    }
    
    for vedic_name, josi_name in planet_mapping.items():
        if vedic_name in vedicastro_planets and josi_name in josi_planets:
            vedic_pos = vedicastro_planets[vedic_name]
            josi_pos = josi_planets[josi_name]
            diff = abs(vedic_pos - josi_pos)
            
            comparison["planets"][vedic_name] = {
                "vedicastro": vedic_pos,
                "josi": josi_pos,
                "difference": diff,
                "arc_minutes": diff * 60,
                "accuracy": "EXCELLENT" if diff < 0.01 else "GOOD" if diff < 0.1 else "NEEDS IMPROVEMENT"
            }
    
    # Calculate overall accuracy
    if comparison["planets"]:
        avg_diff = sum(p["difference"] for p in comparison["planets"].values()) / len(comparison["planets"])
        comparison["average_difference"] = avg_diff
        comparison["average_arc_minutes"] = avg_diff * 60
        comparison["overall_accuracy"] = "EXCELLENT" if avg_diff < 0.01 else "GOOD" if avg_diff < 0.1 else "NEEDS IMPROVEMENT"
    
    return comparison

def main():
    """Run real-world API comparison tests."""
    
    print("Real-World API Comparison Test")
    print("=" * 80)
    print(f"VedicAstroAPI: {VEDICASTRO_BASE_URL}")
    print(f"Josi API: {JOSI_BASE_URL}")
    print()
    
    # Check if Josi API is running
    try:
        response = requests.get(f"{JOSI_BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("ERROR: Josi API is not running!")
            print("Please start the server with: poetry run uvicorn josi.main:app --port 8001")
            return
    except:
        print("ERROR: Cannot connect to Josi API!")
        print("Please start the server with: poetry run uvicorn josi.main:app --port 8001")
        return
    
    all_comparisons = []
    
    for person in TEST_PERSONS:
        print(f"\nTesting: {person['name']}")
        print("-" * 60)
        
        # Call both APIs
        print("  Calling VedicAstroAPI...", end="", flush=True)
        vedicastro_data = call_vedicastro_api(person)
        print(" Done")
        
        print("  Calling Josi API...", end="", flush=True)
        josi_data = call_josi_api(person)
        print(" Done")
        
        # Compare results
        if vedicastro_data and josi_data:
            comparison = compare_results(person, vedicastro_data, josi_data)
            all_comparisons.append(comparison)
            
            # Print results
            print(f"\n  Results for {person['name']}:")
            print(f"  {'Planet':<12} {'VedicAstro':>12} {'Josi':>12} {'Diff (°)':>10} {'Arc Min':>8} {'Accuracy':<10}")
            print(f"  {'-'*12} {'-'*12} {'-'*12} {'-'*10} {'-'*8} {'-'*10}")
            
            for planet, data in comparison["planets"].items():
                print(f"  {planet:<12} {data['vedicastro']:>12.6f} {data['josi']:>12.6f} "
                      f"{data['difference']:>10.6f} {data['arc_minutes']:>8.2f}' {data['accuracy']:<10}")
            
            if "average_difference" in comparison:
                print(f"\n  Average Difference: {comparison['average_difference']:.6f}° "
                      f"({comparison['average_arc_minutes']:.2f} arc minutes)")
                print(f"  Overall Accuracy: {comparison['overall_accuracy']}")
        
        # Small delay between API calls
        time.sleep(1)
    
    # Save comparison results
    if all_comparisons:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/api_comparison_{timestamp}.json"
        
        os.makedirs("reports", exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "vedicastro_api": VEDICASTRO_BASE_URL,
                "josi_api": JOSI_BASE_URL,
                "comparisons": all_comparisons
            }, f, indent=2)
        
        print(f"\n\nComparison results saved to: {output_file}")
        
        # Overall summary
        all_diffs = []
        for comp in all_comparisons:
            all_diffs.extend([p["difference"] for p in comp["planets"].values()])
        
        if all_diffs:
            avg_overall = sum(all_diffs) / len(all_diffs)
            print(f"\n{'='*80}")
            print("OVERALL SUMMARY")
            print(f"{'='*80}")
            print(f"Total comparisons: {len(all_diffs)}")
            print(f"Average difference: {avg_overall:.6f}° ({avg_overall * 60:.2f} arc minutes)")
            print(f"Maximum difference: {max(all_diffs):.6f}° ({max(all_diffs) * 60:.2f} arc minutes)")
            print(f"Minimum difference: {min(all_diffs):.6f}° ({min(all_diffs) * 60:.2f} arc minutes)")
            
            excellent = sum(1 for d in all_diffs if d < 0.01)
            good = sum(1 for d in all_diffs if 0.01 <= d < 0.1)
            needs_work = sum(1 for d in all_diffs if d >= 0.1)
            
            print(f"\nAccuracy Distribution:")
            print(f"  EXCELLENT: {excellent} ({excellent/len(all_diffs)*100:.1f}%)")
            print(f"  GOOD: {good} ({good/len(all_diffs)*100:.1f}%)")
            print(f"  NEEDS IMPROVEMENT: {needs_work} ({needs_work/len(all_diffs)*100:.1f}%)")

if __name__ == "__main__":
    main()