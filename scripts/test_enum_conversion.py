#!/usr/bin/env python3
"""
Test enum conversion to find the issue.
"""

import sys
sys.path.append('/Users/govind/Developer/astrow/src')

from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa

# Test enum conversions
def test_enum_conversions():
    print("Testing enum conversions...")
    
    try:
        # Test AstrologySystem
        print("\n1. Testing AstrologySystem...")
        vedic = AstrologySystem('vedic')
        print(f"   AstrologySystem('vedic') = {vedic}")
        print(f"   Type: {type(vedic)}")
        print(f"   Value: {vedic.value}")
        
        # Test list conversion
        print("\n2. Testing list conversion...")
        chart_types = ['vedic']
        systems = [AstrologySystem(ct) for ct in chart_types]
        print(f"   Systems: {systems}")
        
        # Test HouseSystem
        print("\n3. Testing HouseSystem...")
        hs = HouseSystem('whole_sign')
        print(f"   HouseSystem('whole_sign') = {hs}")
        
        # Test Ayanamsa
        print("\n4. Testing Ayanamsa...")
        ay = Ayanamsa('lahiri')
        print(f"   Ayanamsa('lahiri') = {ay}")
        
        # Test if None handling
        print("\n5. Testing None handling...")
        ay2 = Ayanamsa('lahiri') if 'lahiri' else Ayanamsa.LAHIRI
        print(f"   Ayanamsa with condition = {ay2}")
        
    except Exception as e:
        print(f"\nError occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enum_conversions()