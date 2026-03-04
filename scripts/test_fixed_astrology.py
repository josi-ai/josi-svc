#!/usr/bin/env python3
"""
Test the fixed astrology service with speed calculations
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from josi.services.astrology_service import AstrologyCalculator
from datetime import datetime
import pytz

# Test with Archana's birth data
calc = AstrologyCalculator()
dt = datetime(1998, 12, 7, 21, 15)

# Test Vedic chart calculation
print("=== TESTING FIXED VEDIC CHART CALCULATION ===")
chart = calc.calculate_vedic_chart(dt, 13.0827, 80.2707, 'Asia/Kolkata')

print("Planet speeds from astrology service:")
for planet_name, planet_data in chart['planets'].items():
    speed = planet_data['speed']
    is_retrograde = speed < 0
    print(f"{planet_name:8}: speed={speed:8.4f}°/day {'(RETROGRADE)' if is_retrograde else '(direct)'}")

print("\n=== TESTING WESTERN CHART CALCULATION ===")
western_chart = calc.calculate_western_chart(dt, 13.0827, 80.2707)

print("Planet speeds from Western chart:")
for planet_name, planet_data in western_chart['planets'].items():
    speed = planet_data['speed']
    is_retrograde = speed < 0
    print(f"{planet_name:8}: speed={speed:8.4f}°/day {'(RETROGRADE)' if is_retrograde else '(direct)'}")

print("\n=== RETROGRADE PLANETS ===")
retrograde_planets = []
for planet_name, planet_data in chart['planets'].items():
    if planet_data['speed'] < 0:
        retrograde_planets.append(planet_name)

if retrograde_planets:
    print(f"Retrograde planets: {', '.join(retrograde_planets)}")
else:
    print("No retrograde planets found")

print("\n=== EXPECTED RETROGRADE PLANETS FOR DEC 1998 ===")
print("According to astronomical data, Mercury and Saturn were retrograde in Dec 1998")
print("Let's check if our calculations match:")