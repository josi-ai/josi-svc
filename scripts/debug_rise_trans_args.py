#!/usr/bin/env python3
"""
Debug script to trace exactly what arguments are passed to rise_trans.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import swisseph as swe
from datetime import datetime
import pytz

def test_coordinate_types():
    """Test different data types for coordinates."""
    
    print("=== TESTING COORDINATE TYPES FOR RISE_TRANS ===\n")
    
    # Test data
    jd = 2459431.0
    latitude = 21.304547
    longitude = -157.8581
    
    print(f"Original values:")
    print(f"  latitude: {latitude} (type: {type(latitude)})")
    print(f"  longitude: {longitude} (type: {type(longitude)})")
    print()
    
    # Test 1: Exactly as in panchang service
    print("1. Testing panchang service pattern:")
    try:
        geopos = [longitude, latitude, 0]
        print(f"   geopos: {geopos}")
        print(f"   geopos types: {[type(x) for x in geopos]}")
        
        res_rise, times_rise = swe.rise_trans(
            jd - 1,
            swe.SUN,
            swe.CALC_RISE,
            geopos,
            0.0,
            0.0,
            swe.FLG_SWIEPH
        )
        print(f"   ✅ SUCCESS: res={res_rise}, time={times_rise[0] if res_rise == 0 else 'none'}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test 2: Force float conversion
    print("\n2. Testing with explicit float conversion:")
    try:
        geopos = [float(longitude), float(latitude), 0.0]
        print(f"   geopos: {geopos}")
        print(f"   geopos types: {[type(x) for x in geopos]}")
        
        res_rise, times_rise = swe.rise_trans(
            jd - 1,
            swe.SUN,
            swe.CALC_RISE,
            geopos,
            0.0,
            0.0,
            swe.FLG_SWIEPH
        )
        print(f"   ✅ SUCCESS: res={res_rise}, time={times_rise[0] if res_rise == 0 else 'none'}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test 3: With negative longitude
    print("\n3. Testing with negative longitude:")
    try:
        geopos = [float(-longitude), float(latitude), 0.0]
        print(f"   geopos: {geopos}")
        print(f"   geopos types: {[type(x) for x in geopos]}")
        
        res_rise, times_rise = swe.rise_trans(
            jd - 1,
            swe.SUN,
            swe.CALC_RISE,
            geopos,
            0.0,
            0.0,
            swe.FLG_SWIEPH
        )
        print(f"   ✅ SUCCESS: res={res_rise}, time={times_rise[0] if res_rise == 0 else 'none'}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    # Test 4: Check what happens with string values
    print("\n4. Testing with string longitude (to reproduce error):")
    try:
        geopos = [str(longitude), latitude, 0]  # Force string
        print(f"   geopos: {geopos}")
        print(f"   geopos types: {[type(x) for x in geopos]}")
        
        res_rise, times_rise = swe.rise_trans(
            jd - 1,
            swe.SUN,
            swe.CALC_RISE,
            geopos,
            0.0,
            0.0,
            swe.FLG_SWIEPH
        )
        print(f"   ✅ SUCCESS: res={res_rise}, time={times_rise[0] if res_rise == 0 else 'none'}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        if "must be a float or int" in str(e):
            print("   🎯 This reproduces the error!")

if __name__ == "__main__":
    test_coordinate_types()