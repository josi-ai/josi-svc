#!/usr/bin/env python3
"""
Compare Josi calculations with previously collected VedicAstroAPI test data.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

def load_test_data(filename: str) -> dict:
    """Load previously collected test data."""
    filepath = f"test_data/vedicastro_api/{filename}"
    with open(filepath, 'r') as f:
        return json.load(f)

def calculate_locally(test_case: dict) -> dict:
    """Calculate using local AstrologyCalculator."""
    
    calc = AstrologyCalculator()
    
    # Parse date and time from test case
    dob_parts = test_case['dob'].split('/')
    tob_parts = test_case['tob'].split(':')
    
    dt = datetime(
        int(dob_parts[2]),  # year
        int(dob_parts[1]),  # month
        int(dob_parts[0]),  # day
        int(tob_parts[0]),  # hour
        int(tob_parts[1])   # minute
    )
    
    # Calculate chart
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=test_case['lat'],
        longitude=test_case['lon'],
        timezone="Asia/Kolkata",
        house_system='placidus'
    )
    
    return chart

def compare_results(person_name: str, vedic_data: dict, local_chart: dict):
    """Compare results."""
    
    print(f"\n{'='*80}")
    print(f"Comparing: {person_name}")
    print(f"{'='*80}")
    
    # Extract planet positions from VedicAstroAPI data
    vedic_planets = {}
    planet_details = vedic_data['data']['planet_details']
    
    for planet_id, planet_data in planet_details.items():
        # Skip if planet_data is not a dict
        if not isinstance(planet_data, dict):
            continue
            
        if planet_id == '0':  # Ascendant
            vedic_planets['Ascendant'] = planet_data.get('global_degree', 0)
        else:
            name = planet_data.get('full_name', '')
            if name:
                vedic_planets[name] = planet_data.get('global_degree', 0)
    
    # Compare results
    print(f"\n{'Planet':<12} {'VedicAstro':>12} {'Josi Local':>12} {'Diff (°)':>10} {'Arc Min':>8} {'Accuracy':<10}")
    print(f"{'-'*12} {'-'*12} {'-'*12} {'-'*10} {'-'*8} {'-'*10}")
    
    total_diff = 0
    count = 0
    
    # Compare common planets
    planet_mapping = {
        'Sun': 'Sun',
        'Moon': 'Moon', 
        'Mars': 'Mars',
        'Mercury': 'Mercury',
        'Jupiter': 'Jupiter',
        'Venus': 'Venus',
        'Saturn': 'Saturn',
        'Ascendant': 'Ascendant'
    }
    
    for vedic_name, local_name in planet_mapping.items():
        if vedic_name in vedic_planets:
            vedic_pos = vedic_planets[vedic_name]
            
            if local_name == 'Ascendant':
                local_pos = local_chart['ascendant']['longitude']
            elif local_name in local_chart['planets']:
                local_pos = local_chart['planets'][local_name]['longitude']
            else:
                continue
                
            diff = abs(vedic_pos - local_pos)
            arc_min = diff * 60
            accuracy = 'EXCELLENT' if diff < 0.01 else 'GOOD' if diff < 0.1 else 'POOR'
            
            print(f"{vedic_name:<12} {vedic_pos:>12.6f} {local_pos:>12.6f} {diff:>10.6f} {arc_min:>8.2f}' {accuracy:<10}")
            
            total_diff += diff
            count += 1
    
    # Check Rahu/Ketu
    if 'Rahu' in local_chart['planets'] and 'Ketu' in local_chart['planets']:
        print(f"\nRahu/Ketu Verification:")
        rahu_pos = local_chart['planets']['Rahu']['longitude']
        ketu_pos = local_chart['planets']['Ketu']['longitude']
        ketu_expected = (rahu_pos + 180.0) % 360.0
        ketu_diff = abs(ketu_pos - ketu_expected)
        print(f"  Rahu: {rahu_pos:.6f}°")
        print(f"  Ketu: {ketu_pos:.6f}° (expected: {ketu_expected:.6f}°)")
        print(f"  Ketu accuracy: {'PERFECT' if ketu_diff < 0.0001 else 'ERROR'}")
    
    if count > 0:
        avg_diff = total_diff / count
        print(f"\nSummary for {person_name}:")
        print(f"  Total comparisons: {count}")
        print(f"  Average difference: {avg_diff:.6f}° ({avg_diff * 60:.2f} arc minutes)")
        print(f"  Maximum difference: {max([abs(vedic_planets.get(p, 0) - (local_chart['ascendant']['longitude'] if p == 'Ascendant' else local_chart['planets'].get(p, {}).get('longitude', 0))) for p in planet_mapping.keys() if p in vedic_planets]):.6f}°")
        print(f"  Overall accuracy: {'EXCELLENT' if avg_diff < 0.01 else 'GOOD' if avg_diff < 0.1 else 'NEEDS IMPROVEMENT'}")
        
        return {
            'person': person_name,
            'avg_diff': avg_diff,
            'count': count
        }
    
    return None

def main():
    """Run comparison with test data."""
    
    print("Josi vs VedicAstroAPI Comparison (Using Collected Test Data)")
    print("=" * 80)
    
    # Test files to process
    test_files = [
        ("Valarmathi Kannappan", "collected_Valarmathi_Kannappan.json"),
        ("Janaki Panneerselvam", "collected_Janaki_Panneerselvam.json"),
        ("Govindarajan Panneerselvam", "collected_Govindarajan_Panneerselvam.json"),
        ("Panneerselvam Chandrasekaran", "collected_Panneerselvam_Chandrasekaran.json")
    ]
    
    # Check if we have Archana's data collected
    archana_file = "collected_Archana_M.json"
    if os.path.exists(f"test_data/vedicastro_api/{archana_file}"):
        test_files.append(("Archana M", archana_file))
    
    all_results = []
    
    for person_name, filename in test_files:
        try:
            # Load test data
            vedic_data = load_test_data(filename)
            test_case = vedic_data['test_case']
            
            print(f"\nProcessing: {person_name}")
            print(f"  DOB: {test_case['dob']}, TOB: {test_case['tob']}")
            print(f"  Location: {test_case['place']}")
            
            # Calculate locally
            local_chart = calculate_locally(test_case)
            
            # Compare
            result = compare_results(person_name, vedic_data, local_chart)
            if result:
                all_results.append(result)
                
        except Exception as e:
            print(f"\nError processing {person_name}: {e}")
    
    # Overall summary
    if all_results:
        print(f"\n\n{'='*80}")
        print("OVERALL SUMMARY")
        print(f"{'='*80}")
        
        total_comparisons = sum(r['count'] for r in all_results)
        overall_avg = sum(r['avg_diff'] * r['count'] for r in all_results) / total_comparisons
        
        print(f"\nTotal persons tested: {len(all_results)}")
        print(f"Total celestial bodies compared: {total_comparisons}")
        print(f"Overall average difference: {overall_avg:.6f}° ({overall_avg * 60:.2f} arc minutes)")
        print(f"Overall accuracy: {'EXCELLENT' if overall_avg < 0.01 else 'GOOD' if overall_avg < 0.1 else 'NEEDS IMPROVEMENT'}")

if __name__ == "__main__":
    main()