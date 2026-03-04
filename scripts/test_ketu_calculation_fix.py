#!/usr/bin/env python3
"""
Test script to verify Ketu calculation fix.
Tests that Ketu is always exactly 180 degrees opposite to Rahu.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import pytz
from src.josi.services.astrology_service import AstrologyCalculator

def test_ketu_calculation():
    """Test Ketu calculation for multiple test cases."""
    
    # Initialize calculator
    calc = AstrologyCalculator()
    
    # Test cases with known birth data
    test_cases = [
        {
            "name": "Test Case 1",
            "dt": datetime(1990, 5, 15, 10, 30, 0),
            "latitude": 13.0827,
            "longitude": 80.2707,
            "timezone": "Asia/Kolkata"
        },
        {
            "name": "Test Case 2", 
            "dt": datetime(1985, 12, 25, 22, 15, 0),
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata"
        },
        {
            "name": "Test Case 3",
            "dt": datetime(2000, 1, 1, 0, 0, 0),
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York"
        }
    ]
    
    print("Testing Ketu Calculation Fix")
    print("=" * 60)
    
    all_passed = True
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print(f"  DateTime: {test['dt']} {test['timezone']}")
        print(f"  Location: {test['latitude']}, {test['longitude']}")
        
        # Calculate chart
        chart = calc.calculate_vedic_chart(
            dt=test['dt'],
            latitude=test['latitude'],
            longitude=test['longitude'],
            timezone=test['timezone'],
            house_system='whole_sign'  # Use traditional Vedic house system
        )
        
        # Get Rahu and Ketu positions
        rahu_long = chart['planets']['Rahu']['longitude']
        ketu_long = chart['planets']['Ketu']['longitude']
        
        # Calculate expected Ketu position
        expected_ketu = (rahu_long + 180.0) % 360.0
        
        # Calculate difference
        diff = abs(ketu_long - expected_ketu)
        
        # Check if difference is negligible (< 0.0001 degrees)
        passed = diff < 0.0001
        
        print(f"  Rahu longitude: {rahu_long:.6f}°")
        print(f"  Ketu longitude: {ketu_long:.6f}°")
        print(f"  Expected Ketu: {expected_ketu:.6f}°")
        print(f"  Difference: {diff:.8f}°")
        print(f"  Status: {'PASS' if passed else 'FAIL'}")
        
        # Verify other Ketu properties
        print(f"  Rahu speed: {chart['planets']['Rahu']['speed']:.6f}")
        print(f"  Ketu speed: {chart['planets']['Ketu']['speed']:.6f} (should be negative of Rahu)")
        print(f"  Rahu house: {chart['planets']['Rahu']['house']}")
        print(f"  Ketu house: {chart['planets']['Ketu']['house']}")
        
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    print(f"Overall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    # Test with debug logging enabled
    print("\n\nRunning one test with debug logging:")
    print("=" * 60)
    
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    
    # Run first test case with logging
    test = test_cases[0]
    chart = calc.calculate_vedic_chart(
        dt=test['dt'],
        latitude=test['latitude'],
        longitude=test['longitude'],
        timezone=test['timezone'],
        house_system='whole_sign'
    )
    
    return all_passed

if __name__ == "__main__":
    success = test_ketu_calculation()
    sys.exit(0 if success else 1)