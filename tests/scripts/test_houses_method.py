#!/usr/bin/env python3
"""
Test the _calculate_houses method to see what it returns
"""

import swisseph as swe
from datetime import datetime
import pytz

# Add the src directory to the path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from josi.services.astrology_service import AstrologyCalculator

# Barack Obama's birth data
OBAMA_DATA = {
    "name": "Barack Obama",
    "date": "1961-08-04",
    "time": "19:24:00",
    "lat": 21.3099,
    "lon": -157.8581,
    "timezone": "Pacific/Honolulu"
}

# Create datetime
tz = pytz.timezone(OBAMA_DATA["timezone"])
birth_dt = tz.localize(datetime.strptime(
    f"{OBAMA_DATA['date']} {OBAMA_DATA['time']}", 
    "%Y-%m-%d %H:%M:%S"
))

# Test 1: Direct Swiss Ephemeris call
print("Direct Swiss Ephemeris call:")
print("-" * 40)
utc_dt = birth_dt.astimezone(pytz.UTC)
jd = swe.julday(
    utc_dt.year, utc_dt.month, utc_dt.day,
    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
)
houses_direct, ascmc_direct = swe.houses(jd, OBAMA_DATA["lat"], OBAMA_DATA["lon"], b'P')
print(f"Julian Day: {jd}")
print(f"ASC from houses[0]: {houses_direct[0]:.2f}°")
print(f"ASC from ascmc[0]: {ascmc_direct[0]:.2f}°")
print(f"First 3 houses: {[f'{h:.2f}' for h in houses_direct[:3]]}")
print()

# Test 2: Through AstrologyCalculator
print("Through AstrologyCalculator:")
print("-" * 40)
calc = AstrologyCalculator()

# Get Julian day through calculator
calc_jd = calc._datetime_to_julian(birth_dt)
print(f"Julian Day from calculator: {calc_jd}")

# Get houses through calculator
calc_houses = calc._calculate_houses(calc_jd, OBAMA_DATA["lat"], OBAMA_DATA["lon"])
print(f"ASC from calc houses[0]: {calc_houses[0]:.2f}°")
print(f"First 3 houses: {[f'{h:.2f}' for h in calc_houses[:3]]}")
print()

# Test 3: Full Western chart calculation
print("Full Western chart calculation:")
print("-" * 40)
western_chart = calc.calculate_western_chart(birth_dt, OBAMA_DATA["lat"], OBAMA_DATA["lon"])
print(f"ASC from chart: {western_chart['ascendant']['longitude']:.2f}°")
print(f"ASC sign: {western_chart['ascendant']['sign']}")
print(f"First 3 houses from chart: {[f'{h:.2f}' for h in western_chart['houses'][:3]]}")
print()

# Check if houses is a tuple or list
print("Type checking:")
print("-" * 40)
print(f"Type of houses_direct: {type(houses_direct)}")
print(f"Type of calc_houses: {type(calc_houses)}")
print(f"Type of chart houses: {type(western_chart['houses'])}")
print()

# Check if there's any difference
print("Differences:")
print("-" * 40)
print(f"JD difference: {calc_jd - jd}")
print(f"ASC difference: {calc_houses[0] - houses_direct[0]:.6f}°")

# Check if the issue is with houses being a tuple vs list
if isinstance(houses_direct, tuple) and isinstance(calc_houses, list):
    print("Note: houses_direct is tuple, calc_houses is list")
    
# Check the actual values
print(f"\nActual house values comparison:")
for i in range(12):
    diff = calc_houses[i] - houses_direct[i]
    if abs(diff) > 0.0001:
        print(f"  House {i+1}: direct={houses_direct[i]:.2f}°, calc={calc_houses[i]:.2f}°, diff={diff:.2f}°")