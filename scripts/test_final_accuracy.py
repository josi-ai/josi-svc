#!/usr/bin/env python3
"""
Final accuracy test with correct birth data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

def test_final_accuracy():
    """Test with correct birth data from collected files."""
    
    calc = AstrologyCalculator()
    
    # Correct test data from collected files
    test_cases = [
        {
            "name": "Valarmathi Kannappan",
            "dt": datetime(1961, 2, 11, 15, 30, 0),  # 11/02/1961 15:30
            "latitude": 13.1622,
            "longitude": 80.005,
            "timezone": "Asia/Kolkata",
            "reference_ascendant": 82.16557187740024,
            "reference_planets": {
                "Sun": 299.1395504817733,
                "Moon": 244.34990472992553,
                "Mars": 66.84510622177082,
                "Mercury": 315.64303217173153,
                "Jupiter": 270.255404012214,
                "Venus": 345.3811032679155,
                "Saturn": 271.07782937826585
            }
        },
        {
            "name": "Janaki Panneerselvam",
            "dt": datetime(1982, 12, 18, 10, 10, 0),  # 18/12/1982 10:10
            "latitude": 13.0827,
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata",
            "reference_ascendant": 297.2779524314666,
            "reference_planets": {
                "Sun": 242.31313281639302,
                "Moon": 272.68132107993546,
                "Mars": 282.5741373326083,
                "Mercury": 257.69058107969664,
                "Jupiter": 214.76915240665136,
                "Venus": 253.10888437227936,
                "Saturn": 188.20158296041515
            }
        }
    ]
    
    print("\nFinal Accuracy Test with Correct Birth Data")
    print("=" * 80)
    
    overall_diffs = []
    
    for test in test_cases:
        print(f"\n\nTest Case: {test['name']}")
        print(f"  DOB: {test['dt'].strftime('%d/%m/%Y')}")
        print(f"  TOB: {test['dt'].strftime('%H:%M')}")
        print(f"  Location: {test['latitude']}, {test['longitude']}")
        print("-" * 60)
        
        # Calculate chart with enhanced logging
        chart = calc.calculate_vedic_chart(
            dt=test['dt'],
            latitude=test['latitude'],
            longitude=test['longitude'],
            timezone=test['timezone'],
            house_system='placidus'
        )
        
        # Check ascendant
        asc_calculated = chart['ascendant']['longitude']
        asc_reference = test['reference_ascendant']
        asc_diff = abs(asc_calculated - asc_reference)
        overall_diffs.append(asc_diff)
        
        print(f"\nAscendant:")
        print(f"  Reference:  {asc_reference:.6f}°")
        print(f"  Calculated: {asc_calculated:.6f}°")
        print(f"  Difference: {asc_diff:.6f}° ({asc_diff * 60:.2f} arc minutes)")
        accuracy = 'EXCELLENT (<0.6\')' if asc_diff < 0.01 else 'GOOD (<6\')' if asc_diff < 0.1 else 'FAIR'
        print(f"  Accuracy:   {accuracy}")
        
        # Check planets
        print(f"\nPlanet Positions:")
        print(f"  {'Planet':<10} {'Reference':>12} {'Calculated':>12} {'Diff':>10} {'Arc Min':>8}")
        print(f"  {'-'*10} {'-'*12} {'-'*12} {'-'*10} {'-'*8}")
        
        for planet_name, ref_long in test['reference_planets'].items():
            if planet_name in chart['planets']:
                calc_long = chart['planets'][planet_name]['longitude']
                diff = abs(calc_long - ref_long)
                overall_diffs.append(diff)
                arc_min = diff * 60
                print(f"  {planet_name:<10} {ref_long:>12.6f} {calc_long:>12.6f} {diff:>10.6f} {arc_min:>8.2f}'")
        
        # Rahu/Ketu verification
        if 'Rahu' in chart['planets']:
            print(f"\nRahu/Ketu:")
            print(f"  Rahu: {chart['planets']['Rahu']['longitude']:.6f}°")
            print(f"  Ketu: {chart['planets']['Ketu']['longitude']:.6f}° (correctly 180° opposite)")
    
    # Overall summary
    print(f"\n\n{'='*80}")
    print(f"OVERALL ACCURACY SUMMARY")
    print(f"{'='*80}")
    
    avg_diff = sum(overall_diffs) / len(overall_diffs)
    max_diff = max(overall_diffs)
    min_diff = min(overall_diffs)
    
    print(f"\nStatistics (all celestial bodies):")
    print(f"  Average difference: {avg_diff:.6f}° ({avg_diff * 60:.2f} arc minutes)")
    print(f"  Maximum difference: {max_diff:.6f}° ({max_diff * 60:.2f} arc minutes)")
    print(f"  Minimum difference: {min_diff:.6f}° ({min_diff * 60:.2f} arc minutes)")
    
    excellent_count = sum(1 for d in overall_diffs if d < 0.01)
    good_count = sum(1 for d in overall_diffs if 0.01 <= d < 0.1)
    fair_count = sum(1 for d in overall_diffs if d >= 0.1)
    
    print(f"\nAccuracy Distribution:")
    print(f"  EXCELLENT (<0.01° / <0.6'): {excellent_count} ({excellent_count/len(overall_diffs)*100:.1f}%)")
    print(f"  GOOD (0.01-0.1° / 0.6-6'): {good_count} ({good_count/len(overall_diffs)*100:.1f}%)")
    print(f"  FAIR (>0.1° / >6'): {fair_count} ({fair_count/len(overall_diffs)*100:.1f}%)")
    
    print(f"\nConclusion: {'PROFESSIONAL GRADE' if avg_diff < 0.05 else 'ACCEPTABLE' if avg_diff < 0.1 else 'NEEDS IMPROVEMENT'}")

if __name__ == "__main__":
    test_final_accuracy()