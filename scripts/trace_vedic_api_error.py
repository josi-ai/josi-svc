#!/usr/bin/env python3
"""
Trace the exact location of the Vedic chart error by adding debug prints.
"""

import sys
sys.path.append('/Users/govind/Developer/astrow/src')

from datetime import datetime
import pytz
from josi.services.astrology_service import AstrologyCalculator
from josi.models.chart_model import AstrologySystem, HouseSystem, Ayanamsa

# Test Vedic calculation step by step
def trace_vedic_calculation():
    """Trace Vedic calculation to find where the error occurs."""
    
    print("1. Creating AstrologyCalculator...")
    calc = AstrologyCalculator()
    
    print("2. Setting ayanamsa...")
    calc.set_ayanamsa('lahiri')
    
    print("3. Creating datetime...")
    tz = pytz.timezone('Asia/Kolkata')
    dt = tz.localize(datetime(1990, 1, 15, 10, 30, 0))
    
    print("4. Calculating Vedic chart...")
    try:
        result = calc.calculate_vedic_chart(dt, 28.6139, 77.2090)
        print("✅ Vedic chart calculated successfully")
        print(f"   Keys: {list(result.keys())}")
        
        # Check the structure
        planets = result.get('planets', {})
        print(f"\n5. Checking planet data...")
        for planet, data in list(planets.items())[:2]:  # First 2 planets
            print(f"   {planet}: {list(data.keys())}")
            
    except Exception as e:
        print(f"❌ Error during calculation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    trace_vedic_calculation()