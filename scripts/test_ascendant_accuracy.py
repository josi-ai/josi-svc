#!/usr/bin/env python3
"""
Test script to verify ascendant calculation accuracy.
Compares calculations with debug logging enabled.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import logging
from src.josi.services.astrology_service import AstrologyCalculator

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_ascendant_accuracy():
    """Test ascendant calculation with known reference values."""
    
    calc = AstrologyCalculator()
    
    # Test cases from validation data
    test_cases = [
        {
            "name": "Valarmathi",
            "dt": datetime(1955, 4, 25, 3, 25, 0),
            "latitude": 13.0698,
            "longitude": 80.1943, 
            "timezone": "Asia/Kolkata",
            "reference_ascendant": 82.16557,  # From VedicAstroAPI
            "reference_ayanamsa": 23.073194
        },
        {
            "name": "Janaki",
            "dt": datetime(1960, 8, 24, 22, 10, 0),
            "latitude": 13.0621,
            "longitude": 80.2209,
            "timezone": "Asia/Kolkata", 
            "reference_ascendant": 297.2780,  # From VedicAstroAPI
            "reference_ayanamsa": 23.178905
        }
    ]
    
    print("\nAscendant Accuracy Test Results")
    print("=" * 80)
    
    for test in test_cases:
        print(f"\n\nTest Case: {test['name']}")
        print("-" * 40)
        
        # Test with Placidus (current default)
        print("\nCalculating with Placidus house system:")
        chart_placidus = calc.calculate_vedic_chart(
            dt=test['dt'],
            latitude=test['latitude'],
            longitude=test['longitude'],
            timezone=test['timezone'],
            house_system='placidus'
        )
        
        asc_placidus = chart_placidus['ascendant']['longitude']
        diff_placidus = abs(asc_placidus - test['reference_ascendant'])
        
        print(f"\nPlacidus Results:")
        print(f"  Calculated Ascendant: {asc_placidus:.6f}°")
        print(f"  Reference Ascendant:  {test['reference_ascendant']:.6f}°")
        print(f"  Difference:           {diff_placidus:.6f}° ({diff_placidus * 60:.2f} arc minutes)")
        print(f"  Accuracy:             {'EXCELLENT' if diff_placidus < 0.01 else 'GOOD' if diff_placidus < 0.1 else 'NEEDS IMPROVEMENT'}")
        
        # Test with Whole Sign (traditional Vedic)
        print("\n\nCalculating with Whole Sign house system:")
        chart_whole = calc.calculate_vedic_chart(
            dt=test['dt'],
            latitude=test['latitude'],
            longitude=test['longitude'],
            timezone=test['timezone'],
            house_system='whole_sign'
        )
        
        asc_whole = chart_whole['ascendant']['longitude']
        diff_whole = abs(asc_whole - test['reference_ascendant'])
        
        print(f"\nWhole Sign Results:")
        print(f"  Calculated Ascendant: {asc_whole:.6f}°")
        print(f"  Reference Ascendant:  {test['reference_ascendant']:.6f}°")
        print(f"  Difference:           {diff_whole:.6f}° ({diff_whole * 60:.2f} arc minutes)")
        print(f"  Accuracy:             {'EXCELLENT' if diff_whole < 0.01 else 'GOOD' if diff_whole < 0.1 else 'NEEDS IMPROVEMENT'}")
        
        # Compare ayanamsa
        print(f"\nAyanamsa Comparison:")
        print(f"  Calculated: {chart_placidus['ayanamsa']:.6f}°")
        print(f"  Reference:  {test['reference_ayanamsa']:.6f}°")
        print(f"  Difference: {abs(chart_placidus['ayanamsa'] - test['reference_ayanamsa']):.6f}°")
        
        # Time sensitivity analysis
        print(f"\n\nTime Sensitivity Analysis (1 minute change):")
        # Test with 1 minute earlier
        dt_early = test['dt'].replace(minute=test['dt'].minute - 1)
        chart_early = calc.calculate_vedic_chart(
            dt=dt_early,
            latitude=test['latitude'],
            longitude=test['longitude'],
            timezone=test['timezone'],
            house_system='placidus'
        )
        
        # Test with 1 minute later
        dt_late = test['dt'].replace(minute=test['dt'].minute + 1)
        chart_late = calc.calculate_vedic_chart(
            dt=dt_late,
            latitude=test['latitude'],
            longitude=test['longitude'],
            timezone=test['timezone'],
            house_system='placidus'
        )
        
        asc_change_per_minute = (chart_late['ascendant']['longitude'] - chart_early['ascendant']['longitude']) / 2
        print(f"  Ascendant change per minute: {asc_change_per_minute:.6f}° (expected ~0.25°)")
        
        # Calculate time error that would cause observed difference
        if asc_change_per_minute != 0:
            time_error_minutes = diff_placidus / abs(asc_change_per_minute)
            print(f"  Implied time error: {time_error_minutes:.2f} minutes ({time_error_minutes * 60:.0f} seconds)")

if __name__ == "__main__":
    test_ascendant_accuracy()