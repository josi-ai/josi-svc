#!/usr/bin/env python3
"""
Test swe.get_ayanamsa function signature.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import swisseph as swe

def test_ayanamsa():
    """Test swe.get_ayanamsa function."""
    jd = 2459431.0
    
    print("Testing swe.get_ayanamsa function:")
    print(f"Julian day: {jd}")
    
    # Test 1: With ayanamsa type
    print("\n1. Testing with ayanamsa type:")
    try:
        result = swe.get_ayanamsa(jd, swe.SIDM_LAHIRI)
        print(f"   ✅ SUCCESS: {result}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test 2: Just julian day
    print("\n2. Testing with just julian day:")
    try:
        result = swe.get_ayanamsa(jd)
        print(f"   ✅ SUCCESS: {result}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test 3: Different ayanamsa setting
    print("\n3. Testing with set_sid_mode first:")
    try:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        result = swe.get_ayanamsa(jd)
        print(f"   ✅ SUCCESS: {result}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Check documentation
    print("\n4. Checking documentation:")
    try:
        help(swe.get_ayanamsa)
    except:
        print("   No documentation available")

if __name__ == "__main__":
    test_ayanamsa()