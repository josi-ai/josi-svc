#!/usr/bin/env python3
"""
Test different argument patterns for swe.rise_trans to find the correct one.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import swisseph as swe
from datetime import datetime
import pytz

def test_rise_trans_signatures():
    """Test different argument patterns for swe.rise_trans."""
    
    print("=== TESTING SWE.RISE_TRANS FUNCTION SIGNATURES ===\n")
    
    # Test data
    jd = 2459431.0  # Some julian day
    latitude = 21.304547
    longitude = -157.8581
    
    print(f"Test parameters:")
    print(f"  jd: {jd}")
    print(f"  latitude: {latitude}")
    print(f"  longitude: {longitude}")
    print()
    
    # Test pattern 1: Like in muhurta_service (known working)
    print("1. Testing pattern from muhurta_service (known working):")
    try:
        result = swe.rise_trans(
            jd - 1,  # Start search from previous day
            swe.SUN,
            -longitude,  # Swiss Ephemeris uses negative longitude
            latitude,
            0,  # Sea level
            0,  # Atmospheric pressure
            0,  # Temperature
            swe.BIT_DISC_CENTER | swe.CALC_RISE
        )
        print(f"   ✅ SUCCESS: {result}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test pattern 2: Without BIT_DISC_CENTER
    print("\n2. Testing without BIT_DISC_CENTER:")
    try:
        result = swe.rise_trans(
            jd - 1,
            swe.SUN,
            -longitude,
            latitude,
            0,
            0,
            0,
            swe.CALC_RISE
        )
        print(f"   ✅ SUCCESS: {result}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test pattern 3: Only 6 arguments
    print("\n3. Testing with only 6 arguments:")
    try:
        result = swe.rise_trans(
            jd - 1,
            swe.SUN,
            -longitude,
            latitude,
            0,
            swe.CALC_RISE
        )
        print(f"   ✅ SUCCESS: {result}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test pattern 4: Only 5 arguments
    print("\n4. Testing with only 5 arguments:")
    try:
        result = swe.rise_trans(
            jd - 1,
            swe.SUN,
            -longitude,
            latitude,
            swe.CALC_RISE
        )
        print(f"   ✅ SUCCESS: {result}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test pattern 5: Different ordering
    print("\n5. Testing different parameter order:")
    try:
        result = swe.rise_trans(
            jd - 1,
            swe.SUN,
            longitude,  # Positive longitude
            latitude,
            swe.CALC_RISE
        )
        print(f"   ✅ SUCCESS: {result}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Let's also check the documentation
    print("\n6. Checking swe.rise_trans documentation:")
    try:
        help_text = help(swe.rise_trans)
        print(f"   Documentation: {help_text}")
    except Exception as e:
        print(f"   ❌ No documentation available: {e}")

if __name__ == "__main__":
    test_rise_trans_signatures()