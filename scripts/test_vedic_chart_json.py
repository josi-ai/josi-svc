#!/usr/bin/env python3
"""
Test if Vedic chart data can be serialized to JSON.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import json
from datetime import datetime
import pytz
from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.panchang_service import PanchangCalculator
from josi.services.vedic.dasha_service import VimshottariDashaCalculator
from josi.core.json_serializer import dumps as json_dumps

def test_vedic_chart_json_serialization():
    """Test if Vedic chart data can be serialized to JSON."""
    
    print("=== TESTING VEDIC CHART JSON SERIALIZATION ===\n")
    
    # Test data (Obama's birth info)
    tz = pytz.timezone('Pacific/Honolulu')
    birth_time = tz.localize(datetime(1961, 8, 4, 19, 24, 0))
    latitude = 21.304547
    longitude = -157.8581
    timezone_str = "Pacific/Honolulu"
    
    try:
        print("1. Testing basic Vedic chart calculation...")
        calc = AstrologyCalculator()
        calc.set_ayanamsa('lahiri')
        
        chart_data = calc.calculate_vedic_chart(birth_time, latitude, longitude)
        print("   ✅ Basic chart calculated")
        
        # Test JSON serialization of basic chart
        try:
            json_str = json.dumps(chart_data, indent=2)
            print("   ✅ Basic chart JSON serializable")
        except Exception as e:
            print(f"   ❌ Basic chart NOT JSON serializable: {e}")
            return False
        
        print("\n2. Testing panchang calculation...")
        panchang_calc = PanchangCalculator()
        panchang = panchang_calc.calculate_panchang(
            birth_time, latitude, longitude, timezone_str
        )
        print("   ✅ Panchang calculated")
        
        # Test JSON serialization of panchang
        try:
            json_str = json.dumps(panchang, indent=2)
            print("   ✅ Panchang JSON serializable")
        except Exception as e:
            print(f"   ❌ Panchang NOT JSON serializable: {e}")
            print(f"   Problem data type found in panchang")
            # Let's find the problematic field
            for key, value in panchang.items():
                try:
                    json.dumps({key: value})
                except Exception as sub_e:
                    print(f"      - Field '{key}': {type(value)} - {sub_e}")
            return False
        
        print("\n3. Testing dasha calculation...")
        dasha_calc = VimshottariDashaCalculator()
        moon_long = chart_data["planets"]["Moon"]["longitude"]
        dasha = dasha_calc.calculate_dasha_periods(
            birth_time, moon_long, include_antardashas=True
        )
        print("   ✅ Dasha calculated")
        
        # Test JSON serialization of dasha
        try:
            json_str = json_dumps(dasha, indent=2)
            print("   ✅ Dasha JSON serializable")
        except Exception as e:
            print(f"   ❌ Dasha NOT JSON serializable: {e}")
            print(f"   Problem data type found in dasha")
            # Let's find the problematic field
            for key, value in dasha.items():
                try:
                    json.dumps({key: value})
                except Exception as sub_e:
                    print(f"      - Field '{key}': {type(value)} - {sub_e}")
            return False
        
        print("\n4. Testing combined chart data...")
        combined_data = chart_data.copy()
        combined_data["panchang"] = panchang
        combined_data["dasha"] = dasha
        
        try:
            json_str = json_dumps(combined_data, indent=2)
            print("   ✅ Combined chart data JSON serializable")
            print(f"   JSON length: {len(json_str)} characters")
        except Exception as e:
            print(f"   ❌ Combined chart data NOT JSON serializable: {e}")
            return False
        
        print("\n🎉 All Vedic chart data is JSON serializable!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vedic_chart_json_serialization()
    if success:
        print("\n✅ Vedic chart JSON serialization test passed!")
    else:
        print("\n❌ Vedic chart JSON serialization test failed!")