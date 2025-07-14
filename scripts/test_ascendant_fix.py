#!/usr/bin/env python3
"""
Test script to verify the Ascendant calculation fix.
"""

from datetime import datetime
import pytz
import sys
sys.path.append('/Users/govind/Developer/astrow')

from src.josi.services.astrology_service import AstrologyCalculator

def test_ascendant_calculations():
    """Test Ascendant calculations for key celebrities."""
    calc = AstrologyCalculator()
    
    test_cases = [
        {
            "name": "Barack Obama",
            "datetime": datetime(1961, 8, 4, 19, 24, 0),
            "timezone": "Pacific/Honolulu",
            "latitude": 21.3099,
            "longitude": -157.8581,
            "expected_asc": 318.05,  # 18.05° Aquarius
            "expected_sign": "Aquarius"
        },
        {
            "name": "Princess Diana",
            "datetime": datetime(1961, 7, 1, 19, 45, 0),
            "timezone": "Europe/London",
            "latitude": 52.8245,
            "longitude": 0.5150,
            "expected_asc": 258.43,  # 18.43° Sagittarius
            "expected_sign": "Sagittarius"
        },
        {
            "name": "Steve Jobs",
            "datetime": datetime(1955, 2, 24, 19, 15, 0),
            "timezone": "America/Los_Angeles",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "expected_asc": 172.29,  # 22.29° Virgo
            "expected_sign": "Virgo"
        }
    ]
    
    print("Testing Ascendant Calculations")
    print("=" * 60)
    
    for test in test_cases:
        # Localize the datetime
        tz = pytz.timezone(test["timezone"])
        dt = tz.localize(test["datetime"])
        
        # Calculate chart
        result = calc.calculate_western_chart(dt, test["latitude"], test["longitude"])
        
        # Extract ascendant
        asc_long = result["ascendant"]["longitude"]
        asc_sign = result["ascendant"]["sign"]
        asc_deg = asc_long % 30
        
        # Calculate difference
        diff = abs(asc_long - test["expected_asc"])
        if diff > 180:
            diff = 360 - diff
        
        status = "✓" if diff < 1.0 else "✗"
        
        print(f"\n{test['name']}:")
        print(f"  Expected: {test['expected_asc']:.2f}° ({test['expected_asc']%30:.2f}° {test['expected_sign']})")
        print(f"  Calculated: {asc_long:.2f}° ({asc_deg:.2f}° {asc_sign})")
        print(f"  Difference: {diff:.2f}° {status}")
        
        # Also show the first house cusp
        first_house = result["houses"][0]
        print(f"  First House: {first_house:.2f}°")
        
        # Verify they match
        if abs(asc_long - first_house) > 0.01:
            print(f"  ⚠️  WARNING: Ascendant and First House don't match!")

if __name__ == "__main__":
    test_ascendant_calculations()