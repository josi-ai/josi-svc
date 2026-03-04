#!/usr/bin/env python3
"""
Display VedicAstroAPI results from collected test data.
"""

import json
import os

def load_and_display_test_data(filename: str):
    """Load and display VedicAstroAPI results."""
    filepath = f"test_data/vedicastro_api/{filename}"
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    test_case = data['test_case']
    planet_details = data['data']['planet_details']
    
    print(f"\n{'='*80}")
    print(f"VedicAstroAPI Results for: {test_case['display_name']}")
    print(f"{'='*80}")
    print(f"Date of Birth: {test_case['dob']}")
    print(f"Time of Birth: {test_case['tob']}")
    print(f"Place: {test_case['place']}")
    print(f"Coordinates: {test_case['lat']}, {test_case['lon']}")
    print(f"Timezone: +{test_case['tz']} hours")
    
    print(f"\n{'Planet/Point':<15} {'Longitude':>12} {'Sign':<12} {'House':>6} {'Nakshatra':<15} {'Pada':>5}")
    print(f"{'-'*15} {'-'*12} {'-'*12} {'-'*6} {'-'*15} {'-'*5}")
    
    # Sort planets by ID for consistent display (handle non-numeric keys)
    numeric_planets = [(k, v) for k, v in planet_details.items() if k.isdigit()]
    sorted_planets = sorted(numeric_planets, key=lambda x: int(x[0]))
    
    for planet_id, planet_data in sorted_planets:
        if isinstance(planet_data, dict):
            name = planet_data.get('full_name', planet_data.get('name', ''))
            longitude = planet_data.get('global_degree', 0)
            sign = planet_data.get('zodiac', '')
            house = planet_data.get('house', '')
            nakshatra = planet_data.get('nakshatra', '')
            pada = planet_data.get('nakshatra_pada', '')
            
            # Special formatting for ascendant
            if planet_id == '0':
                name = 'Ascendant'
            
            print(f"{name:<15} {longitude:>12.6f} {sign:<12} {house:>6} {nakshatra:<15} {pada:>5}")
    
    # Additional details
    print(f"\n{'Additional Information':^80}")
    print("-" * 80)
    
    # Show retrograde planets
    retrograde_planets = []
    for planet_id, planet_data in planet_details.items():
        if isinstance(planet_data, dict) and planet_data.get('retro', False):
            retrograde_planets.append(planet_data.get('full_name', ''))
    
    if retrograde_planets:
        print(f"Retrograde Planets: {', '.join(retrograde_planets)}")
    else:
        print("No retrograde planets")
    
    # Show planetary speeds (if available)
    print(f"\nPlanetary Speeds (degrees/day):")
    for planet_id, planet_data in sorted_planets:
        if isinstance(planet_data, dict) and 'speed_radians_per_day' in planet_data:
            name = planet_data.get('full_name', planet_data.get('name', ''))
            if planet_id == '0':  # Skip ascendant
                continue
            # Convert radians to degrees
            speed_rad = planet_data.get('speed_radians_per_day', 0)
            speed_deg = speed_rad * 180 / 3.14159265359
            print(f"  {name:<12}: {speed_deg:>10.6f}°/day")
    
    # Show ayanamsa if available
    if 'extended_kundli' in data.get('data', {}):
        ayanamsa_data = data['data']['extended_kundli'].get('ayanamsa', {})
        if ayanamsa_data:
            print(f"\nAyanamsa Information:")
            print(f"  Type: {ayanamsa_data.get('type', 'N/A')}")
            print(f"  Value: {ayanamsa_data.get('degree', 'N/A')}°")

def main():
    """Display all VedicAstroAPI results."""
    
    print("VedicAstroAPI Collected Test Data Results")
    print("=" * 80)
    
    test_files = [
        "collected_Valarmathi_Kannappan.json",
        "collected_Janaki_Panneerselvam.json",
        "collected_Govindarajan_Panneerselvam.json",
        "collected_Panneerselvam_Chandrasekaran.json"
    ]
    
    for filename in test_files:
        try:
            if os.path.exists(f"test_data/vedicastro_api/{filename}"):
                load_and_display_test_data(filename)
            else:
                print(f"\nFile not found: {filename}")
        except Exception as e:
            print(f"\nError processing {filename}: {e}")
    
    print(f"\n{'='*80}")
    print("End of VedicAstroAPI Results")

if __name__ == "__main__":
    main()