#!/usr/bin/env python3
"""
Test Swiss Ephemeris speeds directly
"""
import swisseph as swe
from datetime import datetime
import pytz

# Test with Archana's birth data
dt = datetime(1998, 12, 7, 21, 15)
tz = pytz.timezone('Asia/Kolkata')
dt = tz.localize(dt)

# Convert to Julian day
utc_dt = dt.astimezone(pytz.UTC)
decimal_hour = (utc_dt.hour * 3600.0 + 
               utc_dt.minute * 60.0 + 
               utc_dt.second + 
               utc_dt.microsecond / 1e6) / 3600.0

julian_day = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)

print(f"Julian day: {julian_day}")
print(f"Date: {dt}")
print()

# Test planetary speeds
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
}

print("=== DIRECT SWISS EPHEMERIS SPEEDS ===")
for planet_name, planet_id in PLANETS.items():
    result = swe.calc(julian_day, planet_id, swe.FLG_SIDEREAL)
    print(f"{planet_name:8}: full result = {result}")
    print(f"         : result[0] = {result[0]}")
    print(f"         : len(result[0]) = {len(result[0])}")
    longitude = result[0][0]
    latitude = result[0][1]
    speed = result[0][3]
    print(f"         : longitude={longitude:7.2f}°, latitude={latitude:7.2f}°, speed={speed:8.4f}°/day")
    
    # Check if retrograde
    if speed < 0:
        print(f"         -> {planet_name} is RETROGRADE!")
    print()

print("=== TESTING WITH DIFFERENT FLAGS ===")
test_planet = swe.SUN
print(f"Testing with Sun (planet_id={test_planet})")
print(f"Julian day: {julian_day}")

# Test different flag combinations
flags_to_test = [
    (0, "No flags (tropical)"),
    (swe.FLG_SIDEREAL, "Sidereal"),
    (swe.FLG_SPEED, "Speed flag"),
    (swe.FLG_SIDEREAL | swe.FLG_SPEED, "Sidereal + Speed flag"),
]

for flag, description in flags_to_test:
    try:
        result = swe.calc(julian_day, test_planet, flag)
        print(f"{description:25}: {result}")
    except Exception as e:
        print(f"{description:25}: ERROR - {e}")

print("\n=== SWISS EPHEMERIS VERSION INFO ===")
print(f"Swiss Ephemeris version: {swe.get_library_path()}")
print(f"Available flags: {[attr for attr in dir(swe) if attr.startswith('FLG_')][:10]}")

print("\n=== TESTING CALC_UT FUNCTION ===")
# Try the calc_ut function which might be more appropriate
try:
    result_ut = swe.calc_ut(julian_day, swe.SUN, swe.FLG_SIDEREAL)
    print(f"calc_ut result: {result_ut}")
except Exception as e:
    print(f"calc_ut error: {e}")