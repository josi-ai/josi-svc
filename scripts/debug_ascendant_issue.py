#!/usr/bin/env python3
"""
Debug script to understand ascendant calculation issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

def debug_ascendant():
    """Debug ascendant calculations."""
    
    calc = AstrologyCalculator()
    
    # Test case: Valarmathi
    dt = datetime(1955, 4, 25, 3, 25, 0)
    latitude = 13.0698
    longitude = 80.1943
    timezone = "Asia/Kolkata"
    reference_ascendant = 82.16557  # From VedicAstroAPI
    
    print("Debugging Ascendant Calculation for Valarmathi")
    print("=" * 60)
    
    # Calculate both tropical and sidereal
    chart_sidereal = calc.calculate_vedic_chart(dt, latitude, longitude, timezone, house_system='placidus')
    chart_tropical = calc.calculate_western_chart(dt, latitude, longitude, timezone, house_system='placidus')
    
    asc_sidereal = chart_sidereal['ascendant']['longitude']
    asc_tropical = chart_tropical['ascendant']['longitude']
    ayanamsa = chart_sidereal['ayanamsa']
    
    print(f"\nCalculations:")
    print(f"  Tropical Ascendant: {asc_tropical:.6f}°")
    print(f"  Sidereal Ascendant: {asc_sidereal:.6f}°")
    print(f"  Ayanamsa: {ayanamsa:.6f}°")
    print(f"  Reference Ascendant: {reference_ascendant:.6f}°")
    
    # Check if reference is tropical
    print(f"\nHypothesis Testing:")
    print(f"  If reference is tropical, expected sidereal: {reference_ascendant - ayanamsa:.6f}°")
    print(f"  If reference is sidereal, expected tropical: {reference_ascendant + ayanamsa:.6f}°")
    
    # Check our calculation consistency
    print(f"\nConsistency Check:")
    print(f"  Tropical - Ayanamsa = {asc_tropical - ayanamsa:.6f}° (should equal sidereal)")
    print(f"  Actual Sidereal = {asc_sidereal:.6f}°")
    print(f"  Difference = {abs((asc_tropical - ayanamsa) - asc_sidereal):.6f}°")
    
    # Check if it's a 360° wrap issue
    print(f"\nChecking 360° wrap possibilities:")
    possible_values = [
        reference_ascendant,
        reference_ascendant + 180,
        reference_ascendant - 180,
        360 - reference_ascendant,
        (reference_ascendant + ayanamsa) % 360,
        (reference_ascendant - ayanamsa) % 360
    ]
    
    for val in possible_values:
        diff_tropical = min(abs(asc_tropical - val), 360 - abs(asc_tropical - val))
        diff_sidereal = min(abs(asc_sidereal - val), 360 - abs(asc_sidereal - val))
        print(f"  Test value {val:.6f}°: Tropical diff={diff_tropical:.6f}°, Sidereal diff={diff_sidereal:.6f}°")
    
    # Manual calculation verification
    print(f"\n\nManual Calculation Check:")
    print(f"  Our Tropical: {asc_tropical:.6f}°")
    print(f"  Our Sidereal: {asc_sidereal:.6f}°")
    print(f"  Difference: {asc_tropical - asc_sidereal:.6f}° (should equal ayanamsa {ayanamsa:.6f}°)")
    
    # Check if reference matches our tropical
    reference_tropical = 105.398471  # From earlier validation data
    print(f"\n\nReference Data Check:")
    print(f"  Reference might be tropical: {reference_tropical:.6f}°")
    print(f"  Our tropical: {asc_tropical:.6f}°")
    print(f"  Difference: {abs(reference_tropical - asc_tropical):.6f}°")

if __name__ == "__main__":
    debug_ascendant()