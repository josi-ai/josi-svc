#!/usr/bin/env python3
"""
Debug script to trace exactly where the Vedic chart error occurs.
"""

import sys
sys.path.append('/Users/govind/Developer/astrow/src')

import traceback
from datetime import datetime
import pytz
from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.panchang_service import PanchangCalculator

def test_vedic_calculation_step_by_step():
    """Test each step of Vedic calculation to isolate the error."""
    
    print("=== DEBUGGING VEDIC CHART CALCULATION ===\n")
    
    # Test data
    tz = pytz.timezone('Pacific/Honolulu')
    birth_time = tz.localize(datetime(1961, 8, 4, 19, 24, 0))
    latitude = 21.304547
    longitude = -157.8581
    timezone_str = "Pacific/Honolulu"
    
    try:
        print("1. Testing AstrologyCalculator initialization...")
        calc = AstrologyCalculator()
        print("   ✅ AstrologyCalculator created successfully")
        
        print("\n2. Testing set_ayanamsa...")
        calc.set_ayanamsa('lahiri')
        print("   ✅ Ayanamsa set successfully")
        
        print("\n3. Testing calculate_vedic_chart...")
        chart_data = calc.calculate_vedic_chart(birth_time, latitude, longitude)
        print("   ✅ Basic Vedic chart calculated successfully")
        print(f"   Keys: {list(chart_data.keys())}")
        
        print("\n4. Testing PanchangCalculator...")
        panchang_calc = PanchangCalculator()
        print("   ✅ PanchangCalculator created successfully")
        
        print("\n5. Testing calculate_panchang (this might be where it fails)...")
        panchang = panchang_calc.calculate_panchang(
            birth_time, latitude, longitude, timezone_str
        )
        print("   ✅ Panchang calculated successfully")
        print(f"   Panchang keys: {list(panchang.keys())}")
        
        print("\n🎉 All Vedic calculations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ ERROR FOUND: {type(e).__name__}: {e}")
        print("\n📍 FULL TRACEBACK:")
        traceback.print_exc()
        
        # Additional debug info
        print(f"\n🔍 ERROR DETAILS:")
        print(f"   - Error type: {type(e)}")
        print(f"   - Error message: '{str(e)}'")
        print(f"   - Arguments passed to function that failed:")
        
        # Check if it's the specific error we're looking for
        if "function takes at most 7 arguments" in str(e):
            print("\n🎯 FOUND THE TARGET ERROR!")
            print("   This is the exact error we've been debugging.")
        
        return False
    
    return True

if __name__ == "__main__":
    success = test_vedic_calculation_step_by_step()
    if success:
        print("\n✅ Vedic calculation works fine in isolation!")
        print("   The error must be occurring in the service layer integration.")
    else:
        print("\n❌ Found the source of the Vedic calculation error.")