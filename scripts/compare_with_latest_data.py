#!/usr/bin/env python3
"""
Compare Josi calculations with latest VedicAstroAPI data for all 5 persons.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

def load_latest_data(filename: str) -> dict:
    """Load latest VedicAstroAPI data."""
    filepath = f"test_data/vedicastro_api/latest_fetch/{filename}"
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
    """Compare results and return statistics."""
    
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
    max_diff = 0
    
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
            max_diff = max(max_diff, diff)
    
    # Check Rahu/Ketu if available
    if 'Rahu' in vedic_planets and 'Rahu' in local_chart['planets']:
        vedic_rahu = vedic_planets['Rahu']
        local_rahu = local_chart['planets']['Rahu']['longitude']
        diff = abs(vedic_rahu - local_rahu)
        print(f"\n{'Rahu':<12} {vedic_rahu:>12.6f} {local_rahu:>12.6f} {diff:>10.6f} {diff*60:>8.2f}' {'EXCELLENT' if diff < 0.01 else 'GOOD'}")
        
    if 'Ketu' in vedic_planets and 'Ketu' in local_chart['planets']:
        vedic_ketu = vedic_planets['Ketu']
        local_ketu = local_chart['planets']['Ketu']['longitude']
        diff = abs(vedic_ketu - local_ketu)
        print(f"{'Ketu':<12} {vedic_ketu:>12.6f} {local_ketu:>12.6f} {diff:>10.6f} {diff*60:>8.2f}' {'EXCELLENT' if diff < 0.01 else 'GOOD'}")
    
    # Verify Ketu is 180° from Rahu
    if 'Rahu' in local_chart['planets'] and 'Ketu' in local_chart['planets']:
        rahu_pos = local_chart['planets']['Rahu']['longitude']
        ketu_pos = local_chart['planets']['Ketu']['longitude']
        ketu_expected = (rahu_pos + 180.0) % 360.0
        ketu_diff = abs(ketu_pos - ketu_expected)
        print(f"\nKetu verification: Expected {ketu_expected:.6f}°, Got {ketu_pos:.6f}° ({'PERFECT' if ketu_diff < 0.0001 else 'ERROR'})")
    
    if count > 0:
        avg_diff = total_diff / count
        print(f"\nSummary for {person_name}:")
        print(f"  Total comparisons: {count}")
        print(f"  Average difference: {avg_diff:.6f}° ({avg_diff * 60:.2f} arc minutes)")
        print(f"  Maximum difference: {max_diff:.6f}° ({max_diff * 60:.2f} arc minutes)")
        print(f"  Overall accuracy: {'EXCELLENT' if avg_diff < 0.01 else 'GOOD' if avg_diff < 0.1 else 'NEEDS IMPROVEMENT'}")
        
        return {
            'person': person_name,
            'avg_diff': avg_diff,
            'max_diff': max_diff,
            'count': count
        }
    
    return None

def main():
    """Run comparison with latest data."""
    
    print("Josi vs VedicAstroAPI Comparison (Latest Data - 2025-07-17)")
    print("=" * 80)
    
    # All 5 persons with their latest data files
    test_files = [
        ("Archana M", "Archana_M_latest.json"),
        ("Valarmathi Kannappan", "Valarmathi_Kannappan_latest.json"),
        ("Janaki Panneerselvam", "Janaki_Panneerselvam_latest.json"),
        ("Govindarajan Panneerselvam", "Govindarajan_Panneerselvam_latest.json"),
        ("Panneerselvam Chandrasekaran", "Panneerselvam_Chandrasekaran_latest.json")
    ]
    
    all_results = []
    
    for person_name, filename in test_files:
        try:
            # Load latest data
            vedic_data = load_latest_data(filename)
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
        print("OVERALL SUMMARY (All 5 Persons with Latest Data)")
        print(f"{'='*80}")
        
        total_comparisons = sum(r['count'] for r in all_results)
        overall_avg = sum(r['avg_diff'] * r['count'] for r in all_results) / total_comparisons
        overall_max = max(r['max_diff'] for r in all_results)
        
        print(f"\nTotal persons tested: {len(all_results)}")
        print(f"Total celestial bodies compared: {total_comparisons}")
        print(f"Overall average difference: {overall_avg:.6f}° ({overall_avg * 60:.2f} arc minutes)")
        print(f"Maximum difference across all: {overall_max:.6f}° ({overall_max * 60:.2f} arc minutes)")
        print(f"Overall accuracy: {'EXCELLENT' if overall_avg < 0.01 else 'GOOD' if overall_avg < 0.1 else 'NEEDS IMPROVEMENT'}")
        
        # Individual summaries
        print(f"\nPerson-wise Summary:")
        print(f"{'Person':<30} {'Avg Diff (°)':>12} {'Max Diff (°)':>12} {'Accuracy':<10}")
        print(f"{'-'*30} {'-'*12} {'-'*12} {'-'*10}")
        for result in all_results:
            accuracy = 'EXCELLENT' if result['avg_diff'] < 0.01 else 'GOOD'
            print(f"{result['person']:<30} {result['avg_diff']:>12.6f} {result['max_diff']:>12.6f} {accuracy:<10}")

if __name__ == "__main__":
    main()