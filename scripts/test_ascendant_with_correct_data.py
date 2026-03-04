#!/usr/bin/env python3
"""
Test ascendant accuracy with correct birth data from validation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

def test_ascendant_with_correct_data():
    """Test ascendant with correct birth data."""
    
    calc = AstrologyCalculator()
    
    # Correct test data from validation files
    test_cases = [
        {
            "name": "Valarmathi Kannappan",
            # DOB: 11/02/1961, TOB: 15:30
            "dt": datetime(1961, 2, 11, 15, 30, 0),
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
            # DOB: 24/08/1960, TOB: 22:10
            "dt": datetime(1960, 8, 24, 22, 10, 0),
            "latitude": 13.0621,
            "longitude": 80.2209,
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
    
    print("\nAscendant and Planet Position Accuracy Test")
    print("=" * 80)
    
    for test in test_cases:
        print(f"\n\nTest Case: {test['name']}")
        print(f"  DOB: {test['dt'].strftime('%d/%m/%Y')}")
        print(f"  TOB: {test['dt'].strftime('%H:%M')}")
        print(f"  Location: {test['latitude']}, {test['longitude']}")
        print("-" * 60)
        
        # Calculate chart
        chart = calc.calculate_vedic_chart(
            dt=test['dt'],
            latitude=test['latitude'],
            longitude=test['longitude'],
            timezone=test['timezone'],
            house_system='placidus'  # Use placidus as that's what validation used
        )
        
        # Check ascendant
        asc_calculated = chart['ascendant']['longitude']
        asc_reference = test['reference_ascendant']
        asc_diff = abs(asc_calculated - asc_reference)
        
        print(f"\nAscendant:")
        print(f"  Reference:  {asc_reference:.6f}°")
        print(f"  Calculated: {asc_calculated:.6f}°")
        print(f"  Difference: {asc_diff:.6f}° ({asc_diff * 60:.2f} arc minutes)")
        print(f"  Accuracy:   {'EXCELLENT' if asc_diff < 0.01 else 'GOOD' if asc_diff < 0.1 else 'NEEDS IMPROVEMENT'}")
        
        # Check planets
        print(f"\nPlanet Positions:")
        print(f"  {'Planet':<10} {'Reference':>12} {'Calculated':>12} {'Diff':>10} {'Accuracy':<10}")
        print(f"  {'-'*10} {'-'*12} {'-'*12} {'-'*10} {'-'*10}")
        
        total_diff = 0
        planet_count = 0
        
        for planet_name, ref_long in test['reference_planets'].items():
            if planet_name in chart['planets']:
                calc_long = chart['planets'][planet_name]['longitude']
                diff = abs(calc_long - ref_long)
                total_diff += diff
                planet_count += 1
                accuracy = 'EXCELLENT' if diff < 0.01 else 'GOOD' if diff < 0.1 else 'POOR'
                print(f"  {planet_name:<10} {ref_long:>12.6f} {calc_long:>12.6f} {diff:>10.6f} {accuracy:<10}")
        
        # Check Rahu/Ketu
        if 'Rahu' in chart['planets'] and 'Ketu' in chart['planets']:
            rahu_long = chart['planets']['Rahu']['longitude']
            ketu_long = chart['planets']['Ketu']['longitude']
            ketu_expected = (rahu_long + 180.0) % 360.0
            ketu_diff = abs(ketu_long - ketu_expected)
            print(f"\nRahu/Ketu Verification:")
            print(f"  Rahu:          {rahu_long:.6f}°")
            print(f"  Ketu:          {ketu_long:.6f}°")
            print(f"  Expected Ketu: {ketu_expected:.6f}°")
            print(f"  Ketu accuracy: {'PERFECT' if ketu_diff < 0.0001 else 'ERROR'}")
        
        # Overall summary
        avg_diff = total_diff / planet_count if planet_count > 0 else 0
        print(f"\nOverall Summary:")
        print(f"  Average planet difference: {avg_diff:.6f}°")
        print(f"  Ayanamsa used: {chart['ayanamsa_name']} = {chart['ayanamsa']:.6f}°")
        print(f"  House system: {chart['house_system']}")

if __name__ == "__main__":
    test_ascendant_with_correct_data()