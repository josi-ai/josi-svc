#!/usr/bin/env python3
"""
Debug Janaki's calculation issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import logging
from src.josi.services.astrology_service import AstrologyCalculator

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def debug_janaki():
    """Debug Janaki's calculation."""
    
    calc = AstrologyCalculator()
    
    # Janaki's data
    dt = datetime(1960, 8, 24, 22, 10, 0)
    latitude = 13.0621
    longitude = 80.2209
    timezone = "Asia/Kolkata"
    
    print("\nDebugging Janaki's Chart Calculation")
    print("=" * 60)
    print(f"Input: {dt} {timezone}")
    print(f"Location: {latitude}, {longitude}")
    
    # Calculate chart
    chart = calc.calculate_vedic_chart(dt, latitude, longitude, timezone)
    
    # Show key outputs
    print(f"\nCalculated Values:")
    print(f"  Ascendant: {chart['ascendant']['longitude']:.6f}°")
    print(f"  Sun: {chart['planets']['Sun']['longitude']:.6f}°")
    print(f"  Moon: {chart['planets']['Moon']['longitude']:.6f}°")
    
    print(f"\nExpected Values:")
    print(f"  Ascendant: 297.277952°")
    print(f"  Sun: 242.313133°")  
    print(f"  Moon: 272.681321°")
    
    # Calculate tropical for comparison
    chart_tropical = calc.calculate_western_chart(dt, latitude, longitude, timezone)
    
    print(f"\nTropical Values:")
    print(f"  Ascendant: {chart_tropical['ascendant']['longitude']:.6f}°")
    print(f"  Sun: {chart_tropical['planets']['Sun']['longitude']:.6f}°")
    
    # Check if it's an ayanamsa issue
    ayanamsa = chart['ayanamsa']
    print(f"\nAyanamsa: {ayanamsa:.6f}°")
    
    # Manual check
    print(f"\nManual Conversion Check:")
    print(f"  Tropical Sun: {chart_tropical['planets']['Sun']['longitude']:.6f}°")
    print(f"  Minus Ayanamsa: {chart_tropical['planets']['Sun']['longitude'] - ayanamsa:.6f}°")
    print(f"  Our Sidereal: {chart['planets']['Sun']['longitude']:.6f}°")
    print(f"  Expected: 242.313133°")
    
    # Check if reference might be using different ayanamsa
    print(f"\nChecking different possibilities:")
    sun_tropical = chart_tropical['planets']['Sun']['longitude']
    print(f"  If ref uses no ayanamsa: {sun_tropical:.6f}°")
    print(f"  If ref uses our ayanamsa: {sun_tropical - ayanamsa:.6f}°")
    print(f"  If ref uses different time: Check timezone conversion")

if __name__ == "__main__":
    debug_janaki()