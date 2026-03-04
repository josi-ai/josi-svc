#!/usr/bin/env python3
"""
Compare Josi calculations for all 5 persons with available reference data.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

def calculate_for_person(person_data):
    """Calculate chart using Josi AstrologyCalculator."""
    calc = AstrologyCalculator()
    
    # Parse date/time based on format
    if 'date_of_birth' in person_data:
        # Format: YYYY-MM-DD
        dob_parts = person_data['date_of_birth'].split('-')
        tob_parts = person_data['time_of_birth'].split(':')
        dt = datetime(
            int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2]),
            int(tob_parts[0]), int(tob_parts[1]), int(tob_parts[2])
        )
    else:
        # Format: DD/MM/YYYY
        dob_parts = person_data['dob'].split('/')
        tob_parts = person_data['tob'].split(':')
        dt = datetime(
            int(dob_parts[2]), int(dob_parts[1]), int(dob_parts[0]),
            int(tob_parts[0]), int(tob_parts[1]), 0
        )
    
    # Get coordinates
    lat = person_data.get('latitude', person_data.get('lat'))
    lon = person_data.get('longitude', person_data.get('lon'))
    
    # Calculate
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=lat,
        longitude=lon,
        timezone="Asia/Kolkata",
        house_system='placidus'
    )
    
    return chart

def main():
    """Compare all 5 persons."""
    print("Josi Astrology Calculations for All 5 Test Persons")
    print("=" * 80)
    
    # All 5 persons with their data
    all_persons = [
        {
            "name": "Archana M",
            "date_of_birth": "1998-12-07",
            "time_of_birth": "21:15:00",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "has_reference": False
        },
        {
            "name": "Valarmathi Kannappan",
            "dob": "11/02/1961",
            "tob": "15:30",
            "lat": 13.1622,
            "lon": 80.005,
            "has_reference": True,
            "reference_file": "collected_Valarmathi_Kannappan.json"
        },
        {
            "name": "Janaki Panneerselvam",
            "dob": "18/12/1982",
            "tob": "10:10",
            "lat": 13.0827,
            "lon": 80.2707,
            "has_reference": True,
            "reference_file": "collected_Janaki_Panneerselvam.json"
        },
        {
            "name": "Govindarajan Panneerselvam",
            "dob": "29/12/1989",
            "tob": "12:12",
            "lat": 13.0827,
            "lon": 80.2707,
            "has_reference": True,
            "reference_file": "collected_Govindarajan_Panneerselvam.json"
        },
        {
            "name": "Panneerselvam Chandrasekaran",
            "dob": "20/08/1954",
            "tob": "18:20",
            "lat": 12.8185,
            "lon": 79.6947,
            "has_reference": True,
            "reference_file": "collected_Panneerselvam_Chandrasekaran.json"
        }
    ]
    
    print("\nSummary of Calculations:\n")
    
    # Header
    print(f"{'Name':<30} {'Ascendant':>12} {'Sun':>12} {'Moon':>12} {'Ref Data':<10}")
    print(f"{'-'*30} {'-'*12} {'-'*12} {'-'*12} {'-'*10}")
    
    for person in all_persons:
        # Calculate chart
        chart = calculate_for_person(person)
        
        # Display summary
        asc = chart['ascendant']['longitude']
        sun = chart['planets']['Sun']['longitude']
        moon = chart['planets']['Moon']['longitude']
        ref_status = "Available" if person['has_reference'] else "Not Available"
        
        print(f"{person['name']:<30} {asc:>12.6f} {sun:>12.6f} {moon:>12.6f} {ref_status:<10}")
    
    # Detailed comparison for those with reference data
    print(f"\n\n{'='*80}")
    print("Detailed Comparison with Reference Data")
    print("=" * 80)
    
    total_comparisons = 0
    total_diff = 0
    
    for person in all_persons:
        if person['has_reference']:
            print(f"\n{person['name']}:")
            
            # Load reference data
            try:
                with open(f"test_data/vedicastro_api/{person['reference_file']}", 'r') as f:
                    ref_data = json.load(f)
                
                # Calculate chart
                chart = calculate_for_person(person)
                
                # Extract reference positions
                planet_details = ref_data['data']['planet_details']
                
                print(f"  {'Planet':<10} {'Reference':>12} {'Calculated':>12} {'Diff (°)':>10} {'Arc Min':>8}")
                print(f"  {'-'*10} {'-'*12} {'-'*12} {'-'*10} {'-'*8}")
                
                # Compare each planet
                comparisons = 0
                person_diff = 0
                
                # Ascendant
                if '0' in planet_details:
                    ref_asc = planet_details['0']['global_degree']
                    calc_asc = chart['ascendant']['longitude']
                    diff = abs(ref_asc - calc_asc)
                    print(f"  {'Ascendant':<10} {ref_asc:>12.6f} {calc_asc:>12.6f} {diff:>10.6f} {diff*60:>8.2f}'")
                    comparisons += 1
                    person_diff += diff
                
                # Planets
                planet_map = {
                    '1': ('Sun', 'Sun'),
                    '2': ('Moon', 'Moon'),
                    '3': ('Mars', 'Mars'),
                    '4': ('Mercury', 'Mercury'),
                    '5': ('Jupiter', 'Jupiter'),
                    '6': ('Venus', 'Venus'),
                    '7': ('Saturn', 'Saturn')
                }
                
                for planet_id, (ref_name, calc_name) in planet_map.items():
                    if planet_id in planet_details and isinstance(planet_details[planet_id], dict):
                        ref_pos = planet_details[planet_id]['global_degree']
                        calc_pos = chart['planets'][calc_name]['longitude']
                        diff = abs(ref_pos - calc_pos)
                        print(f"  {ref_name:<10} {ref_pos:>12.6f} {calc_pos:>12.6f} {diff:>10.6f} {diff*60:>8.2f}'")
                        comparisons += 1
                        person_diff += diff
                
                if comparisons > 0:
                    avg = person_diff / comparisons
                    print(f"\n  Average difference: {avg:.6f}° ({avg*60:.2f} arc minutes)")
                    total_comparisons += comparisons
                    total_diff += person_diff
                    
            except Exception as e:
                print(f"  Error loading reference data: {e}")
    
    if total_comparisons > 0:
        overall_avg = total_diff / total_comparisons
        print(f"\n{'='*80}")
        print(f"OVERALL ACCURACY (4 persons with reference data):")
        print(f"  Total celestial bodies compared: {total_comparisons}")
        print(f"  Overall average difference: {overall_avg:.6f}° ({overall_avg*60:.2f} arc minutes)")
        print(f"  Accuracy: {'EXCELLENT' if overall_avg < 0.01 else 'GOOD' if overall_avg < 0.1 else 'NEEDS IMPROVEMENT'}")

if __name__ == "__main__":
    main()