#!/usr/bin/env python3
"""
Verify that Obama's ascendant is now calculated correctly.
Expected: ~318° (18° Aquarius) from pyswisseph
Previous bug: 176.51° (26.51° Virgo)
"""

from datetime import datetime
import pytz
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from josi.services.astrology_service import AstrologyCalculator

# Barack Obama's birth data
birth_data = {
    "date": "1961-08-04",
    "time": "19:24:00",
    "lat": 21.3099,
    "lon": -157.8581,
    "timezone": "Pacific/Honolulu"
}

# Create datetime object
tz = pytz.timezone(birth_data["timezone"])
birth_dt = tz.localize(datetime.strptime(
    f"{birth_data['date']} {birth_data['time']}", 
    "%Y-%m-%d %H:%M:%S"
))

print("🔍 Verifying Obama's Ascendant Calculation")
print("=" * 50)
print(f"Birth Date/Time: {birth_dt}")
print(f"Location: {birth_data['lat']}°N, {birth_data['lon']}°E")
print()

# Test the calculation
calculator = AstrologyCalculator()
chart = calculator.calculate_western_chart(
    birth_dt, 
    birth_data["lat"], 
    birth_data["lon"]
)

asc_longitude = chart["ascendant"]["longitude"]
asc_sign = chart["ascendant"]["sign"]

print("Result:")
print(f"  Ascendant: {asc_longitude:.2f}° ({asc_sign})")
print()

# Check if the fix worked
if 317 < asc_longitude < 319:  # Should be around 318°
    print("✅ SUCCESS: Ascendant calculation is correct!")
    print("   The timezone conversion bug has been fixed.")
elif 175 < asc_longitude < 178:  # The old buggy value
    print("❌ FAIL: Still getting the buggy value!")
    print("   The timezone conversion is not working correctly.")
else:
    print("⚠️  WARNING: Unexpected ascendant value!")
    print("   This is neither the correct nor the buggy value.")

print()
print("Additional Info:")
print(f"  Sun: {chart['planets']['Sun']['longitude']:.2f}° {chart['planets']['Sun']['sign']}")
print(f"  Moon: {chart['planets']['Moon']['longitude']:.2f}° {chart['planets']['Moon']['sign']}")
print(f"  First House: {chart['houses'][0]:.2f}°")
print(f"  MC (10th house): {chart['houses'][9]:.2f}°")